from fastapi import APIRouter
from app.schemas.auth import RegisterRequest, LoginRequest

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register")
def register_user(register_request: RegisterRequest):
    return {"message": "User registered successfully"}

@router.post("/login")
def login_user(login_request: LoginRequest):
    return {"message": "User logged in successfully"}