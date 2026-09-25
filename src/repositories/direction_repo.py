from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from src.models.direction import Direction
from src.models.faculty import Faculty
from src.models.club import Club
from src.repositories.base import BaseRepository


class DirectionRepository(BaseRepository[Direction]):
    def __init__(self, session: AsyncSession):
        super().__init__(Direction, session)

    async def get_active_by_faculty(self, faculty_id: int) -> List[Direction]:
        """Fetch active directions under a specific faculty for Telegram Bot."""
        stmt = (
            select(Direction)
            .where(
                (Direction.faculty_id == faculty_id) &
                (Direction.is_active == True)
            )
            .order_by(Direction.name)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_all_with_relations(self, faculty_id: Optional[int] = None) -> List[dict]:
        """Fetch directions with faculty name and clubs count for admin panel."""
        stmt = (
            select(
                Direction,
                Faculty.name.label("faculty_name"),
                func.count(Club.id).label("clubs_count")
            )
            .join(Faculty, Direction.faculty_id == Faculty.id)
            .outerjoin(Club, (Club.direction_id == Direction.id) & (Club.is_active == True))
        )
        if faculty_id:
            stmt = stmt.where(Direction.faculty_id == faculty_id)
        
        stmt = stmt.group_by(Direction.id, Faculty.name).order_by(Direction.name)
        result = await self.session.execute(stmt)
        
        items = []
        for direction, faculty_name, clubs_count in result.all():
            items.append({
                "id": direction.id,
                "faculty_id": direction.faculty_id,
                "name": direction.name,
                "code": direction.code,
                "is_active": direction.is_active,
                "created_at": direction.created_at,
                "faculty_name": faculty_name,
                "clubs_count": clubs_count
            })
        return items
