# S&P 500 Short-Term Signal Trader

This app:

- Computes a simple trend signal on SPY (price vs SMA)
- Rebalances to 0% or 100% SPY using Alpaca paper trading
- Adds guardrails: max trades/day + minimum hold window

## Setup
1) Create Alpaca paper keys
2) Copy env:
   cp .env.example .env
   # fill ALPACA_KEY_ID and ALPACA_SECRET_KEY

3) Run:
   docker compose up

## Use
- Health: GET http://localhost:8000/health
- Signal: GET http://localhost:8000/signal
- Rebalance now: POST http://localhost:8000/rebalance
- State: GET http://localhost:8000/state
- Disable: POST /state/toggle  {"enabled": false}

---

## Disciplined Exits (Next Layer of Systematic Portfolio Control)

Building on systematic portfolio control — here’s the next layer: **disciplined exits**.

There are multiple risk-controlled exit frameworks, but almost all of them are derived from the two below:

### 1) Time-Based Exit Strategy — “Capital efficiency over prediction.”
If a position does not hit its target within a defined time window (e.g., **5–10 trading days**), it exits — **regardless of P&L**.

Why?
- Reduces capital lock-up
- Prevents “hope-driven” holding
- Improves turnover discipline
- Forces systematic reassessment

This converts uncertainty into bounded exposure.

### 2) Profit/Loss-Based Exit Strategy — “Cut outcomes, not emotions.”
Each position carries predefined controls:
- Take-profit (e.g., **+3%**)
- Stop-loss (e.g., **-1.5%**)
- Optional trailing stop

**Inputs per position**
- `take_profit_pct` (e.g., +3%)
- `stop_loss_pct` (e.g., -1.5%)
- `max_hold_days` (e.g., 10 trading days)
- Optional: `trailing_stop_pct` (e.g., 1.2% from peak)

**Decision rules (per symbol)**
- If `price >= entry_price * (1 + take_profit_pct)` → **SELL** (take profit)
- If `price <= entry_price * (1 - stop_loss_pct)` → **SELL** (stop loss)
- If `days_held >= max_hold_days` → **SELL** (time exit)
- If using trailing stop:
  - track peak price since entry
  - if `price <= peak * (1 - trailing_stop_pct)` → **SELL** (protect gains)

This gives you:
- quick profit capture
- loss containment
- bounded time exposure (reduces “stuck positions”)

It’s about controlling distribution shape — compressing losses and harvesting small wins consistently.


## Disclaimer
- Market data endpoint requires Alpaca data permissions in some accounts.
- This is a starter. Add risk controls, logging, idempotency, and better execution logic before real money.


