from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from models import ApplicationCreate, Application, SessionLocal, Base, engine

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
    applications = await db.query(Application).all()  # Получает все записи таблицы
    return applications


@app.get("/applications/{application_id}", response_model=ApplicationCreate)
async def get_application(application_id: int, db: Session = Depends(get_db)):
    application = await db.query(Application).filter(Application.id == application_id).first()
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")
    return application
