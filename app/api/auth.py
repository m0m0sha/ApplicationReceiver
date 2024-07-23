from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db
from app.services.auth_service import AuthService
from app.db.schemas import UserAuthenticate, TokenResponse

router = APIRouter() # Создаем маршрутизатор для обработки запросов, связанных с аутентификацией
auth_service = AuthService() # Создаем экземпляр сервиса для работы с аутентификацией


@router.post("/", response_model=TokenResponse) # обработчик для аутентификации пользователя
async def authenticate_user(user_data: UserAuthenticate, db: AsyncSession = Depends(get_db)):
    try:
        return await auth_service.authenticate(user_data, db) # Аутентифицируем пользователя через сервис
    except HTTPException as e:
        raise e # Если возникла ошибка HTTP, пробрасываем её дальше
    except Exception as e:
        # В случае других исключений возвращаем HTTP-исключение с кодом 500
        raise HTTPException(status_code=500, detail=str(e))
