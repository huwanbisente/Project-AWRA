# Project Structure Guide

This document explains the organization of the Project AWRA codebase.

## Root Directory
- **`run_pipeline.py`**: The main entry point. Orchestrates data fetching, summarization, and reporting.
- **`requirements.txt`**: Python dependencies.
- **`.env`**: Configuration for environment variables (API keys).

## Directories

### `config/`
Contains configuration files.
- **`sources.json`**: Defines URLs, selectors, and settings for data scraping.

### `core/`
The brain of the operation. Contains logic for processing data.
- **`generate_summary.py`**: Uses OpenAI to summarize fetched data.
- **`render_report.py`**: Generates the PDF report.
- **`upload_dashboard_data.py`**: Uploads processed data to Google Drive.
- **`send_email.py`**: Handles email distribution.
- **`utils.py`**: Shared utility functions.

### `fetchers/`
Scripts responsible for scraping raw data.
- **`fetch_accuweather.py`**: Scrapes AccuWeather 10-day forecasts.
- **`fetch_typhoon_track.py`**: Downloads cyclone track images.
- **`fetch_pdfs.py`**: Downloads PDF bulletins from PAGASA.
- **`fetch_visualizations.py`**: Downloads satellite images.
- **`fetch_weather_texts.py`**: Scrapes text forecasts.

### `webapp/`
The Google Apps Script (GAS) dashboard frontend.
- **`Code_GAS.gs`**: The backend script for the GAS web app.
- **`index_GAS.html`**: The HTML/JS source for the dashboard.
- **`assets/`**: Local mock assets for testing.

### `utils/`
Helper scripts for maintenance and setup.
- **`download_fonts.py`**: Downloads required fonts.
- **`embed_images.py`**: Converts images to Base64 for embedding in the HTML dashboard.

### `data/`
Storage for runtime data.
- **`output-YYYY-MM-DD/`**: Generated daily, contains all raw logs, images, and the final PDF/JSON.

### `documentation/`
Guides and manuals.
- **`deployment/`**: Guides for deploying the dashboard to Google Apps Script.
