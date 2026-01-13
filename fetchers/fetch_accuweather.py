# cuweather_txt_dual.py
import os
import sys
import time
from datetime import datetime
import requests
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

# ---------------------------
# TARGETS
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
        # Filter for text sources that ARE accuweather
        TARGETS = [
            t for t in config.get("text_sources", [])
            if "accuweather" in t["name"]
        ]
except Exception as e:
    print(f"❌ Error loading config: {e}")
    TARGETS = []

# Default selector fallback if not in config (though it is in our config)
DEFAULT_SELECTOR = (
    "body > div > div.two-column-page-content > div.page-column-1 > "
    "div.page-content.content-module > div.daily-list.content-module"
)

VIEWPORT = {"width": 1200, "height": 1400}
NAV_TIMEOUT = 20000
LOCATOR_TIMEOUT = 12000
HEADLESS_DEFAULT = True

CLICK_TEXTS = ["Accept", "I Accept", "Agree", "Close", "Got it", "OK"]

HIDE_TOP_JS = """
(()=> {
  document.querySelectorAll('*').forEach(el => {
    try {
      const s = window.getComputedStyle(el);
      if ((s.position === 'fixed' || s.position === 'sticky')) {
        const r = el.getBoundingClientRect();
        if (r.top >= -10 && r.top <= 140 && r.width > 40 && r.height > 10)
          el.style.display = 'none';
      }
    } catch(e){}
  });
})();
"""


def make_output_path(filename):
    today = datetime.now().strftime("%Y-%m-%d")
    base_dir = Path(__file__).resolve().parent.parent
    folder = base_dir / "data" / f"output-{today}"
    os.makedirs(folder, exist_ok=True)
    return folder / filename


def try_extract_from_page(page, selector):
    page.wait_for_timeout(700)

    # click overlays
    for t in CLICK_TEXTS:
        try:
            btns = page.locator(f"button:has-text('{t}')")
            if btns.count() > 0:
                btns.nth(0).click(timeout=1500)
                page.wait_for_timeout(400)
        except:
            pass

    # hide sticky headers
    try:
        page.evaluate(HIDE_TOP_JS)
    except:
        pass

    # wait for forecast div
    try:
        page.wait_for_selector(selector, timeout=LOCATOR_TIMEOUT)
    except PWTimeout:
        print("Selector not found after navigation.")
        return None

    locator = page.locator(selector)

    try:
        return locator.inner_text().strip()
    except:
        return (locator.text_content() or "").strip()


def fetch_via_requests(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    try:
        r = requests.get(url, headers=headers, timeout=30)
        if r.status_code == 200 and r.text:
            return r.text
    except:
        pass
    return None


def extract_one_location(playwright, url, selector, output_filename, headless=True):
    out_path = make_output_path(output_filename)
    print(f"\n=== Extracting {output_filename} ===")
    print("Saving to:", out_path)

    # A) chromium normal / retries
    try:
        browser = playwright.chromium.launch(headless=headless, args=["--disable-http2"])
        context = browser.new_context(viewport=VIEWPORT)
        page = context.new_page()

        for label in ["networkidle", "domcontentloaded"]:
            try:
                print(f"Attempt A: goto({label}) ...")
                page.goto(url, wait_until=label, timeout=NAV_TIMEOUT)
                text = try_extract_from_page(page, selector)
                if text:
                    with open(out_path, "w", encoding="utf-8") as f:
                        f.write(text)
                    print("SUCCESS — Text extracted.")
                    context.close(); browser.close(); return
            except Exception as e:
                print("Navigation error:", e)

    except Exception as e:
        print("Chromium startup error:", e)
    finally:
        try:
            context.close(); browser.close()
        except:
            pass

    # B) chrome + spoof UA + non-headless
    try:
        print("\nAttempt B: Chromium non-headless with spoofed UA...")
        browser = playwright.chromium.launch(headless=False, args=["--disable-http2"])
        ua = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
              "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

        context = browser.new_context(ignore_https_errors=True, user_agent=ua, viewport=VIEWPORT)
        page = context.new_page()

        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        text = try_extract_from_page(page, selector)
        if text:
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(text)
            print("SUCCESS — Text extracted (spoofed).")
            context.close(); browser.close(); return

    except Exception as e:
        print("Attempt B error:", e)
    finally:
        try:
            context.close(); browser.close()
        except:
            pass

    # C) firefox
    try:
        print("\nAttempt C: Firefox engine...")
        browser = playwright.firefox.launch(headless=headless)
        context = browser.new_context(viewport=VIEWPORT)
        page = context.new_page()

        page.goto(url, wait_until="domcontentloaded", timeout=25000)
        text = try_extract_from_page(page, selector)

        if text:
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(text)
            print("SUCCESS — Text extracted (Firefox).")
            context.close(); browser.close(); return

    except Exception as e:
        print("Attempt C error:", e)
    finally:
        try:
            context.close(); browser.close()
        except:
            pass

    # D) requests -> set_content
    print("\nAttempt D: requests -> set_content fallback...")
    html = fetch_via_requests(url)
    if html:
        try:
            browser = playwright.chromium.launch(headless=True, args=["--disable-http2"])
            context = browser.new_context(viewport=VIEWPORT)
            page = context.new_page()

            page.set_content(html, timeout=30000)
            page.wait_for_timeout(700)

            text = try_extract_from_page(page, selector)
            if text:
                with open(out_path, "w", encoding="utf-8") as f:
                    f.write(text)
                print("SUCCESS — Text extracted (fallback).")
                context.close(); browser.close(); return
        except Exception as e:
            print("Fallback error:", e)
        finally:
            try:
                context.close(); browser.close()
            except:
                pass

    print("FAILED — Could not extract text for:", output_filename)


def main():
    debug = "--debug" in sys.argv
    headless_flag = False if debug else HEADLESS_DEFAULT

    with sync_playwright() as p:
        for t in TARGETS:
            # Use specific selector from config if available, else default
            target_selector = t.get("selector", DEFAULT_SELECTOR)
            
            # Ensure filename has .txt extension (config has it, but good to be safe)
            fname = t["filename"] if "filename" in t else t["name"]
            
            extract_one_location(
                playwright=p,
                url=t["url"],
                selector=target_selector,
                output_filename=fname,
                headless=headless_flag,
            )


if __name__ == "__main__":
    main()
