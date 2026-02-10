from datetime import datetime, timezone
from .config import settings
from .broker_alpaca import AlpacaBroker

def sma(values: list[float]) -> float:
    return sum(values) / max(len(values), 1)

async def compute_target_weight(symbol: str) -> dict:
    broker = AlpacaBroker()
    closes = await broker.get_daily_closes(symbol, limit=settings.lookback_days + 1)
    if len(closes) < settings.lookback_days:
        # return a graceful response instead of 500
        raise RuntimeError(f"Need {settings.lookback_days} bars, got {len(closes)}.")

    close = closes[-1]
    s = sma(closes[-settings.lookback_days:])

    # Simple rule:
    # if price above SMA => 100% invested, else 0% (cash)
    target = 1.0 if close > s else 0.0

    return {
        "symbol": symbol,
        "lookback_days": settings.lookback_days,
        "close": float(close),
        "sma": float(s),
        "target_weight": float(target),
        "computed_at": datetime.now(timezone.utc),
    }
