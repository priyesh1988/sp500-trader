from datetime import datetime, timedelta, timezone
import httpx
from .config import settings

class AlpacaBroker:
    def __init__(self):
        self.base = settings.alpaca_base_url.rstrip("/")
        self.headers = {
            "APCA-API-KEY-ID": settings.alpaca_key_id,
            "APCA-API-SECRET-KEY": settings.alpaca_secret_key,
        }

    async def get_account(self) -> dict:
        async with httpx.AsyncClient(timeout=20) as c:
            r = await c.get(f"{self.base}/v2/account", headers=self.headers)
            r.raise_for_status()
            return r.json()

    async def get_position_qty(self, symbol: str) -> float:
        async with httpx.AsyncClient(timeout=20) as c:
            r = await c.get(f"{self.base}/v2/positions/{symbol}", headers=self.headers)
            if r.status_code == 404:
                return 0.0
            r.raise_for_status()
            data = r.json()
            return float(data.get("qty", 0))

    async def get_last_trade_price(self, symbol: str) -> float:
        # Alpaca market data requires separate endpoints/permissions in some setups.
        # This starter uses the "bars" endpoint via data.alpaca.markets (v2).
        # If you don't have market data enabled, swap to a free data source for backtesting only.
        data_base = "https://data.alpaca.markets"
        params = {"symbols": symbol, "timeframe": "1Day", "limit": 1}
        async with httpx.AsyncClient(timeout=20) as c:
            r = await c.get(f"{data_base}/v2/stocks/bars", headers=self.headers, params=params)
            r.raise_for_status()
            j = r.json()
            bar = j["bars"][symbol][0]
            return float(bar["c"])

    async def get_daily_closes(self, symbol: str, limit: int) -> list[float]:
        data_base = "https://data.alpaca.markets"

        # Ask for a real time window so Alpaca returns enough bars
        start = (datetime.now(timezone.utc) - timedelta(days=max(120, limit * 3))).isoformat()

        params = {
            "symbols": symbol,
            "timeframe": "1Day",
            "start": start,
            "limit": limit,
            "adjustment": "all",
        }

        async with httpx.AsyncClient(timeout=20) as c:
            r = await c.get(f"{data_base}/v2/stocks/bars", headers=self.headers, params=params)
            r.raise_for_status()
            j = r.json()
            bars = j.get("bars", {}).get(symbol, [])
            closes = [float(b["c"]) for b in bars]
            return closes

    async def submit_market_order(self, symbol: str, qty: float, side: str) -> dict:
        payload = {
            "symbol": symbol,
            "qty": str(qty),
            "side": side,            # "buy" or "sell"
            "type": "market",
            "time_in_force": "day",
        }
        async with httpx.AsyncClient(timeout=20) as c:
            r = await c.post(f"{self.base}/v2/orders", headers=self.headers, json=payload)
            r.raise_for_status()
            return r.json()
