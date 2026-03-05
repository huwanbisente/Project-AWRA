# n8n Migration: Script-to-Node Mapping

## 1. `fetch_weather_texts.py` (PAGASA Scraper)
*   **Python Logic**: Playwright -> Go to URL -> Click Toggle (XPath) -> Wait -> Extract Text.
*   **n8n Equivalent**: **n8n-nodes-puppeteer**
    *   **Operation**: `Get Page Content` (or `Execute Custom Code` for interaction).
    *   **Steps**:
        1.  `await page.goto('https://www.pagasa.dost.gov.ph/weather')`
        2.  `await page.waitForSelector('xpath=//toggle_selector')`
        3.  `await page.click('xpath=//toggle_selector')`
        4.  `const text = await page.$eval('selector', el => el.innerText)`
    *   *Alternative*: **Browserless** via HTTP Request (POST /function) with the same Puppeteer code in the body.

## 2. `fetch_accuweather.py`
*   **Python Logic**: Requests (Static HTML) -> BeautifulSoup -> Extract `.daily-forecast-card`.
*   **n8n Equivalent**:
    1.  **HTTP Request Node**: `GET [AccuWeather URL]`
    2.  **HTML Extract Node**:
        *   **Selector**: `.daily-forecast-card`
        *   **Extract**: `max_temp`, `min_temp`, `rain_prob`, `date`.

## 3. `fetch_pdfs.py` & `fetch_typhoon_track.py`
*   **Python Logic**: Requests -> Download File -> Save to Disk.
*   **n8n Equivalent**:
    1.  **HTTP Request Node**: `GET [URL]` (Response Format: *File/Binary*).
    2.  **(For PDF Text)**: **Extract from File Node** -> Operation: *Extract from PDF*.
    3.  **(For Images)**: Pass binary data to next node (e.g., Google Drive Upload or Email).

## 4. `generate_summary.py` (Aggregator & AI)
*   **Python Logic**: Read files -> Combine Strings -> Call OpenAI -> Save JSON.
*   **n8n Equivalent**:
    1.  **Merge Node**: Combine outputs from all fetchers (PAGASA, AccuWeather, PDF Text).
    2.  **Code Node (JS)**:
        *   Concatenate text into the `source_text` format.
        *   Prepare the System Prompt.
    3.  **OpenAI Node**: Chat Model (GPT-4) -> Input: System Prompt + `source_text`.
    4.  **Code Node (JS)**: `JSON.parse()` the output.
    5.  **Respond to Webhook / Save File**.
