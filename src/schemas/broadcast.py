from typing import Optional
from pydantic import BaseModel, Field


class BroadcastRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000, description="Yuboriladigan xabar matni")
    target: str = Field(default="all", description="'all' (barcha talabalar) yoki 'club' (muayyan to'garak)")
    club_id: Optional[int] = Field(None, description="To'garak a'zolariga yuborish uchun to'garak ID")


class BroadcastResponse(BaseModel):
    success: bool
    total: int
    sent: int
    failed: int
    message: str
