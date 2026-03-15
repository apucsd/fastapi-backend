from datetime import datetime, timedelta, timezone
from app.schemas.auth import RegisterRequest
from app.services.user_service import UserService
from app.models.user import User
from app.core.security import hash_password
from app.utils.otp import generate_otp
from app.utils.email import send_email


class AuthService:
    def __init__(self, db):
        self.db = db

    async def register(self, user: RegisterRequest):
        otp = generate_otp()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)


        new_user = User(
            name = user.name,
            email=user.email,
            password=hash_password(user.password),
            otp=otp,
            otp_expiry = expires_at
        )
        result = UserService(self.db).create_user(new_user)
        if result:
           await send_email(
                to=user.email,
                subject="Welcome! Here is your OTP",
                template_name="verify_otp_email.html",
                otp=otp,
            )
        return result

        