"""
Check if any of the 103 items already have Wikidata items via SPARQL
Query by P373 (Commons category) to find existing items
"""
import csv
import requests
import time
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def query_wikidata_by_commons(commons_category):
    """
    Query Wikidata for items with this P373 (Commons category) value
    """
    sparql_url = 'https://query.wikidata.org/sparql'

    query = f"""
    SELECT ?item WHERE {{
      ?item wdt:P373 "{commons_category}".
    }}
    """

    headers = {
        'User-Agent': 'TokiPonaWikidataBot/1.0',
        'Accept': 'application/sparql-results+json'
    }

    try:
        response = requests.get(sparql_url, params={'query': query}, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()

        results = data.get('results', {}).get('bindings', [])
        if results:
            # Extract QID from URI
            item_uri = results[0]['item']['value']
            qid = item_uri.split('/')[-1]
            return qid
        return None
    except Exception as e:
        print(f"  ERROR querying: {e}", flush=True)
        return None

def main():
    input_file = 'tokipona_wiki_coverage.csv'

    print("Reading CSV to find items without wikidata_id...", flush=True)

    items_to_check = []

    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            wikidata_id = row.get('wikidata_id', '').strip()
            if not wikidata_id:
                # Extract just the category name from the full title
                commons_title = row['commons_title']
                # Remove "Category:" prefix if present
                commons_category = commons_title.replace('Category:', '')

                items_to_check.append({
                    'word': row['word'],
                    'commons_category': commons_category,
                    'category': row['category']
                })

    print(f"Found {len(items_to_check)} items to check\n", flush=True)
    print("="*80, flush=True)

    found_count = 0
    not_found_count = 0
    found_items = []

    for i, item in enumerate(items_to_check, 1):
        print(f"[{i}/{len(items_to_check)}] Checking: {item['word']}", flush=True)
        print(f"  Commons category: {item['commons_category']}", flush=True)

        qid = query_wikidata_by_commons(item['commons_category'])

        if qid:
            print(f"  ✓ FOUND existing item: {qid}", flush=True)
            found_count += 1
            found_items.append({
                'word': item['word'],
                'qid': qid,
                'commons_category': item['commons_category'],
                'category': item['category']
            })
        else:
            print(f"  ✗ No existing item found", flush=True)
            not_found_count += 1

        print(flush=True)
        time.sleep(1)  # Rate limiting

    print("="*80, flush=True)
    print("\nSummary:", flush=True)
    print(f"  Total checked: {len(items_to_check)}", flush=True)
    print(f"  Found existing items: {found_count}", flush=True)
    print(f"  Not found (need creation): {not_found_count}", flush=True)

    if found_items:
        print(f"\n\n{'='*80}", flush=True)
        print("EXISTING ITEMS (need Commons category link back):", flush=True)
        print(f"{'='*80}", flush=True)
        for item in found_items:
            print(f"{item['word']:25s} → {item['qid']:15s} | P373: {item['commons_category']}", flush=True)

        # Write to file
        with open('existing_items_need_commons_link.txt', 'w', encoding='utf-8') as f:
            f.write("Items that already exist on Wikidata but Commons category doesn't link back\n")
            f.write("="*80 + "\n\n")
            for item in found_items:
                f.write(f"{item['word']:25s} {item['qid']:15s} {item['commons_category']}\n")

        print(f"\nList saved to: existing_items_need_commons_link.txt", flush=True)

    print(f"\n✓ Done!", flush=True)

if __name__ == "__main__":
    main()
