# app/exits.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone, date

@dataclass
class ExitConfig:
    enabled: bool = True
    # Profit/Loss exits
    take_profit_pct: float = 0.03      # +3%
    stop_loss_pct: float = 0.015       # -1.5%
    trailing_stop_pct: float | None = 0.012  # 1.2% from peak, set None to disable

    # Time-based exit
    max_hold_days: int = 10

@dataclass
class ExitSignal:
    should_exit: bool
    reason: str | None = None
    pnl_pct: float | None = None

def _days_held(entry_at: datetime | None, now: datetime) -> int:
    if not entry_at:
        return 0
    # Approx calendar-day hold. If you want trading-day precision later, plug in a market calendar.
    return max(0, (now.date() - entry_at.date()).days)

def evaluate_exit(
    *,
    in_position: bool,
    current_price: float,
    entry_price: float | None,
    entry_at: datetime | None,
    peak_price: float | None,
    now: datetime,
    cfg: ExitConfig,
) -> tuple[ExitSignal, float]:
    """
    Returns (ExitSignal, updated_peak_price)
    """
    if not cfg.enabled or not in_position or not entry_price:
        return ExitSignal(False), peak_price or current_price

    updated_peak = max(peak_price or entry_price, current_price)
    pnl_pct = (current_price / entry_price) - 1.0

    # 1) Take-profit
    if pnl_pct >= cfg.take_profit_pct:
        return ExitSignal(True, "TAKE_PROFIT", pnl_pct), updated_peak

    # 2) Stop-loss
    if pnl_pct <= -cfg.stop_loss_pct:
        return ExitSignal(True, "STOP_LOSS", pnl_pct), updated_peak

    # 3) Trailing stop
    if cfg.trailing_stop_pct is not None:
        if current_price <= updated_peak * (1.0 - cfg.trailing_stop_pct):
            return ExitSignal(True, "TRAILING_STOP", pnl_pct), updated_peak

    # 4) Time-based exit
    held = _days_held(entry_at, now)
    if held >= cfg.max_hold_days:
        return ExitSignal(True, "TIME_EXIT", pnl_pct), updated_peak

    return ExitSignal(False), updated_peak
