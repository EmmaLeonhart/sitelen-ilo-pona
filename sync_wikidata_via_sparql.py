"""
Sync Wikidata IDs by querying Wikidata SPARQL for P373 (Commons category) matches
Much faster than checking Commons API
"""
import csv
import requests
import time
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def query_wikidata_by_commons_category(commons_title):
    """
    Query Wikidata SPARQL for item with specific P373 value
    """
    # Remove "Category:" prefix if present
    category_name = commons_title.replace('Category:', '')

    sparql_query = f"""
    SELECT ?item WHERE {{
      ?item wdt:P373 "{category_name}" .
    }}
    LIMIT 1
    """

    endpoint = 'https://query.wikidata.org/sparql'
    headers = {
        'User-Agent': 'TokiPonaWikidataBot/1.0'
    }

    try:
        response = requests.get(
            endpoint,
            params={'query': sparql_query, 'format': 'json'},
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()

        results = data.get('results', {}).get('bindings', [])
        if results:
            item_uri = results[0]['item']['value']
            # Extract QID from URI like http://www.wikidata.org/entity/Q12345
            qid = item_uri.split('/')[-1]
            return qid
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
    not_found_count = 0

    for i, row in enumerate(rows, 1):
        word = row['word']
        commons_title = row['commons_title']
        current_wikidata = row.get('wikidata_id', '').strip()

        print(f"[{i}/{len(rows)}] Checking: {word}", flush=True)

        if current_wikidata:
            print(f"  Already has Wikidata: {current_wikidata}", flush=True)
            already_has_count += 1
        else:
            # Query Wikidata SPARQL for P373 match
            qid = query_wikidata_by_commons_category(commons_title)

            if qid:
                row['wikidata_id'] = qid
                row['wikidata_url'] = f"https://www.wikidata.org/wiki/{qid}"
                print(f"  ✓ Found Wikidata: {qid}", flush=True)
                updated_count += 1
            else:
                print(f"  ✗ No Wikidata found", flush=True)
                not_found_count += 1

        time.sleep(0.1)  # Rate limiting for SPARQL

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
    print(f"  Still without Wikidata: {not_found_count}", flush=True)

if __name__ == "__main__":
    main()
