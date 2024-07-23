from fastapi import FastAPI
from telegram.ext import ApplicationBuilder, CommandHandler
from app.core.dependencies import init_db, shutdown_db
from app.api import applications, auth, users
from app.core.config import settings
from app.telegram_bot.handlers import start, apply, register

TOKEN = settings.TELEGRAM_TOKEN


def create_app() -> FastAPI: # функция для создания приложения
    app = FastAPI() # создаем приложение

    # подключаем маршрутизаторы
    app.include_router(applications.router, prefix="/applications", tags=["applications"])
    app.include_router(auth.router, prefix="/auth", tags=["auth"])
    app.include_router(users.router, prefix="/users", tags=["users"])

    @app.on_event("startup")
    async def startup():
        await init_db()
        app.bot = ApplicationBuilder().token(TOKEN).build()
        app.bot.add_handler(CommandHandler("start", start))
        app.bot.add_handler(CommandHandler("apply", apply))
        app.bot.add_handler(CommandHandler("register", register))
        await app.bot.initialize()
        await app.bot.start()
        await app.bot.updater.start_polling()

    @app.on_event("shutdown")
    async def shutdown():
        await shutdown_db()
        if hasattr(app, 'bot'):
            await app.bot.updater.stop()
            await app.bot.stop()
            await app.bot.shutdown()

    return app
