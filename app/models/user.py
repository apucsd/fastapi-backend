
from sqlalchemy import Column, String, Enum, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum

from app.db.base import Base, TimestampMixin


class UserStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    DELETED = "DELETED"
    BLOCKED = "BLOCKED"

class UserRole(enum.Enum):
    ADMIN = "ADMIN"
    SUPER_ADMIN = "SUPER_ADMIN"
    USER = "USER"

class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    password = Column(String, nullable=False)
    image_url = Column(String, nullable=True)
    role = Column(
        Enum(UserRole, name="user_role"),
        default=UserRole.USER,
        nullable=False
    )


    is_verified = Column(Boolean, default=False)
    is_agreed_to_terms = Column(Boolean, default=True)

    status = Column(
        Enum(UserStatus, name="user_status"),
        default=UserStatus.ACTIVE,
        nullable=False
    )

    otp = Column(String, nullable=True)
    otp_expiry = Column(DateTime(timezone=True), nullable=True)
 
