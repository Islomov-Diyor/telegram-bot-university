from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.repositories.club_repo import ClubRepository
from src.repositories.direction_repo import DirectionRepository
from src.schemas.club import ClubCreate, ClubUpdate, ClubResponse
from src.models.admin import Admin
from src.api.deps import get_current_admin

router = APIRouter(prefix="/clubs", tags=["Club Management"])


@router.get("", response_model=List[ClubResponse])
async def list_clubs(
    faculty_id: Optional[int] = Query(None, description="Fakultet bo'yicha filter"),
    direction_id: Optional[int] = Query(None, description="Yo'nalish bo'yicha filter"),
    current_admin: Admin = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db)
):
    """Retrieve all clubs with student count and academic faculty/direction info."""
    repo = ClubRepository(session)
    items = await repo.get_all_with_stats(faculty_id=faculty_id, direction_id=direction_id)
    return items


@router.post("", response_model=ClubResponse, status_code=status.HTTP_201_CREATED)
async def create_club(
    data: ClubCreate,
    current_admin: Admin = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db)
):
    """Create a new academic/talent club."""
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
        leader_contact=data.leader_contact.strip(),
        max_capacity=data.max_capacity,
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
    """
    Update club properties: schedule days, time, room location, leader, contacts, etc.
    (Requirement 13)
    """
    repo = ClubRepository(session)
    existing = await repo.get_by_id(club_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="To'garak topilmadi."
        )

    update_data = data.model_dump(exclude_unset=True)
    # Strip string fields
    for field in ["name", "description", "schedule_days", "schedule_time", "room_location", "leader_name", "leader_contact"]:
        if field in update_data and isinstance(update_data[field], str):
            update_data[field] = update_data[field].strip()

    await repo.update(club_id, **update_data)
    updated_detailed = await repo.get_detailed_by_id(club_id)
    return updated_detailed


@router.delete("/{club_id}")
async def delete_club(
    club_id: int,
    current_admin: Admin = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db)
):
    """Delete a club and its registrations."""
    repo = ClubRepository(session)
    success = await repo.delete(club_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="To'garak topilmadi."
        )
    return {"message": "To'garak muvaffaqiyatli o'chirildi."}
