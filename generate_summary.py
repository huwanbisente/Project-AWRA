#!/usr/bin/env python3
"""
DAILY WEATHER SUMMARY — SOURCE-DRIVEN, LLM-SUMMARIZED

FINAL STABLE VERSION:
- OLD JSON FORMAT PRESERVED
- Only PROMPT updated for call center–specific logic
- PDF renderer compatibility GUARANTEED
"""

import json
import requests
import os
from pathlib import Path
from datetime import datetime
import pdfplumber
from dotenv import load_dotenv

# Load env vars
base_dir = Path(__file__).resolve().parent
load_dotenv(base_dir / ".env")

# ===============================
# OPENAI CONFIG (GPT-5.2)
# ===============================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_URL = "https://api.openai.com/v1/responses"
MODEL = "gpt-5.2"

OUTPUT_JSON = "summary.json"


# ===============================
# FILE HELPERS
# ===============================
def read_pdf(path: Path) -> str:
    with pdfplumber.open(path) as pdf:
        return "\n".join(page.extract_text() or "" for page in pdf.pages)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def find_latest_output_folder() -> Path:
    base_dir = Path(__file__).resolve().parent
    data_dir = base_dir / "data"
    
    # Ensure data dir exists
    if not data_dir.exists():
        raise RuntimeError(f"❌ Data directory not found: {data_dir}")

    folders = [
        d for d in data_dir.iterdir()
        if d.is_dir() and d.name.startswith("output-")
    ]
    if not folders:
        raise RuntimeError("❌ No output-* folder found")
    return max(folders, key=lambda d: d.stat().st_mtime)


# ===============================
# FILE COLLECTION
# ===============================
# ===============================
# FILE COLLECTION (DYNAMIC)
# ===============================
def load_config_map():
    """Returns a dict mapping filename -> category from sources.json"""
    base_dir = Path(__file__).resolve().parent
    config_path = base_dir / "config" / "sources.json"
    mapping = {}
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Combine pdfs and text_sources
            all_sources = data.get("pdfs", []) + data.get("text_sources", [])
            for item in all_sources:
                # Map expected filename to its category
                fname = item.get("filename", item["name"])
                mapping[fname.lower()] = item.get("category", "UNKNOWN_CATEGORY")
    except Exception as e:
        print(f"❌ Error loading config map: {e}")
    return mapping


def collect_files(folder: Path) -> dict:
    # 1. Load mapping from config
    file_cat_map = load_config_map()
    
    # 2. Initialize buckets dynamic based on config categories
    # We use a dict of lists
    buckets = {}

    for f in folder.iterdir():
        if f.is_dir():
            continue
        
        name_lower = f.name.lower()
        
        # Check if this file is in our config mapping
        if name_lower in file_cat_map:
            cat = file_cat_map[name_lower]
        else:
            # Fallback: ignore or maybe try to guess? 
            # For strictness and cleanliness, we skip unconfigured files 
            # to avoid polluting the prompt with junk.
            continue
            
        if cat not in buckets:
            buckets[cat] = []
        buckets[cat].append(f)
        print(f"📄 Collected source: {f.name} => [{cat}]")

    return buckets


def load_bucket(files: list[Path]) -> str:
    out = []
    for f in files:
        if f.suffix.lower() == ".pdf":
            out.append(read_pdf(f))
        else:
            out.append(read_text(f))
    return "\n".join(out).strip()


# ===============================
# JSON SANITIZER
# ===============================
def extract_json(text: str) -> str:
    text = text.strip()

    if text.startswith("```"):
        text = text.split("```", 1)[1]
        if text.lstrip().startswith("json"):
            text = text.lstrip()[4:]
        text = text.rsplit("```", 1)[0]

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        raise ValueError("❌ No JSON object found in LLM output")

    return json.dumps(json.loads(text[start:end + 1]), indent=2)


# ===============================
# OPENAI GPT-5.2 CALL
# ===============================
def call_llm(prompt: str) -> str:
    r = requests.post(
        OPENAI_URL,
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": MODEL,
            "input": prompt,
            "max_output_tokens": 3500
        },
        timeout=180
    )

    if r.status_code != 200:
        print("❌ OpenAI error:")
        print(r.text)
        r.raise_for_status()

    data = r.json()

    if "output_text" in data:
        return data["output_text"]

    if "output" in data:
        chunks = []
        for block in data["output"]:
            for item in block.get("content", []):
                if item.get("type") in ("output_text", "text"):
                    chunks.append(item.get("text", ""))
        if chunks:
            return "\n".join(chunks)

    raise RuntimeError("❌ No usable text returned by OpenAI")

