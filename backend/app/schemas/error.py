from pydantic import BaseModel


class NotFoundError(Exception):
    pass


# Request model for error responses
class ErrorResponse(BaseModel):
    error: str
    message: str
