from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra="ignore")

    RPC_URL: str = ""
    GRAPH_API_KEY: str = ""
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    CACHE_TTL_SHORT: int = 60
    CACHE_TTL_MEDIUM: int = 300
    CACHE_TTL_LONG: int = 3600
    ADMIN_SECRET: str = "changeme"
    ETHERSCAN_API_KEY: str = ""

settings = Settings()
