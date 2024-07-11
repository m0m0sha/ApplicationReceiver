from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from app.utils.logger import logger


class BotError(Exception):
    """Базовый класс для исключений в боте."""
    def __init__(self, message="Ошибка в боте"):
        self.message = message
        super().__init__(self.message)


class HTTPError(HTTPException):
    """Базовый класс для HTTP исключений."""
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)


class SendMessageError(BotError):
    """Исключение при ошибке отправки сообщения в Telegram."""
    def __init__(self, message="Ошибка при отправке сообщения"):
        super().__init__(message)


class DatabaseError(BotError):
    """Исключение при ошибке работы с базой данных."""
    def __init__(self, message="Ошибка при работе с базой данных"):
        super().__init__(message)


class UserExists(HTTPError):
    """Исключение при попытке создать пользователя с уже существующим email."""
    def __init__(self, email: str):
        super().__init__(status_code=400, detail=f"User with email '{email}' already exists")


class UserNotFound(HTTPError):
    """Исключение при попытке получить пользователя с несуществующим email."""
    def __init__(self, email: str):
        super().__init__(status_code=404, detail=f"User with email '{email}' not found")


class InvalidToken(HTTPError):
    """Исключение при невалидном токене."""
    def __init__(self):
        super().__init__(status_code=401, detail="Invalid token")


class InvalidFieldError(HTTPError):
    """Исключение при использовании невалидного поля для сортировки или фильтрации."""
    def __init__(self, field: str):
        super().__init__(status_code=400, detail=f"Invalid field '{field}'")


class InternalServerError(HTTPError):
    """Исключение при ошибке работы сервера."""
    def __init__(self):
        super().__init__(status_code=500, detail="Internal Server Error")


def register_exception_handlers(app: FastAPI): # Регистрация обработчиков исключений

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        logger.error(f"HTTP Exception: {exc.detail}")
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
        logger.error(f"SQLAlchemy Error: {exc}")
        return JSONResponse(status_code=500, content={"detail": "Database error"})

    @app.exception_handler(SendMessageError)
    async def send_message_error_handler(request: Request, exc: SendMessageError):
        logger.error(f"Telegram Error: {exc.message}")
        return JSONResponse(status_code=500, content={"detail": exc.message})

    @app.exception_handler(DatabaseError)
    async def database_error_handler(request: Request, exc: DatabaseError):
        logger.error(f"Database Error: {exc.message}")
        return JSONResponse(status_code=500, content={"detail": exc.message})

    @app.exception_handler(UserExists)
    async def user_exists_handler(request: Request, exc: UserExists):
        logger.error(f"User Exists: {exc.detail}")
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @app.exception_handler(UserNotFound)
    async def user_not_found_handler(request: Request, exc: UserNotFound):
        logger.error(f"User Not Found: {exc.detail}")
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @app.exception_handler(InvalidToken)
    async def invalid_token_handler(request: Request, exc: InvalidToken):
        logger.error(f"Invalid Token: {exc.detail}")
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @app.exception_handler(InvalidFieldError)
    async def invalid_field_error_handler(request: Request, exc: InvalidFieldError):
        logger.error(f"Invalid Field: {exc.detail}")
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @app.exception_handler(InternalServerError)
    async def internal_server_error_handler(request: Request, exc: InternalServerError):
        logger.error(f"Internal Server Error: {exc.detail}")
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
