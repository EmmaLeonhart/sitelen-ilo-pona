"""
Check Toki Pona categories on Commons against sona.pona.la and tok.wikipedia.org
"""
import io
import sys
import time
import requests
import csv
import re

# Fix Windows encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# API endpoints
COMMONS_API = "https://commons.wikimedia.org/w/api.php"
SONA_API = "https://sona.pona.la/w/api.php"
TOK_API = "https://tok.wikipedia.org/w/api.php"
WIKIDATA_API = "https://www.wikidata.org/w/api.php"

HEADERS = {
    'User-Agent': 'TokiPonaWikiChecker/1.0 (checking toki pona wiki coverage)'
}

def get_category_members(category_name, api_url=COMMONS_API):
    """Get all members of a category using MediaWiki API."""
    members = []
    cmcontinue = None

    print(f"Fetching members of {category_name}...", flush=True)

    while True:
        params = {
            'action': 'query',
            'list': 'categorymembers',
            'cmtitle': category_name,
            'cmlimit': 500,
            'format': 'json'
        }

        if cmcontinue:
            params['cmcontinue'] = cmcontinue

        response = requests.get(api_url, params=params, headers=HEADERS)
        data = response.json()

        if 'query' in data and 'categorymembers' in data['query']:
            members.extend(data['query']['categorymembers'])

        if 'continue' in data and 'cmcontinue' in data['continue']:
            cmcontinue = data['continue']['cmcontinue']
            time.sleep(0.5)  # Be nice to the server
        else:
            break

    print(f"  Found {len(members)} members", flush=True)
    return members

def check_page_exists(page_title, api_url):
    """Check if a page exists on a wiki."""
    params = {
        'action': 'query',
        'titles': page_title,
        'format': 'json'
    }

    try:
        response = requests.get(api_url, params=params, headers=HEADERS, timeout=10)
        data = response.json()

        if 'query' in data and 'pages' in data['query']:
            pages = data['query']['pages']
            # If page doesn't exist, it will have a negative ID
            for page_id, page_data in pages.items():
                if int(page_id) > 0:
                    return True
        return False
    except Exception as e:
        print(f"    Error checking {page_title}: {e}", flush=True)
        return False

def get_wikidata_from_commons(category_title):
    """Get Wikidata item ID from a Commons category page."""
    # First, get the page content to look for wikidata link
    params = {
        'action': 'query',
        'titles': category_title,
        'prop': 'pageprops',
        'format': 'json'
    }

    try:
        response = requests.get(COMMONS_API, params=params, headers=HEADERS, timeout=10)
        data = response.json()

        if 'query' in data and 'pages' in data['query']:
            for page_id, page_data in data['query']['pages'].items():
                # Check for wikibase_item property
                if 'pageprops' in page_data and 'wikibase_item' in page_data['pageprops']:
                    return page_data['pageprops']['wikibase_item']

        # Alternative: parse the page for {{Wikidata Infobox}} or similar
        params2 = {
            'action': 'parse',
            'page': category_title,
            'prop': 'wikitext',
            'format': 'json'
        }

        response2 = requests.get(COMMONS_API, params=params2, headers=HEADERS, timeout=10)
        data2 = response2.json()

        if 'parse' in data2 and 'wikitext' in data2['parse']:
            wikitext = data2['parse']['wikitext']['*']
            # Look for Wikidata item references (Q followed by numbers)
            match = re.search(r'\{\{[Ww]ikidata[^}]*\|([Q]\d+)', wikitext)
            if match:
                return match.group(1)

            # Also check for direct Q-ID mentions
            match = re.search(r'\b(Q\d+)\b', wikitext)
            if match:
                return match.group(1)

        return None
    except Exception as e:
        print(f"    Error getting Wikidata for {category_title}: {e}", flush=True)
        return None

