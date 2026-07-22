"""
utils/pdf_generator.py
----------------------
ReportLab PDF report builder for the Radiology Audit Report.
"""

import io
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.colors import HexColor


# ── Brand Colors ──────────────────────────────────────────────────────────────
TEAL      = HexColor("#0d9488")
DARK_NAVY = HexColor("#0f172a")
SLATE     = HexColor("#475569")
LIGHT_BG  = HexColor("#f0fdfa")
RED       = HexColor("#ef4444")
AMBER     = HexColor("#f59e0b")
GREEN     = HexColor("#10b981")
BLUE      = HexColor("#3b82f6")
PURPLE    = HexColor("#8b5cf6")
WHITE     = colors.white
LIGHT_GRAY = HexColor("#f1f5f9")
BORDER    = HexColor("#e2e8f0")


def _styles():
    base = getSampleStyleSheet()
    styles = {
        "title": ParagraphStyle(
            "title", parent=base["Normal"],
            fontName="Helvetica-Bold", fontSize=22,
            textColor=WHITE, alignment=TA_CENTER, spaceAfter=2
        ),
        "subtitle": ParagraphStyle(
            "subtitle", parent=base["Normal"],
            fontName="Helvetica", fontSize=11,
            textColor=HexColor("#94a3b8"), alignment=TA_CENTER, spaceAfter=0
        ),
        "section_heading": ParagraphStyle(
            "section_heading", parent=base["Normal"],
            fontName="Helvetica-Bold", fontSize=13,
            textColor=DARK_NAVY, spaceBefore=14, spaceAfter=6,
            borderPad=4
        ),
        "body": ParagraphStyle(
            "body", parent=base["Normal"],
            fontName="Helvetica", fontSize=10,
            textColor=SLATE, leading=15, spaceAfter=4
        ),
        "body_bold": ParagraphStyle(
            "body_bold", parent=base["Normal"],
            fontName="Helvetica-Bold", fontSize=10,
            textColor=DARK_NAVY, leading=15
        ),
        "small": ParagraphStyle(
            "small", parent=base["Normal"],
            fontName="Helvetica", fontSize=8.5,
            textColor=SLATE, leading=12
        ),
        "bullet": ParagraphStyle(
            "bullet", parent=base["Normal"],
            fontName="Helvetica", fontSize=10,
            textColor=SLATE, leading=15,
            leftIndent=16, spaceAfter=3,
            bulletIndent=6
        ),
        "footer": ParagraphStyle(
            "footer", parent=base["Normal"],
            fontName="Helvetica", fontSize=8,
            textColor=HexColor("#94a3b8"), alignment=TA_CENTER
        ),
    }
    return styles


def _hr():
    return HRFlowable(width="100%", thickness=1, color=BORDER, spaceAfter=8, spaceBefore=4)


def _section_title(text: str, s):
    return [
        Paragraph(text, s["section_heading"]),
        HRFlowable(width="100%", thickness=1.5, color=TEAL, spaceAfter=8),
    ]


def _readiness_label(status: str) -> tuple:
    mapping = {
        "ready_for_approval":      ("✅  Ready for Approval",      GREEN),
        "minor_revision_required": ("⚠️  Minor Revision Required", AMBER),
        "major_revision_required": ("🔴  Major Revision Required", RED),
    }
    return mapping.get(status, ("Unknown Status", SLATE))


