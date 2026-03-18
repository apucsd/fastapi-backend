from fastapi import APIRouter, Depends
from app.db.session import get_db
from app.schemas.auth import (
    ForgotPasswordRequest,
    RegisterRequest,
    LoginRequest,
    OtpRequest,
    ChangePasswordRequest,
    ResetPasswordOTPRequest,
    ResetPasswordRequest,
)
from sqlalchemy.orm import Session
from app.services import auth_service
from app.services.auth_service import AuthService
from app.schemas.response import api_response
from app.models.user import User
from app.utils import auth
from app.utils.auth import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register")
async def register_user(
    register_request: RegisterRequest, db: Session = Depends(get_db)
):
    auth_service = AuthService(db)
    new_user = await auth_service.register(register_request)
    return api_response(
        status_code=201,
        success=True,
        message="User registered successfully",
        data=new_user,
    )


@router.post("/login")
async def login_user(login_request: LoginRequest, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    user = await auth_service.login(login_request)
    return api_response(
        status_code=200, success=True, message="User logged in successfully", data=user
    )


@router.post("/verify-otp")
async def verify_otp(otp_request: OtpRequest, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    user = await auth_service.verify_otp(otp_request)
    return api_response(
        status_code=200, success=True, message="User verified successfully", data=user
    )


@router.post("/resend-otp")
async def resend_otp(otp_request: OtpRequest, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    user = await auth_service.resend_otp(otp_request)
    return api_response(
        status_code=200, success=True, message="OTP resent successfully", data=user
    )


@router.patch("/change-password")
async def change_password(
    current_user: User = Depends(get_current_user),
    change_password_request: ChangePasswordRequest = None,
    db: Session = Depends(get_db),
):
    auth_service = AuthService(db)
    user = await auth_service.change_password(current_user, change_password_request)
    return api_response(
        status_code=200,
        success=True,
        message="Password changed successfully",
        data=user,
    )


@router.post("/forgot-password")
async def forgot_password(
    forgot_password_request: ForgotPasswordRequest, db: Session = Depends(get_db)
):
    auth_service = AuthService(db)
    user = await auth_service.forgot_password(forgot_password_request)

    return api_response(
        status_code=200,
        success=True,
        message="Reset otp has send to user email",
        data=user,
    )

@router.post("/verify-reset-otp")
async def verify_reset_otp(reset_password_otp_request: ResetPasswordOTPRequest, db: Session= Depends(get_db)):
    auth_service = AuthService(db)
    result = await auth_service.verify_reset_otp(reset_password_otp_request)

    return api_response(status_code= 200, message="OTP verified successfully", data=result)


@router.post("/reset-password")
async def reset_password(reset_password_request: ResetPasswordRequest, db: Session= Depends(get_db)):
    auth_service = AuthService(db)
    result = await auth_service.reset_password(reset_password_request)

    return api_response(status_code= 200, message="Your password has reset successfully", data=result)