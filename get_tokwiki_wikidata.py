"""
Get Wikidata item connections from tok.wikipedia articles
"""
import io
import sys
import time
import requests
import csv

# Fix Windows encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

TOK_API = "https://tok.wikipedia.org/w/api.php"
HEADERS = {
    'User-Agent': 'TokiPonaWikidataFetcher/1.0 (fetching wikidata connections from tok.wikipedia)'
}

def get_wikidata_from_tokwiki(page_title):
    """
    Get the Wikidata item ID connected to a tok.wikipedia article.
    Returns the Q-ID or None.
    """
    params = {
        'action': 'query',
        'titles': page_title,
        'prop': 'pageprops',
        'format': 'json'
    }

    try:
        response = requests.get(TOK_API, params=params, headers=HEADERS, timeout=10)
        data = response.json()

        if 'query' not in data or 'pages' not in data['query']:
            return None

        # Get the first (and only) page
        pages = data['query']['pages']
        for page_id, page_data in pages.items():
            # Check for wikibase_item property
            if 'pageprops' in page_data and 'wikibase_item' in page_data['pageprops']:
                return page_data['pageprops']['wikibase_item']

        return None

    except Exception as e:
        print(f"    Error getting Wikidata for {page_title}: {e}", flush=True)
        return None

def main():
    input_file = 'tokipona_wiki_coverage.csv'
    output_file = 'tokipona_wiki_coverage.csv'
    backup_file = 'tokipona_wiki_coverage_before_tokwiki_wikidata.csv'

    print("Reading CSV...", flush=True)

    # Read all rows
    rows = []
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames)
        rows = list(reader)

    # Add new columns if they don't exist
    if 'tok_wikidata_id' not in fieldnames:
        fieldnames.insert(fieldnames.index('tok_url') + 1, 'tok_wikidata_id')
    if 'tok_wikidata_url' not in fieldnames:
        fieldnames.insert(fieldnames.index('tok_wikidata_id') + 1, 'tok_wikidata_url')

    print(f"Loaded {len(rows)} rows", flush=True)

    # Backup original
    print(f"Creating backup: {backup_file}", flush=True)
    with open(backup_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=reader.fieldnames if 'tok_wikidata_id' not in reader.fieldnames else fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    # Process rows with tok.wikipedia articles
    found_count = 0
    checked_count = 0
    wikidata_connections = []

    for i, row in enumerate(rows):
        # Initialize new fields if they don't exist
        if 'tok_wikidata_id' not in row:
            row['tok_wikidata_id'] = ''
        if 'tok_wikidata_url' not in row:
            row['tok_wikidata_url'] = ''

        if row['tok_exists'] != 'Yes':
            continue

        word = row['word']
        tok_url = row['tok_url']

        # Extract page title from URL
        # https://tok.wikipedia.org/wiki/Page_Title
        page_title = tok_url.split('/wiki/')[-1].replace('_', ' ')

        checked_count += 1

        print(f"\n[{checked_count}] Checking: {word} → {page_title}", flush=True)

        wikidata_id = get_wikidata_from_tokwiki(page_title)

        if wikidata_id:
            print(f"  ✓ Found Wikidata: {wikidata_id}", flush=True)
            found_count += 1

            # Update the row
            row['tok_wikidata_id'] = wikidata_id
            row['tok_wikidata_url'] = f"https://www.wikidata.org/wiki/{wikidata_id}"

            # Store connection info for summary
            wikidata_connections.append({
                'word': word,
                'page': page_title,
                'wikidata': wikidata_id
            })
        else:
            print(f"  ✗ No Wikidata connection", flush=True)

        time.sleep(0.5)  # Rate limit

    # Write updated CSV
    print(f"\n{'='*60}", flush=True)
    print(f"Writing updated CSV...", flush=True)
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"✓ Done!", flush=True)
    print(f"\nSummary:", flush=True)
    print(f"  Checked: {checked_count} tok.wikipedia articles", flush=True)
    print(f"  With Wikidata connections: {found_count}", flush=True)
    print(f"  Without Wikidata: {checked_count - found_count}", flush=True)

    if wikidata_connections:
        print(f"\nSample Wikidata connections found:", flush=True)
        for info in wikidata_connections[:20]:
            print(f"  {info['word']:20s} → {info['page']:30s} → {info['wikidata']}", flush=True)

        # Write connections to file
        summary_file = 'tokwiki_wikidata_connections.txt'
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"Tok Wikipedia Wikidata Connections\n")
            f.write(f"{'='*60}\n\n")
            f.write(f"Total connections found: {found_count}\n\n")
            for info in wikidata_connections:
                f.write(f"{info['word']:20s} → {info['page']:40s} → {info['wikidata']}\n")
        print(f"\nFull list saved to: {summary_file}", flush=True)

if __name__ == "__main__":
    main()
