from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from models import ApplicationCreate, Application, SessionLocal, Base, engine

app = FastAPI()  # Создает приложения FastAPI
Base.metadata.create_all(bind=engine)  # Создает таблицы из models


# https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/
async def get_db():  # Открывает и закрывает сессию, когда запрос выполнен
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/applications", response_model=ApplicationCreate)
async def create_application(application: ApplicationCreate, db: Session = Depends(get_db)):
    db_application = Application(application=application.text)
    db.add(db_application)  # Добавление заявки в сессию
    db.commit()  # Сохранение
    db.refresh(db_application)
    return db_application


@app.get("/applications", response_model=list[ApplicationCreate])
async def get_applications(db: Session = Depends(get_db)):
    applications = db.query(Application).all()  # Получает все записи таблицы
    return applications


@app.get("/applications/{application_id}", response_model=ApplicationCreate)
async def get_application(application_id: int, db: Session = Depends(get_db)):
    application = db.query(Application).filter(Application.id == application_id).first()
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")
    return application
