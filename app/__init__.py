from fastapi import FastAPI
from app.api import applications, auth, users
from app.core.config import settings
from app.core.dependencies import init_db, shutdown_db
from app.telegram_bot.bot import run_telegram_bot, stop_telegram_bot

app = FastAPI() # Инициализация приложения


@app.on_event("startup") # Событие запуска приложения
async def startup_event():
    await init_db()
    await run_telegram_bot()


@app.on_event("shutdown") # Событие остановки приложения
async def shutdown_event():
    await shutdown_db()
    await stop_telegram_bot()

app.include_router(applications.router, prefix="/applications", tags=["applications"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
