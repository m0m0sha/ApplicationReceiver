from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://vova:ghbdtnkjk@localhost/ApplicationReceiver"

engine = create_engine(DATABASE_URL)  # Подключение к БД
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)  # Будет использоваться для сессий с БД
Base = declarative_base()


class Application(Base):  # Модель таблицы для БД
    __tablename__ = "applications"
    id = Column(Integer, primary_key=True, index=True)
    application = Column(String, index=True)


class ApplicationCreate(BaseModel):  # Модель для создания заявки
    application: str
