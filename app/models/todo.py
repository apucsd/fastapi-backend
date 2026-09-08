from sqlalchemy import Enum, String, Column
from sqlalchemy.dialects.postgresql.base import UUID
from app.db.base import Base,TimestampMixin
import uuid
import enum

class TodoStatus(enum.Enum):
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"
    
class Todo(Base, TimestampMixin):
    __tablename__ =  "todos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4())

    title= Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(Enum(TodoStatus), nullable=False, default=TodoStatus.IN_PROGRESS,)

    