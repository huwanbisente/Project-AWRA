# Troubleshooting Guide

## Common Issues

### 1. Missing LPA Warning
- **Check**: `data/output.../public_forecast.txt`.
- **Cause**: PAGASA text format changed.
- **Fix**: Update fallback logic in `fetch_weather_texts.py`.

### 2. AccuWeather Errors (HTTP/2)
- **Fix**: Ensure `--disable-http2` is in `fetch_accuweather.py`.

### 3. Timeouts
- **Fix**: Check internet connection. If permanent, `fetch_pdfs.py` selector might need updating.

### 4. No Email Popup
- **Fix**: Check taskbar/Alt+Tab for hidden window.
