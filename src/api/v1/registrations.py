from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.repositories.registration_repo import RegistrationRepository
from src.services.registration_service import RegistrationService
from src.models.admin import Admin
from src.api.deps import get_current_admin

router = APIRouter(prefix="/registrations", tags=["Student Registrations"])


@router.get("")
async def list_registrations(
    faculty_id: Optional[int] = Query(None, description="Fakultet ID bo'yicha filter"),
    direction_id: Optional[int] = Query(None, description="Yo'nalish ID bo'yicha filter"),
    club_id: Optional[int] = Query(None, description="To'garak ID bo'yicha filter"),
    course_level: Optional[int] = Query(None, description="Kurs bo'yicha filter (1-4)"),
    status: Optional[str] = Query(None, description="A'zolik holati (active, waiting, all)"),
    search: Optional[str] = Query(None, description="Talaba ismi, telefoni yoki Telegram username bo'yicha qidiruv"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_admin: Admin = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Retrieve registered students directory with filtering, queue positions, and searching.
    """
    # Teacher scope enforcement
    if current_admin.role == "teacher" and current_admin.club_id:
        club_id = current_admin.club_id

    repo = RegistrationRepository(session)
    items, total = await repo.get_filtered(
        faculty_id=faculty_id,
        direction_id=direction_id,
        club_id=club_id,
        course_level=course_level,
        status=status,
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


@router.get("/recent")
async def get_recent_registrations(
    limit: int = Query(8, ge=1, le=50),
    current_admin: Admin = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Retrieve recent student registrations for live dashboard display."""
    repo = RegistrationRepository(session)
    recent = await repo.get_recent(limit=limit)
    if current_admin.role == "teacher" and current_admin.club_id:
        recent = [r for r in recent if r.get("club_id") == current_admin.club_id]
    return recent


@router.delete("/{registration_id}")
async def delete_registration(
    registration_id: int,
    current_admin: Admin = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db)
):
    """
    Remove student from a club or cancel registration.
    If the cancelled student held an active spot, the next student on the waiting list
    is automatically promoted and notified via Telegram!
    """
    repo = RegistrationRepository(session)
    reg = await repo.get_by_id(registration_id)
    if not reg:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="A'zolik topilmadi."
        )

    if current_admin.role == "teacher" and current_admin.club_id != reg.club_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="O'qituvchi boshqa to'garak a'zolarini o'chirish huquqiga ega emas."
        )

    reg_service = RegistrationService(session=session)
    success, msg, promoted_info = await reg_service.cancel_registration(registration_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=msg
        )
    return {
        "message": msg,
        "promoted_student": promoted_info
    }

