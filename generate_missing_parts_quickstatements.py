"""
Generate QuickStatements to add P527 (has part) with P1545 (series ordinal) qualifiers
for ligatures that are missing these properties.

Input: query (1).csv - Wikidata query results for ligatures without P527
"""
import io
import sys
import csv

# Fix Windows encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def get_toki_pona_word_qids():
    """
    Load Toki Pona word QIDs from tokipona_wiki_coverage.csv
    Returns a dict mapping word label -> QID
    """
    print("Loading Toki Pona word QIDs from local CSV...", flush=True)

    word_to_qid = {}

    # Categories that contain individual Toki Pona words
    valid_categories = [
        'Category:Toki Pona logograms by word',
        'Category:Toki pona rare words',
    ]

    # Words to skip (not actual words, but subcategory names)
    skip_words = [
        'sitelen Pona ligatures',
        'toki Pona Logograms unsorted by word',
        'toki pona rare words',
    ]

    with open('tokipona_wiki_coverage.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            category = row.get('category', '')
            word = row.get('word', '').strip()
            wikidata_id = row.get('wikidata_id', '').strip()

            # Include words from valid categories, but skip compound words and category names
            if (category in valid_categories and
                wikidata_id and
                ' ' not in word and
                word not in skip_words):

                word_to_qid[word.lower()] = wikidata_id

    # Add manual mappings for common variants/aliases
    # ali is an alternate spelling of ale
    if 'ale' in word_to_qid and 'ali' not in word_to_qid:
        word_to_qid['ali'] = word_to_qid['ale']

    print(f"Found {len(word_to_qid)} Toki Pona vocabulary words", flush=True)
    return word_to_qid


def load_missing_ligatures():
    """
    Load ligatures missing P527 from query (1).csv
    Returns a list of (qid, label) tuples
    """
    ligatures = []

    # Items to skip (not actual ligatures)
    skip_labels = [
        'toki pona ligatures',
    ]

    with open('query (1).csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            item_url = row.get('item', '')
            label = row.get('itemLabel', '').strip()

            # Extract QID from URL
            if '/entity/' in item_url:
                qid = item_url.split('/entity/')[-1]
            else:
                continue

            # Skip non-ligatures
            if label in skip_labels:
                continue

            # Only include multi-word items (actual ligatures)
            if ' ' in label:
                ligatures.append((qid, label))

    print(f"Found {len(ligatures)} ligatures missing P527", flush=True)
    return ligatures


def generate_quickstatements(ligatures, word_to_qid):
    """
    Generate QuickStatements for P527 (has part) with P1545 (series ordinal) qualifiers.

    Format: Q_compound|P527|Q_part|P1545|ordinal
    """
    statements = []
    missing_words = set()

    for qid, label in ligatures:
        parts = label.split()

        for i, part in enumerate(parts):
            part_lower = part.lower()

            if part_lower in word_to_qid:
                part_qid = word_to_qid[part_lower]
                ordinal = i + 1

                # QuickStatements V1 format for qualifier:
                # SUBJECT|PROP|TARGET|QUAL_PROP|QUAL_VALUE
                statement = f"{qid}|P527|{part_qid}|P1545|\"{ordinal}\""
                statements.append({
                    'statement': statement,
                    'compound': label,
                    'compound_qid': qid,
                    'part': part,
                    'part_qid': part_qid,
                    'ordinal': ordinal
                })
            else:
                missing_words.add(part_lower)

    return statements, missing_words


def main():
    print("="*70, flush=True)
    print("Generating P527 (has part) QuickStatements for MISSING ligatures", flush=True)
    print("="*70, flush=True)
    print()

    # Step 1: Get Toki Pona word QIDs
    word_to_qid = get_toki_pona_word_qids()

    if not word_to_qid:
        print("ERROR: Could not load word QIDs!", flush=True)
        return

    # Show some sample words
    print("\nSample word QIDs:", flush=True)
    for word, qid in list(word_to_qid.items())[:10]:
        print(f"  {word}: {qid}", flush=True)

    # Step 2: Load missing ligatures
    ligatures = load_missing_ligatures()

    if not ligatures:
        print("ERROR: No ligatures found!", flush=True)
        return

    # Show some sample ligatures
    print("\nSample missing ligatures:", flush=True)
    for qid, label in ligatures[:10]:
        print(f"  {label}: {qid}", flush=True)

    # Step 3: Generate QuickStatements
    print("\nGenerating QuickStatements...", flush=True)
    statements, missing_words = generate_quickstatements(ligatures, word_to_qid)

    print(f"\nGenerated {len(statements)} statements for {len(ligatures)} ligatures", flush=True)

    if missing_words:
        print(f"\nWARNING: {len(missing_words)} words not found in vocabulary:", flush=True)
        for word in sorted(missing_words):
            print(f"  - {word}", flush=True)

    # Step 4: Write output files
    output_file = 'missing_parts_quickstatements.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        for item in statements:
            f.write(item['statement'] + '\n')

    print(f"\nQuickStatements saved to: {output_file}", flush=True)

    # Write detailed output
    detail_file = 'missing_parts_quickstatements_details.txt'
    with open(detail_file, 'w', encoding='utf-8') as f:
        f.write("P527 (has part) with P1545 (series ordinal) QuickStatements\n")
        f.write("For ligatures that were missing these properties\n")
        f.write("="*80 + "\n\n")
        f.write(f"Total statements: {len(statements)}\n")
        f.write(f"Total ligatures: {len(ligatures)}\n\n")

        # Group by compound word
        current_compound = None
        for item in statements:
            if item['compound'] != current_compound:
                current_compound = item['compound']
                f.write(f"\n{current_compound} ({item['compound_qid']}):\n")
            f.write(f"  [{item['ordinal']}] {item['part']} ({item['part_qid']})\n")

    print(f"Detailed list saved to: {detail_file}", flush=True)

    # Show sample output
    print("\nSample QuickStatements (first 20):", flush=True)
    for item in statements[:20]:
        print(f"  {item['statement']}", flush=True)

    print("\nDone!", flush=True)


if __name__ == "__main__":
    main()
