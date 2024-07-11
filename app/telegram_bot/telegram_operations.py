from telegram.ext import ContextTypes
from app.utils.errors import SendMessageError
from app.utils.logger import logger


async def send_message(context: ContextTypes.DEFAULT_TYPE, chat_id: int, text: str):
    try:
        await context.bot.send_message(chat_id=chat_id, text=text)
    except Exception as e:
        logger.error(f"Error while sending message: {e}")
        raise SendMessageError(f"Error while sending message: {e}")
