from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class TeacherCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)
    full_name: str = Field(..., min_length=3, max_length=100)
    club_id: Optional[int] = None


class TeacherUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=3, max_length=100)
    club_id: Optional[int] = None
    is_active: Optional[bool] = None
    new_password: Optional[str] = Field(None, min_length=6, max_length=100)


class TeacherResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    full_name: str
    role: str
    club_id: Optional[int] = None
    club_name: Optional[str] = None
    is_active: bool
    created_at: datetime
