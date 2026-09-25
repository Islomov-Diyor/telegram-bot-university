import csv
import io
from typing import List, Dict, Any
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter


class ExportService:
    @staticmethod
    def generate_excel(registrations: List[Dict[str, Any]]) -> io.BytesIO:
        """
        Generate a beautifully styled Excel (.xlsx) file with student registrations.
        Includes university headers, navy title styling, zebra striping, and auto column widths.
        """
        wb = Workbook()
        ws = wb.active
        ws.title = "Iqtidorli Talabalar"

        # Headers
        headers = [
            "№",
            "Talaba F.I.Sh",
            "Fakultet",
            "Ta'lim Yo'nalishi",
            "To'garak Nomi",
            "Kursi",
            "Telefon Raqami",
            "Telegram",
            "Ro'yxatdan O'tgan Sana"
        ]
        ws.append(headers)

        # Header Styles
        header_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
        header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        center_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
        left_align = Alignment(horizontal="left", vertical="center")

        thin_border = Border(
            left=Side(style="thin", color="CBD5E1"),
            right=Side(style="thin", color="CBD5E1"),
            top=Side(style="thin", color="CBD5E1"),
            bottom=Side(style="thin", color="CBD5E1")
        )

        ws.row_dimensions[1].height = 28
        for col_num, _ in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = center_align
            cell.border = thin_border

        # Populate rows
        zebra_fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
        white_fill = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")

        for idx, item in enumerate(registrations, 1):
            row_num = idx + 1
            ws.row_dimensions[row_num].height = 22

            reg_date = item.get("registered_at")
            if reg_date and hasattr(reg_date, "strftime"):
                date_str = reg_date.strftime("%d.%m.%Y %H:%M")
            else:
                date_str = str(reg_date or "")

            username = item.get("telegram_username")
            tg_text = f"@{username}" if username else "-"

            row_data = [
                idx,
                item.get("full_name", ""),
                item.get("faculty_name", ""),
                item.get("direction_name", ""),
                item.get("club_name", ""),
                f"{item.get('course_level', '')}-kurs",
                item.get("phone_number", ""),
                tg_text,
                date_str
            ]
            ws.append(row_data)

            # Apply row styling
            row_fill = zebra_fill if idx % 2 == 0 else white_fill
            for col_idx in range(1, len(headers) + 1):
                cell = ws.cell(row=row_num, column=col_idx)
                cell.fill = row_fill
                cell.border = thin_border
                cell.font = Font(name="Calibri", size=10)
                if col_idx in (1, 6, 7, 8, 9):
                    cell.alignment = center_align
                else:
                    cell.alignment = left_align

        # Auto-adjust column widths
        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                val = str(cell.value or "")
                if len(val) > max_len:
                    max_len = len(val)
            ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        return buffer

    @staticmethod
    def generate_csv(registrations: List[Dict[str, Any]]) -> io.BytesIO:
        """
        Generate CSV encoded with UTF-8 BOM (utf-8-sig) to ensure Uzbek characters
        render flawlessly across all spreadsheet applications like Microsoft Excel.
        """
        buffer = io.StringIO()
        writer = csv.writer(buffer, delimiter=",", quoting=csv.QUOTE_MINIMAL)

        # Header
        writer.writerow([
            "№",
            "Talaba F.I.Sh",
            "Fakultet",
            "Yo'nalish",
            "To'garak",
            "Kursi",
            "Telefon Raqami",
            "Telegram",
            "Ro'yxatdan O'tgan Sana"
        ])

        for idx, item in enumerate(registrations, 1):
            reg_date = item.get("registered_at")
            if reg_date and hasattr(reg_date, "strftime"):
                date_str = reg_date.strftime("%d.%m.%Y %H:%M")
            else:
                date_str = str(reg_date or "")

            username = item.get("telegram_username")
            tg_text = f"@{username}" if username else "-"

            writer.writerow([
                idx,
                item.get("full_name", ""),
                item.get("faculty_name", ""),
                item.get("direction_name", ""),
                item.get("club_name", ""),
                f"{item.get('course_level', '')}-kurs",
                item.get("phone_number", ""),
                tg_text,
                date_str
            ])

        bytes_buffer = io.BytesIO()
        # utf-8-sig adds the UTF-8 BOM mark (0xEF, 0xBB, 0xBF)
        bytes_buffer.write(buffer.getvalue().encode("utf-8-sig"))
        bytes_buffer.seek(0)
        return bytes_buffer
