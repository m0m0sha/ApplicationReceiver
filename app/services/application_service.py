from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.repositories import ApplicationRepository
from app.utils.errors import InvalidFieldError, UserNotFound


class ApplicationService: # cервис для работы с заявками
    def __init__(self):
        self.repository = ApplicationRepository()

    async def fetch_applications(self, db: AsyncSession, limit: int, offset: int, order_by: Optional[str],
                                 filter_by_text: Optional[str]): # метод для получения списка заявок
        if order_by and not hasattr(ApplicationRepository, order_by.lstrip("-")):
            raise InvalidFieldError(order_by)

        return await self.repository.fetch_applications(db, limit, offset, order_by, filter_by_text)

    async def fetch_application_by_id(self, db: AsyncSession, application_id: int): # метод для получения заявки по ID
        application = await self.repository.fetch_application_by_id(db, application_id)
        if not application:
            raise UserNotFound(email=f"Application with id {application_id} not found.")
        return application
