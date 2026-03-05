#!/usr/bin/env python3
"""
JSON → Weather Report PDF
DESIGN: MATCHING WEBAPP DASHBOARD AESTHETICS + IMAGES + DETAILED TEXT
"""

import json
from pathlib import Path
from datetime import datetime
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors

# =========================
# CONFIG
# =========================
INPUT_JSON = "summary.json"
today_str = datetime.now().strftime("%Y-%m-%d")
OUTPUT_PDF_NAME = "weather_report.pdf"

IMG_DUMA_NAME = "5day_viz_duma.png"
IMG_NCR_NAME  = "5day_viz_ncr.png"

# Brand Colors (Matching WebApp)
COL_BG_SLATE = colors.HexColor("#f8fafc") # slate-50
COL_TXT_SLATE = colors.HexColor("#1e293b") # slate-800
COL_BLUE_PRI = colors.HexColor("#2563eb") # blue-600
COL_RED_ALRT = colors.HexColor("#dc2626") # red-600
COL_AMB_WARN = colors.HexColor("#d97706") # amber-600
COL_GRN_SAFE = colors.HexColor("#059669") # emerald-600

import sys
# Add project root to sys.path
base_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(base_dir))

from utils.ph_time import get_ph_date_str, get_ph_time

# =========================
# PATH RESOLUTION
# =========================
def get_today_output_folder():
    today = get_ph_date_str()
    base_dir = Path(__file__).resolve().parent.parent
    return base_dir / "data" / f"output-{today}"

def load_json():
    folder = get_today_output_folder()
    json_path = folder / INPUT_JSON
    if not json_path.exists():
        raise FileNotFoundError(f"JSON not found at {json_path}")
    return json.loads(json_path.read_text(encoding="utf-8"))

def safe(val, default="-"):
    if val in (None, "", [], {}): return default
    val = str(val).strip()
    return val if val else default

# =========================
# IMAGE UTILS
# =========================
def normalize_images_to_same_width(left_path, right_path, target_max_width=250, target_max_height=180):
    """Resizes two images so they fit side-by-side nicely."""
    if not left_path.exists() or not right_path.exists():
        return None, None
        
    left = Image(str(left_path))
    right = Image(str(right_path))

    # Scale by width
    left_scale  = target_max_width / left.imageWidth
    right_scale = target_max_width / right.imageWidth

    left.drawWidth  = left.imageWidth * left_scale
    left.drawHeight = left.imageHeight * left_scale

    right.drawWidth  = right.imageWidth * right_scale
    right.drawHeight = right.imageHeight * right_scale

    # Check height constraint
    for img in (left, right):
        if img.drawHeight > target_max_height:
            scale = target_max_height / img.drawHeight
            img.drawHeight *= scale
            img.drawWidth *= scale
        img.hAlign = "CENTER"

    return left, right

# =========================
# STYLES
# =========================
def get_custom_styles():
    styles = getSampleStyleSheet()
    
    # Modern Scientific Typography:
    # Body Text: Serif (Times-Roman) - High readability, academic feel.
    # Headers: Sans-Serif (Helvetica-Bold) - Clean, modern contrast.
    
    body_font = "Times-Roman"
    header_font = "Helvetica-Bold"
    
    return {
        "Title": ParagraphStyle(
            "DashTitle", parent=styles["Heading1"], fontName="Times-Bold", fontSize=26, # Serif Masthead
            textColor=COL_TXT_SLATE, spaceAfter=2, leading=30
        ),
        "Subtitle": ParagraphStyle(
            "DashSubtitle", parent=styles["Normal"], fontName="Helvetica", fontSize=11, # Sans Subtitle
            textColor=colors.gray, spaceAfter=20
        ),
        "SectionHeader": ParagraphStyle(
            "DashSection", parent=styles["Heading2"], fontName=header_font, fontSize=12,
            textColor=COL_TXT_SLATE, spaceBefore=14, spaceAfter=8, # Dark slate headers, not blue
            textTransform="uppercase", # Modern touch
            borderPadding=0, borderWidth=0
        ),
        "CardTitle": ParagraphStyle(
            "CardTitle", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=10,
            textColor=COL_TXT_SLATE, spaceAfter=2, textTransform="uppercase"
        ),
        "CardValue": ParagraphStyle(
            "CardValue", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=10, 
            textColor=COL_TXT_SLATE, leading=12
        ),
        "Normal": ParagraphStyle(
            "DashNormal", parent=styles["Normal"], fontName=body_font, fontSize=10, # Times-Roman Body
            textColor=COL_TXT_SLATE, leading=13 # Increased leading for readability
        ),
        "AlertRed": ParagraphStyle(
            "AlertRed", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=9,
            textColor=COL_RED_ALRT
        ),
        "Footer": ParagraphStyle(
            "Footer", parent=styles["Normal"], fontName="Helvetica", fontSize=8,
            textColor=colors.gray, alignment=1
        )
    }

