from fastapi import APIRouter, Depends
from app.schemas.response import api_response
from app.utils.auth import get_current_user
from app.models.user import User
from sqlalchemy.orm import Session
from app.services.user_service import UserService
from app.db.session import get_db
from app.utils.auth import require_role

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/profile")
def user_profile(current_user: User = Depends(get_current_user)):
    return api_response(success=True, message="User profile retrieved successfully", data=current_user)


@router.get('/users')
def list_users(current_user: User = Depends(require_role("USER")), db: Session = Depends(get_db)):
    print(current_user, "current user")
    user_service = UserService(db)
    users = user_service.get_all_users()
    return api_response(success=True, message="Users retrieved successfully", data=users)