"""
Process toki pona Wikipedia page titles from the fetched CSV.

Reads wikidata_toki_pona.csv (pageid, title) and:
  1. Filters to titles that contain at least one valid toki pona word or proper name
  2. Writes wikidata_toki_pona_names.txt (one title per line, for batch SVG generation)
"""

import csv
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
ROOT_DIR = SCRIPT_DIR.parent
WORD_SVGS_DIR = ROOT_DIR / 'sitelen_seli_kiwen_svgs'


def get_known_words():
    """Get the set of toki pona words that have SVG glyphs."""
    words = set()
    for f in WORD_SVGS_DIR.glob('Sitelen seli kiwen - *.svg'):
        name = f.stem.replace('Sitelen seli kiwen - ', '')
        # Single words only (compounds have hyphens)
        if '-' not in name:
            words.add(name)
    return words


def is_processable(title, known_words):
    """Check if a title can produce any SVG content.

    A title is processable if it contains at least one known toki pona word
    or a capitalized proper name (which would become a sound cartouche).
    """
    tokens = title.split()
    for token in tokens:
        if token.lower() in known_words:
            return True
        # Capitalized token with only letters = proper name for cartouche
        if token[0].isupper() and re.match(r'^[A-Za-z]+$', token):
            return True
    return False


def main():
    src = ROOT_DIR / 'data' / 'wikidata_toki_pona.csv'
    out_names = ROOT_DIR / 'data' / 'wikidata_toki_pona_names.txt'

    if not src.exists():
        print(f'Missing input: {src}', file=sys.stderr)
        sys.exit(1)

    known_words = get_known_words()
    print(f'Known toki pona word glyphs: {len(known_words)}')

    titles = []
    skipped = []

    with open(src, 'r', encoding='utf-8', newline='') as f:
        for row in csv.DictReader(f):
            title = row['title'].strip()
            if not title:
                continue
            if is_processable(title, known_words):
                titles.append(title)
            else:
                skipped.append(title)

    with open(out_names, 'w', encoding='utf-8') as f:
        for title in titles:
            f.write(title + '\n')

    print(f'Processable titles: {len(titles)}')
    print(f'Skipped titles: {len(skipped)}')
    if skipped:
        print(f'  Examples of skipped: {skipped[:10]}')
    print(f'Wrote {out_names}')


if __name__ == '__main__':
    main()
