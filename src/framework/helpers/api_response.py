from pydantic import BaseModel
from typing import Generic, TypeVar, Optional, Any

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    status: str = "success"
    data: Optional[T] = None
    message: Optional[str] = None
    error_code: Optional[str] = None


class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
    error_code: Optional[str] = None
