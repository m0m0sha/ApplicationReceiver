from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from app.utils.logger import logger


async def database_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        return JSONResponse(status_code=500, content={"detail": "Database error"})


def register_middlewares(app: FastAPI):
    app.middleware("http")(database_middleware)
