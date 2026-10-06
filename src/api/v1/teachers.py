from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.core.database import get_db
from src.models.admin import Admin
from src.models.club import Club
from src.repositories.admin_repo import AdminRepository
from src.schemas.teacher import TeacherCreate, TeacherUpdate, TeacherResponse
from src.api.deps import require_superadmin

router = APIRouter(prefix="/teachers", tags=["Teacher Management"])


def build_teacher_response(teacher: Admin) -> TeacherResponse:
    return TeacherResponse(
        id=teacher.id,
        username=teacher.username,
        full_name=teacher.full_name,
        role=teacher.role,
        club_id=teacher.club_id,
        club_name=teacher.club.name if teacher.club else None,
        is_active=teacher.is_active,
        created_at=teacher.created_at
    )


@router.get("", response_model=List[TeacherResponse])
async def list_teachers(
    superadmin: Admin = Depends(require_superadmin),
    session: AsyncSession = Depends(get_db)
):
    """List all teacher accounts (Superadmin only)."""
    repo = AdminRepository(session)
    teachers = await repo.get_all_teachers()
    return [build_teacher_response(t) for t in teachers]


@router.post("", response_model=TeacherResponse, status_code=status.HTTP_201_CREATED)
async def create_teacher(
    data: TeacherCreate,
    superadmin: Admin = Depends(require_superadmin),
    session: AsyncSession = Depends(get_db)
):
    """
    Create a new teacher account with custom login and password.
    (Requirement: Admin har bir o‘qituvchi uchun alohida login va parol yaratadi.)
    """
    repo = AdminRepository(session)

    # Check if username is taken
    existing = await repo.get_by_username(data.username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ushbu login band. Iltimos, boshqa login tanlang."
        )

    # Verify club exists if specified
    if data.club_id:
        club_stmt = select(Club).where(Club.id == data.club_id)
        club = (await session.execute(club_stmt)).scalars().first()
        if not club:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Biriktirilayotgan to'garak topilmadi."
            )

    teacher = await repo.create_teacher(
        username=data.username,
        plain_password=data.password,
        full_name=data.full_name,
        club_id=data.club_id
    )

    # Reload with relations
    reloaded = await repo.get_by_id(teacher.id)
    return build_teacher_response(reloaded)


@router.put("/{teacher_id}", response_model=TeacherResponse)
async def update_teacher(
    teacher_id: int,
    data: TeacherUpdate,
    superadmin: Admin = Depends(require_superadmin),
    session: AsyncSession = Depends(get_db)
):
    """Update teacher profile, assigned club, active status or reset password."""
    repo = AdminRepository(session)

    # Verify club if changed
    if data.club_id:
        club_stmt = select(Club).where(Club.id == data.club_id)
        club = (await session.execute(club_stmt)).scalars().first()
        if not club:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Biriktirilayotgan to'garak topilmadi."
            )

    updated = await repo.update_teacher(
        teacher_id=teacher_id,
        full_name=data.full_name,
        club_id=data.club_id,
        is_active=data.is_active,
        plain_password=data.new_password
    )

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="O'qituvchi topilmadi."
        )

    reloaded = await repo.get_by_id(updated.id)
    return build_teacher_response(reloaded)


@router.delete("/{teacher_id}")
async def delete_teacher(
    teacher_id: int,
    superadmin: Admin = Depends(require_superadmin),
    session: AsyncSession = Depends(get_db)
):
    """Delete a teacher account."""
    repo = AdminRepository(session)
    teacher = await repo.get_by_id(teacher_id)
    if not teacher or teacher.role != "teacher":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="O'qituvchi topilmadi."
        )

    await repo.delete(teacher_id)
    return {"message": "O'qituvchi hisobi muvaffaqiyatli o'chirildi."}
