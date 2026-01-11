"""
Sync ALL Commons Wikidata IDs for items in the CSV
Checks Commons categories for Wikidata connections
"""
import csv
import requests
import time
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def get_commons_wikidata(commons_title):
    """
    Get Wikidata ID from Commons category page
    """
    # Commons API endpoint
    api_url = 'https://commons.wikimedia.org/w/api.php'

    params = {
        'action': 'query',
        'titles': commons_title,
        'prop': 'pageprops',
        'format': 'json'
    }

    headers = {
        'User-Agent': 'TokiPonaWikidataBot/1.0'
    }

    try:
        response = requests.get(api_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        pages = data.get('query', {}).get('pages', {})
        for page_id, page_data in pages.items():
            if page_id == '-1':  # Page doesn't exist
                return None

            pageprops = page_data.get('pageprops', {})
            wikidata_id = pageprops.get('wikibase_item')

            if wikidata_id:
                return wikidata_id

        return None
    except Exception as e:
        print(f"  ERROR: {e}", flush=True)
        return None

def main():
    input_file = 'tokipona_wiki_coverage.csv'

    print("Reading CSV...", flush=True)

    rows = []
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"Found {len(rows)} items to check\n", flush=True)
    print("="*60, flush=True)

    updated_count = 0
    already_has_count = 0

    for i, row in enumerate(rows, 1):
        word = row['word']
        commons_title = row['commons_title']
        current_wikidata = row.get('wikidata_id', '').strip()

        print(f"[{i}/{len(rows)}] Checking: {word}", flush=True)

        if current_wikidata:
            print(f"  Already has Wikidata: {current_wikidata}", flush=True)
            already_has_count += 1
        else:
            # Check Commons for Wikidata
            wikidata_id = get_commons_wikidata(commons_title)

            if wikidata_id:
                row['wikidata_id'] = wikidata_id
                row['wikidata_url'] = f"https://www.wikidata.org/wiki/{wikidata_id}"
                print(f"  ✓ Found Wikidata: {wikidata_id}", flush=True)
                updated_count += 1
            else:
                print(f"  ✗ No Wikidata found", flush=True)

        print(flush=True)
        time.sleep(0.5)  # Rate limiting

    print("="*60, flush=True)
    print("Writing updated CSV...", flush=True)

    # Write back to CSV
    with open(input_file, 'w', encoding='utf-8', newline='') as f:
        fieldnames = rows[0].keys()
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print("✓ Done!", flush=True)
    print(flush=True)
    print("Summary:", flush=True)
    print(f"  Total items checked: {len(rows)}", flush=True)
    print(f"  Already had Wikidata: {already_has_count}", flush=True)
    print(f"  Newly found Wikidata: {updated_count}", flush=True)
    print(f"  Still without Wikidata: {len(rows) - already_has_count - updated_count}", flush=True)

if __name__ == "__main__":
    main()
