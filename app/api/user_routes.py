from fastapi import APIRouter, Depends, Request
from app.schemas.response import api_response
from app.utils.auth import get_current_user
from app.models.user import User
from sqlalchemy.orm import Session
from app.services.user_service import UserService
from app.db.session import get_db
from app.utils.auth import require_role

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/")
def list_users(

    request: Request, current_user: User = Depends(require_role("USER")), db: Session = Depends(get_db)
):
    print(current_user, "current user")
    user_service = UserService(db)
    query_params = dict(request.query_params)
    result = user_service.get_all_users(query_params)
    return api_response(
        success=True, message="Users retrieved successfully", data=result["data"], meta=result["meta"]
    )


@router.get("/profile")
def user_profile(current_user: User = Depends(get_current_user)):
    return api_response(
        success=True, message="User profile retrieved successfully", data=current_user
    )