# =========================
# COMPONENT BUILDERS
# =========================
def build_metric_card(title, value, subtext="", color=COL_TXT_SLATE):
    S = get_custom_styles()
    val_style = ParagraphStyle("ValOverride", parent=S["CardValue"], textColor=color)
    
    return Table(
        [[Paragraph(title, S["CardTitle"])],
         [Paragraph(value, val_style)],
         [Paragraph(subtext, S["Normal"])]],
        colWidths=[240], # Wider for detailed text
        style=[
            ('BACKGROUND', (0,0), (-1,-1), COL_BG_SLATE),
            ('BOX', (0,0), (-1,-1), 0.5, colors.lightgrey),
            ('TOPPADDING', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('LEFTPADDING', (0,0), (-1,-1), 10),
            ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ]
    )

def build_forecast_table(forecast_list):
    S = get_custom_styles()
    data = [[
        Paragraph("<b>DATE</b>", S["CardTitle"]),
        Paragraph("<b>CONDITION</b>", S["CardTitle"]),
        Paragraph("<b>TEMP</b>", S["CardTitle"]),
        Paragraph("<b>CHANCE</b>", S["CardTitle"])
    ]]
    for day in forecast_list[:7]: 
        desc = safe(day.get("description"))
        icon = "☀"
        if "cloud" in desc.lower(): icon = "☁"
        if "rain" in desc.lower() or "shower" in desc.lower(): icon = "☂"
        if "storm" in desc.lower() or "thund" in desc.lower(): icon = "⚡"
        
        data.append([
            Paragraph(safe(day.get("date_label")), S["Normal"]),
            Paragraph(f"{icon} {desc}", S["Normal"]),
            Paragraph(f"{safe(day.get('min_temp'))} - {safe(day.get('max_temp'))}°C", S["Normal"]),
            Paragraph(f"{safe(day.get('pop'))}%", S["Normal"]),
        ])

    t = Table(data, colWidths=[60, 200, 80, 60])
    t.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,0), 1, COL_BLUE_PRI),
        ('LINEBELOW', (0,1), (-1,-1), 0.5, colors.lightgrey),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    return t

def build_section_header(title):
    """Returns a list of flowables for a standardized double-lined section header."""
    S = get_custom_styles()
    
    # Double Line Table
    dbl_line = Table([[""]], colWidths=[500], rowHeights=[3])
    dbl_line.setStyle(TableStyle([
        ('LINEABOVE', (0,0), (-1,-1), 0.5, colors.gray), 
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.gray),
    ]))
    
    return [
        Spacer(1, 15),
        dbl_line,
        Spacer(1, 8),
        Paragraph(title, S["SectionHeader"])
    ]

