from datetime import datetime, timedelta, timezone
from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    create_verification_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    OtpRequest,
    RegisterRequest,
    ResetPasswordOTPRequest,
    ResetPasswordRequest,
)
from app.services.user_service import UserService
from app.utils.email import send_email
from app.utils.exceptions import AppException
from app.utils.otp import generate_otp


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_service = UserService(db)

    async def register_user(self, user_req: RegisterRequest) -> User:
        otp = generate_otp()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)

        new_user = User(
            name=user_req.name,
            email=user_req.email,
            password=hash_password(user_req.password),
            otp=otp,
            otp_expiry=expires_at,
        )
        created_user = self.user_service.create_user(new_user)
        if created_user:
            try:
                await send_email(
                    to=created_user.email,
                    subject="Welcome! Here is your OTP",
                    template_name="verify_otp_email.html",
                    otp=otp,
                )
            except Exception as e:
                print(f"⚠️ Email sending failed: {e}. [DEV OTP]: {otp}")

        return created_user

    async def authenticate_user(self, login_request: LoginRequest) -> dict:
        user = self.db.query(User).filter(User.email == login_request.email).first()

        if not user:
            raise AppException(status_code=401, message="Invalid email or password")

        if not verify_password(login_request.password, user.password):
            raise AppException(status_code=401, message="Invalid email or password")

        if not user.is_verified:
            # Auto-generate fresh OTP and send verification email
            otp = generate_otp()
            expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)
            self.user_service.update_user(user.id, {"otp": otp, "otp_expiry": expires_at})

            try:
                await send_email(
                    to=user.email,
                    subject="Verify Your Account - New OTP",
                    template_name="verify_otp_email.html",
                    otp=otp,
                )
            except Exception as e:
                print(f"⚠️ Email sending failed: {e}. [DEV OTP]: {otp}")

            raise AppException(
                status_code=403,
                message="Your account is not verified. A new verification OTP has been sent to your email.",
            )

        if user.status.value in ["INACTIVE", "BLOCKED", "DELETED"]:
            raise AppException(
                status_code=403,
                message=f"Your account is {user.status.value.lower()}. Please contact support",
            )

        token = create_access_token(
            data={
                "sub": str(user.id),
                "email": user.email,
                "name": user.name,
                "role": user.role.value,
            }
        )

        return {
            "access_token": token,
            "token_type": "bearer",
            "user": user,
        }


    def verify_user_email(self, otp_request: OtpRequest) -> User:
        user = self.user_service.get_user_by_email(otp_request.email)
        if not user:
            raise AppException(
                status_code=404, message="No user found with the provided email"
            )
        if user.otp != otp_request.otp:
            raise AppException(
                status_code=401, message="Your provided OTP is incorrect"
            )
        if user.otp_expiry and user.otp_expiry < datetime.now(timezone.utc):
            raise AppException(
                status_code=401,
                message="Your OTP has expired. Please request a new OTP",
            )

        updated_user = self.user_service.update_user(
            user.id, {"otp": None, "otp_expiry": None, "is_verified": True}
        )
        return updated_user

    async def resend_user_verification_otp(self, otp_request: OtpRequest) -> None:
        user = self.user_service.get_user_by_email(otp_request.email)
        if not user:
            raise AppException(
                status_code=404, message="No user found with the provided email"
            )
        if user.is_verified:
            raise AppException(
                status_code=400, message="Your account is already verified"
            )

        otp = generate_otp()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)
        self.user_service.update_user(user.id, {"otp": otp, "otp_expiry": expires_at})

        try:
            await send_email(
                to=user.email,
                subject=f"Hey {user.name}! Here is your resend OTP",
                template_name="verify_otp_email.html",
                otp=otp,
            )
        except Exception as e:
            print(f"⚠️ Email sending failed: {e}. [DEV OTP]: {otp}")

    def update_user_password(
        self, current_user: User, change_password_request: ChangePasswordRequest
    ) -> User:
        if not verify_password(
            change_password_request.old_password, current_user.password
        ):
            raise AppException(
                status_code=401, message="Your provided old password is incorrect"
            )

        if change_password_request.new_password == change_password_request.old_password:
            raise AppException(
                status_code=400,
                message="New password cannot be the same as the old password",
            )

        updated_data = {"password": hash_password(change_password_request.new_password)}
        return self.user_service.update_user(current_user.id, updated_data)

    async def initiate_password_reset(
        self, forgot_password_request: ForgotPasswordRequest
    ) -> None:
        user = self.user_service.get_user_by_email(forgot_password_request.email)
        if not user:
            raise AppException(status_code=404, message="No user found with this email")

        otp = generate_otp()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)
        self.user_service.update_user(user.id, {"otp": otp, "otp_expiry": expires_at})

        try:
            await send_email(
                to=user.email,
                subject="Welcome Back! Here is your reset password OTP",
                template_name="verify_otp_email.html",
                otp=otp,
            )
        except Exception as e:
            print(f"⚠️ Email sending failed: {e}. [DEV OTP]: {otp}")


    def verify_reset_password_otp(
        self, verify_reset_otp_request: ResetPasswordOTPRequest
    ) -> dict:
        user = self.user_service.get_user_by_email(verify_reset_otp_request.email)
        if not user:
            raise AppException(status_code=404, message="No user found with this email")

        if user.otp != verify_reset_otp_request.otp:
            raise AppException(
                status_code=401, message="Your provided OTP is incorrect"
            )
        if user.otp_expiry and user.otp_expiry < datetime.now(timezone.utc):
            raise AppException(
                status_code=401,
                message="Your OTP has expired. Please request a new OTP",
            )

        reset_token = create_verification_token(
            data={"sub": str(user.id), "email": user.email, "type": "password_reset"},
            expires_minutes=5,
        )
        self.user_service.update_user(user.id, {"otp": None, "otp_expiry": None})

        return {
            "reset_token": reset_token,
            "message": "Use this token to reset your password",
        }

    def reset_user_password_with_token(
        self, reset_password_request: ResetPasswordRequest
    ) -> User:
        payload = decode_access_token(reset_password_request.token)
        user_id = payload.get("sub")
        token_type = payload.get("type")

        if not user_id or token_type != "password_reset":
            raise AppException(status_code=400, message="Invalid password reset token")

        updated_data = {"password": hash_password(reset_password_request.new_password)}
        return self.user_service.update_user(user_id, updated_data)


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)