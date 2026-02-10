from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from .db import Base, engine, get_db
from .config import settings
from .schemas import HealthResponse, SignalResponse, RebalanceResponse, ToggleRequest, StrategyStateResponse
from .strategy import compute_target_weight
from .rebalance import rebalance_to_target, get_or_create_state
from .tasks import start_scheduler

Base.metadata.create_all(bind=engine)

app = FastAPI(title="S&P 500 Short-Term Signal Trader")

@app.on_event("startup")
def _startup():
    # Comment out if you only want manual runs.
    start_scheduler()

@app.get("/health", response_model=HealthResponse)
def health():
    return {"status": "ok"}

@app.get("/state", response_model=StrategyStateResponse)
def state(db: Session = Depends(get_db)):
    st = get_or_create_state(db, settings.symbol)
    return StrategyStateResponse(
        symbol=st.symbol,
        target_weight=st.target_weight,
        enabled=st.enabled,
        last_rebalance_at=st.last_rebalance_at,
        last_trade_day=st.last_trade_day,
        trades_today=st.trades_today,
        hold_until_day=st.hold_until_day,
    )

@app.post("/state/toggle", response_model=StrategyStateResponse)
def toggle(req: ToggleRequest, db: Session = Depends(get_db)):
    st = get_or_create_state(db, settings.symbol)
    st.enabled = req.enabled
    db.commit()
    db.refresh(st)
    return StrategyStateResponse(
        symbol=st.symbol,
        target_weight=st.target_weight,
        enabled=st.enabled,
        last_rebalance_at=st.last_rebalance_at,
        last_trade_day=st.last_trade_day,
        trades_today=st.trades_today,
        hold_until_day=st.hold_until_day,
    )

@app.get("/signal", response_model=SignalResponse)
async def signal():
    s = await compute_target_weight(settings.symbol)
    return s

@app.post("/rebalance", response_model=RebalanceResponse)
async def rebalance(db: Session = Depends(get_db)):
    s = await compute_target_weight(settings.symbol)
    placed, note = await rebalance_to_target(db, settings.symbol, s["target_weight"])
    return RebalanceResponse(
        symbol=settings.symbol,
        target_weight=s["target_weight"],
        placed_order=placed,
        note=note,
        at=datetime.now(timezone.utc),
    )
