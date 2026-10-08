from typing import List, Optional, Dict, Any
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from src.models.attendance import AttendanceLesson, AttendanceRecord
from src.models.club import Club
from src.models.student import Student
from src.models.registration import Registration
from src.repositories.base import BaseRepository


class AttendanceRepository(BaseRepository[AttendanceLesson]):
    def __init__(self, session: AsyncSession):
        super().__init__(AttendanceLesson, session)

    async def get_lessons_for_club(self, club_id: int) -> List[Dict[str, Any]]:
        """Retrieve all lessons for a specific club along with attendance tallies."""
        stmt = (
            select(AttendanceLesson)
            .where(AttendanceLesson.club_id == club_id)
            .order_by(AttendanceLesson.lesson_date.desc(), AttendanceLesson.id.desc())
        )
        result = await self.session.execute(stmt)
        lessons = result.scalars().all()

        output = []
        for l in lessons:
            records = l.records or []
            present_c = sum(1 for r in records if r.status == "present")
            absent_c = sum(1 for r in records if r.status == "absent")
            excused_c = sum(1 for r in records if r.status == "excused")
            output.append({
                "id": l.id,
                "club_id": l.club_id,
                "lesson_date": l.lesson_date,
                "topic": l.topic or "",
                "created_at": l.created_at,
                "present_count": present_c,
                "absent_count": absent_c,
                "excused_count": excused_c,
                "total_records": len(records)
            })
        return output

    async def create_lesson_with_students(
        self,
        club_id: int,
        lesson_date: date,
        topic: Optional[str] = None,
        created_by_id: Optional[int] = None
    ) -> AttendanceLesson:
        """Create a new lesson and pre-seed attendance records for all active club students."""
        lesson = AttendanceLesson(
            club_id=club_id,
            lesson_date=lesson_date,
            topic=topic.strip() if topic else None,
            created_by_id=created_by_id
        )
        self.session.add(lesson)
        await self.session.flush()

        # Query all active students in this club
        reg_stmt = (
            select(Registration.student_id)
            .where(
                and_(
                    Registration.club_id == club_id,
                    Registration.status == "active"
                )
            )
        )
        reg_res = await self.session.execute(reg_stmt)
        active_student_ids = reg_res.scalars().all()

        for sid in active_student_ids:
            rec = AttendanceRecord(
                lesson_id=lesson.id,
                student_id=sid,
                status="present"  # Default to present upon creation
            )
            self.session.add(rec)

        await self.session.commit()
        await self.session.refresh(lesson)
        return lesson

    async def get_lesson_roster(self, lesson_id: int) -> Optional[Dict[str, Any]]:
        """Get lesson details and student attendance status list."""
        stmt = select(AttendanceLesson).where(AttendanceLesson.id == lesson_id)
        res = await self.session.execute(stmt)
        lesson = res.scalars().first()
        if not lesson:
            return None

        # Fetch active students registered in this club
        reg_stmt = (
            select(Registration)
            .where(
                and_(
                    Registration.club_id == lesson.club_id,
                    Registration.status == "active"
                )
            )
        )
        reg_res = await self.session.execute(reg_stmt)
        active_regs = reg_res.scalars().all()

        # Existing records mapped by student_id
        records_map = {r.student_id: r for r in (lesson.records or [])}

        students_roster = []
        for reg in active_regs:
            student = reg.student
            rec = records_map.get(student.id)
            status_val = rec.status if rec else "present"
            notes_val = rec.notes if rec else None

            students_roster.append({
                "student_id": student.id,
                "full_name": student.full_name or "Noma'lum",
                "phone_number": student.phone_number,
                "course_level": reg.course_level,
                "status": status_val,
                "notes": notes_val
            })

        present_c = sum(1 for s in students_roster if s["status"] == "present")
        absent_c = sum(1 for s in students_roster if s["status"] == "absent")
        excused_c = sum(1 for s in students_roster if s["status"] == "excused")

        return {
            "lesson": {
                "id": lesson.id,
                "club_id": lesson.club_id,
                "lesson_date": lesson.lesson_date,
                "topic": lesson.topic or "",
                "created_at": lesson.created_at,
                "present_count": present_c,
                "absent_count": absent_c,
                "excused_count": excused_c,
                "total_records": len(students_roster)
            },
            "students": students_roster
        }

    async def save_roster(self, lesson_id: int, records_data: List[Dict[str, Any]]) -> bool:
        """Save/upsert attendance statuses for students in a lesson."""
        stmt = select(AttendanceLesson).where(AttendanceLesson.id == lesson_id)
        res = await self.session.execute(stmt)
        lesson = res.scalars().first()
        if not lesson:
            return False

        existing_records = {r.student_id: r for r in (lesson.records or [])}

        for item in records_data:
            sid = item["student_id"]
            stat = item.get("status", "present")
            notes = item.get("notes")

            if sid in existing_records:
                existing_records[sid].status = stat
                if notes is not None:
                    existing_records[sid].notes = notes
            else:
                new_rec = AttendanceRecord(
                    lesson_id=lesson_id,
                    student_id=sid,
                    status=stat,
                    notes=notes
                )
                self.session.add(new_rec)

        await self.session.commit()
        return True

    async def get_club_attendance_results(self, club_id: int) -> Dict[str, Any]:
        """
        Calculate total lessons, lessons attended, and percentage per student for course completion.
        (Requirement: 'Kurs oxirida tizim: nechta darsga qatnashgani, qatnashish foizi')
        """
        # 1. Club info
        club_stmt = select(Club).where(Club.id == club_id)
        club = (await self.session.execute(club_stmt)).scalars().first()
        if not club:
            return None

        # 2. Total lessons conducted for this club
        lessons_stmt = select(AttendanceLesson).where(AttendanceLesson.club_id == club_id)
        lessons_res = await self.session.execute(lessons_stmt)
        lessons = list(lessons_res.scalars().all())
        total_lessons_count = len(lessons)
        lesson_ids = [l.id for l in lessons]

        # 3. Active students in this club
        reg_stmt = (
            select(Registration)
            .where(
                and_(
                    Registration.club_id == club_id,
                    Registration.status == "active"
                )
            )
        )
        active_regs = list((await self.session.execute(reg_stmt)).scalars().all())

        # 4. Fetch all records for these lessons
        records_by_student: Dict[int, List[AttendanceRecord]] = {reg.student_id: [] for reg in active_regs}
        if lesson_ids:
            records_stmt = (
                select(AttendanceRecord)
                .where(AttendanceRecord.lesson_id.in_(lesson_ids))
            )
            rec_res = await self.session.execute(records_stmt)
            for rec in rec_res.scalars().all():
                if rec.student_id in records_by_student:
                    records_by_student[rec.student_id].append(rec)

        # 5. Build summary per student
        students_summary = []
        for reg in active_regs:
            student = reg.student
            student_records = records_by_student.get(student.id, [])
            attended = sum(1 for r in student_records if r.status == "present")
            absent = sum(1 for r in student_records if r.status == "absent")
            excused = sum(1 for r in student_records if r.status == "excused")

            if total_lessons_count > 0:
                pct = round((attended / total_lessons_count * 100), 1)
                if pct >= 90:
                    grade_label = "A'lo (90-100%)"
                elif pct >= 75:
                    grade_label = "Yaxshi (75-89%)"
                elif pct >= 60:
                    grade_label = "Qoniqarli (60-74%)"
                else:
                    grade_label = "Qoniqarsiz (<60%)"
            else:
                pct = 0.0
                grade_label = "— (Hali dars o'tilmagan)"

            students_summary.append({
                "student_id": student.id,
                "full_name": student.full_name or "Noma'lum",
                "phone_number": student.phone_number,
                "course_level": reg.course_level,
                "total_lessons": total_lessons_count,
                "attended_lessons": attended,
                "absent_lessons": absent,
                "excused_lessons": excused,
                "attendance_percentage": pct,
                "grade_label": grade_label
            })

        # Sort by attendance percentage descending
        students_summary.sort(key=lambda s: s["attendance_percentage"], reverse=True)

        return {
            "club_id": club.id,
            "club_name": club.name,
            "total_lessons_held": total_lessons_count,
            "students_summary": students_summary
        }
