from app.utils.exceptions import AppException
from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.models.resume import Resume
from app.utils.cloudinary import upload_file_to_cloudinary

class ResumeService:
    def __init__(self, db: Session):
        self.db = db

    async def process_and_save_resume(self, user_id: str, file: UploadFile):
        # 1. Validate PDF
        if not file.filename.endswith('.pdf'):
            raise AppException(status_code=400, message='File must be a PDF')

        # 2. Upload to Cloudinary
        upload_result = await upload_file_to_cloudinary(file, folder="resumes")
        
        if not upload_result or not upload_result.get("url"):
            raise AppException(status_code=500, message='Failed to upload resume to Cloudinary')

        file_url = upload_result.get("url")

        # 3. Save to Database
        # Check if user already has a resume, if so, we can either update or reject
        existing_resume = self.db.query(Resume).filter(Resume.user_id == user_id).first()
        
        if existing_resume:
            existing_resume.file_url = file_url
            self.db.commit()
            self.db.refresh(existing_resume)
            return existing_resume
        else:
            new_resume = Resume(
                user_id=user_id,
                file_url=file_url,
                raw_text="Will parse later!"
            )
            self.db.add(new_resume)
            self.db.commit()
            self.db.refresh(new_resume)
            return new_resume