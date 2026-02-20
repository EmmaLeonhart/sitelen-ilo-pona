"""
Fetch all Wikidata items that have a Toki Pona (tok) label via SPARQL.

Outputs data/wikidata_tok_labels.csv with columns: qid, label

Usage:
    python scripts/fetch_wikidata_sparql.py
"""

import csv
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = ROOT_DIR / 'data'

SPARQL_ENDPOINT = 'https://query.wikidata.org/sparql'
USER_AGENT = 'SitelenBot/1.0 (https://github.com/Emma-Leonhart/Sitelen)'

QUERY = """
SELECT ?item ?label WHERE {
  ?item rdfs:label ?label .
  FILTER(LANG(?label) = "tok")
}
ORDER BY ?item
"""


def fetch_sparql(query, retries=4):
    """Run a SPARQL query against the Wikidata endpoint, with retry on failure."""
    params = urllib.parse.urlencode({
        'query': query,
        'format': 'json',
    })
    url = f'{SPARQL_ENDPOINT}?{params}'
    req = urllib.request.Request(url, headers={
        'User-Agent': USER_AGENT,
        'Accept': 'application/sparql-results+json',
    })

    delay = 2
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                return json.loads(resp.read().decode('utf-8'))
        except Exception as exc:
            if attempt == retries - 1:
                raise
            print(f'  Attempt {attempt + 1} failed: {exc}. Retrying in {delay}s...',
                  file=sys.stderr)
            time.sleep(delay)
            delay *= 2


def main():
    DATA_DIR.mkdir(exist_ok=True)
    out_path = DATA_DIR / 'wikidata_tok_labels.csv'

    print('Querying Wikidata for items with Toki Pona labels...')
    data = fetch_sparql(QUERY)

    rows = []
    for binding in data['results']['bindings']:
        item_uri = binding['item']['value']
        label = binding['label']['value']
        qid = item_uri.split('/')[-1]
        rows.append({'qid': qid, 'label': label})

    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['qid', 'label'])
        writer.writeheader()
        writer.writerows(rows)

    print(f'Found {len(rows)} items. Wrote {out_path}')

    # Also write the plain label list for batch_generate_svgs.py
    names_path = DATA_DIR / 'wikidata_toki_pona_names.txt'
    with open(names_path, 'w', encoding='utf-8') as f:
        for row in rows:
            f.write(row['label'] + '\n')
    print(f'Wrote {names_path}')


if __name__ == '__main__':
    main()
