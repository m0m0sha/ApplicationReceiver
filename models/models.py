from typing import Optional
from pydantic import BaseModel, EmailStr
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

DATABASE_URL = "postgresql+asyncpg://vova:ghbdtnkjk@147.45.247.107:5432/ApplReceiver"

engine = create_async_engine(DATABASE_URL, echo=True)  # Подключение к БД
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)  # Будет использоваться для сессий с БД
Base = declarative_base()


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  # Создает таблицы из models


# https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/
async def get_db(): # Открывает и закрывает сессию, когда запрос выполнен
    async with SessionLocal() as session:
        try:
            yield session
        except OperationalError:
            session.rollback()  # Если БД отключилась
            raise
        finally:
            await session.close()


class Application(Base):  # Модель таблицы для БД
    __tablename__ = "applications"
    id = Column(Integer, primary_key=True, index=True)
    application = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="applications")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    applications = relationship("Application", back_populates="user")


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserDB(UserCreate):
    hashed_password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class ApplicationCreate(BaseModel):  # Модель для создания заявки
    application: str
