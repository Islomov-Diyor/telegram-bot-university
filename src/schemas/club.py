from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ClubBase(BaseModel):
    direction_id: int
    name: str = Field(..., min_length=2, max_length=200)
    description: str = Field(..., min_length=5)
    schedule_days: str = Field(..., min_length=2, max_length=100)
    schedule_time: str = Field(..., min_length=2, max_length=50)
    room_location: str = Field(..., min_length=2, max_length=100)
    leader_name: str = Field(..., min_length=2, max_length=150)
    leader_contact: str = Field(..., min_length=2, max_length=100)
    max_capacity: int = Field(default=0, ge=0)
    is_active: bool = True


class ClubCreate(ClubBase):
    pass


class ClubUpdate(BaseModel):
    direction_id: Optional[int] = None
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    description: Optional[str] = Field(None, min_length=5)
    schedule_days: Optional[str] = Field(None, min_length=2, max_length=100)
    schedule_time: Optional[str] = Field(None, min_length=2, max_length=50)
    room_location: Optional[str] = Field(None, min_length=2, max_length=100)
    leader_name: Optional[str] = Field(None, min_length=2, max_length=150)
    leader_contact: Optional[str] = Field(None, min_length=2, max_length=100)
    max_capacity: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class ClubResponse(ClubBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    direction_name: Optional[str] = None
    faculty_name: Optional[str] = None
    faculty_id: Optional[int] = None
    students_count: int = 0
