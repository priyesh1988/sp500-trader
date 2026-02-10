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

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
