import requests
import time
import sys
import io
import csv

# Fix Unicode encoding on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# API endpoints
SONAPONA_API = "https://sonapona.miraheze.org/w/api.php"
WIKIDATA_API = "https://www.wikidata.org/w/api.php"
WIKIDATA_SPARQL = "https://query.wikidata.org/sparql"

def get_sonapona_categories():
    """Get all categories from sona pona wiki to find word categories"""
    print("Fetching categories from sona pona wiki...")

    params = {
        'action': 'query',
        'list': 'allcategories',
        'aclimit': 'max',
        'format': 'json'
    }

    try:
        response = requests.get(SONAPONA_API, params=params, headers={'User-Agent': 'SonaPona-Wikidata-Checker/1.0'})
        print(f"Status code: {response.status_code}")

        if response.status_code != 200:
            print(f"ERROR: Got status code {response.status_code}")
            print(f"Response text: {response.text[:500]}")
            return []

        data = response.json()
    except Exception as e:
        print(f"ERROR fetching categories: {e}")
        print(f"Response text: {response.text[:500] if 'response' in locals() else 'No response'}")
        return []

    categories = []
    if 'query' in data and 'allcategories' in data['query']:
        for cat in data['query']['allcategories']:
            categories.append(cat['*'])

    print(f"Found {len(categories)} categories")
    for cat in sorted(categories):
        if 'word' in cat.lower() or 'nimi' in cat.lower():
            print(f"  → {cat}")
    print()

    return categories

def get_pages_in_category(category):
    """Get all pages in a specific category"""
    print(f"Fetching pages in category: {category}...")

    pages = []
    params = {
        'action': 'query',
        'list': 'categorymembers',
        'cmtitle': f'Category:{category}',
        'cmlimit': 'max',
        'format': 'json',
        'cmnamespace': 0  # Main namespace only
    }

    while True:
        try:
            response = requests.get(SONAPONA_API, params=params, headers={'User-Agent': 'SonaPona-Wikidata-Checker/1.0'})

            if response.status_code != 200:
                print(f"  ERROR: Got status code {response.status_code}")
                break

            data = response.json()
        except Exception as e:
            print(f"  ERROR fetching category members: {e}")
            print(f"  Response text: {response.text[:200] if 'response' in locals() else 'No response'}")
            break

        if 'query' in data and 'categorymembers' in data['query']:
            for page in data['query']['categorymembers']:
                pages.append(page['title'])

        # Check for continuation
        if 'continue' in data:
            params.update(data['continue'])
        else:
            break

        time.sleep(0.5)

    print(f"Found {len(pages)} pages in {category}\n")
    return pages

def query_wikidata_for_sonapona_links():
    """Query Wikidata for all items with sonapona Miraheze links"""
    print("Querying Wikidata for items with sonapona links...")

    # SPARQL query to find all items with P11250 (Miraheze article ID) starting with "sonapona:"
    sparql_query = """
    SELECT ?item ?itemLabel ?miraheze WHERE {
      ?item wdt:P11250 ?miraheze .
      FILTER(STRSTARTS(?miraheze, "sonapona:"))
      SERVICE wikibase:label { bd:serviceParam wikibase:language "en,tok". }
    }
    """

    response = requests.get(
        WIKIDATA_SPARQL,
        params={'query': sparql_query, 'format': 'json'},
        headers={'User-Agent': 'SonaPona Wikidata Checker/1.0'}
    )

    if response.status_code != 200:
        print(f"ERROR: Wikidata query failed with status {response.status_code}")
        return {}

    data = response.json()

    # Build mapping: page_title -> wikidata_item
    wikidata_map = {}
    for result in data['results']['bindings']:
        miraheze_id = result['miraheze']['value']
        # Extract page name from "sonapona:Page_Name"
        page_name = miraheze_id.replace('sonapona:', '').replace('_', ' ')

        item_uri = result['item']['value']
        item_id = item_uri.split('/')[-1]  # Extract Q12345 from URI
        item_label = result.get('itemLabel', {}).get('value', 'Unknown')

        wikidata_map[page_name] = {
            'qid': item_id,
            'label': item_label,
            'miraheze_id': miraheze_id
        }

    print(f"Found {len(wikidata_map)} items on Wikidata with sonapona links\n")
    return wikidata_map

