#!/usr/bin/env python3
"""
JSON → Weather Report PDF
FULL SCRIPT – NO TRUNCATION
"""

import json
from pathlib import Path
from datetime import datetime
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors


# =========================
# CONFIG
# =========================
INPUT_JSON = "summary.json"
today_str = datetime.now().strftime("%Y-%m-%d")
# We will determine full path in render_pdf or main, but typically ReportLab needs file path string.
# Let's keep just the filename const here, and resolve full path later.
OUTPUT_PDF_NAME = f"Summary_of_Current_Conditions_{today_str}.pdf"

IMG_DUMA_NAME = "5day_viz_duma.png"
IMG_NCR_NAME  = "5day_viz_ncr.png"

IMG_DUMA_TITLE = "Dumaguete City (5-day Weather Outlook)"
IMG_NCR_TITLE  = "Metro Manila (5-day Weather Outlook)"


# =========================
# PATH RESOLUTION
# =========================
def get_today_output_folder():
    today = datetime.now().strftime("%Y-%m-%d")
    base_dir = Path(__file__).resolve().parent
    return base_dir / "data" / f"output-{today}"


# =========================
# LOAD JSON
# =========================
def load_json():
    folder = get_today_output_folder()
    json_path = folder / INPUT_JSON
    if not json_path.exists():
        raise FileNotFoundError(f"JSON not found at {json_path}")
    return json.loads(json_path.read_text(encoding="utf-8"))


# =========================
# IMAGE NORMALIZATION (ALIGN + SCALE UP SMALLER)
# =========================
def normalize_images_to_same_width(
    left_path,
    right_path,
    target_max_width=260,
    target_max_height=150
):
    left = Image(str(left_path))
    right = Image(str(right_path))

    left_scale  = target_max_width / left.imageWidth
    right_scale = target_max_width / right.imageWidth

    left.drawWidth  = left.imageWidth * left_scale
    left.drawHeight = left.imageHeight * left_scale

    right.drawWidth  = right.imageWidth * right_scale
    right.drawHeight = right.imageHeight * right_scale

    for img in (left, right):
        if img.drawHeight > target_max_height:
            scale = target_max_height / img.drawHeight
            img.drawHeight *= scale
            img.drawWidth *= scale
        img.hAlign = "LEFT"

    return left, right


# =========================
# SAFE TEXT
# =========================
def safe(val, default="-"):
    if val in (None, "", [], {}):
        return default
    return str(val)


# =========================
# DOUBLE LINE SEPARATOR
# =========================
def double_separator(width=540):
    sep = Table([[""], [""]], colWidths=[width], rowHeights=[2, 2])
    sep.setStyle(TableStyle([
        ("LINEABOVE", (0, 0), (-1, 0), 0.75, colors.grey),
        ("LINEBELOW", (0, 1), (-1, 1), 0.75, colors.grey),
    ]))
    return sep


