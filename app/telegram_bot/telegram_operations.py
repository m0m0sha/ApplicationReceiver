from typing import Optional
from telegram import ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from app.utils.errors import SendMessageError


# функция для отправки сообщения в чат
async def send_message(chat_id: int, text: str, context: ContextTypes.DEFAULT_TYPE):
    try:
        await context.bot.send_message(chat_id=chat_id, text=text)
    except Exception as e:
        raise SendMessageError(f"Error sending message: {str(e)}")


async def send_message_feedback(chat_id: int, text: str, context: ContextTypes.DEFAULT_TYPE, reply_markup: Optional[ReplyKeyboardMarkup] = None):
    try:
        await context.bot.send_message(chat_id=chat_id, text=text,  reply_markup=reply_markup)
    except Exception as e:
        raise SendMessageError(f"Error sending message: {str(e)}")
