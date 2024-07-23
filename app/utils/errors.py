from fastapi import HTTPException, status


class InvalidFieldError(HTTPException): # исключение для невалидных полей
    def __init__(self, field: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid field: {field}")


class UserNotFound(HTTPException): # исключение для ненахождения юзера
    def __init__(self, email: str):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=f"User not found: {email}")


class InvalidToken(HTTPException): # исключение для невалидного токена
    def __init__(self):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


class InternalServerError(HTTPException): # исключение для внутренних ошибок
    def __init__(self):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


class SendMessageError(Exception): # исключение для ошибок при отправке сообщения
    def __init__(self, message: str):
        super().__init__(message)
