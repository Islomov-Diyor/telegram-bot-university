from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from src.models.faculty import Faculty
from src.models.direction import Direction
from src.repositories.base import BaseRepository


class FacultyRepository(BaseRepository[Faculty]):
    def __init__(self, session: AsyncSession):
        super().__init__(Faculty, session)

    async def get_active_faculties(self) -> List[Faculty]:
        stmt = select(Faculty).where(Faculty.is_active == True).order_by(Faculty.name)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_name(self, name: str) -> Optional[Faculty]:
        stmt = select(Faculty).where(func.lower(Faculty.name) == func.lower(name.strip()))
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_with_directions(self, faculty_id: int) -> Optional[Faculty]:
        stmt = (
            select(Faculty)
            .options(selectinload(Faculty.directions))
            .where(Faculty.id == faculty_id)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_all_with_counts(self) -> List[dict]:
        """Fetch all faculties with directions count for admin panel."""
        stmt = (
            select(
                Faculty,
                func.count(Direction.id).label("directions_count")
            )
            .outerjoin(Direction, (Direction.faculty_id == Faculty.id) & (Direction.is_active == True))
            .group_by(Faculty.id)
            .order_by(Faculty.name)
        )
        result = await self.session.execute(stmt)
        items = []
        for faculty, count in result.all():
            items.append({
                "id": faculty.id,
                "name": faculty.name,
                "code": faculty.code,
                "is_active": faculty.is_active,
                "created_at": faculty.created_at,
                "directions_count": count
            })
        return items
