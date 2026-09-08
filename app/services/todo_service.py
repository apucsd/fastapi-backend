from sqlalchemy.orm import Session
from app.schemas.todo import TodoCreate
from app.models.todo import Todo

class TodoService:
    def __init__(self, db: Session):
        self.db = db

    
    def create_todo(self, data: TodoCreate):
        
        todo = Todo(
            title=data.title,
            description=data.description,
            status=data.status,
        )
        
        self.db.add(todo)
        self.db.commit()
        self.db.refresh(todo)

        return todo

        
    def get_all(self):
        return self.db.query(Todo).all()