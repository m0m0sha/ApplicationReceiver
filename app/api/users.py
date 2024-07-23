from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer
from app.core.dependencies import get_db
from app.services.user_service import UserService
from app.db.schemas import UserCreate, UserOut

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth") # токен для аутентификации

router = APIRouter() # маршрутизатор для обработки запросов, связанных с пользователями
user_service = UserService() # экземпляр сервиса для работы с пользователями


@router.post("/register", response_model=UserOut) # обработчик для регистрации нового пользователя
async def register_user(user: UserCreate):
    try:
        return await user_service.register_new_user(user) # регистрируем нового пользователя через сервис
    except Exception as e: # в случае ошибки возвращаем HTTP-исключение с кодом 500
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/me", response_model=UserOut) # обработчик для получения информации о текущем пользователе
async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    try:
        return await user_service.get_user_by_token(token, db) # получаем информацию о текущем пользователе через сервис
    except Exception as e: # в случае ошибки возвращаем HTTP-исключение с кодом 500
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
