import asyncio
import logging
from logging.handlers import RotatingFileHandler
from microapi import app
from models import Application, SessionLocal
from telegram import Update
from telegram.ext import Application as TelegramApplication, CommandHandler, ContextTypes
from user import UserCreate, User, hash_password

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

file_handler = RotatingFileHandler('app.log', maxBytes=1024*1024, backupCount=5)
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

TOKEN = '7378792011:AAFxT5ebUjpHLRmQkn1047vRpdtWkg1Ai0c'


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Здравствуйте! Пожалуйста, оставьте вашу "
                                                                              "заявку командой /apply <ваша заявка>")
    except Exception as e:
        logger.error(f"Error in start handler: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Произошла ошибка. Пожалуйста, попробуйте"
                                                                              " позже.")


async def apply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    application_text = ' '.join(context.args)
    if application_text:
        try:
            async with SessionLocal() as db:
                db_application = Application(application=application_text)
                db.add(db_application)
                await db.commit()
                await db.close()
                await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Ваша заявка "{application_text}'
                                                                                      f'" была принята!')
                logger.info(f"Application sent: {application_text}")
        except Exception as e:
            logger.error(f"Error in apply handler: {e}")
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Произошла ошибка при отправке "
                                                                                  "заявки. Пожалуйста, попробуйте "
                                                                                  "позже.")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Пожалуйста, напишите текст заявки после '
                                                                              'команды /apply')
        logger.info(f"Empty application text sent")


async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Пожалуйста, отправьте ваш email и пароль в "
                                                                          "формате: /register_user <email> <password>")


async def register_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        email, password = context.args
        user_data = UserCreate(email=email, password=password)
        async with SessionLocal() as db:
            db_user = User(email=user_data.email, hashed_password=hash_password(user_data.password))
            db.add(db_user)
            await db.commit()
            await db.refresh(db_user)
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Регистрация успешна!")
        logger.info(f"User registered: {user_data}")
    except Exception as e:
        logger.error(f"User registration failed: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Произошла ошибка при регистрации. "
                                                                              "Пожалуйста, попробуйте позже.")


telegram_application = TelegramApplication.builder().token(TOKEN).build()  # Инициализация бота
telegram_application.add_handler(CommandHandler("start", start))
telegram_application.add_handler(CommandHandler("apply", apply))
telegram_application.add_handler(CommandHandler("register", register))
telegram_application.add_handler(CommandHandler("register_user", register_user))


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
