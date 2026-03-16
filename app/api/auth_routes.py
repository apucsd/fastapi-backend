
from fastapi import APIRouter, Depends
from app.db.session import get_db
from app.schemas.auth import RegisterRequest, LoginRequest, OtpRequest
from sqlalchemy.orm import Session
from app.services.auth_service import AuthService
from app.schemas.response import api_response


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register")
async def register_user(register_request: RegisterRequest, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    new_user = await auth_service.register(register_request)
    return api_response(status_code=201, success=True, message="User registered successfully", data=new_user)
@router.post("/login")
async def login_user(login_request: LoginRequest, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    user = await auth_service.login(login_request)
    return api_response(status_code=200, success=True, message="User logged in successfully", data=user)


@router.post("/verify-otp")
async def verify_otp(otp_request: OtpRequest, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    user = await auth_service.verify_otp(otp_request)
    return api_response(status_code=200, success=True, message="User verified successfully", data=user)

@router.post("/resend-otp")
async def resend_otp(otp_request: OtpRequest, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    user = await auth_service.resend_otp(otp_request)
    return api_response(status_code=200, success=True, message="OTP resent successfully", data=user)