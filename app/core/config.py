from pydantic_settings import BaseSettings


class Settings(BaseSettings): # Настройки приложения
    DATABASE_URL: str = "postgresql+asyncpg://vova:ghbdtnkjk@localhost:5432/ApplReceiver"
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    TELEGRAM_TOKEN: str = "7378792011:AAFxT5ebUjpHLRmQkn1047vRpdtWkg1Ai0c"


settings = Settings()
