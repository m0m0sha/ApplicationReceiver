from pydantic import BaseModel, EmailStr, constr


class ApplicationCreate(BaseModel): # Схема для создания заявки
    application: constr(min_length=1, max_length=1000, strip_whitespace=True)


class UserCreate(BaseModel): # Схема для создания пользователя
    email: EmailStr
    password: constr(min_length=8)


class UserOut(BaseModel): # Схема для вывода информации о пользователе
    id: int
    email: EmailStr

    class Config:
        orm_mode = True


class UserAuthenticate(BaseModel): # Схема для аутентификации пользователя
    email: EmailStr
    password: str


class TokenResponse(BaseModel): # Схема для возвращения токена
    access_token: str
    token_type: str
