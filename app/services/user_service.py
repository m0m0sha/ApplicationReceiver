from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import User
from app.db.repositories import UserRepository
from app.db.schemas import UserCreate, UserOut
from app.utils.security import hash_password, decode_access_token
from app.utils.errors import UserNotFound, InvalidToken


class UserService: # сервис для работы с пользователями
    def __init__(self):
        self.user_repository = UserRepository()

    async def register_new_user(self, user: UserCreate) -> UserOut: # метод для регистрации нового пользователя
        db_user = User(email=user.email, hashed_password=hash_password(user.password))
        new_user = await self.user_repository.add_user(db_user)
        return UserOut.from_orm(new_user)

    async def get_user_by_token(self, token: str, db: AsyncSession) -> UserOut: # метод для получения юзера по токену
        payload = decode_access_token(token)
        user_email = payload.get("sub")

        if not user_email:
            raise InvalidToken()

        user = await self.user_repository.fetch_user_by_email(db, user_email)
        if not user:
            raise UserNotFound(email=user_email)

        return UserOut.from_orm(user)
