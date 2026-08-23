from typing import Any, Generic, Optional, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    status_code: int = 200
    success: bool = True
    message: str = "Success"
    data: Optional[T] = None
    meta: Optional[dict[str, Any]] = None


