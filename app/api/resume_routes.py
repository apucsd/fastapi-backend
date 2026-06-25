from fastapi import APIRouter, Depends, File, UploadFile
from app.db.session import get_db
from sqlalchemy.orm import Session
from app.models.user import User
from app.utils.auth import get_current_user
from app.services.resume_service import ResumeService
from app.schemas.response import api_response

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
        data={"resume_id": str(saved_resume.id), "file_url": saved_resume.file_url}
    )
@router.get('/me')
async def get_resume(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    resume_service = ResumeService(db)
    resume = resume_service.get_resume_by_user_id(current_user.id)
    return api_response(
        status_code=200, 
        success=True, 
        message="Resume data retrieved successfully!", 
        data={"resume_id": str(resume.id), "file_url": resume.file_url}
    )