# ===============================
# MAIN
# ===============================
def main():
    folder = find_latest_output_folder()
    buckets = collect_files(folder)
    today = datetime.now().strftime("%B %d, %Y")
    
    # Build dynamic source text
    source_text = ""
    # Sort categories to ensure deterministic order
    for category in sorted(buckets.keys()):
        content = load_bucket(buckets[category])
        source_text += f"\n[{category}]\n{content or 'None'}\n"

    # 🔹 ONLY THIS PROMPT WAS UPDATED
    prompt = f"""
You are generating a DAILY OPERATIONAL WEATHER SUMMARY.

OUTPUT MUST MATCH THIS JSON STRUCTURE EXACTLY.
DO NOT ADD OR REMOVE KEYS.
DO NOT RENAME FIELDS.

IMPORTANT OPERATIONAL CONTEXT:

CRITICAL INSTRUCTION:
Check [PAGASA PUBLIC FORECAST] and other sources for active **LOW PRESSURE AREAS (LPA)** or **TROPICAL CYCLONES**. 
If an LPA or Cyclone is present, you MUST mention it in 'system_in_effect' and 'active_pagasa_advisories', even if it is not yet directly affecting the sites.


This organization is a CALL CENTER / BPO COMPANY.

SITE OPERATING MODEL:
- Metro Manila site supports BOTH:
  • On-site employees reporting to the Makati office
  • Work-from-home (WFH) employees within Metro Manila / Greater Manila Area
- Dumaguete site is FULLY ON-SITE.
  • DO NOT include WFH recommendations for Dumaguete.

OPERATIONAL RECOMMENDATION RULES:

1. Scope Control
- WFH-related recommendations are ALLOWED FOR METRO MANILA ONLY.
- Dumaguete recommendations must assume on-site operations only.

2. Metro Manila Recommendation Structure
- Metro Manila recommendations may include:
  • One general recommendation for ON-SITE employees (Makati area)
  • One general recommendation for WFH employees (Metro Manila / Greater Manila)
- Keep recommendations high-level and clearly applicable.

3. Risk-Based Language Calibration
- Mild weather (light rain, brief heavy showers):
  • Use calm, advisory wording
  • Do NOT recommend operational disruption
- Moderate weather:
  • Emphasize monitoring and readiness
- Severe weather (e.g., typhoon, strong monsoon, prolonged heavy rainfall):
  • Allow more specific and directive actions

Avoid alarmist or panic-inducing language.
Do not overreact to minor or short-lived weather events.

4. Specificity Control
- Default to GENERIC, non-intrusive operational guidance.
- Only provide specific actions when a clearly elevated risk exists.

Operational recommendations MUST:
- Be suitable for indoor, office-based, IT-reliant operations
- Focus on:
  - staff attendance and commuting
  - power and connectivity continuity
  - service availability and SLA protection

Operational recommendations MUST NOT include:
- outdoor activities
- field teams
- drainage checks
- sandbags
- securing loose materials
- elevated work
- construction or site safety actions

Limit operational_recommendations to 2–3 concise items per site.

OUTPUT JSON STRUCTURE:

{{
  "summary_of_current_conditions": {{
    "date": "{today}",
    "system_in_effect": "",
    "general_weather": "",
    "winds": "",
    "humidity": "",
    "low_high_temperature": ""
  }},
  "active_pagasa_advisories": {{
    "rainfall_warning": {{
      "metro_manila": {{ "title": "", "summary": "" }},
      "dumaguete": {{ "title": "", "summary": "" }}
    }},
    "thunderstorm_warning": {{
      "metro_manila": {{ "title": "", "summary": "" }},
      "dumaguete": {{ "title": "", "summary": "" }}
    }},
    "other_advisories": [] 
  }},
  "forecast_10day": {{
    "accuweather": {{
      "metro_manila": [
        {{ "date_label": "Today", "max_temp": 30, "min_temp": 24, "pop": 20, "description": "Partly sunny" }}
      ],
      "dumaguete": [
        {{ "date_label": "Today", "max_temp": 31, "min_temp": 25, "pop": 40, "description": "Cloudy" }}
      ]
    }}
  }},
  "site_impact_summary": {{
    "metro_manila": {{ "impact_level": "", "justification": "" }},
    "dumaguete": {{ "impact_level": "", "justification": "" }}
  }},
  "operational_status": {{
    "metro_manila": "",
    "dumaguete": ""
  }},
  "operational_recommendations": {{
    "metro_manila": [],
    "dumaguete": []
  }},
  "key_takeaways": []
}}

SOURCE DATA:

{source_text}
"""

    raw = call_llm(prompt)
    
    # Save summary.json INSIDE the daily folder
    output_path = folder / OUTPUT_JSON
    output_path.write_text(extract_json(raw), encoding="utf-8")
    
    print(f"✅ Clean JSON generated: {output_path}")


if __name__ == "__main__":
    main()
