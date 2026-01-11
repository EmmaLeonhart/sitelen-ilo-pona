"""
Generate QuickStatements to CREATE new Wikidata items for tok.wikipedia articles
that have NO Commons Wikidata and NO tok.wikipedia Wikidata
"""
import io
import sys
import csv

# Fix Windows encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def main():
    input_file = 'tokipona_wiki_coverage.csv'
    output_file = 'create_orphan_tokwiki_quickstatements.txt'

    print("Reading CSV...", flush=True)

    statements = []

    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            # We need:
            # 1. wikidata_id is EMPTY (no Commons Wikidata)
            # 2. tok_wikidata_id is EMPTY (no tok.wikipedia Wikidata)
            # 3. tok_exists = Yes (tok.wikipedia article exists)
            wikidata_id = row.get('wikidata_id', '').strip()
            tok_wikidata_id = row.get('tok_wikidata_id', '').strip()
            tok_exists = row.get('tok_exists', '').strip()
            tok_url = row.get('tok_url', '').strip()

            if not wikidata_id and not tok_wikidata_id and tok_exists == 'Yes' and tok_url:
                word = row['word']
                # Extract page title from tok.wikipedia URL
                page_title = tok_url.split('/wiki/')[-1]  # Keep underscores for sitelink

                statements.append({
                    'word': word,
                    'page_title': page_title,
                    'category': row['category']
                })

    print(f"Found {len(statements)} items to create", flush=True)

    if statements:
        # Write QuickStatements V2 format
        with open(output_file, 'w', encoding='utf-8') as f:
            for item in statements:
                # CREATE new item
                f.write('CREATE\n')
                # Set toki pona label
                f.write(f'LAST|Ltok|"{item["word"]}"\n')
                # Set toki pona description
                f.write(f'LAST|Dtok|"nimi pi toki pona"\n')
                # Set English label
                f.write(f'LAST|Len|"{item["word"]}"\n')
                # Set English description
                f.write(f'LAST|Den|"Toki Pona word"\n')
                # Add sitelink to tok.wikipedia
                f.write(f'LAST|Stokwiki|"{item["page_title"]}"\n')
                # Add blank line between items for readability
                f.write('\n')

        print(f"\nQuickStatements saved to: {output_file}", flush=True)

        # Show all items (since there shouldn't be many)
        print(f"\nAll items to create:", flush=True)
        for item in statements:
            print(f"  {item['word']:20s} → {item['page_title']:40s}", flush=True)

        # Write detailed list
        detail_file = 'create_orphan_tokwiki_quickstatements_details.txt'
        with open(detail_file, 'w', encoding='utf-8') as f:
            f.write("QuickStatements to CREATE Wikidata items for orphan tok.wikipedia articles\n")
            f.write("="*70 + "\n\n")
            f.write(f"Total items to create: {len(statements)}\n\n")
            f.write("Items with tok.wikipedia but NO Wikidata (neither Commons nor tok.wikipedia)\n\n")
            f.write(f"{'Word':<20} {'Category':<40} {'Tok.Wikipedia Page':<30}\n")
            f.write("-"*70 + "\n")
            for item in statements:
                cat_short = item['category'].split(':')[-1] if ':' in item['category'] else item['category']
                f.write(f"{item['word']:<20} {cat_short:<40} {item['page_title']:<30}\n")

        print(f"Detailed list saved to: {detail_file}", flush=True)
    else:
        print("No items found matching criteria!", flush=True)

    print(f"\n✓ Done!", flush=True)

if __name__ == "__main__":
    main()
