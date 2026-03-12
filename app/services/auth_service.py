from app.schemas.auth import RegisterRequest
from app.services.user_service import UserService
from app.models.user import User
from app.core.security import hash_password

class AuthService:
    def __init__(self, db):
        self.db = db

    def register(self, user: RegisterRequest):
        new_user = User(
            name = user.name,
            email=user.email,
            password=hash_password(user.password)
        )
        result = UserService(self.db).create_user(user)
        return result