from app.models.user import User
from fastapi import HTTPException
class UserService:
    def __init__(self, db):
        self.db = db

    def create_user(self, user):
        existing =  self.db.query(User).filter(User.email == user.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user 
    def get_user_by_id(self, user_id):
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, email):
        return self.db.query(User).filter(User.email == email).first()
    
    def update_user(self, user_id, updated_user):
        existing = self.get_user_by_id(user_id)
        if not existing:
            return None
        for key, value in updated_user.items():
            setattr(existing, key, value) 
        self.db.merge(existing)
        self.db.commit()
        return existing
        
        
        