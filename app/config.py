from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_env: str = "dev"
    database_url: str
    redis_url: str

    alpaca_base_url: str
    alpaca_key_id: str
    alpaca_secret_key: str

    symbol: str = "SPY"
    lookback_days: int = 50
    max_trades_per_day: int = 1
    min_hold_days: int = 2
    EXIT_ENABLED = True
    TAKE_PROFIT_PCT = 0.03
    STOP_LOSS_PCT = 0.015
    TRAILING_STOP_PCT = 0.012  # set to None / empty to disable
    MAX_HOLD_DAYS = 10


    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
