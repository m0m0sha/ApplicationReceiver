from pydantic import BaseModel, EmailStr, constr


class ApplicationCreate(BaseModel): # cхема для создания заявки
    application: constr(min_length=1, max_length=1000, strip_whitespace=True)


class UserCreate(BaseModel): # cхема для создания пользователя
    email: EmailStr
    password: constr(min_length=8)


class UserOut(BaseModel): # cхема для получения информации о пользователе
    id: int
    email: EmailStr

    class Config:
        orm_mode = True


class UserAuthenticate(BaseModel): # cхема для аутентификации
    email: EmailStr
    password: str


class TokenResponse(BaseModel): # cхема для получения токена
    access_token: str
    token_type: str