def generate_audit_pdf(
    report_filename: str,
    modality: str,
    audit_result: dict,
    audit_timestamp: datetime = None,
) -> bytes:
    """
    Generates a professional PDF audit report and returns the raw bytes.

    Args:
        report_filename: Name of the original report file.
        modality: Imaging modality string.
        audit_result: Full parsed Gemini JSON result.
        audit_timestamp: datetime of when the audit was run.

    Returns:
        PDF bytes ready for st.download_button.
    """
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=1.5*cm, bottomMargin=2*cm,
        title="Radiology Audit Report",
        author="AI-Powered Radiology Report Audit & Quality Analyzer",
    )

    s = _styles()
    story = []
    ts = audit_timestamp or datetime.now()

    # ── HEADER BANNER ────────────────────────────────────────────────────────
    header_table = Table(
        [[
            Paragraph("⚕️  AI-Powered Radiology Report Audit & Quality Analyzer", s["title"]),
        ]],
        colWidths=["100%"]
    )
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), DARK_NAVY),
        ("ROUNDEDCORNERS", [12]),
        ("TOPPADDING", (0, 0), (-1, -1), 18),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 18),
        ("LEFTPADDING", (0, 0), (-1, -1), 20),
        ("RIGHTPADDING", (0, 0), (-1, -1), 20),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 6))
    story.append(Paragraph("Confidential Clinical Quality Assurance Document", s["subtitle"]))
    story.append(Spacer(1, 16))

    # ── METADATA TABLE ────────────────────────────────────────────────────────
    story += _section_title("📋  Report Information", s)
    meta_data = [
        ["Report Filename", report_filename or "N/A"],
        ["Examination Modality", modality or "N/A"],
        ["Audit Date & Time", ts.strftime("%d %B %Y  •  %I:%M %p")],
        ["Generated By", "AI-Powered Radiology Audit System (Google Gemini)"],
    ]
    meta_table = Table(meta_data, colWidths=[5*cm, "auto"])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), LIGHT_BG),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("TEXTCOLOR", (0, 0), (0, -1), DARK_NAVY),
        ("TEXTCOLOR", (1, 0), (1, -1), SLATE),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [WHITE, LIGHT_GRAY]),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("ROUNDEDCORNERS", [6]),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 14))

    # ── QUALITY SCORE + STATUS ────────────────────────────────────────────────
    story += _section_title("📊  Quality Assessment", s)
    score = audit_result.get("quality_score", 0)
    status = audit_result.get("readiness_status", "")
    status_label, status_color = _readiness_label(status)
    justification = audit_result.get("score_justification", "")

    score_color = GREEN if score >= 85 else (AMBER if score >= 65 else RED)

    score_table = Table([
        [
            Paragraph(f'<font size="28" color="{score_color.hexval()}"><b>{score}/100</b></font>', ParagraphStyle("sc", alignment=TA_CENTER, fontName="Helvetica-Bold")),
            Table([
                [Paragraph(f'<font color="{status_color.hexval()}"><b>{status_label}</b></font>', ParagraphStyle("st", fontName="Helvetica-Bold", fontSize=12))],
                [Paragraph(justification, s["body"])],
            ], colWidths=["100%"]),
        ]
    ], colWidths=[4*cm, "auto"])
    score_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BACKGROUND", (0, 0), (0, 0), LIGHT_BG),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("ROUNDEDCORNERS", [8]),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 14))

    # ── QUALITY BREAKDOWN ────────────────────────────────────────────────────
    breakdown = audit_result.get("quality_breakdown", {})
    if breakdown:
        story += _section_title("📈  Quality Breakdown", s)
        breakdown_labels = {
            "completeness": "Completeness",
            "terminology": "Medical Terminology",
            "clinical_alignment": "Clinical Alignment",
            "formatting": "Formatting",
            "impression_quality": "Impression Quality",
        }
        bd_rows = [["Dimension", "Score", "Rating"]]
        for key, label in breakdown_labels.items():
            val = breakdown.get(key, 0)
            rating = "Excellent" if val >= 85 else ("Good" if val >= 65 else "Needs Work")
            bd_rows.append([label, f"{val}/100", rating])

        bd_table = Table(bd_rows, colWidths=[6*cm, 3*cm, "auto"])
        bd_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), DARK_NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 9.5),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_GRAY]),
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
            ("ALIGN", (1, 0), (2, -1), "CENTER"),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ]))
        story.append(bd_table)
        story.append(Spacer(1, 14))

    # ── STRENGTHS ─────────────────────────────────────────────────────────────
    strengths = audit_result.get("strengths", [])
    if strengths:
        story += _section_title("✅  Strengths Identified", s)
        for st_item in strengths:
            story.append(Paragraph(f"✓  {st_item}", s["bullet"]))
        story.append(Spacer(1, 10))

    # ── MISSING SECTIONS ──────────────────────────────────────────────────────
    missing = audit_result.get("missing_sections_list", [])
    story += _section_title("⚠️  Missing Sections", s)
    if missing:
        for m in missing:
            story.append(Paragraph(f"✗  {m}", s["bullet"]))
    else:
        story.append(Paragraph("✓  All mandatory sections are present.", s["body"]))
    story.append(Spacer(1, 10))

    # ── SECTION AUDIT CHECKLIST ───────────────────────────────────────────────
    sections = audit_result.get("mandatory_sections", [])
    if sections:
        story += _section_title("📋  Section Completeness Audit", s)
        sec_rows = [["Section", "Status", "Notes"]]
        for sec in sections:
            present = sec.get("present", False)
            status_text = "✓ Present" if present else "✗ Missing"
            sec_rows.append([sec.get("name", ""), status_text, sec.get("details", "")])

        sec_table = Table(sec_rows, colWidths=[5*cm, 2.5*cm, "auto"])
        sec_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), DARK_NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_GRAY]),
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ]))
        story.append(sec_table)
        story.append(Spacer(1, 14))

    # ── AI SUGGESTIONS ────────────────────────────────────────────────────────
    suggestions = audit_result.get("ai_suggestions", {})
    sug_map = {
        "missing_sections":      ("🔴 Missing Sections",          RED),
        "template_compliance":   ("🔵 Template Compliance",       BLUE),
        "medical_terminology":   ("🟣 Medical Terminology",       PURPLE),
        "formatting_improvements":("🟢 Formatting Improvements",  TEAL),
        "impression_suggestions":("🟠 Impression Suggestions",    AMBER),
        "overall_remarks":       ("⚫ Overall Remarks",            SLATE),
    }

    has_suggestions = any(suggestions.get(k) for k in sug_map)
    if has_suggestions:
        story += _section_title("💡  AI-Generated Improvement Suggestions", s)
        for key, (label, color) in sug_map.items():
            items = suggestions.get(key, [])
            if not items:
                continue
            story.append(Paragraph(label, ParagraphStyle(
                f"sug_{key}", fontName="Helvetica-Bold", fontSize=10,
                textColor=color, spaceBefore=8, spaceAfter=4
            )))
            for item in items:
                story.append(Paragraph(f"•  {item}", s["bullet"]))
        story.append(Spacer(1, 10))

    # ── OVERALL REMARKS ───────────────────────────────────────────────────────
    overall = audit_result.get("overall_remarks", "")
    if overall:
        story += _section_title("📝  Executive Audit Summary", s)
        remarks_table = Table([[Paragraph(overall, s["body"])]], colWidths=["100%"])
        remarks_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BG),
            ("ROUNDEDCORNERS", [8]),
            ("TOPPADDING", (0, 0), (-1, -1), 12),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
            ("LEFTPADDING", (0, 0), (-1, -1), 14),
            ("RIGHTPADDING", (0, 0), (-1, -1), 14),
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
        ]))
        story.append(remarks_table)
        story.append(Spacer(1, 20))

    # ── FOOTER ────────────────────────────────────────────────────────────────
    story.append(_hr())
    story.append(Paragraph(
        f"Generated by AI-Powered Radiology Report Audit & Quality Analyzer  •  "
        f"{ts.strftime('%d %b %Y, %I:%M %p')}  •  Powered by Google Gemini",
        s["footer"]
    ))
    story.append(Paragraph(
        "⚠️  This report is an AI-assisted quality audit tool and does not constitute a clinical diagnosis. "
        "All findings must be reviewed by a qualified radiologist.",
        ParagraphStyle("disclaimer", fontName="Helvetica-Oblique", fontSize=7.5,
                       textColor=HexColor("#94a3b8"), alignment=TA_CENTER, spaceBefore=4)
    ))

    doc.build(story)
    return buf.getvalue()
