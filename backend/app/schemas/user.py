from pydantic import BaseModel


class UserUpdate(BaseModel):
    full_name: str | None = None
    # email: Optional[EmailStr] = None


class UserStatusUpdate(BaseModel):
    is_active: bool
