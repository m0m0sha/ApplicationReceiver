from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

DATABASE_URL = settings.DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=True) # создаем движок для подключения к базе данных
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False) # создаем сессию
Base = declarative_base() # создаем базовый класс для моделей


class Application(Base): # таблица для хранения заявок
    __tablename__ = "applications"
    id = Column(Integer, primary_key=True, index=True)
    application = Column(String, index=True)
    user_id = Column(Integer, nullable=False)
    status = Column(String, default="Wait for answer")


class User(Base): # таблица для хранения пользователей
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)


class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    feedback = Column(String)
