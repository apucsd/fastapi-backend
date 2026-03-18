from re import A
from app.services import user_service
from app.utils.exceptions import AppException
from datetime import datetime, timedelta, timezone
from app.schemas.auth import (
    RegisterRequest,
    OtpRequest,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    ResetPasswordOTPRequest,
    ResetPasswordRequest,
)
from app.services.user_service import UserService
from app.models.user import User
from app.core.security import (
    decode_access_token,
    hash_password,
    verify_password,
    create_access_token,
    create_verification_token,
)
from app.utils.otp import generate_otp
from app.utils.email import send_email


class AuthService:
    def __init__(self, db):
        self.db = db
        self.user_service = UserService(db)

    async def register_user(self, user: RegisterRequest):
        otp = generate_otp()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)

        new_user = User(
            name=user.name,
            email=user.email,
            password=hash_password(user.password),
            otp=otp,
            otp_expiry=expires_at,
        )
        result = self.user_service.create_user(new_user)
        if result:
            user = self.user_service.get_user_by_email(user.email)
            await send_email(
                to=user.email,
                subject="Welcome! Here is your OTP",
                template_name="verify_otp_email.html",
                otp=otp,
            )
        return result

    async def authenticate_user(self, login_request):
        user = self.db.query(User).filter(User.email == login_request.email).first()

        if not user:
            raise AppException(
                status_code=401,
                message="Your account is not verified. Please verify your account",
            )
        if not verify_password(login_request.password, user.password):
            raise AppException(
                status_code=401, message="Your provided password is incorrect"
            )

        if not user.is_verified:
            raise AppException(
                status_code=401,
                message="Your account is not verified. Please verify your account",
            )

        if user.status == "inactive":
            raise AppException(
                status_code=401,
                message="Your account is inactive. Please contact the administrator",
            )
        if user.status == "deleted":
            raise AppException(
                status_code=401,
                message="Your account is deleted. Please contact the administrator",
            )
        if user.status == "blocked":
            raise AppException(
                status_code=401,
                message="Your account is blocked. Please contact the administrator",
            )

        print(user)

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
            "id": user.id,
            "role": user.role,
            "name": user.name,
            "email": user.email,
        }

    async def verify_user_email(self, otp_request: OtpRequest):
        user = self.user_service.get_user_by_email(otp_request.email)
        if not user:
            raise AppException(
                status_code=404, message="No user found with the provided email"
            )
        if user.otp != otp_request.otp:
            raise AppException(
                status_code=401, message="Your provided OTP is incorrect"
            )
        if user.otp_expiry < datetime.now(timezone.utc):
            raise AppException(
                status_code=401,
                message="Your OTP has expired. Please request a new OTP",
            )

        user = self.user_service.update_user(
            user.id, {"otp": None, "otp_expiry": None}
        )

        return user

    async def resend_user_verification_otp(self, otp_request: OtpRequest):
        user = self.user_service.get_user_by_email(otp_request.email)
        if not user:
            raise AppException(
                status_code=404, message="No user found with the provided email"
            )
        if user.is_verified:
            raise AppException(
                status_code=401, message="Your account is already verified"
            )

        otp = generate_otp()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)
        update_data = {"otp": otp, "otp_expiry": expires_at}
        user = self.user_service.update_user(user.id, update_data)
        await send_email(
            to=user.email,
            subject=f"Hey {user.name}! Here is your resend OTP",
            template_name="verify_otp_email.html",
            otp=otp,
        )
        return user

    async def update_user_password(
        self, current_user: User, change_password_request: ChangePasswordRequest
    ):

        if not verify_password(
            change_password_request.old_password, current_user.password
        ):
            raise AppException(
                status_code=401, message="Your provided old password is incorrect"
            )

        if change_password_request.new_password == change_password_request.old_password:
            raise AppException(
                status_code=401,
                message="New password cannot be the same as the old password",
            )

        updated_user = {"password": hash_password(change_password_request.new_password)}
        user = self.user_service.update_user(current_user.id, updated_user)
        return user

    async def initiate_password_reset(self, forgot_password_request: ForgotPasswordRequest):

        user = self.user_service.get_user_by_email(forgot_password_request.email)
        if not user:
            raise AppException(status_code=404, message="No user found with this email")
        otp = generate_otp()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)

        result = self.user_service.update_user(
            user.id, {"otp": otp, "otp_expiry": expires_at}
        )
        if result:
            await send_email(
                to=user.email,
                subject="Welcome Back! Here is your reset password OTP",
                template_name="verify_otp_email.html",
                otp=otp,
            )

    async def verify_reset_password_otp(self, verify_reset_otp_request: ResetPasswordOTPRequest):
        user_service = UserService(self.db)
        user = user_service.get_user_by_email(verify_reset_otp_request.email)
        if not user:
            raise AppException(status_code=404, message="No user found with this email")
        if not user.is_verified:
            raise AppException(
                status_code=401,
                message="Your account is not verified. Please verify your account",
            )

        if user.status == "inactive":
            raise AppException(
                status_code=401,
                message="Your account is inactive. Please contact the administrator",
            )
        if user.status == "deleted":
            raise AppException(
                status_code=401,
                message="Your account is deleted. Please contact the administrator",
            )
        if user.status == "blocked":
            raise AppException(
                status_code=401,
                message="Your account is blocked. Please contact the administrator",
            )
        if user.otp != verify_reset_otp_request.otp:
            raise AppException(
                status_code=401, message="Your provided OTP is incorrect"
            )
        if user.otp_expiry < datetime.now(timezone.utc):
            raise AppException(
                status_code=401,
                message="Your OTP has expired. Please request a new OTP",
            )

        reset_token = create_verification_token(
            data={"sub": str(user.id), "email": user.email, "type": "password_reset"},
            expires_minutes=5
        )
        self.user_service.update_user(user.id, {"otp": None, "otp_expiry": None})

        return reset_token


    async def reset_user_password_with_token(self, reset_password_request: ResetPasswordRequest):

        payload = decode_access_token(reset_password_request.token)
        user_id = payload.get("sub")
        if not user_id:
            raise AppException(status_code= 404, message="User not found")
        
        # Check if token was issued more than 2 minutes ago (prevents reuse)
        exp = payload.get("exp")
        if exp and (exp - datetime.now(timezone.utc).timestamp()) > 120: 
            raise AppException(status_code=401, message="Token has expired for security reasons")
        
        updated_user ={
            "password": hash_password(reset_password_request.new_password)
        }

        result = self.user_service.update_user(user_id, updated_user)

        return result

