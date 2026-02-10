from datetime import datetime, timezone, date, timedelta
from sqlalchemy.orm import Session
from .config import settings
from .models import StrategyState, AuditLog
from .broker_alpaca import AlpacaBroker

def ymd(d: date) -> str:
    return d.isoformat()

def log(db: Session, event_type: str, message: str):
    db.add(AuditLog(event_type=event_type, message=message))
    db.commit()

def get_or_create_state(db: Session, symbol: str) -> StrategyState:
    st = db.query(StrategyState).filter(StrategyState.symbol == symbol).first()
    if not st:
        st = StrategyState(symbol=symbol, target_weight=0.0, enabled=True, trades_today=0)
        db.add(st)
        db.commit()
        db.refresh(st)
    return st

def reset_daily_counters_if_needed(st: StrategyState):
    today = ymd(date.today())
    if st.last_trade_day != today:
        st.last_trade_day = today
        st.trades_today = 0

def in_hold_period(st: StrategyState) -> bool:
    if not st.hold_until_day:
        return False
    return st.hold_until_day >= ymd(date.today())

async def rebalance_to_target(db: Session, symbol: str, target_weight: float) -> tuple[bool, str]:
    broker = AlpacaBroker()
    st = get_or_create_state(db, symbol)
    reset_daily_counters_if_needed(st)

    if not st.enabled:
        return False, "Strategy disabled."

    if in_hold_period(st):
        return False, f"In hold period until {st.hold_until_day}."

    if st.trades_today >= settings.max_trades_per_day:
        return False, "Trade limit reached for today."

    # Get account equity and current position
    acct = await broker.get_account()
    equity = float(acct["equity"])  # total account equity in USD
    price = await broker.get_last_trade_price(symbol)
    current_qty = await broker.get_position_qty(symbol)

    current_value = current_qty * price
    target_value = equity * target_weight

    diff_value = target_value - current_value

    # Ignore tiny diffs to avoid churn
    if abs(diff_value) < max(10.0, equity * 0.001):  # $10 or 0.1%
        st.target_weight = target_weight
        st.last_rebalance_at = datetime.now(timezone.utc)
        db.commit()
        return False, "No meaningful rebalance needed."

    qty = abs(diff_value) / price
    # Keep qty reasonable; Alpaca accepts fractional shares depending on asset/account.
    qty = round(qty, 4)

    if qty <= 0:
        return False, "Computed qty is zero."

    side = "buy" if diff_value > 0 else "sell"
    await broker.submit_market_order(symbol, qty=qty, side=side)

    # Update state + enforce a minimum hold window
    st.target_weight = target_weight
    st.last_rebalance_at = datetime.now(timezone.utc)
    st.trades_today += 1
    st.hold_until_day = ymd(date.today() + timedelta(days=settings.min_hold_days))
    db.commit()

    log(db, "rebalance", f"{side.upper()} {qty} {symbol} @~{price:.2f} to target {target_weight:.2f}")

    return True, f"Order placed: {side} {qty} {symbol}"
