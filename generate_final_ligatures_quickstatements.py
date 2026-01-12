"""
Generate QuickStatements ONLY for the 92 ligatures that don't exist yet
Excluding the 11 rare words that already exist on Wikidata
"""
import csv
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# The 11 rare words that already exist
EXISTING_ITEMS = {
    'jonke': 'Q137768887',
    'kisa': 'Q137768888',
    'kutopoma': 'Q137768889',
    'linluwi': 'Q137768891',
    'melome': 'Q137768892',
    'mulapisu': 'Q137768893',
    'nimisin': 'Q137768894',
    'nja': 'Q137768895',
    'soto': 'Q137768896',
    'sutopatikuna': 'Q137768897',
    'teje': 'Q137768898'
}

def get_svg_filename(word):
    """Convert word to expected SVG filename"""
    return f"{word}.svg"

def main():
    input_file = 'tokipona_wiki_coverage.csv'
    output_file = 'create_ligature_items_with_concepts_quickstatements.txt'

    print("Reading CSV...", flush=True)

    statements = []

    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            word = row['word']

            # Skip items that already exist
            if word in EXISTING_ITEMS:
                continue

            # Only include ligatures without wikidata_id
            wikidata_id = row.get('wikidata_id', '').strip()
            tok_wikidata_id = row.get('tok_wikidata_id', '').strip()
            category = row.get('category', '')

            if not wikidata_id and tok_wikidata_id and 'ligatures' in category.lower():
                commons_title = row['commons_title']

                statements.append({
                    'word': word,
                    'commons_title': commons_title,
                    'concept_qid': tok_wikidata_id,
                    'svg_filename': get_svg_filename(word)
                })

    print(f"Found {len(statements)} ligature items to create", flush=True)

    if statements:
        # Write QuickStatements V2 format
        with open(output_file, 'w', encoding='utf-8') as f:
            for item in statements:
                # CREATE new item
                f.write('CREATE\n')
                # Set multilingual label
                f.write(f'LAST|Lmul|"{item["word"]}"\n')
                # Set toki pona label
                f.write(f'LAST|Ltok|"{item["word"]}"\n')
                # Set English label
                f.write(f'LAST|Len|"{item["word"]}"\n')
                # Add P31 (instance of) = Q137763215 (Toki Pona compound word)
                f.write(f'LAST|P31|Q137763215\n')
                # Add P373 (Commons category)
                f.write(f'LAST|P373|"{item["commons_title"]}"\n')
                # Add P921 (main subject) = the concept item
                f.write(f'LAST|P921|{item["concept_qid"]}\n')
                # Add P18 (image) = SVG file
                f.write(f'LAST|P18|"{item["svg_filename"]}"\n')
                # Add blank line between items for readability
                f.write('\n')

        print(f"\nQuickStatements saved to: {output_file}", flush=True)

        # Write detailed list
        detail_file = 'create_ligature_items_with_concepts_details.txt'
        with open(detail_file, 'w', encoding='utf-8') as f:
            f.write("QuickStatements to CREATE Wikidata items for 92 ligatures with concept links\n")
            f.write("="*80 + "\n\n")
            f.write(f"Total items to create: {len(statements)}\n\n")
            f.write(f"{'Word':<25} {'Concept QID':<15} {'SVG File':<30}\n")
            f.write("-"*80 + "\n")
            for item in statements:
                f.write(f"{item['word']:<25} {item['concept_qid']:<15} {item['svg_filename']:<30}\n")

        print(f"Detailed list saved to: {detail_file}", flush=True)

        # Show all items
        print(f"\nAll {len(statements)} ligature items to create:", flush=True)
        for item in statements:
            print(f"  {item['word']:25s} → P31|Q137763215 + P373|{item['commons_title']} + P921|{item['concept_qid']} + P18|{item['svg_filename']}", flush=True)
    else:
        print("No items found matching criteria!", flush=True)

    print(f"\n✓ Done!", flush=True)

if __name__ == "__main__":
    main()
