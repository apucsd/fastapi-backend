from datetime import datetime, timedelta, timezone
from app.schemas.auth import RegisterRequest, OtpRequest
from app.services.user_service import UserService
from app.models.user import User
from app.core.security import hash_password
from app.utils.otp import generate_otp
from app.utils.email import send_email
from fastapi import HTTPException
from app.core.security import verify_password, create_access_token


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
    async def login(self, login_request):
        user = self.db.query(User).filter(User.email == login_request.email).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="No user found with the provided email")
        if not verify_password(login_request.password, user.password):
            raise HTTPException(status_code=401, detail="Your provided password is incorrect")

        if not user.is_verified:
            raise HTTPException(status_code=401, detail="Your account is not verified. Please verify your account")

        if user.status == "inactive":
            raise HTTPException(status_code=401, detail="Your account is inactive. Please contact the administrator")
        if user.status == "deleted":
            raise HTTPException(status_code=401, detail="Your account is deleted. Please contact the administrator")
        if user.status == "blocked":
            raise HTTPException(status_code=401, detail="Your account is blocked. Please contact the administrator")

        token = create_access_token(data={
            "sub": str(user.id),  # "sub" (subject) is standard for the user's unique ID
            "email": user.email,
            "name": user.name
        })
        return {
            "access_token": token,
            "user": {
                "id": user.id,
                "role": user.role,
                "name": user.name,
                "email": user.email,
                "status": user.status
            }
        }


    async def verify_otp(self, otp_request: OtpRequest):
        user = UserService(self.db).get_user_by_email(otp_request.email)
        if not user:
            raise HTTPException(status_code=404, detail="No user found with the provided email")
        if user.otp != otp_request.otp:
            raise HTTPException(status_code=401, detail="Your provided OTP is incorrect")
        if user.otp_expiry < datetime.now(timezone.utc):
            raise HTTPException(status_code=401, detail="Your OTP has expired. Please request a new OTP")
        user.is_verified = True
        user = UserService(self.db).update_user(user.id, user)
        
        return user
        
        
        