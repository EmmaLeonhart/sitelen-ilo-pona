"""
Generate QuickStatements to add P1268 (represents) to Commons category Wikidata items
"""
import io
import sys
import csv

# Fix Windows encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def main():
    input_file = 'tokipona_wiki_coverage.csv'
    output_file = 'represents_quickstatements.txt'

    print("Reading CSV...", flush=True)

    statements = []

    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            # We need both:
            # 1. wikidata_id (Commons category's Wikidata item)
            # 2. tok_wikidata_id (what the category represents)
            wikidata_id = row.get('wikidata_id', '').strip()
            tok_wikidata_id = row.get('tok_wikidata_id', '').strip()

            if wikidata_id and tok_wikidata_id:
                word = row['word']
                # Format: Q12345|P1268|Q67890
                statement = f"{wikidata_id}|P1268|{tok_wikidata_id}"
                statements.append({
                    'statement': statement,
                    'word': word,
                    'category_qid': wikidata_id,
                    'represents_qid': tok_wikidata_id
                })

    print(f"Found {len(statements)} items with both Commons Wikidata and tok.wikipedia Wikidata", flush=True)

    if statements:
        # Write QuickStatements
        with open(output_file, 'w', encoding='utf-8') as f:
            for item in statements:
                f.write(item['statement'] + '\n')

        print(f"\nQuickStatements saved to: {output_file}", flush=True)

        # Show sample
        print(f"\nSample QuickStatements (first 20):", flush=True)
        for item in statements[:20]:
            print(f"  {item['word']:20s} | {item['statement']}", flush=True)

        # Write detailed list
        detail_file = 'represents_quickstatements_details.txt'
        with open(detail_file, 'w', encoding='utf-8') as f:
            f.write("P1268 (represents) QuickStatements - Detailed List\n")
            f.write("="*70 + "\n\n")
            f.write(f"Total statements: {len(statements)}\n\n")
            f.write(f"{'Word':<20} {'Category QID':<15} {'Represents QID':<15}\n")
            f.write("-"*70 + "\n")
            for item in statements:
                f.write(f"{item['word']:<20} {item['category_qid']:<15} {item['represents_qid']:<15}\n")

        print(f"Detailed list saved to: {detail_file}", flush=True)
    else:
        print("No items found with both Wikidata IDs!", flush=True)

    print(f"\n✓ Done!", flush=True)

if __name__ == "__main__":
    main()
