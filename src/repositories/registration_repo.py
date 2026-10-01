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
        """Check if student is already active or in waiting list for this club (Requirement 11)."""
        stmt = (
            select(Registration.id)
            .where(
                (Registration.student_id == student_id) &
                (Registration.club_id == club_id) &
                (Registration.status.in_(["active", "waiting"]))
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().first() is not None

    async def get_by_student_and_club(self, student_id: int, club_id: int) -> Optional[Registration]:
        """Fetch registration record for student in a specific club."""
        stmt = (
            select(Registration)
            .where(
                (Registration.student_id == student_id) &
                (Registration.club_id == club_id)
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def count_active_by_club(self, club_id: int) -> int:
        """Count currently enrolled active students in a club."""
        stmt = (
            select(func.count(Registration.id))
            .where(
                (Registration.club_id == club_id) &
                (Registration.status == "active")
            )
        )
        res = await self.session.execute(stmt)
        return res.scalar() or 0

    async def count_waiting_by_club(self, club_id: int) -> int:
        """Count students on the waiting list for a club."""
        stmt = (
            select(func.count(Registration.id))
            .where(
                (Registration.club_id == club_id) &
                (Registration.status == "waiting")
            )
        )
        res = await self.session.execute(stmt)
        return res.scalar() or 0

    async def get_next_waiting_student(self, club_id: int) -> Optional[Registration]:
        """Fetch the first student in the waiting queue for this club."""
        stmt = (
            select(Registration)
            .where(
                (Registration.club_id == club_id) &
                (Registration.status == "waiting")
            )
            .order_by(
                Registration.queue_position.asc().nulls_last(),
                Registration.registered_at.asc()
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def reorder_queue(self, club_id: int) -> None:
        """Re-assign contiguous 1-based queue numbers to waiting list students after promotion or cancellation."""
        stmt = (
            select(Registration)
            .where(
                (Registration.club_id == club_id) &
                (Registration.status == "waiting")
            )
            .order_by(
                Registration.queue_position.asc().nulls_last(),
                Registration.registered_at.asc()
            )
        )
        result = await self.session.execute(stmt)
        waiting_list = list(result.scalars().all())
        for idx, reg in enumerate(waiting_list, 1):
            reg.queue_position = idx
        await self.session.commit()

    async def get_filtered(
        self,
        faculty_id: Optional[int] = None,
        direction_id: Optional[int] = None,
        club_id: Optional[int] = None,
        course_level: Optional[int] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[dict], int]:
        """
        Fetch registrations with rich student, club, direction, and faculty info.
        Uses OUTER joins to prevent dropping records if direction or faculty records were altered.
        """
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
            .outerjoin(Direction, Club.direction_id == Direction.id)
            .outerjoin(Faculty, Direction.faculty_id == Faculty.id)
        )

        count_query = (
            select(func.count(Registration.id))
            .join(Student, Registration.student_id == Student.id)
            .join(Club, Registration.club_id == Club.id)
            .outerjoin(Direction, Club.direction_id == Direction.id)
            .outerjoin(Faculty, Direction.faculty_id == Faculty.id)
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
        if status and status != "all":
            conditions.append(Registration.status == status)
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
                "queue_position": reg.queue_position,
                "registered_at": reg.registered_at
            })

        return items, total

    async def get_recent(self, limit: int = 8) -> List[dict]:
        """Fetch latest registrations for the admin dashboard widget."""
        items, _ = await self.get_filtered(limit=limit, offset=0)
        return items

    async def get_all_for_export(
        self,
        club_id: Optional[int] = None,
        direction_id: Optional[int] = None,
        faculty_id: Optional[int] = None,
        status: Optional[str] = None
    ) -> List[dict]:
        """Fetch all registrations without limit for Excel/CSV export."""
        items, _ = await self.get_filtered(
            faculty_id=faculty_id,
            direction_id=direction_id,
            club_id=club_id,
            status=status,
            limit=100000,
            offset=0
        )
        return items
