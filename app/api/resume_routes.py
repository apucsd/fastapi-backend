from fastapi import APIRouter, Depends, File, UploadFile, status

from app.models.user import User
from app.schemas.response import ApiResponse
from app.schemas.resume import ResumeResponse, ResumeUpdate
from app.services.resume_service import ResumeService, get_resume_service
from app.utils.auth import get_current_user
from app.utils.exceptions import AppException

router = APIRouter(prefix="/resume", tags=["Resume"])


@router.post(
    "/",
    response_model=ApiResponse[ResumeResponse],
    status_code=status.HTTP_201_CREATED,
)
async def upload_resume(
    current_user: User = Depends(get_current_user),
    file: UploadFile = File(...),
    resume_service: ResumeService = Depends(get_resume_service),
):
    saved_resume = await resume_service.process_and_save_resume(
        user_id=current_user.id, file=file
    )
    return ApiResponse(
        message="Resume uploaded successfully!",
        data=saved_resume,
    )


@router.get(
    "/me",
    response_model=ApiResponse[ResumeResponse],
    status_code=status.HTTP_200_OK,
)
def get_resume(
    current_user: User = Depends(get_current_user),
    resume_service: ResumeService = Depends(get_resume_service),
):
    resume = resume_service.get_resume_by_user_id(current_user.id)
    if not resume:
        raise AppException(
            status_code=404,
            message="Resume not found. Please upload your resume first.",
        )

    return ApiResponse(
        message="Resume data retrieved successfully!",
        data=resume,
    )


@router.patch(
    "/me",
    response_model=ApiResponse[ResumeResponse],
    status_code=status.HTTP_200_OK,
)
def update_resume(
    body: ResumeUpdate,
    current_user: User = Depends(get_current_user),
    resume_service: ResumeService = Depends(get_resume_service),
):
    updated_resume = resume_service.update_resume(
        user_id=current_user.id,
        update_data=body.model_dump(exclude_unset=True),
    )
    return ApiResponse(
        message="Resume updated successfully!",
        data=updated_resume,
    )