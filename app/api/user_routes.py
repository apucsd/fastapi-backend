from typing import Any, List
from fastapi import APIRouter, Depends, Request, status

from app.models.user import User
from app.schemas.response import ApiResponse
from app.schemas.user import UserResponse
from app.services.user_service import UserService, get_user_service
from app.utils.auth import get_current_user, require_role

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=ApiResponse[List[dict[str, Any]]])
def list_users(
    request: Request,
    current_user: User = Depends(require_role("USER")),
    user_service: UserService = Depends(get_user_service),
):
    query_params = dict(request.query_params)
    result = user_service.get_all_users(query_params)
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



