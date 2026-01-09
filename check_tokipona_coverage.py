import requests
import time
import sys
import io
import csv
from collections import defaultdict

# Fix Unicode encoding on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# API endpoints
SONAPONA_API = "https://sonapona.miraheze.org/w/api.php"
SIMPLEWIKI_API = "https://simple.wikipedia.org/w/api.php"
WIKIDATA_SPARQL = "https://query.wikidata.org/sparql"

def get_pages_from_category(category_name):
    """Get all pages from a specific category on sona pona wiki"""
    pages = []
    params = {
        'action': 'query',
        'list': 'categorymembers',
        'cmtitle': f'Category:{category_name}',
        'cmlimit': 'max',
        'format': 'json',
        'cmnamespace': 0  # Main namespace only
    }

    while True:
        try:
            response = requests.get(SONAPONA_API, params=params, headers={'User-Agent': 'TokiPona-Coverage-Checker/1.0'})
            if response.status_code != 200:
                print(f"  ERROR: Got status code {response.status_code}")
                break

            data = response.json()

            if 'query' in data and 'categorymembers' in data['query']:
                for page in data['query']['categorymembers']:
                    title = page['title']
                    # Only include single words (no spaces)
                    if ' ' not in title and title.islower():
                        pages.append(title)

            if 'continue' in data:
                params.update(data['continue'])
            else:
                break

            time.sleep(0.3)

        except Exception as e:
            print(f"  ERROR: {e}")
            break

    return pages

def get_sonapona_words():
    """Get all Toki Pona words from sona pona wiki using authoritative sources"""
    print("Fetching words from sona pona wiki...")

    # Obscure words list from user
    obscure_words = [
        'apeja', 'isipin', 'jami', 'jonke', 'kamalawala', 'kapesi', 'kese', 'kiki',
        'kokosila', 'konwe', 'kulijo', 'melome', 'mijomi', 'misa', 'mulapisu', 'nja',
        'ojuta', 'oke', 'omekapo', 'owe', 'pake', 'pakola', 'penpo', 'peto', 'pika',
        'po', 'powe', 'puwa', 'san', 'soto', 'sutopatikuna', 'taki', 'te', 'teje',
        'to', 'unu', 'usawi', 'wa', 'wasoweli', 'wekama', 'wuwojiti', 'yupekosi',
        'epiku', 'jasima', 'lanpan', 'linluwi', 'majuna', 'meso', 'nimisin', 'oko', 'su'
    ]

    # Get words from "Words not included in the Linku survey" category
    print("  Fetching from Category:Words not included in the Linku survey...")
    linku_excluded = get_pages_from_category('Words not included in the Linku survey')
    print(f"    Found {len(linku_excluded)} words from Linku exclusion category")

    # Combine all sources
    all_words = set(obscure_words) | set(linku_excluded)

    print(f"  Total: {len(all_words)} words on sona pona\n")
    return all_words

def get_simplewiki_words():
    """Get words from Simple English Wikipedia's List of Toki Pona words"""
    print("Fetching from Simple English Wikipedia...")

    params = {
        'action': 'parse',
        'page': 'List of Toki Pona words',
        'format': 'json',
        'prop': 'wikitext'
    }

    try:
        response = requests.get(SIMPLEWIKI_API, params=params, headers={'User-Agent': 'TokiPona-Coverage-Checker/1.0'})

        if response.status_code != 200:
            print(f"  ERROR: Got status code {response.status_code}")
            return set()

        data = response.json()

        if 'parse' not in data or 'wikitext' not in data['parse']:
            print("  ERROR: Could not get wikitext")
            return set()

        wikitext = data['parse']['wikitext']['*']

        # Extract words - they appear in various formats in the list
        # Simple heuristic: look for lines that start with a word (lowercase toki pona word)
        import re
        words = set()

        # Pattern to find toki pona words (usually lowercase, may have hyphens)
        for line in wikitext.split('\n'):
            # Look for table rows or list items with toki pona words
            match = re.search(r'\|\s*([a-z][a-z\-]*[a-z]|[a-z])\s*\|', line)
            if match:
                word = match.group(1).strip()
                if word and len(word) <= 20:  # Reasonable word length
                    words.add(word)

        print(f"  Found {len(words)} words on Simple Wikipedia\n")
        return words

    except Exception as e:
        print(f"  ERROR: {e}")
        return set()

