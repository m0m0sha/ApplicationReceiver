from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

DATABASE_URL = settings.DATABASE_URL # URL для подключения к базе данных

engine = create_async_engine(DATABASE_URL, echo=True) # Создание движка для подключения к базе данных
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False) # Создание сессии для подключения к бд
Base = declarative_base() # Создание базы данных


class Application(Base): # Модель для хранения заявок
    __tablename__ = "applications"
    id = Column(Integer, primary_key=True, index=True)
    application = Column(String, index=True)


class User(Base): # Модель для хранения пользователей
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
