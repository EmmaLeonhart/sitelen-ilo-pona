import csv
import requests
import time
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Load the CSV
with open('tokipona_wiki_coverage.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

# Find entries missing wikidata_id
missing = [r for r in rows if not r.get('wikidata_id', '').strip()]
print(f"Found {len(missing)} entries missing wikidata_id")

def get_wikidata_from_commons_category(word):
    """Get Wikidata QID for a Commons category via the API"""
    # Try both capitalizations
    titles_to_try = [
        f"Category:{word.title()} (Toki Pona)",  # Title case word + Toki Pona
        f"Category:{word} (Toki Pona)",  # Original case + Toki Pona
        f"Category:{word.title()} (toki pona)",  # Title case word + toki pona
        f"Category:{word} (toki pona)",  # Original case + toki pona
    ]

    for title in titles_to_try:
        url = "https://commons.wikimedia.org/w/api.php"
        params = {
            'action': 'query',
            'titles': title,
            'prop': 'pageprops',
            'format': 'json'
        }

        try:
            r = requests.get(url, params=params, headers={'User-Agent': 'TokiPonaBot/1.0'})
            data = r.json()
            pages = data.get('query', {}).get('pages', {})

            for page_id, page_data in pages.items():
                if page_id != '-1':  # Page exists
                    wikibase_item = page_data.get('pageprops', {}).get('wikibase_item')
                    if wikibase_item:
                        return wikibase_item, title
        except Exception as e:
            print(f"  Error querying {title}: {e}")

    return None, None

# Fetch QIDs for missing entries
results = []
for i, row in enumerate(missing):
    word = row['word']
    print(f"[{i+1}/{len(missing)}] Looking up: {word}")

    qid, found_title = get_wikidata_from_commons_category(word)

    if qid:
        print(f"  Found: {qid} via {found_title}")
        results.append((word, qid, found_title))
    else:
        print(f"  NOT FOUND")
        results.append((word, None, None))

    time.sleep(0.5)  # Be nice to the API

# Summary
found = [(w, q, t) for w, q, t in results if q]
not_found = [(w, q, t) for w, q, t in results if not q]

print(f"\n=== SUMMARY ===")
print(f"Found: {len(found)}")
print(f"Not found: {len(not_found)}")

if not_found:
    print(f"\nWords still missing QIDs:")
    for w, _, _ in not_found:
        print(f"  {w}")

# Save results
with open('missing_qids_resolved.txt', 'w', encoding='utf-8') as f:
    for word, qid, title in results:
        if qid:
            f.write(f"{word}\t{qid}\t{title}\n")
        else:
            f.write(f"{word}\tNOT_FOUND\t\n")

print(f"\nResults saved to missing_qids_resolved.txt")
