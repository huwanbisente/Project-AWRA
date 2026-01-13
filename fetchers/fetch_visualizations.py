import os
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

# VIS → save as duma.png
VIS = {
    "name": "5day_viz_duma",
    "url": "https://www.pagasa.dost.gov.ph/regional-forecast/visprsd",
    "selector": "body > div.container-fluid.container-space > div.col-md-12.prsd-page > div > div:nth-child(1) > div > div:nth-child(3) > div.outlook-container"
}

# NCR → save as ncr.png
NCR = {
    "name": "5day_viz_ncr",
    "url": "https://www.pagasa.dost.gov.ph/regional-forecast/ncrprsd",
    "selector": "body > div.container-fluid.container-space > div.col-md-12.prsd-page > div > div:nth-child(1) > div > div:nth-child(3) > div.outlook-container"
}

TARGETS = [VIS, NCR]


def test_selector(targets, headless=False, timeout_ms=10000):

    # Create ONE folder: output-YYYY-MM-DD
    today = datetime.now().strftime("%Y-%m-%d")
    base_dir = Path(__file__).resolve().parent.parent
    output_folder = base_dir / "data" / f"output-{today}"
    os.makedirs(output_folder, exist_ok=True)

    print(f"\nSaving screenshots to: {output_folder}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()

        for tgt in targets:
            url = tgt["url"]
            selector = tgt["selector"]
            name = tgt["name"]                          # duma or ncr
            output_path = os.path.join(output_folder, f"{name}.png")

            print(f"\n-> Loading {name.upper()} page: {url}")

            try:
                page.goto(url, wait_until="networkidle", timeout=timeout_ms)
            except Exception as e:
                print(f"ERROR — Failed to load {url}: {e}")
                continue

            try:
                page.wait_for_selector(selector, timeout=timeout_ms)

                locator = page.locator(selector)

                # Scroll if needed
                try:
                    locator.scroll_into_view_if_needed(timeout=2000)
                except Exception:
                    pass

                # Screenshot element
                locator.screenshot(path=output_path)
                print(f"SUCCESS — Saved: {output_path}")

            except PWTimeout:
                print(f"FAILED — Selector not found within timeout on {url}")
            except Exception as e:
                print(f"ERROR — Screenshot failed for {url}: {e}")

        browser.close()


if __name__ == "__main__":
    test_selector(TARGETS, headless=False)
