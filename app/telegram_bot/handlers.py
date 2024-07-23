from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from app.db.models import Application, User
from app.utils.security import hash_password
from app.utils.logger import logger
from app.utils.errors import SendMessageError
from app.telegram_bot.telegram_operations import send_message
from app.db.repositories import UserRepository, ApplicationRepository


# Создаем клавиатуру для команды /start
def get_start_keyboard():
    keyboard = [
        [KeyboardButton("/apply")],
        [KeyboardButton("/register")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): # обработчик команды /start
    user = update.effective_user
    welcome_message = f"Здравствуйте {user.first_name}, Добро пожаловать в наш бот!"
    keyboard = get_start_keyboard()  # Получаем клавиатуру
    try:
        await update.message.reply_text(welcome_message, reply_markup=keyboard)
    except SendMessageError as e:
        logger.error(f"Error in start handler: {str(e)}")


async def apply(update: Update, context: ContextTypes.DEFAULT_TYPE): # обработчик команды /apply
    user = update.effective_user
    message_text = " ".join(context.args)
    if not message_text:
        await send_message(user.id, "Пожалуйста, введите текст для вашей заявки /apply <текст>.", context)
        return

    application = Application(application=message_text)
    try:
        await ApplicationRepository.add_application(application)
        await send_message(user.id, "Ваша заявка успешно отправлена!", context)
    except Exception as e:
        logger.error(f"Error in apply handler: {str(e)}")
        await send_message(user.id, "Ваша заявка не была отправлена. Пожалуйста, попробуйте еще раз.", context)


async def register(update: Update, context: ContextTypes.DEFAULT_TYPE): # обработчик команды /register
    user = update.effective_user
    if len(context.args) != 2:
        await send_message(user.id, "Используйте: /register email password", context)
        return

    email, password = context.args
    hashed_password = hash_password(password)
    db_user = User(email=email, hashed_password=hashed_password)

    try:
        await UserRepository.add_user(db_user)
        await send_message(user.id, "Регистрация прошла успешно!", context)
    except Exception as e:
        logger.error(f"Error in register handler: {str(e)}")
        await send_message(user.id, "Регистрация не удалась. Пожалуйста, попробуйте еще раз.", context)
