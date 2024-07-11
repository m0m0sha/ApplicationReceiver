from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models import Application
from app.core.dependencies import get_db
from app.utils.logger import logger
from app.db.schemas import ApplicationCreate
from app.utils.errors import InvalidFieldError, UserNotFound, InternalServerError

router = APIRouter()


@router.get("/", response_model=list[ApplicationCreate])
async def get_applications(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    order_by: Optional[str] = Query(None),
    filter_by_text: Optional[str] = Query(None)
):
    query = select(Application)

    if filter_by_text:
        query = query.filter(Application.application.contains(filter_by_text))

    if order_by:
        if not hasattr(Application, order_by.lstrip("-")):
            raise InvalidFieldError(order_by)
        order_field = getattr(Application, order_by.lstrip("-"))
        if order_by.startswith("-"):
            query = query.order_by(order_field.desc())
        else:
            query = query.order_by(order_field.asc())

    query = query.limit(limit).offset(offset)

    try:
        result = await db.execute(query)
        applications = result.scalars().all()
        logger.info("Applications fetched successfully")
        return applications
    except InvalidFieldError as e:
        logger.error(f"InvalidFieldError in get_applications: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"Error in get_applications: {str(e)}")
        raise InternalServerError()


@router.get("/{application_id}", response_model=ApplicationCreate)
async def get_application(application_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Application).filter(Application.id == application_id)

    try:
        result = await db.execute(query)
        application = result.scalar_one_or_none()

        if not application:
            raise UserNotFound(email=f"Application with id '{application_id}'")

        return application
    except UserNotFound as e:
        logger.error(f"UserNotFound in get_application: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"Error in get_application: {str(e)}")
        raise InternalServerError()
