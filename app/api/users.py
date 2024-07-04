from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from starlette import status
from app.db.schemas import UserCreate, UserOut
from app.db.models import User
from app.core.dependencies import get_db
from app.utils.security import hash_password, decode_access_token
from app.utils.logger import logger
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth")

router = APIRouter()


@router.post("/register", response_model=UserOut) # Маршрут для регистрации пользователя
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        hashed_password = hash_password(user.password)
        db_user = User(email=user.email, hashed_password=hashed_password)
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        logger.info(f"User registered: {db_user.email}")
        return db_user
    except Exception as e:
        logger.error(f"Error registering user: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/me", response_model=UserOut) # Маршрут для получения текущего пользователя
async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    try:
        payload = decode_access_token(token) # Декодирование токена
        if not payload:
            logger.info(f"Invalid token: {token}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        email = payload.get("sub") # Извлечение email из токена
        if not email:
            logger.info(f"Invalid token: {token}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        user = await db.execute(select(User).filter(User.email == email))
        db_user = user.scalar_one_or_none() # Получение одного пользователя или None
        if not db_user:
            logger.info(f"User not found: {email}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        logger.info(f"Current user fetched: {db_user.email}")
        return db_user
    except Exception as e:
        logger.error(f"Error fetching current user: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
