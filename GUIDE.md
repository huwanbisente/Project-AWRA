# Project AWRA: Full Implementation Guide

Welcome to the comprehensive guide for **Project AWRA (Automated Weather Reporting Assistant)**. This document provides a step-by-step walkthrough of the system architecture, setup procedures, and operational workflows.

---

## 📖 Table of Contents
1. [System Overview](#system-overview)
2. [Prerequisites](#prerequisites)
3. [Environment Setup](#environment-setup)
4. [The n8n Intelligence Engine](#n8n-intelligence-engine)
5. [The Python Execution Pipeline](#python-execution-pipeline)
6. [Dashboard & Frontend Deployment](#dashboard--frontend-deployment)
7. [Maintenance & Troubleshooting](#maintenance--troubleshooting)

---

## 1. System Overview
Project AWRA is a hybrid automation system. It uses **n8n** for cloud-based scraping and AI synthesis, and a **Python Pipeline** for local data orchestration and high-fidelity report rendering. The final output is synced to a **Google Apps Script** dashboard for real-time monitoring.

---

## 2. Prerequisites
Before starting, ensure you have the following:
- **Python 3.10+** installed on your reporting machine.
- **Node.js** (optional, for local n8n testing).
- **Google Cloud Project** with:
  - Google Sheets API enabled.
  - Service Account JSON key.
- **API Keys**:
  - OpenAI (for GPT-4 summaries).
  - AccuWeather (for hyper-local data).

---

## 3. Environment Setup

### Local Repository Setup
```bash
# Clone and Navigate
git clone https://github.com/huwanbisente/Project-AWRA.git
cd Project-AWRA

# Create Virtual Environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install Dependencies
pip install -r requirements.txt
```

### Credentials Config
Create a `.env` file in the root based on `.env.example`.
```ini
OPENAI_API_KEY=your_openai_key
ACCUWEATHER_API_KEY=your_accuweather_key
SPREADSHEET_ID=your_google_sheet_id
```
Place your `service_account.json` in the project root.

---

## 4. The n8n Intelligence Engine

The n8n workflow is the "brain" of the operation. It handles the heavy lifting of parsing official PAGASA documents.

### Importing the Workflow
1. Locate `n8n/n8n_workflow_spec.json`.
2. In n8n, go to **Workflows > Import**.
3. Configure the **Webhook** node to listen for triggers (or set a Cron job for daily reports).
4. Update the **AI Transform** nodes with your OpenAI credentials.

---

## 5. The Python Execution Pipeline

The `run_pipeline.py` script manages Phase 1 (Parallel Fetching) and Phase 2 (Serial Processing).

### Flow:
1. **Parallel Fetchers**: Triggers all scripts in `fetchers/` simultaneously to minimize latency.
2. **Aggregator**: Consolidates raw JSON data from fetchers.
3. **Renderer**: Uses `core/render_report.py` to create the `weather_report.pdf`.
4. **Uploader**: Pushes the latest stats to Google Sheets for the webapp to consume.

---

## 6. Dashboard & Frontend Deployment

The dashboard is served via Google Apps Script (GAS).

1. Go to [script.google.com](https://script.google.com).
2. Create a new project.
3. Copy the content of `webapp/Code.gs` and `webapp/index_GAS_v2.html` into the project.
4. Deploy as a **Web App**.
5. Set Permissions to "Anyone with the link".

---

## 7. Maintenance & Troubleshooting

- **Fetcher Failures**: Check `logs/` (if enabled) or run individual fetchers manually:
  ```bash
  python fetchers/fetch_accuweather.py
  ```
- **PDF Errors**: Ensure `assets/fonts` contains the necessary .ttf files for `fpdf2`.
- **API Quotas**: Monitor AccuWeather usage; the pipeline is optimized to cache results for 1 hour to stay within free tier limits.

---

*For more technical details, refer to the [Internal Documentation](documentation/README.md).*
