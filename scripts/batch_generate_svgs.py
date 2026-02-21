"""
Batch generate sitelen kalama pona SVGs for all toki pona Wikipedia titles.

Reads wikidata_toki_pona_names.txt (one title per line) and runs
generate_sitelen_kalama_pona.generate() for each one.

Usage:
    python batch_generate_svgs.py
"""

import csv
import json
import sys
from pathlib import Path

from generate_sitelen_kalama_pona import generate

SCRIPT_DIR = Path(__file__).parent
ROOT_DIR = SCRIPT_DIR.parent


def main():
    csv_file = ROOT_DIR / 'data' / 'wikidata_tok_labels.csv'
    if not csv_file.exists():
        print(f'Missing {csv_file} - run fetch_wikidata_sparql.py first',
              file=sys.stderr)
        sys.exit(1)

    rows = []
    with open(csv_file, encoding='utf-8', newline='') as f:
        for row in csv.DictReader(f):
            rows.append({'qid': row['qid'], 'label': row['label']})

    print(f'Generating SVGs for {len(rows)} titles...\n')

    success = 0
    failed = []
    index = {}  # filename -> qid

    for i, row in enumerate(rows, 1):
        label, qid = row['label'], row['qid']
        print(f'[{i}/{len(rows)}] {label}')
        try:
            output_path = generate(label)
            if output_path:
                index[output_path.name] = qid
            success += 1
        except Exception as exc:
            print(f'  ERROR: {exc}')
            failed.append((label, str(exc)))
        print()

    index_path = ROOT_DIR / 'data' / 'output_index.json'
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=None)
    print(f'Wrote {index_path} ({len(index)} entries)')

    print(f'\nDone! {success} succeeded, {len(failed)} failed.')
    if failed:
        print('\nFailed titles:')
        for title, err in failed:
            print(f'  {title}: {err}')


if __name__ == '__main__':
    main()
