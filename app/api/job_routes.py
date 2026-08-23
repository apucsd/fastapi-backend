from typing import List
from fastapi import APIRouter, Depends, status

from app.models.user import User
from app.schemas.job import (
    CoverLetterResponse,
    JobResponse,
    JobStatusResponse,
    JobStatusUpdate,
    JobSummaryResponse,
)
from app.schemas.response import ApiResponse
from app.services.job_service import JobService, get_job_service
from app.utils.auth import get_current_user
from app.utils.exceptions import AppException

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post(
    "/discover",
    response_model=ApiResponse[List[JobSummaryResponse]],
    status_code=status.HTTP_201_CREATED,
)
async def discover_jobs(
    current_user: User = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service),
):
    saved_jobs = await job_service.discover_jobs_for_user(user_id=current_user.id)
    return ApiResponse(
        status_code=status.HTTP_201_CREATED,
        message=f"Discovered and scored {len(saved_jobs)} new jobs!",
        data=saved_jobs,
    )


@router.get(
    "/matched",
    response_model=ApiResponse[List[JobResponse]],
    status_code=status.HTTP_200_OK,
)
def get_matched_jobs(
    current_user: User = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service),
):
    jobs = job_service.get_matched_jobs(user_id=current_user.id)
    return ApiResponse(
        status_code=status.HTTP_200_OK,
        message="Matched jobs retrieved successfully!",
        data=jobs,
    )


@router.get(
    "/{job_id}",
    response_model=ApiResponse[JobResponse],
    status_code=status.HTTP_200_OK,
)
def get_job_detail(
    job_id: str,
    current_user: User = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service),
):
    job = job_service.get_job_by_id(job_id=job_id, user_id=current_user.id)
    return ApiResponse(
        status_code=status.HTTP_200_OK,
        message="Job details retrieved!",
        data=job,
    )


@router.patch(
    "/{job_id}/status",
    response_model=ApiResponse[JobStatusResponse],
    status_code=status.HTTP_200_OK,
)
def update_job_status(
    job_id: str,
    body: JobStatusUpdate,
    current_user: User = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service),
):
    updated_job = job_service.update_job_status(
        job_id=job_id,
        user_id=current_user.id,
        new_status=body.status,
    )
    return ApiResponse(
        status_code=status.HTTP_200_OK,
        message=f"Job status updated to {updated_job.status.value}!",
        data=updated_job,
    )


@router.post(
    "/{job_id}/cover-letter",
    response_model=ApiResponse[CoverLetterResponse],
    status_code=status.HTTP_201_CREATED,
)
async def generate_cover_letter(
    job_id: str,
    current_user: User = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service),
):
    job = await job_service.generate_cover_letter_for_job(
        job_id=job_id,
        user_id=current_user.id,
    )
    return ApiResponse(
        status_code=status.HTTP_201_CREATED,
        message="Cover letter generated successfully!",
        data={
            "job_id": job.id,
            "title": job.title,
            "company": job.company,
            "cover_letter": job.cover_letter,
        },
    )


@router.get(
    "/{job_id}/cover-letter",
    response_model=ApiResponse[CoverLetterResponse],
    status_code=status.HTTP_200_OK,
)
def get_cover_letter(
    job_id: str,
    current_user: User = Depends(get_current_user),
    job_service: JobService = Depends(get_job_service),
):
    job = job_service.get_job_by_id(job_id=job_id, user_id=current_user.id)
    if not job.cover_letter:
        raise AppException(
            status_code=404,
            message="No cover letter generated yet. Use POST to generate one.",
        )

    return ApiResponse(
        status_code=status.HTTP_200_OK,
        message="Cover letter retrieved!",
        data={
            "job_id": job.id,
            "title": job.title,
            "company": job.company,
            "cover_letter": job.cover_letter,
        },
    )

