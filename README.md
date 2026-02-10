# S&P 500 Short-Term Signal Trader

This app:
- Computes a simple trend signal on SPY (price vs SMA)
- Rebalances to 0% or 100% SPY using Alpaca trading
- Adds guardrails: max trades/day + minimum hold window

## Setup
1) Create Alpaca keys
2) Copy env:
   cp .env.example .env
   -- fill ALPACA_KEY_ID and ALPACA_SECRET_KEY

3) Run:
   docker compose up

## Use
- Health: GET http://localhost:8000/health
- Signal: GET http://localhost:8000/signal
- Rebalance now: POST http://localhost:8000/rebalance
- State: GET http://localhost:8000/state
- Disable: POST /state/toggle  {"enabled": false}

## Example

Example where the system says “invest in SPY”

Signal: GET /signal
{
  "symbol": "SPY",
  "lookback_days": 50,
  "close": 680.42,
  "sma": 665.10,
  "target_weight": 1.0,
  "computed_at": "2026-02-10T15:45:12.331980Z"
}

Because:
close (680.42)  >  sma (665.10)

So the rule says:
👉 Risk-on → fully invested in SPY

POST /rebalance would try to buy enough SPY to make your portfolio 100% SPY.

## Disclaimer
- Market data endpoint requires Alpaca data permissions in some accounts.
- This is a starter. Add risk controls, logging, idempotency, and better execution logic before real money.
