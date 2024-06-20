from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://vova:ghbdtnkjk@147.45.247.107:5432/ApplReceiver"

engine = create_async_engine(DATABASE_URL, echo=True)  # Подключение к БД
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)  # Будет использоваться для сессий с БД
Base = declarative_base()


class Application(Base):  # Модель таблицы для БД
    __tablename__ = "applications"
    id = Column(Integer, primary_key=True, index=True)
    application = Column(String, index=True)


class ApplicationCreate(BaseModel):  # Модель для создания заявки
    application: str
