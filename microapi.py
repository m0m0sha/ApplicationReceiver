import logging
from logging.handlers import RotatingFileHandler
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query, BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from starlette import status
from models import ApplicationCreate, Application, SessionLocal, Base, engine
from user import User, UserCreate, hash_password, TokenResponse, UserAuthenticate, verify_password, create_access_token, \
    oauth2_scheme, decode_access_token, UserOut

app = FastAPI()  # Создает приложения FastAPI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
file_handler = RotatingFileHandler('app.log', maxBytes=1024*1024, backupCount=5)
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all) # Создает таблицы из models


@app.on_event("startup")
async def startup():
    await init_db()


# https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/
async def get_db():  # Открывает и закрывает сессию, когда запрос выполнен
    async with SessionLocal() as session:
        yield session


@app.post("/applications", response_model=ApplicationCreate)
async def create_application(application: ApplicationCreate, db: AsyncSession = Depends(get_db)):
    try:
        db_application = Application(application=application.text)
        db.add(db_application)
        await db.commit()
        await db.refresh(db_application)
        logger.info(f"Application created: {db_application.application}")
        return db_application
    except Exception as e:
        logger.error(f"Error creating application: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/applications", response_model=List[ApplicationCreate])
async def get_applications(
        db: AsyncSession = Depends(get_db),
        limit: int = Query(10, ge=1, le=100),
        offset: int = Query(0, ge=0),
        order_by: Optional[str] = Query(None),
        filter_by_text: Optional[str] = Query(None)):
    try:
        query = select(Application)
        if filter_by_text:  # Фильтрация
            query = query.filter(Application.application.contains(filter_by_text))
        if order_by:  # Сортировка
            if hasattr(Application, order_by.lstrip("-")):
                if order_by.startswith("-"):
                    query = query.order_by(getattr(Application, order_by[1:]).desc())
                else:
                    query = query.order_by(getattr(Application, order_by).asc())
            else:
                logger.info(f"Invalid order_by field: {order_by}")
                raise HTTPException(status_code=400, detail=f"Invalid order_by field: {order_by}")
        query = query.limit(limit).offset(offset)  # Пагинация
        result = await db.execute(query)
        applications = result.scalars().all()  # Получает все записи
        logger.info("Applications fetched successfully")
        return applications
    except Exception as e:
        logger.error(f"Error fetching applications: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/applications/{application_id}", response_model=ApplicationCreate)
async def get_application(application_id: int, db: Session = Depends(get_db)):
    try:
        result = await db.execute(select(Application).filter(Application.id == application_id))
        application = result.scalar_one_or_none()
        if application is None:
            logger.info(f"Application not found: {application_id}")
            raise HTTPException(status_code=404, detail="Application not found")
        return application
    except Exception as e:
        logger.error(f"Error fetching application: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.post("/register", response_model=UserOut)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        hashed_password = hash_password(user.password)
        db_user = User(email=user.email, hashed_password=hashed_password)
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        logger.info(f"User registered: {db_user.email}")
        return db_user
    except Exception as e:
        logger.error(f"Error registering user: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.post("/auth", response_model=TokenResponse)
async def authenticate_user(user_data: UserAuthenticate, db: AsyncSession = Depends(get_db)):
    try:
        user = await db.execute(select(User).filter(User.email == user_data.email))
        db_user = user.scalar_one_or_none()
        if not db_user or not verify_password(user_data.password, db_user.hashed_password):
            logger.info(f"Incorrect email or password: {user_data}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

        access_token = create_access_token({"sub": db_user.email})
        logger.info(f"User authenticated: {db_user.email}")
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        logger.error(f"Error authenticating user: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/users/me", response_model=UserOut)
async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    try:
        payload = decode_access_token(token)
        if not payload:
            logger.info(f"Invalid token: {token}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        email = payload.get("sub")
        if not email:
            logger.info(f"Invalid token: {token}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        user = await db.execute(select(User).filter(User.email == email))
        db_user = user.scalar_one_or_none()
        if not db_user:
            logger.info(f"User not found: {email}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        logger.info(f"Current user fetched: {db_user.email}")
        return db_user
    except Exception as e:
        logger.error(f"Error fetching current user: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
