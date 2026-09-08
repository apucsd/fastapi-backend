from app.db.session import get_db
from fastapi import Depends
from sqlalchemy.orm import Session
from app.schemas.todo import TodoCreate
from app.schemas.todo import TodoResponse
from app.schemas.response import ApiResponse
from fastapi import APIRouter

from app.services.todo_service import TodoService


router = APIRouter(prefix="/todos", tags=["Todo"])


@router.post(
    "/create",
    response_model=ApiResponse[TodoResponse],
)
async def create_todo(todo_request: TodoCreate, db: Session = Depends(get_db)):
    todo_service = TodoService(db)
    todo_service = await todo_service.create_todo(todo_request)
    return ApiResponse(
        message="Todo created successfully",
        data=todo_service,
    )
    