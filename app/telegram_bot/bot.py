from telegram.ext import Application as TelegramApplication, CommandHandler
from app import settings
from app.telegram_bot.handlers import start, apply, register

TOKEN = settings.TELEGRAM_TOKEN # Токен бота

telegram_application = TelegramApplication.builder().token(TOKEN).build() # Инициализация бота
telegram_application.add_handler(CommandHandler("start", start))
telegram_application.add_handler(CommandHandler("apply", apply))
telegram_application.add_handler(CommandHandler("register", register))


async def run_telegram_bot(): # Запуск бота
    await telegram_application.initialize()
    await telegram_application.start()
    await telegram_application.updater.start_polling()


async def stop_telegram_bot(): # Остановка бота
    await telegram_application.updater.stop()
    await telegram_application.stop()
    await telegram_application.shutdown()
