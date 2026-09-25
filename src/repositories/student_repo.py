from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models.student import Student
from src.repositories.base import BaseRepository


class StudentRepository(BaseRepository[Student]):
    def __init__(self, session: AsyncSession):
        super().__init__(Student, session)

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[Student]:
        stmt = select(Student).where(Student.telegram_id == telegram_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def upsert_student(
        self,
        telegram_id: int,
        full_name: str,
        phone_number: str,
        username: Optional[str] = None
    ) -> Student:
        student = await self.get_by_telegram_id(telegram_id)
        if student:
            student.full_name = full_name
            student.phone_number = phone_number
            student.username = username
            await self.session.commit()
            await self.session.refresh(student)
            return student
        else:
            return await self.create(
                telegram_id=telegram_id,
                full_name=full_name,
                phone_number=phone_number,
                username=username
            )
