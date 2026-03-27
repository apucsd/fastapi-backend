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