from fastapi import APIRouter, Depends, status

from app.models.user import User
from app.schemas.auth import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    OtpRequest,
    RegisterRequest,
    ResetPasswordOTPRequest,
    ResetPasswordRequest,
    ResetTokenResponse,
    TokenResponse,
    UserResponse,
)
from app.schemas.response import ApiResponse
from app.services.auth_service import AuthService, get_auth_service
from app.utils.auth import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=ApiResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    register_request: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    new_user = await auth_service.register_user(register_request)
    return ApiResponse(
        status_code=status.HTTP_201_CREATED,
        message="User registered successfully. Please check your email for the OTP.",
        data=new_user,
    )


@router.post(
    "/login",
    response_model=ApiResponse[TokenResponse],
    status_code=status.HTTP_200_OK,
)
async def login_user(
    login_request: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    result = await auth_service.authenticate_user(login_request)
    return ApiResponse(
        status_code=status.HTTP_200_OK,
        message="User logged in successfully",
        data=result,
    )



@router.post(
    "/verify-otp",
    response_model=ApiResponse[UserResponse],
    status_code=status.HTTP_200_OK,
)
def verify_otp(
    otp_request: OtpRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    result = auth_service.verify_user_email(otp_request)
    return ApiResponse(
        status_code=status.HTTP_200_OK,
        message="User verified successfully",
        data=result,
    )


@router.post(
    "/resend-otp",
    response_model=ApiResponse[None],
    status_code=status.HTTP_200_OK,
)
async def resend_otp(
    otp_request: OtpRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    await auth_service.resend_user_verification_otp(otp_request)
    return ApiResponse(
        status_code=status.HTTP_200_OK,
        message="OTP resent successfully",
        data=None,
    )


@router.patch(
    "/change-password",
    response_model=ApiResponse[UserResponse],
    status_code=status.HTTP_200_OK,
)
def change_password(
    change_password_request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
):
    result = auth_service.update_user_password(
        current_user, change_password_request
    )
    return ApiResponse(
        status_code=status.HTTP_200_OK,
        message="Password changed successfully",
        data=result,
    )


@router.post(
    "/forgot-password",
    response_model=ApiResponse[None],
    status_code=status.HTTP_200_OK,
)
async def forgot_password(
    forgot_password_request: ForgotPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    await auth_service.initiate_password_reset(forgot_password_request)
    return ApiResponse(
        status_code=status.HTTP_200_OK,
        message="Password reset OTP has been sent to your email",
        data=None,
    )


@router.post(
    "/verify-reset-otp",
    response_model=ApiResponse[ResetTokenResponse],
    status_code=status.HTTP_200_OK,
)
def verify_reset_otp(
    reset_password_otp_request: ResetPasswordOTPRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    result = auth_service.verify_reset_password_otp(reset_password_otp_request)
    return ApiResponse(
        status_code=status.HTTP_200_OK,
        message="OTP verified successfully",
        data=result,
    )


@router.post(
    "/reset-password",
    response_model=ApiResponse[UserResponse],
    status_code=status.HTTP_200_OK,
)
def reset_password(
    reset_password_request: ResetPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    result = auth_service.reset_user_password_with_token(reset_password_request)
    return ApiResponse(
        status_code=status.HTTP_200_OK,
        message="Your password has been reset successfully",
        data=result,
    )