from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.repositories.registration_repo import RegistrationRepository
from src.schemas.registration import RegistrationResponse
from src.models.admin import Admin
from src.api.deps import get_current_admin

router = APIRouter(prefix="/registrations", tags=["Student Registrations"])


@router.get("")
async def list_registrations(
    faculty_id: Optional[int] = Query(None, description="Fakultet ID bo'yicha filter"),
    direction_id: Optional[int] = Query(None, description="Yo'nalish ID bo'yicha filter"),
    club_id: Optional[int] = Query(None, description="To'garak ID bo'yicha filter"),
    course_level: Optional[int] = Query(None, description="Kurs bo'yicha filter (1-4)"),
    search: Optional[str] = Query(None, description="Talaba ismi, telefoni yoki Telegram username bo'yicha qidiruv"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_admin: Admin = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Retrieve registered students directory with filtering and searching (Requirement 14).
    Returns list of students with: ism-familiya, fakultet, yo'nalish, kurs, telefon, Telegram username.
    """
    repo = RegistrationRepository(session)
    items, total = await repo.get_filtered(
        faculty_id=faculty_id,
        direction_id=direction_id,
        club_id=club_id,
        course_level=course_level,
        search=search,
        limit=limit,
        offset=offset
    )

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": items
    }


@router.delete("/{registration_id}")
async def delete_registration(
    registration_id: int,
    current_admin: Admin = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db)
):
    """Remove student from a club or cancel registration."""
    repo = RegistrationRepository(session)
    success = await repo.delete(registration_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="A'zolik yozuvi topilmadi."
        )
    return {"message": "Talaba a'zoligi muvaffaqiyatli bekor qilindi."}
