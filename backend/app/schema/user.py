from typing import Optional

from pydantic import BaseModel


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    # email: Optional[EmailStr] = None


class UserStatusUpdate(BaseModel):
    is_active: bool
