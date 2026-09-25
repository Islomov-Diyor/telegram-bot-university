from typing import Dict, Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src.core.database import get_db
from src.models.faculty import Faculty
from src.models.direction import Direction
from src.models.club import Club
from src.models.student import Student
from src.models.registration import Registration
from src.models.admin import Admin
from src.api.deps import get_current_admin

router = APIRouter(prefix="/stats", tags=["Dashboard Statistics"])


@router.get("/overview")
async def get_dashboard_overview(
    current_admin: Admin = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Retrieve summarized analytics for the admin dashboard."""
    # 1. Total counts
    fac_count = (await session.execute(select(func.count(Faculty.id)))).scalar() or 0
    dir_count = (await session.execute(select(func.count(Direction.id)))).scalar() or 0
    club_count = (await session.execute(select(func.count(Club.id)))).scalar() or 0
    student_count = (await session.execute(select(func.count(Student.id)))).scalar() or 0
    reg_count = (await session.execute(select(func.count(Registration.id)).where(Registration.status == "active"))).scalar() or 0

    # 2. Top 5 popular clubs
    top_clubs_stmt = (
        select(
            Club.name,
            func.count(Registration.id).label("count")
        )
        .outerjoin(Registration, (Registration.club_id == Club.id) & (Registration.status == "active"))
        .group_by(Club.id, Club.name)
        .order_by(func.count(Registration.id).desc())
        .limit(5)
    )
    top_clubs_res = await session.execute(top_clubs_stmt)
    top_clubs = [{"name": name, "count": count} for name, count in top_clubs_res.all()]

    # 3. Registrations per faculty
    fac_reg_stmt = (
        select(
            Faculty.name,
            func.count(Registration.id).label("count")
        )
        .join(Direction, Direction.faculty_id == Faculty.id)
        .join(Club, Club.direction_id == Direction.id)
        .outerjoin(Registration, (Registration.club_id == Club.id) & (Registration.status == "active"))
        .group_by(Faculty.id, Faculty.name)
        .order_by(Faculty.name)
    )
    fac_reg_res = await session.execute(fac_reg_stmt)
    faculty_breakdown = [{"name": name, "count": count} for name, count in fac_reg_res.all()]

    return {
        "faculties_count": fac_count,
        "directions_count": dir_count,
        "clubs_count": club_count,
        "students_count": student_count,
        "registrations_count": reg_count,
        "top_clubs": top_clubs,
        "faculty_breakdown": faculty_breakdown
    }
