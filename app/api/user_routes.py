from typing import Any, List
from fastapi import APIRouter, Depends, Request, status

from app.models.user import User
from app.schemas.response import ApiResponse
from app.schemas.user import UserResponse
from app.services.user_service import UserService, get_user_service
from app.utils.auth import get_current_user, require_role

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=ApiResponse[List[dict[str, Any]]])
def list_users(
    page: int = 1,
    limit:int =10,
    search_term:str | None = None,
    user_service: UserService = Depends(get_user_service),
):
    result = user_service.get_all_users(page, limit, search_term)
    return ApiResponse(
        message="Users retrieved successfully",
        data=result["data"],
        meta=result["meta"],
    )


@router.get("/profile", response_model=ApiResponse[UserResponse])
def user_profile(current_user: User = Depends(get_current_user)):
    return ApiResponse(
        message="User profile retrieved successfully",
        data=current_user,
    )



