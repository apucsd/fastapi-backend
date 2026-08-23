from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    name: str = Field(default="Apu Sutradhar")
    email: EmailStr = Field(default="apusutradhar77@gmail.com")
    password: str = Field(default="password123")


class LoginRequest(BaseModel):
    email: EmailStr = Field(default="apusutradhar77@gmail.com")
    password: str = Field(default="password123")



class OtpRequest(BaseModel):
    email: EmailStr = Field(default="apusutradhar77@gmail.com")
    otp: str = Field(default="123456")


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordOTPRequest(BaseModel):
    email: EmailStr
    otp: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str





# ---Response Schemas ---#
class UserResponse(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    role: str
    is_verified: bool = False
    status: str
    image_url: Optional[str] = None

    created_at: Optional[datetime]= None
    updated_at: Optional[datetime]= None
    
    class Config:
        from_attributes = True
        
    

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
class ResetTokenResponse(BaseModel):
    reset_token: str
    message: str = "Use this token to reset your password"
