# Project AWRA v2 - Project Overview

**Automated Weather Report Analytics (AWRA)**

## 📖 Introduction
Project AWRA is an automated pipeline designed to streamline the daily weather reporting process. It systematically collects weather data from PAGASA and AccuWeather, analyzes it using AI, and generates professional PDF reports.

## 🚀 Key Features
- **Multi-Source Data Collection**: Scrapes text forecasts, downloadable PDFs, and satellite images.
- **AI-Powered Summarization**: Uses GPT-5.2 to synthesize data into an "Operational Weather Summary".
- **Smart LPA Detection**: Specifically engineered to detect "Low Pressure Area" warnings.
- **Automated PDF Generation**: Renders a branded, high-quality PDF report.
- **Flexible Delivery**: Interactive Email Sender supports "Test" and "Live" modes.

## 🛠️ Technology Stack
- **Language**: Python 3.x
- **Scraping**: Playwright
- **AI**: OpenAI API
- **PDF**: ReportLab, pdfplumber

## 📂 Project Structure
```text
Project AWRA v2/
├── .venv/                  # Virtual Environment
├── config/
│   └── sources.json        # Configuration
├── data/
│   └── output-YYYY-MM-DD/  # Daily output
├── documentation/          # Docs
├── fetchers/               # Scripts
├── run_pipeline.py         # Main Orchestrator
└── ...
```
