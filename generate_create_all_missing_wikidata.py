"""
Generate QuickStatements to CREATE Wikidata items for all items without Wikidata
"""
import csv
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def main():
    input_file = 'tokipona_wiki_coverage.csv'
    output_file = 'create_all_missing_wikidata_quickstatements.txt'

    print("Reading CSV...", flush=True)

    statements = []

    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            # Items without ANY Wikidata
            wikidata_id = row.get('wikidata_id', '').strip()
            tok_wikidata_id = row.get('tok_wikidata_id', '').strip()

            if not wikidata_id and not tok_wikidata_id:
                word = row['word']
                commons_title = row['commons_title']
                category = row['category']

                # Determine P31 value based on category
                if 'rare words' in category:
                    p31_value = 'Q137374997'  # Toki Pona word
                elif 'ligatures' in category:
                    p31_value = 'Q137763215'  # Toki Pona compound word
                else:
                    # Base category items - treat as Toki Pona words
                    p31_value = 'Q137374997'

                statements.append({
                    'word': word,
                    'commons_title': commons_title,
                    'category': category,
                    'p31_value': p31_value
                })

    print(f"Found {len(statements)} items to create", flush=True)

    if statements:
        # Write QuickStatements V2 format
        with open(output_file, 'w', encoding='utf-8') as f:
            for item in statements:
                # CREATE new item
                f.write('CREATE\n')
                # Set multilingual label (decapitalized word)
                f.write(f'LAST|Lmul|"{item["word"]}"\n')
                # Set toki pona label (decapitalized word)
                f.write(f'LAST|Ltok|"{item["word"]}"\n')
                # Set English label (decapitalized word)
                f.write(f'LAST|Len|"{item["word"]}"\n')
                # Add P31 (instance of)
                f.write(f'LAST|P31|{item["p31_value"]}\n')
                # Add P373 (Commons category)
                f.write(f'LAST|P373|"{item["commons_title"]}"\n')
                # Add blank line between items for readability
                f.write('\n')

        print(f"\nQuickStatements saved to: {output_file}", flush=True)

        # Summary by category
        rare_words = sum(1 for s in statements if s['p31_value'] == 'Q137374997' and 'rare words' in s['category'])
        ligatures = sum(1 for s in statements if s['p31_value'] == 'Q137763215')
        base_category = sum(1 for s in statements if 'rare words' not in s['category'] and 'ligatures' not in s['category'])

        print(f"\nSummary by type:", flush=True)
        print(f"  Rare words (P31|Q137374997): {rare_words}", flush=True)
        print(f"  Ligatures (P31|Q137763215): {ligatures}", flush=True)
        print(f"  Base category items (P31|Q137374997): {base_category}", flush=True)

        # Write detailed list
        detail_file = 'create_all_missing_wikidata_details.txt'
        with open(detail_file, 'w', encoding='utf-8') as f:
            f.write("QuickStatements to CREATE Wikidata items for all items without Wikidata\n")
            f.write("="*80 + "\n\n")
            f.write(f"Total items to create: {len(statements)}\n\n")
            f.write(f"Breakdown:\n")
            f.write(f"  - Rare words: {rare_words}\n")
            f.write(f"  - Ligatures/compound words: {ligatures}\n")
            f.write(f"  - Base category items: {base_category}\n\n")
            f.write(f"{'Word':<30} {'P31 Type':<15} {'Commons Category':<50}\n")
            f.write("-"*80 + "\n")
            for item in statements:
                p31_type = 'Rare word' if item['p31_value'] == 'Q137374997' and 'rare words' in item['category'] else 'Compound word' if item['p31_value'] == 'Q137763215' else 'Base word'
                f.write(f"{item['word']:<30} {p31_type:<15} {item['commons_title']:<50}\n")

        print(f"Detailed list saved to: {detail_file}", flush=True)

        # Show first 20 examples
        print(f"\nFirst 20 items to create:", flush=True)
        for item in statements[:20]:
            p31_type = 'Q137374997' if item['p31_value'] == 'Q137374997' else 'Q137763215'
            print(f"  {item['word']:30s} → P31|{p31_type} + P373|{item['commons_title']}", flush=True)
    else:
        print("No items found matching criteria!", flush=True)

    print(f"\n✓ Done!", flush=True)

if __name__ == "__main__":
    main()
