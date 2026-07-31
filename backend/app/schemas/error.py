from pydantic import BaseModel


class NotFoundError(Exception):
    pass


class ErrorResponse(BaseModel):
    error: str
    message: str


class ApiErrorResponse(BaseModel):
    detail: str
