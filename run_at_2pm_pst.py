"""
Wait until 2:10 PM PST, then:
1. Sync CSV to get newly created Wikidata IDs
2. Generate P18 image QuickStatements
"""
import time
import datetime
import pytz
import subprocess
import sys

def main():
    # Set PST timezone
    pst = pytz.timezone('America/Los_Angeles')

    # Get current time in PST
    now = datetime.datetime.now(pst)
    print(f"Current time (PST): {now.strftime('%Y-%m-%d %H:%M:%S')}", flush=True)

    # Set target time to 2:10 PM today
    target = now.replace(hour=14, minute=10, second=0, microsecond=0)

    # If we're past 2:10 PM, run immediately
    if now >= target:
        print("Already past 2:10 PM PST - running immediately!", flush=True)
        wait_seconds = 0
    else:
        wait_seconds = (target - now).total_seconds()
        print(f"Waiting until 2:10 PM PST ({wait_seconds:.0f} seconds / {wait_seconds/60:.1f} minutes)...", flush=True)
        time.sleep(wait_seconds)

    print("\n" + "="*60, flush=True)
    print("2:10 PM PST reached! Starting operations...", flush=True)
    print("="*60 + "\n", flush=True)

    # Step 1: Sync CSV to get new Wikidata IDs
    print("STEP 1: Syncing CSV with newly created Wikidata items...\n", flush=True)
    result = subprocess.run([sys.executable, 'get_tokwiki_wikidata.py'],
                          capture_output=False, text=True)
    if result.returncode != 0:
        print(f"ERROR: Sync failed with exit code {result.returncode}", flush=True)
        return

    print("\n" + "-"*60 + "\n", flush=True)

    # Step 2: Generate P18 QuickStatements
    print("STEP 2: Generating P18 image QuickStatements...\n", flush=True)
    result = subprocess.run([sys.executable, 'generate_p18_images_for_new_items.py'],
                          capture_output=False, text=True)
    if result.returncode != 0:
        print(f"ERROR: P18 generation failed with exit code {result.returncode}", flush=True)
        return

    print("\n" + "="*60, flush=True)
    print("✓ All operations completed successfully!", flush=True)
    print("="*60, flush=True)

if __name__ == "__main__":
    main()
