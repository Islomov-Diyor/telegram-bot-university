from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from src.models.registration import Registration
from src.models.student import Student
from src.models.club import Club
from src.models.direction import Direction
from src.models.faculty import Faculty
from src.repositories.base import BaseRepository


class RegistrationRepository(BaseRepository[Registration]):
    def __init__(self, session: AsyncSession):
        super().__init__(Registration, session)

    async def is_already_registered(self, student_id: int, club_id: int) -> bool:
        """Check if student is already registered to this club (Requirement 11)."""
        stmt = (
            select(Registration.id)
            .where(
                (Registration.student_id == student_id) &
                (Registration.club_id == club_id) &
                (Registration.status == "active")
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().first() is not None

    async def get_filtered(
        self,
        faculty_id: Optional[int] = None,
        direction_id: Optional[int] = None,
        club_id: Optional[int] = None,
        course_level: Optional[int] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[dict], int]:
        """Fetch registrations with rich student, club, direction, and faculty info."""
        base_query = (
            select(
                Registration,
                Student.full_name,
                Student.phone_number,
                Student.username.label("telegram_username"),
                Student.telegram_id,
                Club.name.label("club_name"),
                Direction.name.label("direction_name"),
                Faculty.name.label("faculty_name")
            )
            .join(Student, Registration.student_id == Student.id)
            .join(Club, Registration.club_id == Club.id)
            .join(Direction, Club.direction_id == Direction.id)
            .join(Faculty, Direction.faculty_id == Faculty.id)
        )

        count_query = (
            select(func.count(Registration.id))
            .join(Student, Registration.student_id == Student.id)
            .join(Club, Registration.club_id == Club.id)
            .join(Direction, Club.direction_id == Direction.id)
            .join(Faculty, Direction.faculty_id == Faculty.id)
        )

        conditions = []
        if club_id:
            conditions.append(Registration.club_id == club_id)
        if direction_id:
            conditions.append(Club.direction_id == direction_id)
        if faculty_id:
            conditions.append(Direction.faculty_id == faculty_id)
        if course_level:
            conditions.append(Registration.course_level == course_level)
        if search and search.strip():
            term = f"%{search.strip()}%"
            conditions.append(
                or_(
                    Student.full_name.ilike(term),
                    Student.phone_number.ilike(term),
                    Student.username.ilike(term)
                )
            )

        if conditions:
            base_query = base_query.where(*conditions)
            count_query = count_query.where(*conditions)

        total_res = await self.session.execute(count_query)
        total = total_res.scalar() or 0

        stmt = base_query.order_by(Registration.registered_at.desc()).limit(limit).offset(offset)
        result = await self.session.execute(stmt)

        items = []
        for reg, full_name, phone, username, tg_id, club_name, dir_name, fac_name in result.all():
            items.append({
                "id": reg.id,
                "student_id": reg.student_id,
                "club_id": reg.club_id,
                "full_name": full_name,
                "phone_number": phone,
                "telegram_username": username,
                "telegram_id": tg_id,
                "club_name": club_name,
                "faculty_name": fac_name or reg.faculty_name_snap,
                "direction_name": dir_name or reg.direction_name_snap,
                "course_level": reg.course_level,
                "status": reg.status,
                "registered_at": reg.registered_at
            })

        return items, total

    async def get_all_for_export(
        self,
        club_id: Optional[int] = None,
        direction_id: Optional[int] = None,
        faculty_id: Optional[int] = None
    ) -> List[dict]:
        """Fetch all registrations without limit for Excel/CSV export."""
        items, _ = await self.get_filtered(
            faculty_id=faculty_id,
            direction_id=direction_id,
            club_id=club_id,
            limit=100000,
            offset=0
        )
        return items
