from fastapi import APIRouter, Depends, File, UploadFile
from app.db.session import get_db
from sqlalchemy.orm import Session
from app.models.user import User
from app.utils.auth import get_current_user
from app.services.resume_service import ResumeService
from app.schemas.response import api_response
from app.schemas.resume import ResumeUpdate

router = APIRouter(prefix="/resume", tags=["Resume"])

@router.post('/')
async def upload_resume(
    current_user: User = Depends(get_current_user),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):  
    resume_service = ResumeService(db)

    saved_resume = await resume_service.process_and_save_resume(
        user_id=current_user.id, 
        file=file
    )
    
    return api_response(
        status_code=201, 
        success=True, 
        message="Resume uploaded successfully!", 
        data={
            "resume_id": str(saved_resume.id), 
            "file_url": saved_resume.file_url,
            "skills": saved_resume.skills,
            "experience": saved_resume.experience,
            "education": saved_resume.education
        }
    )

@router.get('/me')
async def get_resume(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    resume_service = ResumeService(db)
    resume = resume_service.get_resume_by_user_id(current_user.id)
    
    if not resume:
        return api_response(
            status_code=404,
            success=False,
            message="Resume not found. Please upload your resume first.",
            data=None
        )
    
    return api_response(
        status_code=200, 
        success=True, 
        message="Resume data retrieved successfully!", 
        data={
            "resume_id": str(resume.id),
            "file_url": resume.file_url,
            "raw_text": resume.raw_text,
            "skills": resume.skills,
            "experience": resume.experience,
            "education": resume.education,
            "created_at": str(resume.created_at),
            "updated_at": str(resume.updated_at)
        }
    )

@router.patch('/me')
async def update_resume(
    body: ResumeUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    resume_service = ResumeService(db)
    updated_resume = resume_service.update_resume(
        user_id=current_user.id,
        update_data=body.model_dump(exclude_unset=True)
    )
    
    return api_response(
        status_code=200,
        success=True,
        message="Resume updated successfully!",
        data={
            "resume_id": str(updated_resume.id),
            "file_url": updated_resume.file_url,
            "skills": updated_resume.skills,
            "experience": updated_resume.experience,
            "education": updated_resume.education
        }
    )