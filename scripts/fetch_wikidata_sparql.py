"""
Fetch all Wikidata items that have a Toki Pona (tok) label via SPARQL.

Outputs data/wikidata_tok_labels.csv with columns: qid, label, tok_title
  tok_title is the tok.wikipedia.org article title (empty if none).

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

API_URL = 'https://www.wikidata.org/w/api.php'
USER_AGENT = 'SitelenBot/1.0 (https://github.com/Emma-Leonhart/Sitelen)'


def fetch_wikidata_search(limit=500, continue_token=None):
    """Fetch items with Toki Pona labels using the Wikidata Search API."""
    params = {
        'action': 'query',
        'list': 'search',
        'srsearch': 'haslabel:tok',
        'srlimit': str(limit),
        'format': 'json',
    }
    if continue_token:
        params['sroffset'] = str(continue_token)

    url = API_URL + '?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={
        'User-Agent': USER_AGENT,
    })

    retries = 4
    delay = 2
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
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

    print('Fetching Wikidata items with Toki Pona labels via Search API...')

    rows = []
    offset = 0

    while True:
        data = fetch_wikidata_search(continue_token=offset)
        if 'query' not in data or 'search' not in data['query']:
            break

        results = data['query']['search']
        for item in results:
            qid = item['title']
            rows.append({'qid': qid, 'label': qid})

        print(f'  ...found {len(rows)} items')

        if 'continue' in data:
            offset = data['continue']['sroffset']
        else:
            break

    print(f'Fetching actual "tok" labels and sitelinks for {len(rows)} QIDs...')
    final_rows = []

    for i in range(0, len(rows), 50):
        batch = rows[i:i+50]
        qids = '|'.join(r['qid'] for r in batch)

        params = {
            'action': 'wbgetentities',
            'ids': qids,
            'props': 'labels|sitelinks',
            'languages': 'tok',
            'sitefilter': 'tokwiki',
            'format': 'json',
        }
        url = API_URL + '?' + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})

        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode('utf-8'))

        entities = data.get('entities', {})
        for qid, entity in entities.items():
            label_obj = entity.get('labels', {}).get('tok', {})
            label = label_obj.get('value')
            if label:
                tok_title = entity.get('sitelinks', {}).get('tokwiki', {}).get('title', '')
                final_rows.append({'qid': qid, 'label': label, 'tok_title': tok_title})

        if (i // 50) % 5 == 0:
            print(f'  Progress: {len(final_rows)} labels fetched')

    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['qid', 'label', 'tok_title'])
        writer.writeheader()
        writer.writerows(final_rows)

    print(f'Total found {len(final_rows)} items with "tok" labels. Wrote {out_path}')

    names_path = DATA_DIR / 'wikidata_toki_pona_names.txt'
    with open(names_path, 'w', encoding='utf-8') as f:
        for row in final_rows:
            f.write(row['label'] + '\n')
    print(f'Wrote {names_path}')


if __name__ == '__main__':
    main()
