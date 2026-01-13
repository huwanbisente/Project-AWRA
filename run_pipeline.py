#!/usr/bin/env python3
import subprocess
import sys
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_DIR = Path(__file__).resolve().parent

def run_script(script_name):
    """Runs a single script and returns (success, script_name)"""
    script_path = BASE_DIR / script_name
    print(f"🚀 Starting {script_name}...")
    try:
        # Capture output to avoid messy interleaving, or let it stream if preferred.
        # For parallel, streaming is messy. Capturing is better.
        subprocess.run(["python", str(script_path)], check=True)
        print(f"✅ Finished {script_name}")
        return True, script_name
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running {script_name}: {e}")
        return False, script_name

def main():
    print("=== ⛈️ WEATHER REPORT PIPELINE STARTED ===")
    start_time = time.time()

    # 1. IDENTIFY FETCHER SCRIPTS
    # We look for all python scripts in the 'fetchers' directory
    fetchers_dir = BASE_DIR / "fetchers"
    fetchers = sorted([f.name for f in fetchers_dir.glob("*.py")])
    
    if not fetchers:
        print("⚠️ No fetcher scripts found in fetchers/ directory!")
        # We don't exit here because maybe we just want to run the reporting part?
        # But usually this implies missing setup.
    else:
        print(f"📝 Found {len(fetchers)} fetcher scripts: {fetchers}")

    # 2. RUN FETCHERS IN PARALLEL
    print("\n--- PHASE 1: PARALLEL DATA FETCHING ---")
    
    # We need to run them from the main dir, but pointing to the subfolder?
    # Or should we just pass the full relative path to subprocess?
    # run_script function handles BASE_DIR / script_name.
    # So we need to pass "fetchers/script_name.py"
    
    fetcher_paths = [f"fetchers/{name}" for name in fetchers]

    with ThreadPoolExecutor(max_workers=len(fetchers)) as executor:
        future_to_script = {executor.submit(run_script, script): script for script in fetcher_paths}
        
        for future in as_completed(future_to_script):
            success, script = future.result()
            if not success:
                print(f"⚠️ Warning: {script} failed. Continuing with available data.")

    # 3. RUN SEQUENTIAL PIPELINE
    print("\n--- PHASE 2: PROCESSING & REPORTING ---")
    
    pipeline = [
        "generate_summary.py",
        "render_report.py",
        "send_email.py"
    ]

    for script in pipeline:
        print(f"\n▶️ Running {script}...")
        success, _ = run_script(script)
        if not success:
            print(f"⛔ Critical Pipeline Failure at {script}. Stopping.")
            sys.exit(1)

    elapsed = time.time() - start_time
    print(f"\n✨ PIPELINE COMPLETED IN {elapsed:.2f} SECONDS ✨")

if __name__ == "__main__":
    main()
