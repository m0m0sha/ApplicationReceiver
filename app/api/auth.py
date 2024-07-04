from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.schemas import UserAuthenticate, TokenResponse
from app.db.models import User
from app.core.dependencies import get_db
from app.utils.security import verify_password, create_access_token
from app.utils.logger import logger

router = APIRouter()


@router.post("/", response_model=TokenResponse) # Маршрут для аутентификации пользователя
async def authenticate_user(user_data: UserAuthenticate, db: AsyncSession = Depends(get_db)):
    try:
        user = await db.execute(select(User).filter(User.email == user_data.email)) # Выборка пользователя по email
        db_user = user.scalar_one_or_none() # Получение одного пользователя или None
        if not db_user or not verify_password(user_data.password, db_user.hashed_password):
            logger.info(f"Incorrect email or password: {user_data}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
        access_token = create_access_token({"sub": db_user.email})
        logger.info(f"User authenticated: {db_user.email}")
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        logger.error(f"Error authenticating user: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
