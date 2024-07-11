from telegram import Update
from telegram.ext import ContextTypes
from app.db.models import Application, User, SessionLocal
from app.db.schemas import UserCreate
from app.utils.logger import logger
from app.utils.security import hash_password
from app.telegram_bot.telegram_operations import send_message
from app.utils.errors import SendMessageError, DatabaseError, UserExists, UserNotFound


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    try:
        await send_message(context, chat_id, "Здравствуйте! Пожалуйста, оставьте вашу заявку командой /apply <ваша "
                                             "заявка>")
        logger.info("Sent start message successfully")
    except SendMessageError as e:
        logger.error(f"Error in start function: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in start function: {str(e)}")


async def apply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    application_text = ' '.join(context.args)
    chat_id = update.effective_chat.id

    if not application_text:
        try:
            await send_message(context, chat_id, 'Пожалуйста, напишите текст заявки после команды /apply')
            logger.info("Empty application text sent")
        except SendMessageError as e:
            logger.error(f"Error sending empty application text: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in apply function: {str(e)}")
        return

    try:
        async with SessionLocal() as db:
            db_application = Application(application=application_text)
            db.add(db_application)
            await db.commit()
            await send_message(context, chat_id, f'Ваша заявка "{application_text}" была принята!')
        logger.info(f"Application sent: {application_text}")
    except DatabaseError as e:
        logger.error(f"Database error in apply function: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in apply function: {str(e)}")


async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not context.args:
        try:
            await send_message(context, chat_id, "Пожалуйста, отправьте ваш email и пароль в формате: /register <email>"
                                                 "<password>")
        except SendMessageError as e:
            logger.error(f"Error sending registration prompt: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in register function: {str(e)}")
        return

    email, password = context.args
    try:
        async with SessionLocal() as db:
            user_data = UserCreate(email=email, password=password)
            db_user = User(email=user_data.email, hashed_password=hash_password(user_data.password))
            db.add(db_user)
            await db.commit()
            await db.refresh(db_user)
        try:
            await send_message(context, chat_id, "Регистрация успешна!")
        except SendMessageError as e:
            logger.error(f"Error sending registration success message: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in register function: {str(e)}")
        logger.info(f"User registered: {user_data.email}")
    except DatabaseError as e:
        logger.error(f"Database error in register function: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in register function: {str(e)}")
