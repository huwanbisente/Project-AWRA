
import os
import json
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from dotenv import load_dotenv

# --- CONFIG ---
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = BASE_DIR / 'service_account.json'

# Load Env
load_dotenv(BASE_DIR / ".env")
GDRIVE_FOLDER_ID = os.getenv("GDRIVE_FOLDER_ID")

def find_latest_data():
    """Finds the latest JSON and PDF."""
    if not DATA_DIR.exists(): return None, None
    folders = [d for d in DATA_DIR.iterdir() if d.is_dir() and d.name.startswith("output-")]
    if not folders: return None, None
    latest = max(folders, key=lambda d: d.stat().st_mtime)
    
    json_path = latest / "summary.json"
    
    # Find PDF (Prioritize the static 'weather_report.pdf')
    pdf_path = latest / "weather_report.pdf"
    if not pdf_path.exists():
        pdfs = list(latest.glob("*.pdf"))
        pdf_path = next((p for p in pdfs if "Summary" in p.name or "report" in p.name), None)
    
    # Find Typhoon Track
    track_path = latest / "typhoon_track.png"
    
    return json_path if json_path.exists() else None, pdf_path, track_path if track_path.exists() else None

def authenticate():
    """Authenticates using Service Account."""
    if not SERVICE_ACCOUNT_FILE.exists():
        print(f"⚠️ Service Account file not found at: {SERVICE_ACCOUNT_FILE}")
        print("   Please place your 'service_account.json' in the project root.")
        return None
    try:
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        return build('drive', 'v3', credentials=creds)
    except Exception as e:
        print(f"❌ Authentication Failed: {e}")
        return None

def upload_file(service, file_path, folder_id, mime_type):
    """Uploads a file. Updates if exists, creates if new."""
    file_name = file_path.name
    
    # 1. Search for existing file
    query = f"name = '{file_name}' and '{folder_id}' in parents and trashed = false"
    results = service.files().list(
        q=query, 
        spaces='drive', 
        fields='files(id, name)',
        supportsAllDrives=True,
        includeItemsFromAllDrives=True
    ).execute()
    files = results.get('files', [])
    
    media = MediaFileUpload(str(file_path), mimetype=mime_type, resumable=True)
    
    if files:
        # UPDATE existing
        file_id = files[0]['id']
        print(f"   🔄 Updating existing '{file_name}' (ID: {file_id})...")
        service.files().update(fileId=file_id, media_body=media, supportsAllDrives=True).execute()
        return file_id
    else:
        # CREATE new
        print(f"   🆕 Uploading new '{file_name}'...")
        file_metadata = {'name': file_name, 'parents': [folder_id]}
        # Note: supportsAllDrives allows service accounts to use the storage quota of the folder owner
        file = service.files().create(body=file_metadata, media_body=media, fields='id', supportsAllDrives=True).execute()
        return file.get('id')

def main():
    print("=== ☁️ GOOGLE DRIVE ULOADER ===")
    
    # 1. Check Data
    json_path, pdf_path, track_path = find_latest_data()
    if not json_path:
        print("❌ No data found to upload.")
        return

    print(f"📦 Found Data:")
    print(f"   - JSON: {json_path.name}")
    print(f"   - PDF:  {pdf_path.name if pdf_path else 'None'}")
    print(f"   - Track: {track_path.name if track_path else 'None'}")
    
    # 2. Check Folder Config
    if not GDRIVE_FOLDER_ID:
        print("❌ GDRIVE_FOLDER_ID not set in .env")
        print("   Please create a folder in Drive, get its ID, and add it to .env")
        return

    # 3. Auth
    service = authenticate()
    if not service:
        print("❌ Skipping upload due to missing credentials.")
        return

    # 4. Upload
    try:
        # Upload JSON
        json_id = upload_file(service, json_path, GDRIVE_FOLDER_ID, 'application/json')
        print(f"   ✅ JSON Uploaded! ID: {json_id}")
        
        # Upload PDF (if exists)
        if pdf_path:
            pdf_id = upload_file(service, pdf_path, GDRIVE_FOLDER_ID, 'application/pdf')
            print(f"   ✅ PDF Uploaded!  ID: {pdf_id}")
            
        # Upload Track Image (if exists)
        if track_path:
            track_id = upload_file(service, track_path, GDRIVE_FOLDER_ID, 'image/png')
            print(f"   ✅ Track Uploaded! ID: {track_id}")
            
        print("\n✨ Upload Sequence Complete!")
        
    except Exception as e:
        print(f"❌ Upload Error: {e}")

if __name__ == "__main__":
    main()