def extract_word_from_title(title):
    """Extract the toki pona word from a category title by removing (toki pona) suffix."""
    # Remove "Category:" prefix if present
    if title.startswith('Category:'):
        title = title[9:]

    # Remove " (toki pona)" or " (Toki Pona)" suffix
    title = re.sub(r'\s*\([Tt]oki [Pp]ona\)\s*$', '', title)

    # Also remove file extension if it's a file
    title = re.sub(r'\.(svg|png|jpg|jpeg)$', '', title, flags=re.IGNORECASE)

    return title.strip()

def main():
    categories = [
        'Category:Sitelen Pona ligatures',
        'Category:Toki Pona logograms by word',
        'Category:Toki pona rare words'
    ]

    all_results = []

    for category in categories:
        print(f"\n{'='*60}", flush=True)
        print(f"Processing {category}", flush=True)
        print(f"{'='*60}", flush=True)

        members = get_category_members(category)

        for i, member in enumerate(members):
            title = member['title']
            word = extract_word_from_title(title)

            print(f"\n[{i+1}/{len(members)}] {title} → '{word}'", flush=True)

            # Check Commons category link
            commons_url = f"https://commons.wikimedia.org/wiki/{title.replace(' ', '_')}"

            # Get Wikidata item
            print(f"  Checking Wikidata...", flush=True)
            wikidata_id = get_wikidata_from_commons(title)
            if wikidata_id:
                print(f"    ✓ Found: {wikidata_id}", flush=True)
                wikidata_url = f"https://www.wikidata.org/wiki/{wikidata_id}"
            else:
                print(f"    ✗ Not found", flush=True)
                wikidata_url = ""

            time.sleep(0.5)  # Rate limit

            # Check sona.pona.la
            print(f"  Checking sona.pona.la...", flush=True)
            sona_exists = check_page_exists(word, SONA_API)
            if sona_exists:
                print(f"    ✓ Article exists", flush=True)
                sona_url = f"https://sona.pona.la/wiki/{word.replace(' ', '_')}"
            else:
                print(f"    ✗ No article", flush=True)
                sona_url = ""

            time.sleep(0.5)  # Rate limit

            # Check tok.wikipedia.org
            print(f"  Checking tok.wikipedia.org...", flush=True)
            tok_exists = check_page_exists(word, TOK_API)
            if tok_exists:
                print(f"    ✓ Article exists", flush=True)
                tok_url = f"https://tok.wikipedia.org/wiki/{word.replace(' ', '_')}"
            else:
                print(f"    ✗ No article", flush=True)
                tok_url = ""

            time.sleep(0.5)  # Rate limit

            all_results.append({
                'category': category,
                'commons_title': title,
                'word': word,
                'commons_url': commons_url,
                'wikidata_id': wikidata_id if wikidata_id else '',
                'wikidata_url': wikidata_url,
                'sona_exists': 'Yes' if sona_exists else 'No',
                'sona_url': sona_url,
                'tok_exists': 'Yes' if tok_exists else 'No',
                'tok_url': tok_url
            })

    # Write to CSV
    output_file = 'tokipona_wiki_coverage.csv'
    print(f"\n{'='*60}", flush=True)
    print(f"Writing results to {output_file}...", flush=True)

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = [
            'category', 'word', 'commons_title', 'commons_url',
            'wikidata_id', 'wikidata_url',
            'sona_exists', 'sona_url',
            'tok_exists', 'tok_url'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_results)

    print(f"✓ Done! Processed {len(all_results)} items", flush=True)

    # Print summary statistics
    sona_count = sum(1 for r in all_results if r['sona_exists'] == 'Yes')
    tok_count = sum(1 for r in all_results if r['tok_exists'] == 'Yes')
    wikidata_count = sum(1 for r in all_results if r['wikidata_id'])

    print(f"\nSummary:", flush=True)
    print(f"  Total items: {len(all_results)}", flush=True)
    print(f"  With Wikidata: {wikidata_count} ({wikidata_count*100//len(all_results)}%)", flush=True)
    print(f"  On sona.pona.la: {sona_count} ({sona_count*100//len(all_results)}%)", flush=True)
    print(f"  On tok.wikipedia.org: {tok_count} ({tok_count*100//len(all_results)}%)", flush=True)

if __name__ == "__main__":
    main()
