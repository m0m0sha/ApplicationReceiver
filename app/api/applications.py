from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.core.dependencies import get_db
from app.services.application_service import ApplicationService
from app.db.schemas import ApplicationCreate


router = APIRouter() # маршрутизатор для обработки запросов, связанных с заявками
application_service = ApplicationService() # экземпляр сервиса для работы с заявками


@router.get("/", response_model=list[ApplicationCreate]) # обработчик для получения списка заявок
async def get_applications(
    db: AsyncSession = Depends(get_db),  # зависимость для получения сессии базы данных
    limit: int = Query(10, ge=1, le=100),  # параметр запроса для ограничения количества результатов
    offset: int = Query(0, ge=0),  # параметр запроса для смещения результатов
    order_by: Optional[str] = Query(None),  # параметр запроса для сортировки результатов
    filter_by_text: Optional[str] = Query(None)  # параметр запроса для фильтрации результатов по тексту
):
    try:
        # получаем список заявок через сервис
        return await application_service.fetch_applications(db, limit, offset, order_by, filter_by_text)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{application_id}", response_model=ApplicationCreate) # Обработчик для получения одной заявки по ID
async def get_application(application_id: int, db: AsyncSession = Depends(get_db)):
    try:
        # получаем заявку по ID через сервис
        return await application_service.fetch_application_by_id(db, application_id)
    except Exception as e:
        # в случае ошибки возвращаем HTTP-исключение с кодом 500
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
