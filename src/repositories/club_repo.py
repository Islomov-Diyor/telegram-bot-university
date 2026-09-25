from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from src.models.club import Club
from src.models.direction import Direction
from src.models.faculty import Faculty
from src.models.registration import Registration
from src.repositories.base import BaseRepository


class ClubRepository(BaseRepository[Club]):
    def __init__(self, session: AsyncSession):
        super().__init__(Club, session)

    async def get_active_by_direction(self, direction_id: int) -> List[Club]:
        """Fetch active clubs under a specific direction for Telegram Bot."""
        stmt = (
            select(Club)
            .where(
                (Club.direction_id == direction_id) &
                (Club.is_active == True)
            )
            .order_by(Club.name)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_detailed_by_id(self, club_id: int) -> Optional[dict]:
        """Fetch club details including direction and faculty name."""
        stmt = (
            select(
                Club,
                Direction.name.label("direction_name"),
                Faculty.name.label("faculty_name"),
                Faculty.id.label("faculty_id"),
                func.count(Registration.id).label("students_count")
            )
            .join(Direction, Club.direction_id == Direction.id)
            .join(Faculty, Direction.faculty_id == Faculty.id)
            .outerjoin(Registration, (Registration.club_id == Club.id) & (Registration.status == "active"))
            .where(Club.id == club_id)
            .group_by(Club.id, Direction.name, Faculty.name, Faculty.id)
        )
        result = await self.session.execute(stmt)
        row = result.first()
        if not row:
            return None
        
        club, dir_name, fac_name, fac_id, count = row
        return {
            "id": club.id,
            "direction_id": club.direction_id,
            "name": club.name,
            "description": club.description,
            "schedule_days": club.schedule_days,
            "schedule_time": club.schedule_time,
            "room_location": club.room_location,
            "leader_name": club.leader_name,
            "leader_contact": club.leader_contact,
            "max_capacity": club.max_capacity,
            "is_active": club.is_active,
            "created_at": club.created_at,
            "updated_at": club.updated_at,
            "direction_name": dir_name,
            "faculty_name": fac_name,
            "faculty_id": fac_id,
            "students_count": count
        }

    async def get_all_with_stats(
        self,
        faculty_id: Optional[int] = None,
        direction_id: Optional[int] = None
    ) -> List[dict]:
        """Fetch all clubs with students count, direction name, and faculty name."""
        stmt = (
            select(
                Club,
                Direction.name.label("direction_name"),
                Faculty.name.label("faculty_name"),
                Faculty.id.label("faculty_id"),
                func.count(Registration.id).label("students_count")
            )
            .join(Direction, Club.direction_id == Direction.id)
            .join(Faculty, Direction.faculty_id == Faculty.id)
            .outerjoin(Registration, (Registration.club_id == Club.id) & (Registration.status == "active"))
        )
        if direction_id:
            stmt = stmt.where(Club.direction_id == direction_id)
        elif faculty_id:
            stmt = stmt.where(Direction.faculty_id == faculty_id)

        stmt = stmt.group_by(Club.id, Direction.name, Faculty.name, Faculty.id).order_by(Club.name)
        result = await self.session.execute(stmt)

        items = []
        for club, dir_name, fac_name, fac_id, count in result.all():
            items.append({
                "id": club.id,
                "direction_id": club.direction_id,
                "name": club.name,
                "description": club.description,
                "schedule_days": club.schedule_days,
                "schedule_time": club.schedule_time,
                "room_location": club.room_location,
                "leader_name": club.leader_name,
                "leader_contact": club.leader_contact,
                "max_capacity": club.max_capacity,
                "is_active": club.is_active,
                "created_at": club.created_at,
                "updated_at": club.updated_at,
                "direction_name": dir_name,
                "faculty_name": fac_name,
                "faculty_id": fac_id,
                "students_count": count
            })
        return items
