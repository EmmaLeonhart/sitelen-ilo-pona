"""
Generate QuickStatements to CREATE Wikidata items for ligatures AND rare words with concept links
These are words that have tok_wikidata_id (concept) but no wikidata_id (word item)
"""
import csv
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

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
            # Items that have tok_wikidata_id (concept) but no wikidata_id (word item)
            wikidata_id = row.get('wikidata_id', '').strip()
            tok_wikidata_id = row.get('tok_wikidata_id', '').strip()
            category = row.get('category', '')

            if not wikidata_id and tok_wikidata_id:
                word = row['word']
                commons_title = row['commons_title']
                commons_url = row['commons_url']

                # Determine P31 value based on category
                if 'ligatures' in category.lower():
                    p31_value = 'Q137763215'  # Toki Pona compound word
                    item_type = 'ligature'
                elif 'rare words' in category.lower():
                    p31_value = 'Q137374997'  # Toki Pona word
                    item_type = 'rare_word'
                else:
                    p31_value = 'Q137374997'  # Default to Toki Pona word
                    item_type = 'other'

                statements.append({
                    'word': word,
                    'commons_title': commons_title,
                    'commons_url': commons_url,
                    'concept_qid': tok_wikidata_id,
                    'svg_filename': get_svg_filename(word),
                    'p31_value': p31_value,
                    'item_type': item_type
                })

    print(f"Found {len(statements)} items to create", flush=True)

    if statements:
        # Write QuickStatements V2 format
        with open(output_file, 'w', encoding='utf-8') as f:
            for item in statements:
                # CREATE new item
                f.write('CREATE\n')
                # Set multilingual label (the word)
                f.write(f'LAST|Lmul|"{item["word"]}"\n')
                # Set toki pona label
                f.write(f'LAST|Ltok|"{item["word"]}"\n')
                # Set English label
                f.write(f'LAST|Len|"{item["word"]}"\n')
                # Add P31 (instance of) - varies by type
                f.write(f'LAST|P31|{item["p31_value"]}\n')
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

        # Count by type
        ligatures = [s for s in statements if s['item_type'] == 'ligature']
        rare_words = [s for s in statements if s['item_type'] == 'rare_word']

        with open(detail_file, 'w', encoding='utf-8') as f:
            f.write("QuickStatements to CREATE Wikidata items for ligatures and rare words with concept links\n")
            f.write("="*80 + "\n\n")
            f.write(f"Total items to create: {len(statements)}\n")
            f.write(f"  Ligatures (P31=Q137763215): {len(ligatures)}\n")
            f.write(f"  Rare words (P31=Q137374997): {len(rare_words)}\n\n")
            f.write(f"{'Word':<25} {'Type':<12} {'Concept QID':<15} {'SVG File':<30}\n")
            f.write("-"*80 + "\n")
            for item in statements:
                item_type_label = 'Ligature' if item['item_type'] == 'ligature' else 'Rare word'
                f.write(f"{item['word']:<25} {item_type_label:<12} {item['concept_qid']:<15} {item['svg_filename']:<30}\n")

        print(f"Detailed list saved to: {detail_file}", flush=True)
        print(f"\nBreakdown:", flush=True)
        print(f"  Ligatures: {len(ligatures)}", flush=True)
        print(f"  Rare words: {len(rare_words)}", flush=True)

        # Show all items
        print(f"\nAll {len(statements)} items to create:", flush=True)
        for item in statements:
            print(f"  {item['word']:25s} → P31|{item['p31_value']} + P373|{item['commons_title']} + P921|{item['concept_qid']} + P18|{item['svg_filename']}", flush=True)
    else:
        print("No items found matching criteria!", flush=True)

    print(f"\n✓ Done!", flush=True)

if __name__ == "__main__":
    main()
