from uuid import UUID
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class ResumeBase(BaseModel):
    file_url: Optional[str] = Field(None, description="Url of the resume")
    raw_text: Optional[str] = Field(None, description="Raw text extracted from the PDF")
    
    skills: Optional[List[str]] = Field(None)
    experience: Optional[List[Dict[str, Any]]] = Field(None)
    education: Optional[List[Dict[str, Any]]] = Field(None)


class ResumeCreate(ResumeBase):
    user_id: UUID

    model_config = {
        "json_schema_extra": {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "file_url": "https://s3.amazonaws.com/mybucket/my-resume.pdf",
                "raw_text": "Experienced Python Developer with FastAPI...",
                "skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
                "experience": [
                    {
                        "company": "Tech Corp",
                        "role": "Backend Engineer",
                        "years": 2,
                        "description": "Built scalable APIs using FastAPI."
                    }
                ],
                "education": [
                    {
                        "institution": "MIT",
                        "degree": "B.S. Computer Science"
                    }
                ]
            }
        } 
    }

