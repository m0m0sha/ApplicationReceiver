from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from starlette import status
from models import ApplicationCreate, Application, SessionLocal, Base, engine
from user import User, UserCreate, hash_password, TokenResponse, UserAuthenticate, verify_password, create_access_token, \
    oauth2_scheme, decode_access_token, UserOut

app = FastAPI()  # Создает приложения FastAPI


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
    db_application = Application(application=application.text)
    db.add(db_application)  # Добавление заявки в сессию
    await db.commit()  # Сохранение
    await db.refresh(db_application)
    return db_application


@app.get("/applications", response_model=list[ApplicationCreate])
async def get_applications(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Application))
    applications = result.scalars().all()  # Получает все записи таблицы
    return applications


@app.get("/applications/{application_id}", response_model=ApplicationCreate)
async def get_application(application_id: int, db: Session = Depends(get_db)):
    result = await db.execute(select(Application).filter(Application.id == application_id))
    application = result.scalar_one_or_none()
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")
    return application


@app.post("/register", response_model=UserOut)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    hashed_password = hash_password(user.password)
    db_user = User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


@app.post("/auth", response_model=TokenResponse)
async def authenticate_user(user_data: UserAuthenticate, db: AsyncSession = Depends(get_db)):
    user = await db.execute(select(User).filter(User.email == user_data.email))
    db_user = user.scalar_one_or_none()
    if not db_user or not verify_password(user_data.password, db_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

    access_token = create_access_token({"sub": db_user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me", response_model=UserOut)
async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = await db.execute(select(User).filter(User.email == email))
    db_user = user.scalar_one_or_none()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return db_user
