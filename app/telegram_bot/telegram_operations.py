from telegram.ext import ContextTypes
from app.utils.errors import SendMessageError


# функция для отправки сообщения в чат
async def send_message(user_id: int, text: str, context: ContextTypes.DEFAULT_TYPE):
    try:
        await context.bot.send_message(chat_id=user_id, text=text)
    except Exception as e:
        raise SendMessageError(f"Failed to send message to user {user_id}: {str(e)}")


