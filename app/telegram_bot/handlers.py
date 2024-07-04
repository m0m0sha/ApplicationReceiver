from telegram import Update
from telegram.ext import ContextTypes
from app.db.models import Application, SessionLocal, User
from app.db.schemas import UserCreate
from app.utils.logger import logger
from app.utils.security import hash_password


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): # Обработчик команды /start
    try:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Здравствуйте! Пожалуйста, оставьте вашу "
                                                                              "заявку командой /apply <ваша заявка>")
    except Exception as e:
        logger.error(f"Error in start handler: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Произошла ошибка. Пожалуйста, "
                                                                              "попробуйте позже.")


async def apply(update: Update, context: ContextTypes.DEFAULT_TYPE): # Обработчик команды /apply
    application_text = ' '.join(context.args)
    if application_text:
        try:
            async with SessionLocal() as db:
                db_application = Application(application=application_text)
                db.add(db_application)
                await db.commit()
                await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Ваша заявка '
                                                                                      f'"{application_text}'
                                                                                      f'" была принята!')
                logger.info(f"Application sent: {application_text}")
        except Exception as e:
            logger.error(f"Error in apply handler: {e}")
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Произошла ошибка при отправке "
                                                                                  "заявки. Пожалуйста, попробуйте "
                                                                                  "позже.")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Пожалуйста, напишите текст заявки '
                                                                              'после команды /apply')
        logger.info("Empty application text sent")


async def register(update: Update, context: ContextTypes.DEFAULT_TYPE): # Обработчик команды /register
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Пожалуйста, отправьте ваш email и пароль в "
                                                                          "формате: /register_user <email> <password>")


async def register_user(update: Update, context: ContextTypes.DEFAULT_TYPE): # Обработчик команды /register_user
    try:
        email, password = context.args
        async with SessionLocal() as db:
            user_data = UserCreate(email=email, password=password)
            db_user = User(email=user_data.email, hashed_password=hash_password(user_data.password))
            db.add(db_user)
            await db.commit()
            await db.refresh(db_user)
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Регистрация успешна!")
        logger.info(f"User registered: {user_data.email}")
    except Exception as e:
        logger.error(f"User registration failed: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Произошла ошибка при регистрации. "
                                                                              "Пожалуйста, попробуйте позже.")
