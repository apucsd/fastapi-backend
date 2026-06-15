import fitz
from app.utils.exceptions import AppException
from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.models.resume import Resume
from app.utils.cloudinary import upload_file_to_cloudinary

class ResumeService:
    def __init__(self, db: Session):
        self.db = db

    async def process_and_save_resume(self, user_id: str, file: UploadFile):
        if not file.filename.endswith('.pdf'):
            raise AppException(status_code=400, message='File must be a PDF')

        upload_result = await upload_file_to_cloudinary(file, folder="resumes")
        
        if not upload_result or not upload_result.get("url"):
            raise AppException(status_code=500, message='Failed to upload resume to Cloudinary')

        file_url = upload_result.get("url")
        
        await file.seek(0)
        file_content = await file.read()
        raw_text = await self.extract_text_from_pdf(file_content)
        existing_resume = self.db.query(Resume).filter(Resume.user_id == user_id).first()
        
        if existing_resume:
            existing_resume.file_url = file_url
            existing_resume.raw_text = raw_text
            self.db.commit()
            self.db.refresh(existing_resume)
            return existing_resume
        else:
            new_resume = Resume(
                user_id=user_id,
                file_url=file_url,
                raw_text=raw_text,
                
            )
            self.db.add(new_resume)
            self.db.commit()
            self.db.refresh(new_resume)
            return new_resume
    
    async def extract_text_from_pdf(self, file_content: bytes) -> str:
        try:
            doc = fitz.open(stream=file_content, filetype="pdf")
            
            text_pages = []
            for page in doc:
                text_pages.append(page.get_text())
            
            doc.close()
            
            return "\n".join(text_pages)
            
        except Exception as e:
            raise AppException(status_code=500, message=f'Failed to extract text from PDF: {str(e)}')    
    