from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from app.db.models import Application
from app.db.schemas import ApplicationCreate
from app.core.dependencies import get_db
from app.utils.logger import logger

router = APIRouter()


@router.post("/", response_model=ApplicationCreate) # Маршрут для создания новой заявки
async def create_application(application: ApplicationCreate, db: AsyncSession = Depends(get_db)):
    try:  # Создание объекта заявки
        db_application = Application(application=application.text)
        db.add(db_application)
        await db.commit()
        await db.refresh(db_application)
        logger.info(f"Application created: {db_application.application}")
        return db_application
    except Exception as e:
        logger.error(f"Error creating application: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/", response_model=List[ApplicationCreate]) # Маршрут для получения списка заявок
async def get_applications(
        db: AsyncSession = Depends(get_db),
        limit: int = Query(10, ge=1, le=100),
        offset: int = Query(0, ge=0),
        order_by: Optional[str] = Query(None),
        filter_by_text: Optional[str] = Query(None)):
    try:
        query = select(Application) # Создание запроса для выборки заявок
        if filter_by_text:
            query = query.filter(Application.application.contains(filter_by_text))
        if order_by:
            if hasattr(Application, order_by.lstrip("-")):
                if order_by.startswith("-"):
                    query = query.order_by(getattr(Application, order_by[1:]).desc())
                else:
                    query = query.order_by(getattr(Application, order_by).asc())
            else:
                logger.info(f"Invalid order_by field: {order_by}")
                raise HTTPException(status_code=400, detail=f"Invalid order_by field: {order_by}")
        query = query.limit(limit).offset(offset)
        result = await db.execute(query)
        applications = result.scalars().all()
        logger.info("Applications fetched successfully")
        return applications
    except Exception as e:
        logger.error(f"Error fetching applications: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/{application_id}", response_model=ApplicationCreate) # Маршрут для получения одной заявки по ID
async def get_application(application_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Application).filter(Application.id == application_id))
        application = result.scalar_one_or_none()  # Получение одной записи или None
        if application is None:
            logger.info(f"Application not found: {application_id}")
            raise HTTPException(status_code=404, detail="Application not found")
        return application
    except Exception as e:
        logger.error(f"Error fetching application: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
