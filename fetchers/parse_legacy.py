#!/usr/bin/env python3
# parse_accuweather_texts_json_only.py

import re
import json
import sys
from pathlib import Path
from datetime import datetime

# --- Settings ---
INPUT_FILES = {
    "accuweather_dumaguete.txt": "accuweather_dumaguete_parse.json",
    "accuweather_ncr.txt": "accuweather_ncr_parsed.json",
}

OUTPUT_FOLDER_PREFIX = "output-"
DATE_PATTERN = re.compile(r"^output-(\d{4})-(\d{2})-(\d{2})$")

# --- helper parsing functions ---
def normalize_lines(text):
    return [ln.strip() for ln in text.splitlines() if ln.strip()]

date_re = re.compile(r'^\d{1,2}/\d{1,2}$')
temp_re = re.compile(r'^\d+\s*°$')
percent_re = re.compile(r'^(\d{1,3})\s*%$')
weekday_names = {
    "TODAY","SUN","MON","TUE","WED","THU","FRI","SAT",
    "SUNDAY","MONDAY","TUESDAY","WEDNESDAY","THURSDAY","FRIDAY","SATURDAY"
}

def parse_lines(lines):
    results = []
    n = len(lines)

    for i in range(n - 1):
        if temp_re.match(lines[i]) and temp_re.match(lines[i + 1]):
            max_temp = int(re.sub(r'\D', '', lines[i]))
            min_temp = int(re.sub(r'\D', '', lines[i + 1]))

            date_label = None
            for j in range(i - 1, -1, -1):
                if date_re.match(lines[j]) or lines[j].upper() in weekday_names:
                    date_label = lines[j]
                    break

            pop = None
            description = ""
            for k in range(i + 2, min(i + 20, n)):
                m = percent_re.match(lines[k])
                if m:
                    pop = int(m.group(1))
                    if k > i + 2:
                        description = " ".join(lines[i + 2:k]).strip()
                    break

            results.append({
                "date_label": date_label,
                "max_temp": max_temp,
                "min_temp": min_temp,
                "pop": pop,
                "description": description
            })

    return results

def parse_file(path: Path):
    if not path.exists():
        raise FileNotFoundError(path)
    text = path.read_text(encoding="utf-8")
    return parse_lines(normalize_lines(text))

# ---------------------------
# Folder resolution helpers
# ---------------------------
def find_most_recent_output_folder(explicit_path: str = None) -> Path:
    base_dir = Path(__file__).resolve().parent.parent
    data_dir = base_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    if explicit_path:
        p = Path(explicit_path)
        p.mkdir(parents=True, exist_ok=True)
        return p.resolve()

    matches = []
    # Search inside src2/data/
    for entry in data_dir.iterdir():
        if entry.is_dir() and entry.name.startswith(OUTPUT_FOLDER_PREFIX):
            m = DATE_PATTERN.match(entry.name)
            if m:
                y, mo, d = map(int, m.groups())
                matches.append((datetime(y, mo, d), entry))

    if matches:
        matches.sort(key=lambda x: x[0], reverse=True)
        return matches[0][1].resolve()

    today = data_dir / f"{OUTPUT_FOLDER_PREFIX}{datetime.now().strftime('%Y-%m-%d')}"
    today.mkdir(parents=True, exist_ok=True)
    return today.resolve()

# --- main ---
def main():
    explicit_folder = sys.argv[1] if len(sys.argv) > 1 else None
    out = find_most_recent_output_folder(explicit_folder)

    print("Using folder:", out)

    for txt_name, json_name in INPUT_FILES.items():
        txt_path = out / txt_name
        json_path = out / json_name

        try:
            parsed = parse_file(txt_path)
        except FileNotFoundError:
            print(f"Skipping missing file: {txt_path}")
            continue

        with open(json_path, "w", encoding="utf-8") as fh:
            json.dump(parsed, fh, ensure_ascii=False, indent=2)

        # delete raw text file after successful parse
        try:
            txt_path.unlink()
            print(f"Saved {json_name} and deleted {txt_name}")
        except Exception as e:
            print(f"Saved {json_name} but failed to delete {txt_name}: {e}")

    print("Done.")

if __name__ == "__main__":
    main()
