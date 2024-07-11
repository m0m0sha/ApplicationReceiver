from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models import User
from app.db.schemas import UserCreate, UserOut
from app.core.dependencies import get_db, add_to_db
from app.utils.security import hash_password, decode_access_token
from app.utils.logger import logger
from app.utils.errors import InvalidToken, UserNotFound
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth")

router = APIRouter()


@router.post("/register", response_model=UserOut)
async def register_user(user: UserCreate):
    hashed_password = hash_password(user.password)
    db_user = User(email=user.email, hashed_password=hashed_password)
    try:
        await add_to_db(db_user)
        logger.info(f"User registered: {db_user.email}")
        return db_user
    except Exception as e:
        logger.error(f"Failed to register user: {user.email}. Error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to register user")


@router.get("/me", response_model=UserOut)
async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    payload = decode_access_token(token)

    if not payload or "sub" not in payload:
        logger.info(f"Invalid token: {token}")
        raise InvalidToken()

    email = payload["sub"]
    user = await db.execute(select(User).filter(User.email == email))
    db_user = user.scalar_one_or_none()

    if not db_user:
        logger.info(f"User not found: {email}")
        raise UserNotFound(email=email)

    logger.info(f"Current user fetched: {db_user.email}")
    return db_user
