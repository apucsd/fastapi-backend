from uuid import UUID
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


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
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class JobStatusUpdate(BaseModel):
    status: str = Field(..., description="One of: INTERESTED, SKIPPED, APPLIED")

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "INTERESTED"
            }
        }
    }
