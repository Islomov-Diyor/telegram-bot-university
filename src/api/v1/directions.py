from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.repositories.direction_repo import DirectionRepository
from src.repositories.faculty_repo import FacultyRepository
from src.schemas.direction import DirectionCreate, DirectionUpdate, DirectionResponse
from src.models.admin import Admin
from src.api.deps import get_current_admin

router = APIRouter(prefix="/directions", tags=["Direction Management"])


@router.get("", response_model=List[DirectionResponse])
async def list_directions(
    faculty_id: Optional[int] = Query(None, description="Fakultet ID bo'yicha filter"),
    current_admin: Admin = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db)
):
    """Retrieve all study directions with parent faculty name and clubs count."""
    repo = DirectionRepository(session)
    items = await repo.get_all_with_relations(faculty_id=faculty_id)
    return items


@router.post("", response_model=DirectionResponse, status_code=status.HTTP_201_CREATED)
async def create_direction(
    data: DirectionCreate,
    current_admin: Admin = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db)
):
    """Create a new study direction under a faculty."""
    fac_repo = FacultyRepository(session)
    faculty = await fac_repo.get_by_id(data.faculty_id)
    if not faculty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Biriktirilayotgan fakultet topilmadi."
        )

    repo = DirectionRepository(session)
    direction = await repo.create(
        faculty_id=data.faculty_id,
        name=data.name.strip(),
        code=data.code.strip() if data.code else None,
        is_active=data.is_active
    )
    return {
        "id": direction.id,
        "faculty_id": direction.faculty_id,
        "name": direction.name,
        "code": direction.code,
        "is_active": direction.is_active,
        "created_at": direction.created_at,
        "faculty_name": faculty.name,
        "clubs_count": 0
    }


@router.put("/{direction_id}", response_model=DirectionResponse)
async def update_direction(
    direction_id: int,
    data: DirectionUpdate,
    current_admin: Admin = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db)
):
    """Update study direction details."""
    repo = DirectionRepository(session)
    direction = await repo.get_by_id(direction_id)
    if not direction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Yo'nalish topilmadi."
        )

    update_data = data.model_dump(exclude_unset=True)
    if "name" in update_data and update_data["name"]:
        update_data["name"] = update_data["name"].strip()

    updated = await repo.update(direction_id, **update_data)
    faculty_name = updated.faculty.name if updated.faculty else ""
    return {
        "id": updated.id,
        "faculty_id": updated.faculty_id,
        "name": updated.name,
        "code": updated.code,
        "is_active": updated.is_active,
        "created_at": updated.created_at,
        "faculty_name": faculty_name,
        "clubs_count": len(updated.clubs)
    }


@router.delete("/{direction_id}")
async def delete_direction(
    direction_id: int,
    current_admin: Admin = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db)
):
    """Delete a study direction."""
    repo = DirectionRepository(session)
    success = await repo.delete(direction_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Yo'nalish topilmadi."
        )
    return {"message": "Yo'nalish muvaffaqiyatli o'chirildi."}