def main():
    print("=" * 70)
    print("Checking sona pona wiki pages against Wikidata")
    print("=" * 70)
    print()

    # First, explore categories to find word categories
    categories = get_sonapona_categories()

    # Ask user which category to check, or check common word categories
    word_categories = [cat for cat in categories if 'word' in cat.lower() or 'nimi' in cat.lower()]

    if not word_categories:
        print("No obvious word categories found. Checking all main namespace pages...")
        # Fall back to getting all pages
        params = {
            'action': 'query',
            'list': 'allpages',
            'aplimit': 'max',
            'format': 'json',
            'apnamespace': 0
        }
        response = requests.get(SONAPONA_API, params=params)
        data = response.json()
        sonapona_pages = [p['title'] for p in data['query']['allpages']]
    else:
        # Get pages from all word categories
        sonapona_pages = set()
        for cat in word_categories:
            pages = get_pages_in_category(cat)
            sonapona_pages.update(pages)
        sonapona_pages = list(sonapona_pages)

    print(f"Total unique word pages from sona pona: {len(sonapona_pages)}\n")

    # Get all Wikidata items with sonapona links
    wikidata_map = query_wikidata_for_sonapona_links()

    # Build reverse lookup: which Wikidata items DON'T have sonapona pages?
    wikidata_pages_set = set(wikidata_map.keys())
    sonapona_pages_set = set(sonapona_pages)

    # CSV 1: Sonapona words WITHOUT Wikidata
    sonapona_no_wikidata = sorted(sonapona_pages_set - wikidata_pages_set)

    # CSV 2: Wikidata items WITHOUT sonapona pages
    # These are items that have P11250 starting with "sonapona:" but the page doesn't exist
    wikidata_no_sonapona = []
    for page, info in wikidata_map.items():
        if page not in sonapona_pages_set:
            wikidata_no_sonapona.append((page, info['qid'], info['label'], info['miraheze_id']))

    # Report results
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    print()

    print(f"📊 Summary:")
    print(f"  Sonapona words checked: {len(sonapona_pages)}")
    print(f"  Wikidata items with sonapona links: {len(wikidata_map)}")
    print(f"  Sonapona words WITHOUT Wikidata: {len(sonapona_no_wikidata)}")
    print(f"  Wikidata items WITHOUT sonapona page: {len(wikidata_no_sonapona)}")
    print()

    # Save CSV 1: Sonapona words without Wikidata
    csv1_path = 'sonapona_no_wikidata.csv'
    with open(csv1_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Page Title', 'Sonapona URL'])
        for page in sonapona_no_wikidata:
            url = f"https://sonapona.miraheze.org/wiki/{page.replace(' ', '_')}"
            writer.writerow([page, url])

    print(f"✓ Saved: {csv1_path} ({len(sonapona_no_wikidata)} entries)")

    # Save CSV 2: Wikidata items without sonapona page
    csv2_path = 'wikidata_no_sonapona.csv'
    with open(csv2_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Wikidata QID', 'Label', 'Expected Sonapona Page', 'Miraheze ID', 'Wikidata URL'])
        for page, qid, label, miraheze_id in wikidata_no_sonapona:
            wikidata_url = f"https://www.wikidata.org/wiki/{qid}"
            writer.writerow([qid, label, page, miraheze_id, wikidata_url])

    print(f"✓ Saved: {csv2_path} ({len(wikidata_no_sonapona)} entries)")
    print()

    # Preview results
    if sonapona_no_wikidata:
        print("Sample sonapona words WITHOUT Wikidata (first 10):")
        for page in sonapona_no_wikidata[:10]:
            print(f"  • {page}")
        print()

    if wikidata_no_sonapona:
        print("Sample Wikidata items WITHOUT sonapona page (first 10):")
        for page, qid, label, miraheze_id in wikidata_no_sonapona[:10]:
            print(f"  • {qid}: {label} (expects: {page})")
        print()

if __name__ == "__main__":
    main()
