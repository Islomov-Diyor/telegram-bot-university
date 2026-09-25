from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.repositories.registration_repo import RegistrationRepository
from src.services.export_service import ExportService
from src.models.admin import Admin
from src.api.deps import get_current_admin

router = APIRouter(prefix="/export", tags=["Export Data"])


@router.get("/excel")
async def export_to_excel(
    club_id: Optional[int] = Query(None, description="To'garak bo'yicha filter"),
    direction_id: Optional[int] = Query(None, description="Yo'nalish bo'yicha filter"),
    faculty_id: Optional[int] = Query(None, description="Fakultet bo'yicha filter"),
    current_admin: Admin = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db)
):
    """
    Export students data to Microsoft Excel (.xlsx) file with professional table styling (Requirement 15).
    """
    repo = RegistrationRepository(session)
    items = await repo.get_all_for_export(
        club_id=club_id,
        direction_id=direction_id,
        faculty_id=faculty_id
    )

    buffer = ExportService.generate_excel(items)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"iqtidorli_talabalar_{timestamp}.xlsx"

    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.get("/csv")
async def export_to_csv(
    club_id: Optional[int] = Query(None, description="To'garak bo'yicha filter"),
    direction_id: Optional[int] = Query(None, description="Yo'nalish bo'yicha filter"),
    faculty_id: Optional[int] = Query(None, description="Fakultet bo'yicha filter"),
    current_admin: Admin = Depends(get_current_admin),
    session: AsyncSession = Depends(get_db)
):
    """
    Export students data to CSV format with UTF-8 BOM encoding for complete Uzbek character compatibility (Requirement 15).
    """
    repo = RegistrationRepository(session)
    items = await repo.get_all_for_export(
        club_id=club_id,
        direction_id=direction_id,
        faculty_id=faculty_id
    )

    buffer = ExportService.generate_csv(items)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"iqtidorli_talabalar_{timestamp}.csv"

    return StreamingResponse(
        buffer,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
