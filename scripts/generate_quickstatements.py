"""
Generate QuickStatements to add P18 (image) claims on Wikidata items.

Reads data/wikidata_tok_labels.csv (qid, label) and output/ SVG files.
For each QID whose label has a generated SVG in output/, emits a
QuickStatements line to add the image on Wikimedia Commons as P18.

Output: data/quickstatements.txt

Usage:
    python scripts/generate_quickstatements.py
"""

import csv
import re
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = ROOT_DIR / 'data'
OUTPUT_DIR = ROOT_DIR / 'output'

COMMONS_BASE = 'https://commons.wikimedia.org/wiki/File:'


def safe_filename(text):
    """Produce a filesystem-safe version of text (mirrors generate_sitelen_kalama_pona.py)."""
    return re.sub(r'[<>:"/\\|?*]', '_', text)


def commons_filename(label):
    """The expected Wikimedia Commons filename for a given label."""
    # SVG files are named 'sitelen kalama pona - {label}.svg'
    # Commons convention: capitalise first letter, underscores for spaces
    name = f'Sitelen kalama pona - {label}.svg'
    return name.replace(' ', '_')


def main():
    DATA_DIR.mkdir(exist_ok=True)
    labels_path = DATA_DIR / 'wikidata_tok_labels.csv'

    if not labels_path.exists():
        print(f'Missing {labels_path} — run fetch_wikidata_sparql.py first')
        return

    rows = []
    with open(labels_path, 'r', encoding='utf-8', newline='') as f:
        rows = list(csv.DictReader(f))

    lines = []
    skipped = 0

    for row in rows:
        qid = row['qid'].strip()
        label = row['label'].strip()
        if not qid or not label:
            continue

        # Check if an SVG was generated for this label
        svg_name = f'sitelen kalama pona - {safe_filename(label)}.svg'
        svg_path = OUTPUT_DIR / svg_name
        if not svg_path.exists():
            skipped += 1
            continue

        cf = commons_filename(label)
        commons_url = COMMONS_BASE + cf.replace(' ', '_')

        # QuickStatements V1 format:
        # QID <tab> P18 <tab> "filename" <tab> S854 <tab> "source-url"
        line = f'{qid}\tP18\t"{cf}"\tS854\t"{commons_url}"'
        lines.append(line)

    out_path = DATA_DIR / 'quickstatements.txt'
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')

    print(f'Generated {len(lines)} QuickStatements lines '
          f'({skipped} labels skipped — no SVG output).')
    print(f'Wrote {out_path}')
    print()
    print('To apply: go to https://quickstatements.toolforge.org/ and paste the file contents.')


if __name__ == '__main__':
    main()
