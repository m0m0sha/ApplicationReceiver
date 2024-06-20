import asyncio
from microapi import app
from models import Application, SessionLocal
from telegram import Update
from telegram.ext import Application as TelegramApplication, CommandHandler, ContextTypes

TOKEN = '7378792011:AAFxT5ebUjpHLRmQkn1047vRpdtWkg1Ai0c'


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):  # Update содержит инфу о полученном сообщении
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Здравствуйте! Пожалуйста, оставьте вашу "
                                                                          "заявку командой /apply <ваша заявка>")


async def apply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    application_text = ' '.join(context.args)
    if application_text:
        async with SessionLocal() as db:
            db_application = Application(application=application_text)
            db.add(db_application)
            await db.commit()
            await db.close()
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Ваша заявка "{application_text}" была '
                                                                                  'принята!')
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Пожалуйста, напишите текст заявки после '
                                                                              'команды /apply')

telegram_application = TelegramApplication.builder().token(TOKEN).build()  # Инициализация бота
telegram_application.add_handler(CommandHandler("start", start))
telegram_application.add_handler(CommandHandler("apply", apply))


async def run_telegram_bot():
    await telegram_application.initialize()
    await telegram_application.start()
    await telegram_application.updater.start_polling()  # Бесконечный цикл опроса обновлений


async def stop_telegram_bot():
    await telegram_application.updater.stop()  # Остановка цикла опроса обновлений
    await telegram_application.stop()
    await telegram_application.shutdown()


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(run_telegram_bot())


@app.on_event("shutdown")
async def shutdown_event():
    await stop_telegram_bot()
