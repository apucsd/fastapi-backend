
from fastapi import APIRouter, Depends
from app.db.session import get_db
from app.schemas.auth import RegisterRequest, LoginRequest
from sqlalchemy.orm import Session
from app.services.auth_service import AuthService


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register")
async def register_user(register_request: RegisterRequest, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    new_user = await auth_service.register(register_request)
    return {"message": "User registered successfully", "user_id": new_user}
@router.post("/login")
async def login_user(login_request: LoginRequest):
    return {"message": "User logged in successfully"}