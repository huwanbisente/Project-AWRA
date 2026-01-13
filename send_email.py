#!/usr/bin/env python3
"""
Daily Weather Email Sender
- TEST / LIVE mode selector
- Correct recipient lists
- HTML email + PDF attachment
- Signature image embedded
"""

# =========================
# IMPORTS
# =========================
import json
import smtplib
import os
import sys
from datetime import datetime
from email.message import EmailMessage
import tkinter as tk
from tkinter import messagebox


# =========================
# MODE SELECTION POPUP
# =========================
def select_mode():
    root = tk.Tk()
    root.title("Send Weather Email")
    root.geometry("360x160")
    root.resizable(False, False)

    mode = {"value": None}

    def choose_test():
        mode["value"] = "TEST"
        root.destroy()

    def choose_live():
        confirm = messagebox.askyesno(
            "Confirm Live Send",
            "This will send the email to the FULL mailing list.\n\nProceed?"
        )
        if confirm:
            mode["value"] = "LIVE"
            root.destroy()

    tk.Label(
        root,
        text="Select Email Mode",
        font=("Arial", 12, "bold")
    ).pack(pady=12)

    tk.Button(
        root,
        text="Test Mode (Audit First)",
        width=28,
        command=choose_test
    ).pack(pady=5)

    tk.Button(
        root,
        text="Live Mode (Send to Mailing List)",
        width=28,
        fg="red",
        command=choose_live
    ).pack(pady=5)

    root.mainloop()
    return mode["value"]


MODE = select_mode()

if MODE is None:
    print("❌ No mode selected. Exiting.")
    sys.exit(0)

TEST_MODE = MODE == "TEST"


# =========================
# HELPERS
# =========================
def normalize_text(val):
    if isinstance(val, str):
        val = val.strip()
        if val.lower() in ["none", "none issued"]:
            return ""
        return val
    return ""


def flatten_dict(val):
    if not isinstance(val, dict):
        return ""
    parts = []
    for v in val.values():
        if isinstance(v, str) and v.lower() not in ["none", "none issued"]:
            parts.append(v.strip())
    return " ".join(parts)


def is_critical_system(text):
    keywords = ["tropical", "depression", "storm", "typhoon", "cyclone"]
    return any(k in text.lower() for k in keywords)


def attach_pdf(msg, pdf_path):
    if not os.path.exists(pdf_path):
        print(f"⚠️ PDF not found: {pdf_path}")
        return

    with open(pdf_path, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="application",
            subtype="pdf",
            filename=os.path.basename(pdf_path)
        )


def attach_signature_image(msg, image_path):
    if not os.path.exists(image_path):
        print(f"⚠️ Signature image not found: {image_path}")
        return

    with open(image_path, "rb") as img:
        msg.get_payload()[-1].add_related(
            img.read(),
            maintype="image",
            subtype="jpeg",
            cid="signature_img"
        )


# =========================
# EMAIL GENERATOR
# =========================
def generate_weather_email(json_path):
    # Locate daily folder
    today = datetime.now().strftime("%Y-%m-%d")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    daily_folder = os.path.join(base_dir, "data", f"output-{today}")
    
    # Path to summary.json
    full_json_path = os.path.join(daily_folder, json_path)
    
    with open(full_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    date_str = data.get("summary_of_current_conditions", {}).get(
        "date", datetime.now().strftime("%B %d, %Y")
    )
    date_for_filename = datetime.strptime(date_str, "%B %d, %Y").strftime("%Y-%m-%d")

    subject = f"Weather Update – {date_str} (Manila & Dumaguete)"
    if TEST_MODE:
        subject = f"[TEST] {subject}"

    system = normalize_text(
        data.get("summary_of_current_conditions", {}).get("system_in_effect")
    ) or "No active tropical cyclone affecting either site."

    system_html = f"<b>{system}</b>" if is_critical_system(system) else system

    current = data.get("current_conditions", {})

    metro_manila = (
        normalize_text(current.get("metro_manila"))
        or flatten_dict(current.get("metro_manila"))
        or "Generally stable weather conditions."
    )

    dumaguete = (
        normalize_text(current.get("dumaguete"))
        or flatten_dict(current.get("dumaguete"))
        or "Generally stable weather conditions."
    )

    bullets = [
        f"<li>{system_html}</li>",
        f"<li><b>Metro Manila:</b> {metro_manila}</li>",
        f"<li><b>Dumaguete / Visayas:</b> {dumaguete}</li>",
    ]

    html_body = f"""
    <html>
    <body style="font-family: Arial; font-size: 13px;">
        <p>Dear Team,</p>

        <p>
            Please see below the <b>weather summary for today, {date_str}</b>
            based on the latest PAGASA and AccuWeather updates.
        </p>

        <ul>
            {''.join(bullets)}
        </ul>

        <p>We will continue to monitor and share updates if conditions change.</p>

        <p>
            Best regards,<br>
            <b>Jan Vincent Chioco</b>
        </p>

        <br>
        <img src="cid:signature_img" style="max-width:400px;">
    </body>
    </html>
    """

    pdf_filename = f"Summary_of_Current_Conditions_{date_for_filename}.pdf"
    full_pdf_path = os.path.join(daily_folder, pdf_filename)
    
    return subject, html_body, full_pdf_path


# =========================
# EMAIL SENDER
# =========================
msg = EmailMessage()
msg["From"] = "jan.chioco@ececontactcenters.com"

if TEST_MODE:
    to_recipients = [
        "jvchioco3@gmail.com",
        "jvchioco.p1@gmail.com",
    ]
    cc_recipients = [
        "huwanbisente@gmail.com",
        "chioco.jv@gmail.com",
    ]
    print("🧪 TEST MODE")

else:
    to_recipients = [
        "ece_managers@ececontactcenters.com",
        "ece_seniorteamleaders@ececontactcenters.com",
    ]
    cc_recipients = [
        "hr@ececontactcenters.com",
        "eceadmin@ececontactcenters.com",
        "workforcertaleaders@ececontactcenters.com",
        "michael@ececontactcenters.com",
        "jennifer@ececontactcenters.com",
        "chris@ececontactcenters.com",
        "marta@ececontactcenters.com",
        "jeremiah@ececontactcenters.com",
        "akespino@ececontactcenters.com",
        "chelsea@ececontactcenters.com",
        "breana@ececontactcenters.com",
        "jan.chioco@ececontactcenters.com",
        "salcedo@ececontactcenters.com",
        "suzanne@ececontactcenters.com",
    ]
    print("🚀 LIVE MODE")

msg["To"] = ", ".join(to_recipients)
msg["Cc"] = ", ".join(cc_recipients)

subject, html_body, full_pdf_path = generate_weather_email("summary.json")

msg["Subject"] = subject
msg.add_alternative(html_body, subtype="html")

attach_signature_image(msg, "assets/jv_signature.jpg")
# Use the full path we got from the function
attach_pdf(msg, full_pdf_path)

all_recipients = to_recipients + cc_recipients

# Load env vars
from dotenv import load_dotenv
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
    server.login("jan.chioco@ececontactcenters.com", EMAIL_PASSWORD)
    server.send_message(msg, to_addrs=all_recipients)

print("✅ Email sent successfully")
