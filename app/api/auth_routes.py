
from fastapi import APIRouter, Depends
from app.db.session import get_db
from app.schemas.auth import RegisterRequest, LoginRequest, OtpRequest
from sqlalchemy.orm import Session
from app.services.auth_service import AuthService


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register")
async def register_user(register_request: RegisterRequest, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    new_user = await auth_service.register(register_request)
    return {"message": "User registered successfully", "user_id": new_user}
@router.post("/login")
async def login_user(login_request: LoginRequest, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    user = await auth_service.login(login_request)
    return user


@router.post("/verify-otp")
async def verify_otp(otp_request: OtpRequest, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    user = await auth_service.verify_otp(otp_request)
    return user