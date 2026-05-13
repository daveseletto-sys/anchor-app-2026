"""PDF report generator for clinician/sponsor exports."""
import io
from datetime import datetime, date, timedelta, timezone

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)


SAGE = colors.HexColor("#4A6552")
TERRACOTTA = colors.HexColor("#C86B52")
BONE = colors.HexColor("#F2EFE8")
SAND = colors.HexColor("#E8E3D6")
INK = colors.HexColor("#2A2E2B")
MUTED = colors.HexColor("#5C6160")


def _styles():
    s = getSampleStyleSheet()
    s.add(ParagraphStyle("AnchorTitle", parent=s["Title"], fontName="Helvetica-Bold", fontSize=26, leading=30, textColor=INK, alignment=TA_LEFT, spaceAfter=4))
    s.add(ParagraphStyle("AnchorSub", parent=s["Normal"], fontName="Helvetica", fontSize=10, leading=14, textColor=MUTED, spaceAfter=16))
    s.add(ParagraphStyle("AnchorEyebrow", parent=s["Normal"], fontName="Helvetica-Bold", fontSize=8, textColor=MUTED, spaceAfter=4))
    s.add(ParagraphStyle("AnchorH2", parent=s["Heading2"], fontName="Helvetica-Bold", fontSize=14, leading=18, textColor=INK, spaceBefore=14, spaceAfter=8))
    s.add(ParagraphStyle("AnchorBody", parent=s["Normal"], fontName="Helvetica", fontSize=10, leading=15, textColor=INK))
    s.add(ParagraphStyle("AnchorMuted", parent=s["Normal"], fontName="Helvetica", fontSize=9, leading=13, textColor=MUTED))
    s.add(ParagraphStyle("AnchorBig", parent=s["Normal"], fontName="Helvetica-Bold", fontSize=22, leading=24, textColor=SAGE))
    return s


def _kv_table(rows):
    t = Table(rows, colWidths=[1.7 * inch, 4.0 * inch])
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (0, 0), (0, -1), MUTED),
        ("TEXTCOLOR", (1, 0), (1, -1), INK),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("LINEBELOW", (0, 0), (-1, -2), 0.25, SAND),
    ]))
    return t


def _data_table(header, rows):
    full = [header] + rows
    t = Table(full, repeatRows=1, colWidths=None)
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BACKGROUND", (0, 0), (-1, 0), BONE),
        ("TEXTCOLOR", (0, 0), (-1, 0), INK),
        ("TEXTCOLOR", (0, 1), (-1, -1), INK),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, BONE]),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    return t


