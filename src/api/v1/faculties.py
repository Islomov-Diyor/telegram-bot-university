from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.repositories.faculty_repo import FacultyRepository
from src.schemas.faculty import FacultyCreate, FacultyUpdate, FacultyResponse
from src.models.admin import Admin
from src.api.deps import get_current_admin

router = APIRouter(prefix="/faculties", tags=["Faculty Management"])


@router.get("", response_model=List[FacultyResponse])
async def list_faculties(
    current_admin: Admin = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db)
):
    """Retrieve all faculties with active directions count."""
    repo = FacultyRepository(session)
    items = await repo.get_all_with_counts()
    return items


@router.post("", response_model=FacultyResponse, status_code=status.HTTP_201_CREATED)
async def create_faculty(
    data: FacultyCreate,
    current_admin: Admin = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db)
):
    """Create a new academic faculty."""
    repo = FacultyRepository(session)
    existing = await repo.get_by_name(data.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bunday nomli fakultet allaqachon mavjud."
        )

    faculty = await repo.create(
        name=data.name.strip(),
        code=data.code.strip() if data.code else None,
        is_active=data.is_active
    )
    return {
        "id": faculty.id,
        "name": faculty.name,
        "code": faculty.code,
        "is_active": faculty.is_active,
        "created_at": faculty.created_at,
        "directions_count": 0
    }


@router.put("/{faculty_id}", response_model=FacultyResponse)
async def update_faculty(
    faculty_id: int,
    data: FacultyUpdate,
    current_admin: Admin = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db)
):
    """Update faculty details."""
    repo = FacultyRepository(session)
    update_data = data.model_dump(exclude_unset=True)
    if "name" in update_data and update_data["name"]:
        update_data["name"] = update_data["name"].strip()

    faculty = await repo.update(faculty_id, **update_data)
    if not faculty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fakultet topilmadi."
        )

    return {
        "id": faculty.id,
        "name": faculty.name,
        "code": faculty.code,
        "is_active": faculty.is_active,
        "created_at": faculty.created_at,
        "directions_count": len(faculty.directions)
    }


@router.delete("/{faculty_id}")
async def delete_faculty(
    faculty_id: int,
    current_admin: Admin = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db)
):
    """Delete a faculty along with its directions and clubs."""
    repo = FacultyRepository(session)
    success = await repo.delete(faculty_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fakultet topilmadi."
        )
    return {"message": "Fakultet muvaffaqiyatli o'chirildi."}
