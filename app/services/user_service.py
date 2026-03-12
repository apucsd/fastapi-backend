from app.schemas.auth import RegisterRequest
from app.models.user import User
from fastapi import HTTPException
class UserService:
    def __init__(self, db):
        self.db = db

    def create_user(self, user: RegisterRequest):
        existing = self.db.query(User).filter(User.email == user.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user