from app.db.models import engine, Base, SessionLocal


async def init_db(): # инициализация базы данных
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def shutdown_db(): # завершение работы с базой данных
    await SessionLocal.close_all()


async def get_db(): # функция для получения сессии базы данных
    async with SessionLocal() as session:
        yield session