def get_wikidata_words():
    """Query Wikidata for all Toki Pona words - first find the correct class"""
    print("Querying Wikidata for Toki Pona words...")

    # First, query what "jan" is an instance of to find the correct class
    discover_query = """
    SELECT ?class ?classLabel WHERE {
      wd:Q105816257 wdt:P31 ?class .
      SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
    }
    """

    try:
        # First discover what class "jan" belongs to
        response = requests.get(
            WIKIDATA_SPARQL,
            params={'query': discover_query, 'format': 'json'},
            headers={'User-Agent': 'TokiPona-Coverage-Checker/1.0'}
        )

        tokipona_word_class = None
        if response.status_code == 200:
            data = response.json()
            for result in data['results']['bindings']:
                class_qid = result['class']['value'].split('/')[-1]
                class_label = result['classLabel']['value']
                print(f"  'jan' is instance of: {class_qid} ({class_label})")
                if 'tok' in class_label.lower() or 'word' in class_label.lower():
                    tokipona_word_class = class_qid

        # Query all Toki Pona words using Miraheze links
        sparql_query = """
        SELECT DISTINCT ?item ?itemLabel ?miraheze WHERE {
          # Get items with Miraheze links starting with "sonapona:"
          ?item wdt:P11250 ?miraheze .
          FILTER(STRSTARTS(?miraheze, "sonapona:"))

          SERVICE wikibase:label { bd:serviceParam wikibase:language "tok,en". }
        }
        """
        response = requests.get(
            WIKIDATA_SPARQL,
            params={'query': sparql_query, 'format': 'json'},
            headers={'User-Agent': 'TokiPona-Coverage-Checker/1.0'}
        )

        if response.status_code != 200:
            print(f"  ERROR: Got status code {response.status_code}")
            return set(), {}

        data = response.json()

        words = set()
        word_info = {}  # Map word -> {qid, miraheze}

        for result in data['results']['bindings']:
            label = result['itemLabel']['value']
            qid = result['item']['value'].split('/')[-1]
            miraheze = result.get('miraheze', {}).get('value', '')

            # Only include single words (no spaces)
            if ' ' not in label and label.islower():
                words.add(label)
                word_info[label] = {
                    'qid': qid,
                    'miraheze': miraheze
                }

        print(f"  Found {len(words)} words on Wikidata\n")
        return words, word_info

    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()
        return set(), {}

def main():
    print("=" * 70)
    print("Toki Pona Words Coverage Analysis")
    print("Checking: sona pona, Simple Wikipedia, and Wikidata")
    print("=" * 70)
    print()

    # Fetch from all three sources
    sonapona_words = get_sonapona_words()
    simplewiki_words = get_simplewiki_words()
    wikidata_words, wikidata_info = get_wikidata_words()

    # Build coverage map
    all_words = sonapona_words | simplewiki_words | wikidata_words

    coverage = defaultdict(lambda: {'sonapona': False, 'simplewiki': False, 'wikidata': False})

    for word in all_words:
        if word in sonapona_words:
            coverage[word]['sonapona'] = True
        if word in simplewiki_words:
            coverage[word]['simplewiki'] = True
        if word in wikidata_words:
            coverage[word]['wikidata'] = True

    # Categorize
    in_all_three = []
    in_sonapona_wikidata = []
    in_sonapona_simplewiki = []
    in_wikidata_simplewiki = []
    only_sonapona = []
    only_simplewiki = []
    only_wikidata = []

    for word, sources in coverage.items():
        count = sum(sources.values())

        if count == 3:
            in_all_three.append(word)
        elif count == 2:
            if sources['sonapona'] and sources['wikidata']:
                in_sonapona_wikidata.append(word)
            elif sources['sonapona'] and sources['simplewiki']:
                in_sonapona_simplewiki.append(word)
            elif sources['wikidata'] and sources['simplewiki']:
                in_wikidata_simplewiki.append(word)
        elif count == 1:
            if sources['sonapona']:
                only_sonapona.append(word)
            elif sources['simplewiki']:
                only_simplewiki.append(word)
            elif sources['wikidata']:
                only_wikidata.append(word)

    # Print summary
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    print()

    print(f"📊 Total unique words: {len(all_words)}")
    print(f"  → In all three sources: {len(in_all_three)}")
    print(f"  → In sona pona + Wikidata only: {len(in_sonapona_wikidata)}")
    print(f"  → In sona pona + Simple Wiki only: {len(in_sonapona_simplewiki)}")
    print(f"  → In Wikidata + Simple Wiki only: {len(in_wikidata_simplewiki)}")
    print(f"  → Only in sona pona: {len(only_sonapona)}")
    print(f"  → Only in Simple Wikipedia: {len(only_simplewiki)}")
    print(f"  → Only in Wikidata: {len(only_wikidata)}")
    print()

    # Save comprehensive CSV
    with open('tokipona_coverage.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Word', 'In Sona Pona', 'In Simple Wiki', 'In Wikidata', 'Coverage'])

        for word in sorted(all_words):
            sources = coverage[word]
            coverage_str = ', '.join([k for k, v in sources.items() if v])
            writer.writerow([
                word,
                'Yes' if sources['sonapona'] else 'No',
                'Yes' if sources['simplewiki'] else 'No',
                'Yes' if sources['wikidata'] else 'No',
                coverage_str
            ])

    print("✓ Saved: tokipona_coverage.csv")

    # Save individual gap CSVs
    with open('only_sonapona.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Word', 'Sonapona URL'])
        for word in sorted(only_sonapona):
            writer.writerow([word, f"https://sonapona.miraheze.org/wiki/{word.replace(' ', '_')}"])

    print(f"✓ Saved: only_sonapona.csv ({len(only_sonapona)} entries)")

    with open('only_wikidata.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Word', 'Wikidata QID', 'Has Miraheze Link', 'Wikidata URL'])
        for word in sorted(only_wikidata):
            info = wikidata_info.get(word, {})
            qid = info.get('qid', '')
            miraheze = info.get('miraheze', '')
            wikidata_url = f"https://www.wikidata.org/wiki/{qid}" if qid else ''
            writer.writerow([word, qid, 'Yes' if miraheze else 'No', wikidata_url])

    print(f"✓ Saved: only_wikidata.csv ({len(only_wikidata)} entries)")

    with open('only_simplewiki.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Word'])
        for word in sorted(only_simplewiki):
            writer.writerow([word])

    print(f"✓ Saved: only_simplewiki.csv ({len(only_simplewiki)} entries)")
    print()

if __name__ == "__main__":
    main()
