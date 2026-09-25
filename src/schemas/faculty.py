from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class FacultyBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    code: Optional[str] = Field(None, max_length=20)
    is_active: bool = True


class FacultyCreate(FacultyBase):
    pass


class FacultyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=150)
    code: Optional[str] = Field(None, max_length=20)
    is_active: Optional[bool] = None


class FacultyResponse(FacultyBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    directions_count: Optional[int] = 0
