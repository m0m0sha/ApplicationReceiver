from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from app.db.models import Application, User
from app.utils.logger import logger
from app.utils.errors import SendMessageError
from app.telegram_bot.telegram_operations import send_message, send_message_feedback
from app.db.repositories import UserRepository, ApplicationRepository, FeedbackRepository
from app.utils.security import hash_password


# Создаем клавиатуру
def get_start_keyboard():
    keyboard = [
        [KeyboardButton("/apply")],
        [KeyboardButton("/register")],
        [KeyboardButton("/my_applications")],
        [KeyboardButton("/feedback")]

    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_feedback_keyboard():
    keyboard = [
        [KeyboardButton("Отлично")],
        [KeyboardButton("Хорошо")],
        [KeyboardButton("Нормально")],
        [KeyboardButton("Плохо")],
        [KeyboardButton("Ужасно")]
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


async def apply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id  # Получаем user_id из Telegram
    message_text = " ".join(context.args)

    if not message_text:
        await send_message(user_id, "Пожалуйста, введите текст для вашей заявки /apply <текст>.", context)
        return

    # Создаем новую заявку с Telegram user_id
    application = Application(application=message_text, user_id=user_id, status="pending")

    try:
        await ApplicationRepository.add_application(application)
        await send_message(user_id, "Ваша заявка успешно отправлена!", context)
    except Exception as e:
        logger.error(f"Error in apply handler: {str(e)}")
        await send_message(user_id, "Ваша заявка не была отправлена. Пожалуйста, попробуйте еще раз.", context)


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


async def my_applications(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id  # Получаем Telegram ID пользователя

    try:
        user_applications = await ApplicationRepository.get_applications_by_user_id(user_id)

        if user_applications:
            applications_text = "\n".join([f"{app.id}: {app.application} - {app.status}" for app in user_applications])
            await send_message(user_id, f"Ваши заявки:\n{applications_text}", context)
        else:
            await send_message(user_id, "У вас нет заявок.", context)
    except Exception as e:
        logger.error(f"Error in my_applications handler: {str(e)}")
        await send_message(user_id, "Произошла ошибка при получении заявок.", context)


async def feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    feedback_keyboard = get_feedback_keyboard()

    try:
        await send_message_feedback(user_id, "Пожалуйста, выберите оценку:", context, reply_markup=feedback_keyboard)
    except SendMessageError as e:
        logger.error(f"Error in feedback handler: {str(e)}")


async def handle_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    feedback_text = update.message.text

    # Убедитесь, что это один из вариантов обратной связи
    valid_feedbacks = {"Отлично", "Хорошо", "Нормально", "Плохо", "Ужасно"}

    if feedback_text in valid_feedbacks:
        try:
            # Сохраните отзыв в базе данных
            await FeedbackRepository.add_feedback(user_id, feedback_text)
            await send_message(user_id, "Спасибо за ваш отзыв!", context)
        except Exception as e:
            logger.error(f"Error in handle_feedback handler: {str(e)}")
            await send_message(user_id, "Произошла ошибка при отправке отзыва. Пожалуйста, попробуйте еще раз.",
                               context)
    else:
        await send_message(user_id, "Пожалуйста, выберите один из предложенных вариантов.", context)

