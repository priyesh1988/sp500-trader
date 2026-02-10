from sqlalchemy import String, Integer, DateTime, Boolean, Float, func
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base

class StrategyState(Base):
    __tablename__ = "strategy_state"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    symbol: Mapped[str] = mapped_column(String(16), index=True)
    target_weight: Mapped[float] = mapped_column(Float, default=0.0)  # 0.0 or 1.0 for now
    last_rebalance_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=True)
    last_trade_day: Mapped[str] = mapped_column(String(10), nullable=True)  # YYYY-MM-DD
    trades_today: Mapped[int] = mapped_column(Integer, default=0)
    hold_until_day: Mapped[str] = mapped_column(String(10), nullable=True)  # YYYY-MM-DD
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    event_type: Mapped[str] = mapped_column(String(64), index=True)
    message: Mapped[str] = mapped_column(String(2048))
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
