from playwright.sync_api import sync_playwright

def check_pagasa():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        url = "https://www.pagasa.dost.gov.ph/weather#daily-weather-forecast"
        print(f"Navigating to {url}...")
        page.goto(url, timeout=60000)
        
        try:
            # wait for tab content
            page.wait_for_selector(".tab-content", timeout=10000)
            print("Found .tab-content")
        except:
            print("Timeout waiting for .tab-content")

        # Check what is active
        try:
            active_tab = page.locator(".tab-pane.active")
            if active_tab.count() > 0:
                print(f"Found {active_tab.count()} active tab panes.")
                text = active_tab.first.inner_text()
                print("--- Active Tab Text Preview ---")
                print(text[:500])
                print("-------------------------------")
                
                # Check for "Daily Weather Forecast" in text
                if "Daily Weather Forecast" in text or "Synopsis" in text:
                    print("SUCCESS: It appears to be the forecast/synopsis.")
                else:
                    print("WARNING: Text does not look like the forecast.")
            else:
                print("No .tab-pane.active found.")
                
            # Check specifically for #daily-weather-forecast id if exists
            specific = page.locator("#daily-weather-forecast")
            if specific.count() > 0:
                 print("\nFound element with id 'daily-weather-forecast'")
                 print(specific.first.inner_text()[:200])
            else:
                 print("\nElement with id 'daily-weather-forecast' NOT found.")

        except Exception as e:
            print(f"Error during inspection: {e}")

        browser.close()

if __name__ == "__main__":
    check_pagasa()
