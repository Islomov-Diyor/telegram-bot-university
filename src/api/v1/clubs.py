from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.repositories.club_repo import ClubRepository
from src.repositories.direction_repo import DirectionRepository
from src.schemas.club import ClubCreate, ClubUpdate, ClubResponse
from src.models.admin import Admin
from src.api.deps import get_current_admin, require_superadmin, check_club_access
from src.services.reminder_service import ReminderService

router = APIRouter(prefix="/clubs", tags=["Club Management"])


class ReminderSendRequest(BaseModel):
    custom_note: Optional[str] = None


@router.get("", response_model=List[ClubResponse])
async def list_clubs(
    faculty_id: Optional[int] = Query(None, description="Fakultet bo'yicha filter"),
    direction_id: Optional[int] = Query(None, description="Yo'nalish bo'yicha filter"),
    current_admin: Admin = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db)
):
    """Retrieve clubs. Teachers only receive their assigned club."""
    repo = ClubRepository(session)
    items = await repo.get_all_with_stats(faculty_id=faculty_id, direction_id=direction_id)
    if current_admin.role == "teacher":
        if current_admin.club_id:
            items = [c for c in items if (c.get("id") if isinstance(c, dict) else getattr(c, "id", None)) == current_admin.club_id]
        else:
            items = []
    return items


@router.post("", response_model=ClubResponse, status_code=status.HTTP_201_CREATED)
async def create_club(
    data: ClubCreate,
    current_admin: Admin = Depends(require_superadmin),
    session: AsyncSession = Depends(get_db)
):
    """Create a new academic/talent club (Superadmin only)."""
    dir_repo = DirectionRepository(session)
    direction = await dir_repo.get_by_id(data.direction_id)
    if not direction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Biriktirilayotgan ta'lim yo'nalishi topilmadi."
        )

    repo = ClubRepository(session)
    club = await repo.create(
        direction_id=data.direction_id,
        name=data.name.strip(),
        description=data.description.strip(),
        schedule_days=data.schedule_days.strip(),
        schedule_time=data.schedule_time.strip(),
        room_location=data.room_location.strip(),
        leader_name=data.leader_name.strip(),
        max_capacity=data.max_capacity,
        registration_deadline=data.registration_deadline,
        is_active=data.is_active
    )

    detailed = await repo.get_detailed_by_id(club.id)
    return detailed


@router.get("/{club_id}", response_model=ClubResponse)
async def get_club_by_id(
    club_id: int,
    current_admin: Admin = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db)
):
    """Retrieve detailed information of a specific club."""
    check_club_access(current_admin, club_id)
    repo = ClubRepository(session)
    club_data = await repo.get_detailed_by_id(club_id)
    if not club_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="To'garak topilmadi."
        )
    return club_data


@router.put("/{club_id}", response_model=ClubResponse)
async def update_club(
    club_id: int,
    data: ClubUpdate,
    current_admin: Admin = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db)
):
    """Update club properties."""
    check_club_access(current_admin, club_id)
    repo = ClubRepository(session)
    existing = await repo.get_by_id(club_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="To'garak topilmadi."
        )

    update_data = data.model_dump(exclude_unset=True)
    for field in ["name", "description", "schedule_days", "schedule_time", "room_location", "leader_name", "leader_contact"]:
        if field in update_data and isinstance(update_data[field], str):
            update_data[field] = update_data[field].strip()

    await repo.update(club_id, **update_data)
    updated_detailed = await repo.get_detailed_by_id(club_id)
    return updated_detailed


@router.delete("/{club_id}")
async def delete_club(
    club_id: int,
    current_admin: Admin = Depends(require_superadmin),
    session: AsyncSession = Depends(get_db)
):
    """Delete a club (Superadmin only)."""
    repo = ClubRepository(session)
    success = await repo.delete(club_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="To'garak topilmadi."
        )
    return {"message": "To'garak muvaffaqiyatli o'chirildi."}


@router.post("/{club_id}/remind")
async def send_reminder_for_club(
    club_id: int,
    payload: Optional[ReminderSendRequest] = None,
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Send on-demand lesson reminder to all active students in the club.
    (Requirement: Avtomatik eslatma: 🔔 Eslatma Bugun soat 15:00 da “...” mashg‘uloti bor.)
    """
    check_club_access(current_admin, club_id)
    note = payload.custom_note if payload else None
    result = await ReminderService.send_club_reminder(
        club_id=club_id,
        custom_note=note,
        reminder_type="manual"
    )
    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("message", "Eslatma yuborishda xatolik.")
        )
    return result

