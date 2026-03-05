#!/usr/bin/env python3
"""
FETCHER: TYPHOON TRACK FROM PAGASA
Scrapes bagong.pagasa.dost.gov.ph for an active cyclone track image.
"""

import requests
import re
import shutil
import sys
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime

# =========================
# CONFIG
# =========================
PAGASA_BULLETIN_URL = "https://bagong.pagasa.dost.gov.ph/tropical-cyclone/severe-weather-bulletin"
OUTPUT_FILENAME = "typhoon_track.png"

import sys
# Add project root to sys.path
base_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(base_dir))

from utils.ph_time import get_ph_date_str

# =========================
# PATH RESOLUTION
# =========================
def get_today_output_folder():
    base_dir = Path(__file__).resolve().parent.parent # core -> root
    today = get_ph_date_str()
    folder = base_dir / "data" / f"output-{today}"
    folder.mkdir(parents=True, exist_ok=True)
    return folder

# =========================
# MAIN
# =========================
def main():
    print("🌀 Checking for Active Typhoon Track...")
    
    try:
        # 1. Fetch Page
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        resp = requests.get(PAGASA_BULLETIN_URL, headers=headers, timeout=15)
        
        if resp.status_code != 200:
            print(f"⚠️ Could not access PAGASA site (Status {resp.status_code}).")
            return

        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # 2. Check content
        # PAGASA often says "There is no active tropical cyclone" in text
        text_content = soup.get_text().lower()
        if "no active tropical cyclone" in text_content:
            print("✅ No active tropical cyclone found.")
            return

        # 3. Search for Track Image
        # Strategy: Look for images with 'track' in src or alt, or inside specific containers
        candidates = []
        
        # Method A: Look for images in the cyclone-info container
        # Note: Class names might change, so checking all images first is safer
        imgs = soup.find_all('img')
        
        for img in imgs:
            src = img.get('src', '')
            alt = img.get('alt', '')
            
            # Filter logic
            if "track" in src.lower() or "track" in alt.lower():
                # Usually standard tracks are PNG/JPG
                if src.lower().endswith('.png') or src.lower().endswith('.jpg') or src.lower().endswith('.jpeg'):
                    candidates.append(src)
        
        target_url = None
        if candidates:
            # Pick the most likely one (e.g. pubfiles)
            # PAGASA tracks often hosted on pubfiles.pagasa.dost.gov.ph
            print(f"🔎 Found {len(candidates)} candidate images.")
            
            for c in candidates:
                if "pubfiles" in c:
                    target_url = c
                    break
            
            # Fallback to first if no pubfiles match
            if not target_url:
                target_url = candidates[0]
        
        if not target_url:
            print("⚠️ Active cyclone might exist, but no track image found in predictable format.")
            return

        print(f"🎯 Target Image: {target_url}")
        
        # 4. Download Image
        # Handle relative URLs
        if not target_url.startswith("http"):
            # PAGASA base url
            target_url = "https://bagong.pagasa.dost.gov.ph" + target_url

        img_resp = requests.get(target_url, headers=headers, stream=True, timeout=15)
        if img_resp.status_code == 200:
            out_folder = get_today_output_folder()
            out_path = out_folder / OUTPUT_FILENAME
            
            with open(out_path, 'wb') as f:
                img_resp.raw.decode_content = True
                shutil.copyfileobj(img_resp.raw, f)
            
            print(f"✅ Typhoon Track saved to: {out_path}")
        else:
            print(f"❌ Failed to download image (Status {img_resp.status_code})")

    except Exception as e:
        print(f"❌ Error fetching typhoon track: {e}")

if __name__ == "__main__":
    main()
