from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class DirectionBase(BaseModel):
    faculty_id: int
    name: str = Field(..., min_length=2, max_length=200)
    code: Optional[str] = Field(None, max_length=30)
    is_active: bool = True


class DirectionCreate(DirectionBase):
    pass


class DirectionUpdate(BaseModel):
    faculty_id: Optional[int] = None
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    code: Optional[str] = Field(None, max_length=30)
    is_active: Optional[bool] = None


class DirectionResponse(DirectionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    faculty_name: Optional[str] = None
    clubs_count: Optional[int] = 0
