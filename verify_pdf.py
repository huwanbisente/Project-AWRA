
import pdfplumber
import sys
from pathlib import Path

p = Path(r"f:\for PORTFOLIO\PROJECT AWRA\src2\data\output-2026-01-13\public_forecast.pdf")
print(f"Checking {p}...")

try:
    with pdfplumber.open(p) as pdf:
        print(f"Pages: {len(pdf.pages)}")
        full_text = ""
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            print(f"--- Page {i+1} ---")
            if text:
                print(text[:200])  # Print first 200 chars
                full_text += text
            else:
                print("[NO TEXT EXTRACTED]")
        
        if "LPA" in full_text or "Low Pressure Area" in full_text:
            print("\n✅ FOUND 'LPA' or 'Low Pressure Area' in text!")
        else:
            print("\n❌ 'LPA' / 'Low Pressure Area' NOT found in text.")
            
except Exception as e:
    print(f"Error reading PDF: {e}")
