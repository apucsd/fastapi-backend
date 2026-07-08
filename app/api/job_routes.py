from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.utils.auth import get_current_user
from app.services.job_service import JobService
from app.schemas.job import JobStatusUpdate
from app.schemas.response import api_response

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post('/discover')
async def discover_jobs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job_service = JobService(db)
    saved_jobs = await job_service.discover_jobs_for_user(user_id=current_user.id)

    return api_response(
        status_code=201,
        success=True,
        message=f"Discovered and scored {len(saved_jobs)} new jobs!",
        data=[
            {
                "id": str(j.id),
                "title": j.title,
                "company": j.company,
                "match_score": j.match_score,
            }
            for j in saved_jobs
        ],
    )


@router.get('/matched')
async def get_matched_jobs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job_service = JobService(db)
    jobs = job_service.get_matched_jobs(user_id=current_user.id)

    return api_response(
        status_code=200,
        success=True,
        message="Matched jobs retrieved successfully!",
        data=[
            {
                "id": str(j.id),
                "title": j.title,
                "company": j.company,
                "location": j.location,
                "url": j.url,
                "match_score": j.match_score,
                "matching_skills": j.matching_skills,
                "missing_skills": j.missing_skills,
                "status": j.status.value,
            }
            for j in jobs
        ],
    )


@router.get('/{job_id}')
async def get_job_detail(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job_service = JobService(db)
    job = job_service.get_job_by_id(job_id=job_id, user_id=current_user.id)

    return api_response(
        status_code=200,
        success=True,
        message="Job details retrieved!",
        data={
            "id": str(job.id),
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "description": job.description,
            "url": job.url,
            "source": job.source,
            "match_score": job.match_score,
            "matching_skills": job.matching_skills,
            "missing_skills": job.missing_skills,
            "status": job.status.value,
            "created_at": str(job.created_at),
        },
    )


@router.patch('/{job_id}/status')
async def update_job_status(
    job_id: str,
    body: JobStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job_service = JobService(db)
    updated_job = job_service.update_job_status(
        job_id=job_id,
        user_id=current_user.id,
        new_status=body.status,
    )

    return api_response(
        status_code=200,
        success=True,
        message=f"Job status updated to {updated_job.status.value}!",
        data={
            "id": str(updated_job.id),
            "title": updated_job.title,
            "status": updated_job.status.value,
        },
    )


@router.post('/{job_id}/cover-letter')
async def generate_cover_letter(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job_service = JobService(db)
    job = await job_service.generate_cover_letter_for_job(
        job_id=job_id,
        user_id=current_user.id,
    )

    return api_response(
        status_code=201,
        success=True,
        message="Cover letter generated successfully!",
        data={
            "job_id": str(job.id),
            "title": job.title,
            "company": job.company,
            "cover_letter": job.cover_letter,
        },
    )


@router.get('/{job_id}/cover-letter')
async def get_cover_letter(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job_service = JobService(db)
    job = job_service.get_job_by_id(job_id=job_id, user_id=current_user.id)

    if not job.cover_letter:
        return api_response(
            status_code=404,
            success=False,
            message="No cover letter generated yet. Use POST to generate one.",
            data=None,
        )

    return api_response(
        status_code=200,
        success=True,
        message="Cover letter retrieved!",
        data={
            "job_id": str(job.id),
            "title": job.title,
            "company": job.company,
            "cover_letter": job.cover_letter,
        },
    )