# =========================
# PDF RENDERER
# =========================
def render_pdf(data):
    styles = getSampleStyleSheet()

    H1 = ParagraphStyle("H1", parent=styles["Heading1"], fontSize=16, spaceAfter=6)
    H2 = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=12, alignment=0, spaceAfter=2)
    H3 = ParagraphStyle("H3", parent=styles["Heading3"], fontSize=11, spaceAfter=4)
    BODY = ParagraphStyle("BODY", parent=styles["BodyText"], fontSize=10, leading=14)
    TABLETXT = ParagraphStyle("TABLETXT", fontSize=9, leading=11, wordWrap="CJK")

    FOOTER = ParagraphStyle(
        "FOOTER",
        fontSize=8,
        textColor=colors.grey,
        alignment=1,
        spaceBefore=18,
    )

    story = []

    # =====================================================
    # HEADER VISUALS (FIXED & ALIGNED)
    # =====================================================
    output_dir = get_today_output_folder()
    duma_img = output_dir / IMG_DUMA_NAME
    ncr_img  = output_dir / IMG_NCR_NAME

    if duma_img.exists() and ncr_img.exists():
        duma_vis, ncr_vis = normalize_images_to_same_width(
            duma_img,
            ncr_img,
            target_max_width=260,
            target_max_height=150
        )

        header_table = Table(
            [
                [Paragraph(IMG_DUMA_TITLE, H2), Paragraph(IMG_NCR_TITLE, H2)],
                [duma_vis, ncr_vis],
            ],
            colWidths=[270, 270],
        )

        header_table.setStyle(TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ]))

        story.append(header_table)
        story.append(Spacer(1, 14))

    story.append(double_separator())
    story.append(Spacer(1, 18))

    # =====================================================
    # SUMMARY OF CURRENT CONDITIONS
    # =====================================================
    s = data.get("summary_of_current_conditions", {})

    story.append(Paragraph("SUMMARY OF CURRENT CONDITIONS", H1))
    for k, label in [
        ("date", "Date"),
        ("system_in_effect", "System in Effect"),
        ("general_weather", "General Weather"),
        ("winds", "Winds"),
        ("humidity", "Humidity"),
        ("low_high_temperature", "Temperature Range"),
    ]:
        story.append(Paragraph(f"<b>{label}:</b> {safe(s.get(k))}", BODY))

    story.append(Spacer(1, 14))
    story.append(double_separator())
    story.append(Spacer(1, 18))

    # =====================================================
    # ACTIVE PAGASA ADVISORIES
    # =====================================================
    story.append(Paragraph("ACTIVE PAGASA ADVISORIES", H1))
    advisories = data.get("active_pagasa_advisories", {})

    for adv_type, sites in advisories.items():
        if not isinstance(sites, dict):
             # Skip empty lists or non-dict items (like "other_advisories": [])
             continue
        
        story.append(Paragraph(adv_type.replace("_", " ").title(), H3))
        for site, block in sites.items():
            story.append(Paragraph(site.replace("_", " ").title(), BODY))
            story.append(Paragraph(safe(block.get("title")), BODY))
            story.append(Paragraph(safe(block.get("summary")), BODY))
            story.append(Spacer(1, 6))

    story.append(Spacer(1, 12))
    story.append(double_separator())
    story.append(Spacer(1, 18))

    # =====================================================
    # 10-DAY ACCUWEATHER FORECAST
    # =====================================================
    story.append(Paragraph("10-DAY ACCUWEATHER FORECAST", H1))
    story.append(Spacer(1, 10))

    accuweather = data.get("forecast_10day", {}).get("accuweather", {})

    for site, forecast in accuweather.items():
        story.append(Paragraph(site.replace("_", " ").title(), H3))
        story.append(Spacer(1, 6))

        if not forecast:
            story.append(Paragraph("No forecast data available.", BODY))
            story.append(Spacer(1, 12))
            continue

        table_data = [[
            Paragraph("<b>Date</b>", TABLETXT),
            Paragraph("<b>High</b>", TABLETXT),
            Paragraph("<b>Low</b>", TABLETXT),
            Paragraph("<b>Rain %</b>", TABLETXT),
            Paragraph("<b>Description</b>", TABLETXT),
        ]]

        for d in forecast:
            table_data.append([
                Paragraph(safe(d.get("date_label")), TABLETXT),
                Paragraph(f"{safe(d.get('max_temp'))}°C", TABLETXT),
                Paragraph(f"{safe(d.get('min_temp'))}°C", TABLETXT),
                Paragraph(f"{safe(d.get('pop'))}%", TABLETXT),
                Paragraph(safe(d.get("description")), TABLETXT),
            ])

        table = Table(table_data, colWidths=[60, 45, 45, 45, 245], repeatRows=1)
        table.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ]))

        story.append(table)
        story.append(Spacer(1, 16))

    story.append(double_separator())
    story.append(Spacer(1, 18))

    # =====================================================
    # SITE IMPACT SUMMARY
    # =====================================================
    story.append(Paragraph("SITE IMPACT SUMMARY", H1))
    for site, info in data.get("site_impact_summary", {}).items():
        story.append(Paragraph(site.replace("_", " ").title(), styles["Heading2"]))
        story.append(Paragraph(f"<b>Impact Level:</b> {safe(info.get('impact_level'))}", BODY))
        story.append(Paragraph(safe(info.get("justification")), BODY))
        story.append(Spacer(1, 6))

    story.append(Spacer(1, 12))
    story.append(double_separator())
    story.append(Spacer(1, 18))

    # =====================================================
    # OPERATIONAL RECOMMENDATIONS
    # =====================================================
    story.append(Paragraph("OPERATIONAL RECOMMENDATIONS", H1))
    for site, recs in data.get("operational_recommendations", {}).items():
        story.append(Paragraph(site.replace("_", " ").title(), styles["Heading2"]))
        for r in recs or ["-"]:
            story.append(Paragraph("• " + safe(r), BODY))

    story.append(Spacer(1, 18))
    story.append(double_separator())
    story.append(Spacer(1, 18))

    # =====================================================
    # KEY TAKEAWAYS
    # =====================================================
    story.append(Paragraph("KEY TAKEAWAYS", H1))
    for item in data.get("key_takeaways", []):
        story.append(Paragraph("• " + safe(item), BODY))

    # =====================================================
    # FOOTER
    # =====================================================
    generated_ts = datetime.now().strftime("%B %d, %Y %I:%M %p")
    story.append(Spacer(1, 18))
    story.append(double_separator())
    story.append(Spacer(1, 10))

    story.append(Paragraph(
        f"Generated on {generated_ts} · by Project AWRA "
        f"(Automated Weather Report Analytics) ® Jan Vincent Chioco",
        FOOTER
    ))

    today_folder = get_today_output_folder()
    output_pdf_path = today_folder / OUTPUT_PDF_NAME

    doc = SimpleDocTemplate(
        str(output_pdf_path),
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    doc.build(story)


# =========================
# MAIN
# =========================
if __name__ == "__main__":
    render_pdf(load_json())
    print("✅ PDF generated:", get_today_output_folder() / OUTPUT_PDF_NAME)
