from uuid import UUID
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.todo import TodoStatus
class TodoResponse(BaseModel):
    id: UUID
    title : str
    description : str
    status : TodoStatus
    class Config:
        from_attributes = True
    
class TodoCreate(BaseModel):
    title : str
    description : Optional[str]= None
    status: TodoStatus = TodoStatus.IN_PROGRESS
    

class TodoUpdate(BaseModel):
    title : Optional[str] = None
    description : Optional[str] = None
    status : Optional[TodoStatus] = None