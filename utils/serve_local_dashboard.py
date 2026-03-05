
import http.server
import socketserver
import os
import shutil
import webbrowser
from pathlib import Path
import time
import threading

PORT = 8000
BASE_DIR = Path(__file__).resolve().parent.parent
WEBAPP_DIR = BASE_DIR / "webapp"
DATA_DIR = BASE_DIR / "data"

def find_latest_summary_json():
    """Finds the summary.json file in the most recent output folder."""
    if not DATA_DIR.exists():
        print("❌ Data directory not found.")
        return None
        
    # Get all output folders
    folders = [d for d in DATA_DIR.iterdir() if d.is_dir() and d.name.startswith("output-")]
    if not folders:
        print("❌ No output folders found in data/.")
        return None
        
    # Sort by modification time (newest first)
    latest_folder = max(folders, key=lambda d: d.stat().st_mtime)
    summary_path = latest_folder / "summary.json"
    
    if not summary_path.exists():
        print(f"❌ summary.json not found in {latest_folder}")
        return None
        
    print(f"✅ Found latest data: {summary_path}")
    return summary_path

def setup_webapp_data():
    """Copies the latest summary.json to the webapp folder for the server."""
    source = find_latest_summary_json()
    if not source:
        return False
        
    dest = WEBAPP_DIR / "summary.json"
    try:
        shutil.copy2(source, dest)
        print(f"✅ Copied data to {dest}")
        # Also copy the PDF for the download link if it exists
        pdf_source = source.parent / "weather_report.pdf"
        # The PDF naming might vary, let's check the folder content or use a standard name
        # generate_summary.py doesn't rename the PDF, render_report.py does.
        # Let's just look for *any* PDF in that folder that looks like a report
        pdfs = list(source.parent.glob("*.pdf"))
        # Prefer "Summary..." or "weather_report"
        report_pdf = next((p for p in pdfs if "Summary" in p.name or "report" in p.name), None)
        
        if report_pdf:
            shutil.copy2(report_pdf, WEBAPP_DIR / "weather_report.pdf")
            print(f"✅ Copied report PDF: {report_pdf.name}")
        
        return True
    except Exception as e:
        print(f"❌ Error copying data: {e}")
        return False

def start_server():
    """Starts the HTTP server from the webapp directory."""
    os.chdir(WEBAPP_DIR)
    
    handler = http.server.SimpleHTTPRequestHandler
    
    # Allow reuse of address to prevent "Port already in use" errors during quick restarts
    socketserver.TCPServer.allow_reuse_address = True
    
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"\n🚀 Server started at http://localhost:{PORT}")
        print(f"👉 Dashboard: http://localhost:{PORT}/dashboard_mockup.html")
        print("⌨️  Press Ctrl+C to stop.")
        
        # Open in browser slightly after start
        threading.Timer(1.5, lambda: webbrowser.open(f"http://localhost:{PORT}/dashboard_mockup.html")).start()
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped.")
            httpd.shutdown()

if __name__ == "__main__":
    print("=== 🛠️ DASHBOARD LOCAL TEST SERVER ===")
    if setup_webapp_data():
        start_server()
    else:
        print("❌ Could not proceed. Please generate data first using the pipeline.")
