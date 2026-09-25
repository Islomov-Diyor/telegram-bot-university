from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class StudentBase(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    full_name: str = Field(..., min_length=3, max_length=150)
    phone_number: str = Field(..., min_length=9, max_length=20)


class StudentCreate(StudentBase):
    pass


class StudentResponse(StudentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
