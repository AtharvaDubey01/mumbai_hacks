from pydantic import BaseSettings

class Settings(BaseSettings):
    MONGO_URI: str
    NEWSAPI_KEY: str | None = None
    OPENAI_API_KEY: str | None = None
    HUGGINGFACE_API_KEY: str | None = None
    GOOGLE_CSE_API_KEY: str | None = None
    GOOGLE_CSE_ID: str | None = None
    SCHED_RUN_INTERVAL_MIN: int = 10
    JWT_SECRET: str = "devsecret"
    PORT: int = 8000

    class Config:
        env_file = "../.env"

settings = Settings()
