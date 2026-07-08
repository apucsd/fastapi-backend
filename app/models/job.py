import uuid
import enum

from sqlalchemy import Column, String, Text, Integer, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.db.base import Base, TimestampMixin


class JobStatus(enum.Enum):
    NEW = "NEW"
    INTERESTED = "INTERESTED"
    SKIPPED = "SKIPPED"
    APPLIED = "APPLIED"


class Job(Base, TimestampMixin):
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    title = Column(String, nullable=False)
    company = Column(String, nullable=True)
    location = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    url = Column(String, nullable=True)
    source = Column(String, nullable=True)  # e.g. "remoteok", "manual"

    match_score = Column(Integer, nullable=True)  # 0-100
    matching_skills = Column(JSONB, nullable=True)  # ["Python", "FastAPI"]
    missing_skills = Column(JSONB, nullable=True)   # ["Kubernetes", "Terraform"]

    status = Column(
        Enum(JobStatus, name="job_status"), default=JobStatus.NEW, nullable=False
    )

    cover_letter = Column(Text, nullable=True)

    # Relationship
    user = relationship("User", back_populates="jobs")
