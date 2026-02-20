"""
Batch generate sitelen kalama pona SVGs for all toki pona Wikipedia titles.

Reads wikidata_toki_pona_names.txt (one title per line) and runs
generate_sitelen_kalama_pona.generate() for each one.

Usage:
    python batch_generate_svgs.py
"""

import sys
from pathlib import Path

from generate_sitelen_kalama_pona import generate

SCRIPT_DIR = Path(__file__).parent
ROOT_DIR = SCRIPT_DIR.parent


def main():
    names_file = ROOT_DIR / 'data' / 'wikidata_toki_pona_names.txt'
    if not names_file.exists():
        print(f'Missing {names_file} - run process_wikidata_toki_pona.py first',
              file=sys.stderr)
        sys.exit(1)

    titles = [line.strip() for line in
              names_file.read_text(encoding='utf-8').splitlines()
              if line.strip()]

    print(f'Generating SVGs for {len(titles)} titles...\n')

    success = 0
    failed = []

    for i, title in enumerate(titles, 1):
        print(f'[{i}/{len(titles)}] {title}')
        try:
            generate(title)
            success += 1
        except Exception as exc:
            print(f'  ERROR: {exc}')
            failed.append((title, str(exc)))
        print()

    print(f'\nDone! {success} succeeded, {len(failed)} failed.')
    if failed:
        print('\nFailed titles:')
        for title, err in failed:
            print(f'  {title}: {err}')


if __name__ == '__main__':
    main()
