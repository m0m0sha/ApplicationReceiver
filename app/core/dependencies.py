from app.db.models import engine, Base, SessionLocal


async def init_db(): # Функция для инициализации базы данных
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def shutdown_db(): # Функция для закрытия базы данных
    await SessionLocal.close_all()


async def get_db():
    async with SessionLocal() as session:
        yield session


async def add_to_db(model):
    async with SessionLocal() as db:
        db.add(model)
        await db.commit()
        await db.refresh(model)
