from app.db.models import engine, Base, SessionLocal


async def init_db(): # Функция для инициализации базы данных
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def shutdown_db(): # Функция для закрытия базы данных
    await SessionLocal.close_all()


async def get_db():
    async with SessionLocal() as session:
        yield session
