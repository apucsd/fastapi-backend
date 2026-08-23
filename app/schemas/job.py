from uuid import UUID
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class JobSummaryResponse(BaseModel):
    id: UUID
    title: str
    company: Optional[str] = None
    match_score: Optional[int] = None

    class Config:
        from_attributes = True


class JobResponse(BaseModel):
    id: UUID
    title: str
    company: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    source: Optional[str] = None
    match_score: Optional[int] = None
    matching_skills: Optional[List[str]] = None
    missing_skills: Optional[List[str]] = None
    status: str
    cover_letter: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CoverLetterResponse(BaseModel):
    job_id: UUID
    title: str
    company: Optional[str] = None
    cover_letter: Optional[str] = None


class JobStatusUpdate(BaseModel):
    status: str = Field(..., description="One of: NEW, INTERESTED, SKIPPED, APPLIED")

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "INTERESTED"
            }
        }
    }


class JobStatusResponse(BaseModel):
    id: UUID
    title: str
    status: str

