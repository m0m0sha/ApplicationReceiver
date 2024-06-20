from datetime import timedelta
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from starlette.status import HTTP_401_UNAUTHORIZED
from models import ApplicationCreate, Application, User, UserCreate, Token, get_db
from users import get_user, get_password_hash, authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, \
    get_current_active_user

app = FastAPI()  # Создает приложения FastAPI


@app.post("/applications", response_model=ApplicationCreate)
async def create_application(application: ApplicationCreate, db: AsyncSession = Depends(get_db)):
    db_application = Application(application=application.text)
    db.add(db_application)  # Добавление заявки в сессию
    await db.commit()  # Сохранение
    await db.refresh(db_application)
    return db_application


@app.get("/applications", response_model=list[ApplicationCreate])
async def get_applications(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Application))
    applications = result.scalars().all() # Получает все записи таблицы
    return applications


@app.get("/applications/{application_id}", response_model=ApplicationCreate)
async def get_application(application_id: int, db: Session = Depends(get_db)):
    result = await db.execute(select(Application).filter(Application.id == application_id))
    application = result.scalar_one_or_none()
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")
    return application


@app.post("/users", response_model=User)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = await get_user(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(user.password)
    db_user = User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user
