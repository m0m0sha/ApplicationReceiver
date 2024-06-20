import aiohttp
from models import Application, SessionLocal
from telegram import Update
from telegram.ext import Application as TelegramApplication, CommandHandler, ContextTypes
from users import get_user

TOKEN = '7378792011:AAFxT5ebUjpHLRmQkn1047vRpdtWkg1Ai0c'


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):  # Update содержит инфу о полученном сообщении
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Здравствуйте! Пожалуйста, оставьте вашу '
                                                                          'заявку командой /apply <ваша заявка>')


async def apply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    application_text = ' '.join(context.args)
    if application_text:
        async with SessionLocal() as db:
            db_user = await get_user(db, email=update.effective_user.email)
            if not db_user:
                await context.bot.send_message(chat_id=update.effective_chat.id, text='Для начала вам нужно '
                                                                                      'зарегистрироваться! Используйте '
                                                                                      'команду /register <email> '
                                                                                      '<password> для регистрации')
                return
            db_application = Application(application=application_text)
            db.add(db_application)
            await db.commit()
            await db.close()
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Ваша заявка "{application_text}" '
                                                                                  f'была принята!')
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Пожалуйста, напишите текст заявки после '
                                                                              'команды /apply')


async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if len(args) != 2:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Пожалуйста, используйте команду '
                                                                              '/register <email> <password>')
        return
    email, password = args
    url = f"http://m0m0sha-applicationreceiver-284d.twc1.net/users"
    data = {"email": email, "password": password}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            if response.status == 200:
                await context.bot.send_message(chat_id=update.effective_chat.id, text='Вы успешно зарегистрировались!')
            else:
                await context.bot.send_message(chat_id=update.effective_chat.id, text='При регистрации произошла '
                                                                                      'ошибка!')

telegram_application = TelegramApplication.builder().token(TOKEN).build()  # Инициализация бота
telegram_application.add_handler(CommandHandler("start", start))
telegram_application.add_handler(CommandHandler("apply", apply))
telegram_application.add_handler(CommandHandler("register", register))


async def run_telegram_bot():
    await telegram_application.initialize()
    await telegram_application.start()
    await telegram_application.updater.start_polling()  # Бесконечный цикл опроса обновлений


async def stop_telegram_bot():
    await telegram_application.updater.stop()  # Остановка цикла опроса обновлений
    await telegram_application.stop()
    await telegram_application.shutdown()
