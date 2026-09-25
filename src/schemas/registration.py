from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class RegistrationCreate(BaseModel):
    telegram_id: int
    telegram_username: Optional[str] = None
    full_name: str = Field(..., min_length=3, max_length=150)
    phone_number: str = Field(..., min_length=9, max_length=20)
    club_id: int
    course_level: int = Field(..., ge=1, le=4)


class RegistrationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: int
    club_id: int
    full_name: str
    phone_number: str
    telegram_username: Optional[str] = None
    faculty_name: str
    direction_name: str
    club_name: str
    course_level: int
    status: str
    registered_at: datetime


class RegistrationFilterParams(BaseModel):
    faculty_id: Optional[int] = None
    direction_id: Optional[int] = None
    club_id: Optional[int] = None
    course_level: Optional[int] = None
    search: Optional[str] = None
    limit: int = 50
    offset: int = 0
