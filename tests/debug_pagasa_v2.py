from playwright.sync_api import sync_playwright

def check_pagasa_content():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        # Navigate to the specific daily forecast anchor
        url = "https://www.pagasa.dost.gov.ph/weather#daily-weather-forecast"
        print(f"Navigating to {url}...")
        
        try:
            page.goto(url, timeout=60000, wait_until="domcontentloaded")
            # Wait a bit for JS to render tabs
            page.wait_for_timeout(5000)
            
            # 1. Capture the "Synopsis" text specifically
            print("\n--- CONTENT CHECK: Synopsis ---")
            try:
                # Based on typical structure, checks for synopsis text container
                synopsis = page.locator("div.synopsis").first
                if synopsis.count() > 0:
                     print(synopsis.inner_text().strip())
                else:
                     print("Specific '.synopsis' class not found.")
            except Exception as e:
                print(f"Error checking synopsis: {e}")

            # 2. Capture the "Daily Forecast" Tab Content (which should have the table)
            print("\n--- CONTENT CHECK: Tab Content ---")
            try:
                # Try to find the active tab pane
                active_pane = page.locator(".tab-pane.active")
                if active_pane.count() > 0:
                    text = active_pane.inner_text()
                    print(f"Active Pane Text Length: {len(text)}")
                    print("Preview (First 500 chars):")
                    print(text[:500])
                    
                    if "Temp" in text or "Wind" in text:
                        print("\n[CONFIRMED] Temperature/Wind keywords found in active pane.")
                    else:
                        print("\n[WARNING] Temperature/Wind keywords NOT found in active pane.")
                else:
                    print("No .tab-pane.active found.")
            except Exception as e:
                print(f"Error checking tab content: {e}")

            # 3. Check for specific table data if separate
            print("\n--- CONTENT CHECK: Forecast Table ---")
            try:
                # Often in #daily-weather-forecast id
                daily_div = page.locator("#daily-weather-forecast") 
                if daily_div.count() > 0:
                    print("Found #daily-weather-forecast div. Text content:")
                    print(daily_div.inner_text()[:500])
                else:
                    print("#daily-weather-forecast div not found.")
            except Exception as e:
                print(f"Error checking table: {e}")

        except Exception as e:
            print(f"Global Error: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    check_pagasa_content()
