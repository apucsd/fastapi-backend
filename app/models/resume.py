import uuid

from sqlalchemy.orm import relationship
from sqlalchemy import Text, ForeignKey, Column, String
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.db.base import Base, TimestampMixin

class Resume(Base, TimestampMixin):
    __tablename__ = "resumes"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    file_url = Column(String, nullable=True)

    raw_text = Column(Text, nullable=True)

    skills = Column(JSONB, nullable=True)
    experience = Column(JSONB, nullable=True)
    education = Column(JSONB, nullable=True)  

    # SQLAlchemy relationship
    user = relationship("User", back_populates="resume")
