from sqlalchemy.dialects.postgresql.base import UUID
from sqlalchemy import Column
from app.db.base import Base,TimestampMixin
import uuid
import enum

class Status(enum.Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"
    
class Todo(Base, TimestampMixin):
    __tablename__ = "todo"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4())

    title = Column(String, nullable=False)

    description = Column(String, nullable=True)

    status = Column(
        Enum(Status, name="todo_status"), default=Status.TODO, nullable=False
    )   
    


