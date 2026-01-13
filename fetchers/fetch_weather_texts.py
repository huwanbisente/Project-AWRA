# save as extract_weather_texts_with_toggle.py
import os
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

# ---------------------------
# WEATHER TEXT TARGETS (with optional toggle_xpath)
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
        # Filter for text sources that are NOT accuweather
        WEATHER_TARGETS = [
            t for t in config.get("text_sources", [])
            if "accuweather" not in t["name"]
        ]
except Exception as e:
    print(f"❌ Error loading config: {e}")
    WEATHER_TARGETS = []


# ---------------------------
# MAIN EXTRACTION FUNCTION (with toggles)
# ---------------------------

def extract_weather_texts(targets, headless=True, timeout_ms=15000):
    # Create output folder named data/output-YYYY-MM-DD
    today = datetime.now().strftime("%Y-%m-%d")
    base_dir = Path(__file__).resolve().parent.parent
    output_folder = base_dir / "data" / f"output-{today}"
    os.makedirs(output_folder, exist_ok=True)

    print(f"\nWeather text files will be saved to: {output_folder}\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context()
        page = context.new_page()

        for tgt in targets:

            name = tgt["name"]
            url = tgt["url"]
            
            # Skip if no xpath/toggle (e.g. public forecast handled separately)
            if "xpath" not in tgt:
                continue
                
            xpath = tgt["xpath"]
            filename = tgt["filename"]
            toggle_xpath = tgt.get("toggle_xpath")  # may be None

            save_path = os.path.join(output_folder, filename)

            print(f"--- Extracting {name.replace('_', ' ').upper()} ---")
            print(f"URL: {url}")

            # Load page
            try:
                page.goto(url, wait_until="networkidle", timeout=timeout_ms)
            except Exception as e:
                print(f"ERROR — Could not load {url}\n{e}\n")
                continue

            # If a toggle is required, click it first
            if toggle_xpath:
                try:
                    print(f"Clicking toggle (xpath): {toggle_xpath}")
                    # wait for toggle to be visible, then click
                    page.wait_for_selector(f'xpath={toggle_xpath}', timeout=8000)
                    toggle_locator = page.locator(f'xpath={toggle_xpath}')
                    # sometimes clickable element is small - use scroll_into_view and click
                    try:
                        toggle_locator.scroll_into_view_if_needed(timeout=2000)
                    except Exception:
                        pass
                    toggle_locator.click()
                    # short wait to allow the tab content to render
                    page.wait_for_timeout(600)  # 600 ms
                except PWTimeout:
                    print(f"WARNING — Toggle not found (xpath) for {name}; continuing without toggle.")
                except Exception as e:
                    print(f"WARNING — Clicking toggle failed for {name}: {e}")

            # Wait for XPath element (the actual content) to appear after toggle/click
            try:
                page.wait_for_selector(f'xpath={xpath}', timeout=10000)
            except PWTimeout:
                print(f"ERROR — XPath not found for {name}\n")
                continue

            # Extract text
            try:
                locator = page.locator(f'xpath={xpath}')

                # Try inner_text first, fallback to text_content
                try:
                    text = locator.inner_text()
                except Exception:
                    text = locator.text_content() or ""

                text = (text or "").strip()

                with open(save_path, "w", encoding="utf-8") as f:
                    f.write(text)

                print(f"SUCCESS — Saved → {save_path}\n")

            except Exception as e:
                print(f"ERROR — Failed to extract/save for {name}\n{e}\n")

        
    # ---------------------------------------------------------
    # 3. PUBLIC FORECAST (LPA Extraction Fix)
    # The PDF is image-based, so we scrape the text directly from the site.
    # ---------------------------------------------------------
        path_pf = output_folder / "public_forecast.txt"
        print("\n--- Scrape PUBLIC FORECAST Text ---")
        url_pf = "https://www.pagasa.dost.gov.ph/weather" # Main weather page usually has the synopsis
        
        try:
            print(f"Navigating to {url_pf}...")
            page.goto(url_pf, wait_until="networkidle", timeout=30000)
            
            # The daily forecast is usually in a tab or specific section.
            # Section title: "Daily Weather Forecast"
            # Content id: "daily-weather-forecast" or similar.
            # Let's grab the entire text of the tab-content if possible or specific container.
            # Based on typical PAGASA site structure:
            
            # Wait for content to load (optional)
            try:
                page.wait_for_selector(".tab-content", timeout=5000)
            except:
                print("Selector .tab-content not found or timed out. Proceeding to fallback.")
            
            # Try to extracting the synopsis/forecast text
            # Usually inside id="daily-forecast" or checking for text "Synopsis"
            
            content = ""
            
            # Strategy 1: Look for "Synopsis" and "Forecast" headers
            try:
                selector = ".tab-pane.active" 
                content = page.locator(selector).inner_text()
            except:
                pass # Initial attempt failed

            if not content:
                print("Specific selectors failed. Dumping 'body' text...")
                try:
                    content = page.inner_text("body")
                except:
                    pass

            if content and len(content) > 50:
                path_pf.write_text(content, encoding="utf-8")
                print(f"SUCCESS — Scraped Public Forecast Text → {path_pf}")
            else:
                print("WARNING — Extracted text seems empty or too short.")
                
        except Exception as e:
            print(f"ERROR scraping Public Forecast: {e}")

        context.close()
        browser.close()


# ---------------------------
# RUN SCRIPT
# ---------------------------

if __name__ == "__main__":
    extract_weather_texts(WEATHER_TARGETS, headless=True)
