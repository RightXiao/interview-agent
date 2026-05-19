from __future__ import annotations

from datetime import datetime
from pathlib import Path
from textwrap import wrap


class PdfExportError(RuntimeError):
    """Raised when PDF generation fails."""


def export_answer_to_pdf(
    title: str,
    content: str,
    sources: list[str],
    output_path: Path | str,
    font_path: str | None = None,
) -> Path:
    return _export_pdf(title=title, content=content, sources=sources, output_path=output_path, font_path=font_path)


def export_study_plan_to_pdf(
    plan: str,
    output_path: Path | str,
    font_path: str | None = None,
) -> Path:
    return _export_pdf(title="Study Plan", content=plan, sources=[], output_path=output_path, font_path=font_path)


def _export_pdf(
    title: str,
    content: str,
    sources: list[str],
    output_path: Path | str,
    font_path: str | None,
) -> Path:
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.pdfgen import canvas
    except ImportError as exc:
        raise PdfExportError("ReportLab is required for PDF export. Install dependency: reportlab") from exc

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    font_name = "Helvetica"
    if font_path:
        font_file = Path(font_path)
        if not font_file.exists():
            raise PdfExportError(f"Configured PDF font does not exist: {font_file}")
        font_name = "CustomPdfFont"
        pdfmetrics.registerFont(TTFont(font_name, str(font_file)))

    try:
        pdf = canvas.Canvas(str(path), pagesize=A4)
        width, height = A4
        y = height - 48
        margin = 48

        def draw_line(text: str, size: int = 11, leading: int = 16) -> None:
            nonlocal y
            if y < 56:
                pdf.showPage()
                pdf.setFont(font_name, size)
                y = height - 48
            pdf.setFont(font_name, size)
            pdf.drawString(margin, y, text)
            y -= leading

        draw_line(title, size=18, leading=26)
        draw_line(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", size=9, leading=22)
        for paragraph in content.splitlines() or [content]:
            if not paragraph.strip():
                y -= 8
                continue
            for line in wrap(paragraph, width=88):
                draw_line(line)
        if sources:
            y -= 10
            draw_line("Sources", size=13, leading=20)
            for source in sources:
                for line in wrap(f"- {source}", width=88):
                    draw_line(line)
        pdf.save()
    except Exception as exc:
        raise PdfExportError(f"Failed to export PDF: {path}") from exc
    return path

