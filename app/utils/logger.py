import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger(__name__) # Инициализация логгера

file_handler = RotatingFileHandler('app.log', maxBytes=1024*1024, backupCount=5) # Настройки логгера
file_handler.setLevel(logging.INFO) # Уровень логгирования
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s') # Формат логгирования
file_handler.setFormatter(formatter) # Настройка формата
logger.addHandler(file_handler) # Настройка логгера
logger.setLevel(logging.INFO) # Уровень логгирования
