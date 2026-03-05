<h1 align="center">Project AWRA</h1>

<p align="center">
  Automated Weather Reporting Assistant harnessing n8n for orchestration, Python for high-fidelity rendering, and Google Apps Script for live monitoring.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Author-Jan%20Vincent%20Chioco-red?style=flat-square" alt="Author">
  <img src="https://img.shields.io/badge/Frontend-Google%20Apps%20Script%20%2B%20Tailwind-green?style=flat-square" alt="Frontend">
  <img src="https://img.shields.io/badge/Backend-Python%20%2B%20n8n-blue?style=flat-square&logo=python&logoColor=white" alt="Backend">
  <img src="https://img.shields.io/badge/AI-Gemini%20%2F%20OpenAI-purple?style=flat-square" alt="AI">
</p>

---

*   If you find this weather automation tool useful for your meteorological workflows, please consider giving it a star!

**Project AWRA** (Automated Weather Reporting Assistant) is a robust, self-hosted weather intelligence pipeline. It systematically collects data from multiple sources (PAGASA, AccuWeather, Windy), processes it using the latest Generative AI models for professional summaries, and provides a polished, interactive Dashboard for real-time monitoring and PDF export.

The project uses a **Hybrid Automation Architecture**, separating the cloud-based orchestration (n8n Intelligence) from the high-performance local processing (Python Pipeline), secured via Google Workspace integration.

---

## System Architecture

The following diagram illustrates the Project AWRA ETL pipeline and data flow:

```mermaid
graph LR
    %% Data Sources
    subgraph "1. DATA COLLECTION"
        PAGASA["PAGASA<br/>(Bulletins & PDFs)"]
        Accu["AccuWeather API<br/>(Forecasts)"]
        Windy["Windy Live<br/>(Satellite Maps)"]
    end

    %% Intelligence Layer
    subgraph "2. INTELLIGENCE (n8n)"
        Workflow["n8n Orchestrator"]
        LLM["GenAI Analytics<br/>(Gemini/OpenAI)"]
        Workflow <--> LLM
    end

    %% Local Processing
    subgraph "3. PROCESSING (Python)"
        Pipeline["run_pipeline.py"]
        Render["Report Renderer<br/>(PDFGen)"]
        Pipeline --> Render
    end

    %% Delivery / View
    subgraph "4. DELIVERY & DASHBOARD"
        Sheets[("Google Sheets<br/>(Central DB)")]
        GAS["GAS Web App<br/>(Live UI)"]
        Email["Email Dispatch<br/>(Daily Reports)"]
    end

    %% Connections
    PAGASA & Accu & Windy --> Workflow
    Workflow -->|JSON Payload| Pipeline
    Pipeline -->|Sync Data| Sheets
    Sheets --> GAS
    Render --> Email
```

**Key Components:**
- **n8n Workflow**: Cloud orchestrator that scrapes technical bulletins and uses LLMs to synthesize weather "Key Takeaways."
- **Python Execution Pipeline**: Multi-threaded local runner that retrieves maps, renders specialized charts, and compiles the final PDF.
- **Google Sheets & GAS**: Acts as a lightweight, real-time database that powers the reactive glassmorphic dashboard.
- **Automated Dispatch**: System handles simultaneous updates to the web dashboard and executive email lists.

---

## User Interface

The application features a modern, responsive weather-focused interface.

### Weather Intelligence Dashboard
Monitor real-time satellite feeds, heat index tracking, and localized 10-day forecasts.
![Dashboard Preview](assets/images/webapp_live.png)

### Automated PDF Reporting & Analysis
Review AI-generated summaries and trend visualizations in executive-ready PDF format.
![Report Preview](assets/images/pdf_report_preview.png)

---

## Features

*   **Self-Hosted & Private**: Designed to run on local infrastructure with cloud-synced monitoring.
*   **Modern UI**: Beautiful, responsive dashboard built with TailwindCSS and Google Apps Script.
*   **Intelligent Extraction**: Uses LLMs to parse complex PAGASA bulletins and generate safety advisories.
*   **Multi-Source Sync**: Real-time integration of AccuWeather, Windy, and official government data.
*   **Automated Delivery**: Scheduled PDF generation and email dispatch for daily weather briefings.
*   **Operational Readiness**: AI-driven "Ops Recos" providing actionable guidance based on weather severity.

---

## Requirements

*   Python 3.10+
*   n8n Instance (Self-hosted or Cloud)
*   Google Cloud Service Account (for Sheets/GAS API)
*   OpenAI or Gemini API Key

---

## Installation

Clone the repository:

```bash
git clone https://github.com/huwanbisente/Project-AWRA.git
cd Project-AWRA
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Configuration

1.  **Environment Variables**: Create a `.env` file in the root directory:
    ```ini
    OPENAI_API_KEY=your_key
    ACCUWEATHER_API_KEY=your_key
    SPREADSHEET_ID=your_id
    ```

2.  **Start Local Pipeline**:
    ```bash
    python run_pipeline.py
    ```

3.  **Deploy Dashboard**:
    Copy `webapp/Code.gs` and `webapp/index_GAS_v2.html` to a new Google Apps Script project and deploy as a Web App.

---

## Project Structure

```text
├── run_pipeline.py         # Main Automation Orchestrator
├── core/                   # PDF Rendering and Processing Logic
├── fetchers/               # Parallel Data Retrieval Scripts
├── n8n/                    # Workflow Definitions and JS Parsers
├── webapp/                 # Dashboard Code and HTML Templates
├── assets/                 # Brand Assets and Documentation Images
└── documentation/          # Detailed Architecture and Setup Guides
```