def build_report_pdf(
    *,
    user: dict,
    period_label: str,
    start_date: date,
    end_date: date,
    days_sober: int,
    scope: str,
    diet_summary: dict,
    diet_compliance: dict,
    blood_tests: list,
    medications: list,
    medication_adherence: dict,
    goals: list,
    diary: list,
    diary_avg_rating: float | None,
) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=LETTER,
        leftMargin=0.75 * inch, rightMargin=0.75 * inch,
        topMargin=0.7 * inch, bottomMargin=0.7 * inch,
        title=f"Anchor Health Report — {user.get('name','')}",
        author="Anchor Recovery",
    )
    s = _styles()
    story = []

    # Header
    story.append(Paragraph("Anchor &nbsp; · &nbsp; Recovery Health Report", s["AnchorEyebrow"]))
    story.append(Paragraph(user.get("name", ""), s["AnchorTitle"]))
    sub = f"{period_label} &nbsp; · &nbsp; {start_date.isoformat()} → {end_date.isoformat()} &nbsp; · &nbsp; generated {datetime.now(timezone.utc).strftime('%Y-%m-%d')}"
    story.append(Paragraph(sub, s["AnchorSub"]))

    # Patient summary
    story.append(Paragraph("Summary", s["AnchorH2"]))
    rows = [
        ["Sobriety start", user.get("sobriety_start") or "—"],
        ["Days sober (today)", str(days_sober)],
    ]
    if user.get("height_cm"):
        rows.append(["Height", f"{user.get('height_cm')} cm"])
    if user.get("weight_kg"):
        rows.append(["Weight", f"{user.get('weight_kg')} kg"])
    rows.append(["Report scope", scope.title()])
    story.append(_kv_table(rows))

    # Diet
    story.append(Paragraph("Diet", s["AnchorH2"]))
    story.append(Paragraph(
        f"Targets: protein ≥ {diet_summary['targets']['protein_g_min']} g/day · "
        f"salt ≤ {diet_summary['targets']['salt_g_max']} g/day · "
        f"water ≤ {diet_summary['targets']['water_ml_max']} ml/day",
        s["AnchorMuted"],
    ))
    story.append(Spacer(1, 6))
    diet_rows = [
        ["Days logged", str(diet_summary["days_logged"])],
        ["Avg protein", f"{diet_summary['avg_protein_g']} g  (compliance: {diet_compliance['protein_pct']}%)"],
        ["Avg salt", f"{diet_summary['avg_salt_g']} g  (within limit: {diet_compliance['salt_pct']}%)"],
        ["Avg water", f"{diet_summary['avg_water_ml']} ml  (within limit: {diet_compliance['water_pct']}%)"],
    ]
    story.append(_kv_table(diet_rows))

    # Blood tests
    story.append(Paragraph("Blood test results", s["AnchorH2"]))
    if not blood_tests:
        story.append(Paragraph("No blood tests recorded in this period.", s["AnchorMuted"]))
    else:
        # build flat marker rows: date | marker | value | unit | reference
        rows = []
        for t in blood_tests:
            for m in t.get("markers", []):
                rows.append([
                    t.get("date", ""),
                    m.get("name", ""),
                    str(m.get("value", "")),
                    m.get("unit", "") or "—",
                    m.get("reference_range", "") or "—",
                ])
        story.append(_data_table(
            ["Date", "Marker", "Value", "Unit", "Reference"],
            rows,
        ))

    # Medications
    story.append(Paragraph("Medications", s["AnchorH2"]))
    if not medications:
        story.append(Paragraph("No medications recorded.", s["AnchorMuted"]))
    else:
        med_rows = []
        for m in medications:
            adh = medication_adherence.get(m["id"], {})
            taken = adh.get("taken", 0)
            expected = adh.get("expected", 0)
            pct = round((taken / expected * 100) if expected else 0)
            med_rows.append([
                m.get("name", ""),
                m.get("dose", "") or "—",
                m.get("schedule", "") or "—",
                f"{taken}/{expected} ({pct}%)" if expected else "—",
            ])
        story.append(_data_table(
            ["Medication", "Dose", "Schedule", "Adherence"],
            med_rows,
        ))

    # Goals
    story.append(Paragraph("Weekly goals", s["AnchorH2"]))
    if not goals:
        story.append(Paragraph("No goals set in this period.", s["AnchorMuted"]))
    else:
        rows = [[g.get("week_start", ""), g.get("title", ""), "✓ Done" if g.get("completed") else "Open"] for g in goals]
        story.append(_data_table(["Week of", "Goal", "Status"], rows))

    # Diary (only if scope includes diary)
    if scope in ("full", "personal"):
        story.append(PageBreak())
        story.append(Paragraph("Daily diary", s["AnchorH2"]))
        if diary_avg_rating is not None:
            story.append(Paragraph(f"Average daily rating: <b>{diary_avg_rating}/10</b> across {len(diary)} entries.", s["AnchorBody"]))
            story.append(Spacer(1, 8))
        if not diary:
            story.append(Paragraph("No diary entries in this period.", s["AnchorMuted"]))
        else:
            for e in diary:
                story.append(Paragraph(f"<b>{e.get('date', '')}</b> &nbsp; · &nbsp; {e.get('rating', '')}/10", s["AnchorBody"]))
                tags = e.get("mood_tags") or []
                if tags:
                    story.append(Paragraph("&nbsp;&nbsp;Mood: " + ", ".join(tags), s["AnchorMuted"]))
                notes = (e.get("notes") or "").strip()
                if notes:
                    safe = notes.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br/>")
                    story.append(Paragraph(safe, s["AnchorBody"]))
                story.append(Spacer(1, 8))

    # Footer
    story.append(Spacer(1, 18))
    story.append(Paragraph(
        "Generated by Anchor Recovery. This is a self-reported summary and is not a substitute for clinical assessment.",
        s["AnchorMuted"],
    ))

    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf
