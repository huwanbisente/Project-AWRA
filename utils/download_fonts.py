import requests
from pathlib import Path

# Resolve assets directory relative to this script (assumes script is in utils/)
ASSETS_DIR = Path(__file__).parent.parent / "assets"
ASSETS_DIR.mkdir(exist_ok=True)

def download_font(url, filename):
    print(f"Downloading {filename}...")
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            (ASSETS_DIR / filename).write_bytes(r.content)
            print(f"✅ Saved {filename}")
        else:
            print(f"❌ Failed {filename}: {r.status_code}")
    except Exception as e:
        print(f"❌ Error {filename}: {e}")

if __name__ == "__main__":
    download_font("https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Regular.ttf", "Roboto-Regular.ttf")
    download_font("https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Bold.ttf", "Roboto-Bold.ttf")
