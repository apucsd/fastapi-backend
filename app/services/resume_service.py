import fitz
from app.utils.exceptions import AppException
from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.models.resume import Resume
from app.utils.cloudinary import upload_file_to_cloudinary
from app.services.ai_service import AIService


class ResumeService:
    def __init__(self, db: Session):
        self.db = db
        self.ai_service = AIService()

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
        
        # print(f"Extracted text from PDF: {raw_text}")

        existing_resume = self.db.query(Resume).filter(Resume.user_id == user_id).first()
        
        print(f"[DEBUG] existing_resume found: {existing_resume is not None}")
        
        if existing_resume:
            print(f"[DEBUG] Updating existing resume")
            existing_resume.file_url = file_url
            existing_resume.raw_text = raw_text
            self.db.commit()
            self.db.refresh(existing_resume)
            
            # Extract AI data for existing resume too
            print(f"[DEBUG] Calling _extract_and_update_resume_data for existing resume")
            await self._extract_and_update_resume_data(existing_resume.id, raw_text)
            print(f"[DEBUG] Called _extract_and_update_resume_data for existing resume")
            
            return existing_resume
        else:
            print(f"[DEBUG] Creating new resume")
            new_resume = Resume(
                user_id=user_id,
                file_url=file_url,
                raw_text=raw_text
            )
            self.db.add(new_resume)
            self.db.commit()
            self.db.refresh(new_resume)
            
            # Extract AI data in background
            print(f"[DEBUG] Calling _extract_and_update_resume_data")
            await self._extract_and_update_resume_data(new_resume.id, raw_text)
            print(f"[DEBUG] Called _extract_and_update_resume_data")
            
            return new_resume
    
    async def _extract_and_update_resume_data(self, resume_id: int, raw_text: str):
        print(f"[DEBUG] _extract_and_update_resume_data called with resume_id={resume_id}")
        try:
            print(f"Starting AI extraction for resume ID: {resume_id}")
            extracted_data = await self.ai_service.extract_resume_data(raw_text)
            print(f"AI extraction successful")
            
            resume = self.db.query(Resume).filter(Resume.id == resume_id).first()
            if resume:
                resume.skills = extracted_data.get("skills")
                resume.experience = extracted_data.get("experience")
                resume.education = extracted_data.get("education")
                self.db.commit()
                self.db.refresh(resume)
                print(f"Updated resume {resume_id} with AI data")
            else:
                print(f"Resume with ID {resume_id} not found")
        except Exception as e:
            print(f"AI extraction failed: {e}")
            import traceback
            traceback.print_exc()

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