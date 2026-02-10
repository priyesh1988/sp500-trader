from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class HealthResponse(BaseModel):
    status: str

class SignalResponse(BaseModel):
    symbol: str
    lookback_days: int
    close: float
    sma: float
    target_weight: float
    computed_at: datetime

class RebalanceResponse(BaseModel):
    symbol: str
    target_weight: float
    placed_order: bool
    note: str
    at: datetime

class ToggleRequest(BaseModel):
    enabled: bool

class StrategyStateResponse(BaseModel):
    symbol: str
    target_weight: float
    enabled: bool
    last_rebalance_at: Optional[datetime] = None
    last_trade_day: Optional[str] = None
    trades_today: int
    hold_until_day: Optional[str] = None
