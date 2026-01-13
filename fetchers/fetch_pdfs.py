import os
from datetime import datetime
from playwright.sync_api import (
    sync_playwright,
    TimeoutError as PWTimeout,
)

# ---------------------------
# PDF TARGETS
# ---------------------------

import json
from pathlib import Path

# ---------------------------
# LOAD TARGETS FROM CONFIG
# ---------------------------
# We are in src2/fetchers/. Config is in src2/config/.
BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config" / "sources.json"

try:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)
        PDF_TARGETS = config.get("pdfs", [])
except Exception as e:
    print(f"❌ Error loading config: {e}")
    PDF_TARGETS = []


# ---------------------------
# MAIN PDF DOWNLOAD FUNCTION
# ---------------------------
def download_all_pdfs(targets, headless=True, timeout_ms=15000):
    # Create one folder: output-YYYY-MM-DD
    today = datetime.now().strftime("%Y-%m-%d")
    # UPDATED: Save to src2/data/output-YYYY-MM-DD
    # We are in src2/fetchers/. Parent is src2/.
    base_dir = Path(__file__).resolve().parent.parent 
    output_folder = base_dir / "data" / f"output-{today}"
    os.makedirs(output_folder, exist_ok=True)

    print(f"\nPDF downloads will be saved to: {output_folder}\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        for tgt in targets:
            name = tgt["name"]
            url = tgt["url"]
            selector = tgt["selector"]
            filename = tgt["filename"]

            save_path = os.path.join(output_folder, filename)

            print(f"--- Downloading PDF for {name.upper()} ---")
            print(f"URL: {url}")

            # CASE A: Direct Download (No Selector)
            if not selector:
                print("Direct PDF link detected (no selector).")
                try:
                    # Expect download to start upon navigation
                    with page.expect_download(timeout=timeout_ms) as dl_info:
                        # We use execute_script or goto. goto might raise "Download is starting" error but that's fine if we catch it or if expect_download catches it?
                        # Actually, safe way is to wrap goto.
                        try:
                            page.goto(url, timeout=timeout_ms)
                        except Exception as e:
                            # If it says "Download is starting", that's good!
                            if "Download is starting" not in str(e):
                                print(f"Warning during goto: {e}")
                    
                    download = dl_info.value
                    download.save_as(save_path)
                    print(f"SUCCESS: Direct PDF saved → {save_path}\n")
                    continue
                except Exception as e:
                    print(f"ERROR: Direct download failed for {name}\n{e}\n")
                    continue

            # 2. DUMA (Visayas)
            # This is a special case that doesn't fit the generic target structure well.
            # It's hardcoded here for now.
            if name == "5DAY_PDF_DUMA":
                try:
                    print(f"\n--- Downloading PDF for 5DAY_PDF_DUMA ---")
                    print(f"URL: {url}")
                    
                    page.goto(url, timeout=60000)
                    
                    # Try specific selector first
                    # Updated selector based on recent inspection (approximate)
                    # Or just look for specific text
                    
                    output_path = output_folder / "5day_duma.pdf"
                    
                    try:
                        # Try finding the link by text first - often more robust
                        with page.expect_download(timeout=15000) as download_info:
                            # Look for link containing "Five-Day Regional" or similar, or just click the first PDF link in the content area
                            # The visual selector was: .outlook-container > div > a
                            page.locator(".outlook-container a").first.click()
                            
                        download = download_info.value
                        download.save_as(output_path)
                        print(f"SUCCESS: PDF downloaded via generic container selector -> {output_path}")
                        continue # Move to next target if successful

                    except Exception as e_primary:
                        print(f"Primary selector failed: {e_primary}. Trying fallback...")
                        
                        # Fallback 1: Text "Weather Outlook"
                        try:
                            with page.expect_download(timeout=10000) as download_info:
                                page.get_by_text("Weather Outlook").nth(0).click()
                            download = download_info.value
                            download.save_as(output_path)
                            print(f"SUCCESS: PDF downloaded via text fallback -> {output_path}")
                            continue
                        except:
                            pass

                        # Fallback 2: Any Link ending in .pdf
                        try:
                            print("Attempting to find ANY pdf link on page...")
                            # Evaluate js to find first pdf link
                            href = page.evaluate("""() => {
                                const anchors = Array.from(document.querySelectorAll('a'));
                                const pdf = anchors.find(a => a.href.toLowerCase().endsWith('.pdf'));
                                return pdf ? pdf.href : null;
                            }""")
                            
                            if href:
                                print(f"Found PDF link: {href}")
                                # Navigate directly to download (or click it)
                                # If we goto the pdf url, it might trigger download or view. 
                                # Better to click the element if possible, or use requests?
                                # Let's try page.goto for the pdf url, expecting download event?
                                
                                # Actually, just downloading via requests might be safer if we have cookies? 
                                # But let's try python requests since we have the URL now.
                                import requests
                                r = requests.get(href, verify=False, timeout=60)
                                if r.status_code == 200:
                                    output_path.write_bytes(r.content)
                                    print(f"SUCCESS: PDF downloaded via requests fallback -> {output_path}")
                                    continue
                        except Exception as e_any:
                            print(f"Fallback 2 failed: {e_any}")

                except Exception as e:
                    print(f"ERROR in DUMA fetching: {e}")
                continue

            # CASE B: Standard Page Load + Click Selector
            # Load the page
            try:
                page.goto(url, wait_until="networkidle", timeout=timeout_ms)
            except Exception as e:
                print(f"ERROR: Could not load {url}\n{e}\n")
                continue

            # Wait for download link
            try:
                page.wait_for_selector(selector, timeout=8000)
            except PWTimeout:
                print(f"ERROR: Download link {selector} not found for {name}\n")
                continue

            link = page.locator(selector)

            # Try normal download via click
            try:
                with page.expect_download(timeout=12000) as dl_info:
                    link.click()
                download = dl_info.value
                download.save_as(save_path)

                print(f"SUCCESS: PDF downloaded via expect_download → {save_path}\n")
                continue  # ✔ successful, move to next target
            except Exception:
                print("Normal file download not triggered, using fallback fetch...\n")

            # Fallback: GET the PDF directly from its href
            try:
                href = link.get_attribute("href")
                if not href:
                    print(f"ERROR: Link has no href attribute for {name}\n")
                    continue

                # Resolve absolute URL
                absolute_url = page.evaluate(
                    "url => new URL(url, document.baseURI).toString()",
                    href,
                )

                print(f"Fetching PDF directly from: {absolute_url}")

                response = page.request.get(absolute_url, timeout=30000)

                if response.ok:
                    with open(save_path, "wb") as f:
                        f.write(response.body())
                    print(f"SUCCESS: Fallback PDF saved → {save_path}\n")
                else:
                    print(f"ERROR: Failed to fetch PDF ({response.status}) for {name}\n")

            except Exception as e:
                print(f"ERROR: Fallback PDF fetch failed for {name}\n{e}\n")

        context.close()
        browser.close()


# ---------------------------
# RUN SCRIPT
# ---------------------------
if __name__ == "__main__":
    download_all_pdfs(PDF_TARGETS, headless=True)