# =========================
# PDF BUILDER
# =========================
def render_pdf(data):
    S = get_custom_styles()
    story = []
    
    # --- HEADER ---
    last_update = safe(data.get("summary_of_current_conditions", {}).get("date"))
    system_fx = safe(data.get("summary_of_current_conditions", {}).get("system_in_effect"))
    
    # --- HEADER ---
    last_update = safe(data.get("summary_of_current_conditions", {}).get("date"))
    system_fx = safe(data.get("summary_of_current_conditions", {}).get("system_in_effect"))
    
    # Research-Style Centered Header
    # Main Title: Times-Bold (Serif)
    story.append(Paragraph("PROJECT AWRA", ParagraphStyle("HeadTitle", parent=S["Title"], alignment=1, fontSize=26, textColor=COL_TXT_SLATE, spaceAfter=8)))
    
    # Subtitle: Helvetica (Sans) - "Modern" contrast
    story.append(Paragraph("Automated Weather Report Analytics", ParagraphStyle("HeadSub", parent=S["Subtitle"], alignment=1, fontSize=11, textColor=colors.gray, textTransform="uppercase", spaceAfter=4)))
    
    # Date: Helvetica (Sans)
    story.append(Paragraph(last_update, ParagraphStyle("HeadDate", parent=S["Subtitle"], alignment=1, fontSize=9, textColor=colors.gray, spaceAfter=15)))
    
    # Divider Line
    story.append(Table([[""]], colWidths=[500], style=[('LINEABOVE', (0,0), (-1,0), 2, COL_TXT_SLATE)]))
    story.append(Spacer(1, 15))

    # System Status Banner (Professional Colored Box)
    sys_color = COL_GRN_SAFE
    bg_color = colors.HexColor("#ecfdf5") # Light emerald bg
    
    # Check for keywords indicating bad weather to switch to Red/Amber
    warn_keywords = ["storm", "typhoon", "depression", "signal", "warning"]
    if any(k in system_fx.lower() for k in warn_keywords):
        sys_color = COL_RED_ALRT
        bg_color = colors.HexColor("#fef2f2") # Light red bg
    
    status_content = []
    status_content.append(Paragraph("SYSTEM IN EFFECT", ParagraphStyle("StatLabel", parent=S["CardTitle"], fontSize=8, textColor=sys_color)))
    status_content.append(Paragraph(system_fx, ParagraphStyle("StatBody", parent=S["Normal"], fontSize=11, textColor=COL_TXT_SLATE, leading=14)))
    
    # Render status as a colored box
    status_table = Table([[status_content]], colWidths=[500])
    status_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), bg_color),
        ('LEFTPADDING', (0,0), (-1,-1), 15),
        ('RIGHTPADDING', (0,0), (-1,-1), 15),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('BOX', (0,0), (-1,-1), 0.5, sys_color), # Border matching the alert color
    ]))
    story.append(status_table)
    story.append(Spacer(1, 20))

    # --- 5-DAY VISUALS ---
    out_dir = get_today_output_folder()
    duma_img_path = out_dir / IMG_DUMA_NAME
    ncr_img_path = out_dir / IMG_NCR_NAME
    
    d_img, n_img = normalize_images_to_same_width(duma_img_path, ncr_img_path, target_max_width=240)
    
    if d_img and n_img:
        story.extend(build_section_header("5-DAY OUTLOOK VISUALIZATION"))
        story.append(Table([[d_img, Spacer(20,20), n_img]], colWidths=[240, 20, 240]))
        story.append(Spacer(1, 20))


    # --- DETAILED CURRENT CONDITIONS ---
    story.extend(build_section_header("SUMMARY OF CURRENT CONDITIONS (DETAILED)"))
    
    s = data.get("summary_of_current_conditions", {})
    
    def format_as_bullets(raw_text):
        if not raw_text or raw_text == "No Data.":
            return [Paragraph("No Data.", S["Normal"])]
        
        # Insert breaks for "bullet" points
        # We try to identify standard headers in the text and break before them
        cleaned = raw_text.replace("Winds:", "<br/>• <b>Winds:</b>") \
                          .replace("Coastal waters:", "<br/>• <b>Coastal waters:</b>") \
                          .replace("Sea state:", "<br/>• <b>Sea state:</b>") \
                          .replace("Temp:", "<br/>• <b>Temp:</b>") \
                          .replace("Heat Index:", "<br/>• <b>Heat Index:</b>")
        
        # The first part (general condition) might not have a bullet, let's treat the whole thing as one paragraph 
        # but with manual break tags which ReportLab supports.
        # Also ensure the main text is NOT bold (S["Normal"] is non-bold).
        return Paragraph(cleaned, S["Normal"])

    # Metro Manila
    story.append(Paragraph("METRO MANILA", S["CardTitle"]))
    story.append(format_as_bullets(safe(s.get("metro_manila_detailed"), "No Data.")))
    story.append(Spacer(1, 12))
    
    # Dumaguete
    story.append(Paragraph("DUMAGUETE", S["CardTitle"]))
    story.append(format_as_bullets(safe(s.get("dumaguete_detailed"), "No Data.")))
    story.append(Spacer(1, 20))

    # --- TYPHOON TRACK (CONDITIONAL) ---
    track_img_path = out_dir / "typhoon_track.png"
    if track_img_path.exists():
        # Create a list for the kept-together content
        typhoon_section = []
        typhoon_section.extend(build_section_header("TROPICAL CYCLONE MONITORING"))
        typhoon_section.append(Paragraph("Latest forecast track from PAGASA.", S["Subtitle"]))
        
        # Load and resize keeping aspect ratio
        try:
            track_img = Image(str(track_img_path))
            
            # Constrain dimensions to fit better (Max W: 450, Max H: 300)
            max_w = 450
            max_h = 300
            
            # Calculate aspect ratio
            aspect = track_img.imageHeight / float(track_img.imageWidth)
            
            # Tentative width based on max_w
            new_w = max_w
            new_h = new_w * aspect
            
            # If height exceeds max_h, scale down by height instead
            if new_h > max_h:
                new_h = max_h
                new_w = new_h / aspect

            track_img.drawWidth = new_w
            track_img.drawHeight = new_h
            
            track_img.hAlign = 'CENTER'
            
            typhoon_section.append(track_img)
            typhoon_section.append(Spacer(1, 20))
            
            # Append as a single atomic block
            story.append(KeepTogether(typhoon_section))

        except Exception as e:
            print(f"⚠️ Error loading typhoon track image: {e}")

    # --- FORECASTS (TABLE) ---
    story.extend(build_section_header("10-DAY PROBABILISTIC FORECAST"))
    story.append(Paragraph("Full data forecast for valid upcoming period.", S["Subtitle"]))
    
    acc = data.get("forecast_10day", {}).get("accuweather", {})
    if "metro_manila" in acc:
        story.append(Paragraph("Metro Manila", S["CardTitle"]))
        story.append(build_forecast_table(acc["metro_manila"]))
        story.append(Spacer(1, 10))
    if "dumaguete" in acc:
        story.append(Paragraph("Dumaguete City", S["CardTitle"]))
        story.append(build_forecast_table(acc["dumaguete"]))
    
    story.append(Spacer(1, 20))

    # --- IMPACT & ACTIVE ADVISORIES ---
    story.extend(build_section_header("ACTIVE ALERTS & SITE IMPACT"))
    
    impacts = data.get("site_impact_summary", {})
    advisories = data.get("active_pagasa_advisories", {})
    
    def process_site_alerts(site_key, site_label):
        lines = []
        # Impact
        imp = impacts.get(site_key, {})
        lvl = safe(imp.get("impact_level")).upper()
        if "HIGH" in lvl or "DANGER" in lvl: col = COL_RED_ALRT
        elif "MEDIUM" in lvl or "MOD" in lvl: col = COL_AMB_WARN
        else: col = COL_TXT_SLATE
        
        lines.append(Paragraph(f"{site_label} IMPACT: <b>{lvl}</b>", 
                               ParagraphStyle("Imp", parent=S["Normal"], textColor=col)))
        
        # Pagasa Alerts (Full text)
        for cat in ["rainfall_warning", "thunderstorm_warning"]:
            w = advisories.get(cat, {}).get(site_key, {})
            title = safe(w.get("title"))
            summary = safe(w.get("summary"))
            
            if "no active" not in title.lower() and "no heavy" not in title.lower() and title != "-":
                lines.append(Spacer(1, 4))
                lines.append(Paragraph(f"• {cat.replace('_',' ').title()}: <b>{title}</b>", S["AlertRed"]))
                lines.append(Paragraph(f"  {summary}", S["Normal"]))
        
        return lines

    mnl_alerts = [Paragraph("METRO MANILA", S["CardTitle"])] + process_site_alerts("metro_manila", "NCR")
    dgt_alerts = [Paragraph("DUMAGUETE", S["CardTitle"])] + process_site_alerts("dumaguete", "DGT")
    
    story.append(Table([[mnl_alerts, Spacer(20,20), dgt_alerts]], 
                       colWidths=[240, 20, 240], 
                       style=[('VALIGN', (0,0), (-1,-1), 'TOP')]))

    # --- RECOMMENDATIONS ---
    # Double line is now part of the section header function
    story.extend(build_section_header("OPERATIONAL RECOMMENDATIONS"))
    recs = data.get("operational_recommendations", {})
    
    def render_rec_list(rec_list):
        items = []
        if isinstance(rec_list, str): rec_list = [rec_list] # Handle edge case if string
        for r in rec_list:
            text = r.strip()
            if not text: continue
            # Add bullet if missing
            if not text.startswith("•") and not text.startswith("-"):
                text = f"• {text}"
            items.append(Paragraph(text, S["Normal"]))
            items.append(Spacer(1, 6)) # Spacing between items
        return items

    if recs.get("metro_manila"):
        story.append(Paragraph("Metro Manila", S["CardTitle"]))
        story.extend(render_rec_list(recs["metro_manila"]))
        
    if recs.get("dumaguete"):
        story.append(Paragraph("Dumaguete", S["CardTitle"]))
        story.extend(render_rec_list(recs["dumaguete"]))

    # Closing Divider
    story.append(Spacer(1, 15))
    dbl_line = Table([[""]], colWidths=[500], rowHeights=[3])
    dbl_line.setStyle(TableStyle([
        ('LINEABOVE', (0,0), (-1,-1), 0.5, colors.gray), 
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.gray),
    ]))
    story.append(dbl_line)

    # --- FOOTER ---
    # Centered Professional Footer
    # "Generated on February 03, 2026 09:29 AM · by Project AWRA (Automated Weather Report Analytics) ® Jan Vincent Chioco"
    
    timestamp = get_ph_time().strftime("%B %d, %Y %I:%M %p")
    footer_text = f"Generated on {timestamp} · by Project AWRA (Automated Weather Report Analytics) ® Jan Vincent Chioco"
    
    story.append(Spacer(1, 40))
    story.append(Paragraph(footer_text, ParagraphStyle("FooterNew", parent=S["Footer"], alignment=1, fontSize=7, textColor=colors.gray)))

    # BUILD
    output_pdf_path = out_dir / OUTPUT_PDF_NAME
    doc = SimpleDocTemplate(
        str(output_pdf_path),
        pagesize=letter,
        leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36
    )
    doc.build(story)

if __name__ == "__main__":
    render_pdf(load_json())
    print("✅ PDF generated (Detailed + Visuals):", get_today_output_folder() / OUTPUT_PDF_NAME)
