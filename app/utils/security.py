from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from app.core.config import settings
from app.utils.errors import InvalidToken

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") # контекст для хеширования пароля
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


def hash_password(password: str) -> str: # функция для хеширования пароля
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool: # функция для проверки хешированного пароля
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str: # функция для создания токена
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict: # функция для декодирования токена
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.JWTError as e:
        raise InvalidToken(f"Invalid token: {str(e)}")
