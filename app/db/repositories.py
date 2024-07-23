from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models import Application, User, SessionLocal


class ApplicationRepository: # репозиторий для работы с заявками
    @staticmethod
    async def fetch_applications(db: AsyncSession, limit: int, offset: int, order_by: Optional[str],
                                 filter_by_text: Optional[str]): # метод для получения списка заявок
        query = select(Application)

        if filter_by_text:
            query = query.filter(Application.application.contains(filter_by_text))

        if order_by:
            order_field = getattr(Application, order_by.lstrip("-"))
            query = query.order_by(order_field.desc() if order_by.startswith("-") else order_field.asc())

        query = query.limit(limit).offset(offset)
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def fetch_application_by_id(db: AsyncSession, application_id: int): # метод для получения заявки по ID
        query = select(Application).filter(Application.id == application_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def add_application(application: Application): # метод для добавления заявки
        async with SessionLocal() as db:
            db.add(application)
            await db.commit()
            await db.refresh(application)
            return application


class UserRepository: # репозиторий для работы с пользователями
    @staticmethod
    async def fetch_user_by_email(db: AsyncSession, email: str): # метод для получения пользователя по email
        query = select(User).filter(User.email == email)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def add_user(user: User): # метод для добавления пользователя
        async with SessionLocal() as db:
            db.add(user)
            await db.commit()
            await db.refresh(user)
            return user
