from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel, Field, ConfigDict


class AttendanceLessonCreate(BaseModel):
    club_id: int
    lesson_date: date
    topic: Optional[str] = Field(None, max_length=255)


class AttendanceLessonResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    club_id: int
    lesson_date: date
    topic: Optional[str] = None
    created_at: datetime
    present_count: int = 0
    absent_count: int = 0
    excused_count: int = 0
    total_records: int = 0


class AttendanceRecordItem(BaseModel):
    student_id: int
    status: str = Field(..., pattern="^(present|absent|excused)$")
    notes: Optional[str] = None


class AttendanceSubmitRequest(BaseModel):
    records: List[AttendanceRecordItem]


class StudentAttendanceDetail(BaseModel):
    student_id: int
    full_name: str
    phone_number: Optional[str] = None
    course_level: int
    status: str = "present"  # present, absent, excused
    notes: Optional[str] = None


class LessonWithRosterResponse(BaseModel):
    lesson: AttendanceLessonResponse
    students: List[StudentAttendanceDetail]


class StudentAttendanceSummary(BaseModel):
    student_id: int
    full_name: str
    phone_number: Optional[str] = None
    course_level: int
    total_lessons: int
    attended_lessons: int
    absent_lessons: int
    excused_lessons: int
    attendance_percentage: float
    grade_label: str  # A'lo, Yaxshi, Qoniqarli, Qoniqarsiz


class ClubAttendanceResultsResponse(BaseModel):
    club_id: int
    club_name: str
    total_lessons_held: int
    students_summary: List[StudentAttendanceSummary]
