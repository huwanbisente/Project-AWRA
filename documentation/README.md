Project AWRA 🌦️
Automated Weather Report Analytics

Project AWRA is an automated pipeline designed to streamline daily weather reporting. It systematically collects data from multiple meteorological sources, synthesizes it using advanced AI, and generates professional-grade PDF reports for distribution.

📖 Introduction
AWRA (Automated Weather Report Analytics) eliminates the manual labor involved in weather data aggregation. By scraping text forecasts, satellite imagery, and Outlook PDFs, it provides a comprehensive "Operational Weather Summary" powered by AI.

🚀 Key Features
Multi-Source Data Collection: Scrapes text forecasts, downloadable PDFs, and satellite images from PAGASA and AccuWeather.

AI-Powered Summarization: Utilizes GPT-5.2 to synthesize complex meteorological data into concise summaries.

Smart LPA Detection: Engineered with specific logic to detect "Low Pressure Area" warnings.

Automated PDF Generation: Uses ReportLab and pdfplumber to render branded, high-quality PDF reports.

Flexible Delivery: Features an interactive email sender with support for "Test" and "Live" modes.

🛠️ Technology Stack
Language: Python 3.x

Scraping: Playwright

AI Engine: OpenAI API (GPT-5.2)

PDF Processing: ReportLab, pdfplumber

🔄 Visual Workflow
The project follows a modular pipeline managed by a central orchestrator.

Code snippet

graph TD
    Start([Start: run_pipeline.py]) --> Phase1
    subgraph Phase1 [Data Fetching]
       F1[fetch_accuweather.py]
       F2[fetch_pdfs.py]
       F3[fetch_visualizations.py]
       F4[fetch_weather_texts.py]
    end
    Phase1 --> Phase2[AI Analysis]
    Phase2 --> Phase3[Report Generation]
    Phase3 --> Phase4[Email Distribution]
Orchestration: run_pipeline.py triggers all fetchers concurrently.

Fetching: Extracts data from PAGASA (text/PDF) and AccuWeather (10-day forecasts).

Summarization: generate_summary.py synthesizes data into summary.json via OpenAI.

Rendering: render_report.py creates the final document.

Distribution: send_email.py handles the final delivery based on the selected mode.

📂 Project Structure
Plaintext

Project AWRA v2/
├── .venv/                  # Virtual Environment
├── config/
│   └── sources.json        # Configuration settings
├── data/
│   └── output-YYYY-MM-DD/  # Daily output storage
├── documentation/          # Project documentation
├── fetchers/               # Data extraction scripts
├── run_pipeline.py         # Main Orchestrator
└── ...
📥 Installation & Usage
Setup
Activate Virtual Environment:

PowerShell

cd "F:\for PORTFOLIO\Project AWRA v2"
.\.venv\Scripts\activate
Install Dependencies:

PowerShell

pip install -r requirements.txt
playwright install chromium
Execution
Run the orchestrator: python run_pipeline.py.

Wait approximately 2 minutes for completion.

Select TEST or LIVE on the popup to send the report.

🔧 Troubleshooting
Missing LPA Warning: Usually caused by a change in PAGASA's text format; update fallback logic in fetch_weather_texts.py.

AccuWeather Errors: Ensure --disable-http2 is enabled in fetch_accuweather.py.

Timeouts: Check your internet connection or update the selector in fetch_pdfs.py.

Hidden Popups: If the email window doesn't appear, check the taskbar or use Alt+Tab.