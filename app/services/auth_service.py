from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.utils.security import verify_password, create_access_token
from app.db.repositories import UserRepository
from app.db.schemas import UserAuthenticate, TokenResponse


class AuthService: # сервис для работы с аутентификацией
    def __init__(self):
        self.user_repository = UserRepository()

    # метод для аутентификации пользователя
    async def authenticate(self, user_data: UserAuthenticate, db: AsyncSession) -> TokenResponse:
        user = await self.user_repository.fetch_user_by_email(db, user_data.email)
        if not user or not verify_password(user_data.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        access_token = create_access_token(data={"sub": user.email})
        return TokenResponse(access_token=access_token, token_type="bearer")
