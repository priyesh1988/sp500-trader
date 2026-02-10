import asyncio
from apscheduler.schedulers.background import BackgroundScheduler
from .db import SessionLocal
from .config import settings
from .strategy import compute_target_weight
from .rebalance import rebalance_to_target

scheduler = BackgroundScheduler()

def run_daily():
    # In dev, you can call /rebalance manually; this shows how to automate.
    async def job():
        signal = await compute_target_weight(settings.symbol)
        db = SessionLocal()
        try:
            await rebalance_to_target(db, settings.symbol, signal["target_weight"])
        finally:
            db.close()

    asyncio.run(job())

def start_scheduler():
    # Runs every weekday at 1pm UTC by default here (simple starter).
    # Adjust for market close/open as you like.
    scheduler.add_job(run_daily, "cron", day_of_week="mon-fri", hour=13, minute=0)
    scheduler.start()
