
import pdfplumber
from pathlib import Path

# Fix path: resolve relative to this script (tests/ -> root -> data)
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

def find_latest_pdf():
    # Find all public_forecast.pdf files in subfolders
    pdfs = list(DATA_DIR.glob("output-*/public_forecast.pdf"))
    if not pdfs:
        print(f"No public_forecast.pdf found in {DATA_DIR}")
        return None
    # Sort by modification time
    return max(pdfs, key=lambda p: p.stat().st_mtime)

def debug_read_pdf():
    path = find_latest_pdf()
    if not path:
        return

    print(f"DEBUG: Reading {path}")
    try:
        with pdfplumber.open(path) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)
            print("--- EXTRACTED TEXT START ---")
            print(text[:1000]) # Preview first 1000 chars
            print("--- EXTRACTED TEXT END ---")
            
            if "LPA" in text or "Low Pressure Area" in text:
                print("FOUND: LPA/Low Pressure Area in text")
            else:
                print("MISSING: LPA/Low Pressure Area NOT found in text")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    debug_read_pdf()
