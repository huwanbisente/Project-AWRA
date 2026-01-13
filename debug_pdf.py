
import pdfplumber
from pathlib import Path

path = Path('data/output-2026-01-13/public_forecast.pdf')
try:
    with pdfplumber.open(path) as pdf:
        text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        print("--- EXTRACTED TEXT START ---")
        print(text)
        print("--- EXTRACTED TEXT END ---")
        
        if "LPA" in text or "Low Pressure Area" in text:
            print("FOUND: LPA/Low Pressure Area in text")
        else:
            print("MISSING: LPA/Low Pressure Area NOT found in text")
except Exception as e:
    print(f"ERROR: {e}")
