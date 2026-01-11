"""
Generate QuickStatements to CREATE new Wikidata items for toki pona words
that have Commons Wikidata and tok.wikipedia but no tok.wikipedia Wikidata
"""
import io
import sys
import csv

# Fix Windows encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def main():
    input_file = 'tokipona_wiki_coverage.csv'
    output_file = 'create_tokword_quickstatements.txt'

    print("Reading CSV...", flush=True)

    statements = []

    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            # We need:
            # 1. wikidata_id (Commons category's Wikidata item) - EXISTS
            # 2. tok_exists = Yes - EXISTS
            # 3. tok_wikidata_id is EMPTY - to create
            wikidata_id = row.get('wikidata_id', '').strip()
            tok_exists = row.get('tok_exists', '').strip()
            tok_wikidata_id = row.get('tok_wikidata_id', '').strip()
            tok_url = row.get('tok_url', '').strip()

            if wikidata_id and tok_exists == 'Yes' and not tok_wikidata_id and tok_url:
                word = row['word']
                # Extract page title from tok.wikipedia URL
                # https://tok.wikipedia.org/wiki/Page_Title
                page_title = tok_url.split('/wiki/')[-1]  # Keep underscores for sitelink

                statements.append({
                    'word': word,
                    'page_title': page_title,
                    'commons_qid': wikidata_id
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
                # Set toki pona description (optional, can customize)
                f.write(f'LAST|Dtok|"nimi pi toki pona"\n')
                # Set English label
                f.write(f'LAST|Len|"{item["word"]}"\n')
                # Set English description
                f.write(f'LAST|Den|"Toki Pona word"\n')
                # Add sitelink to tok.wikipedia
                f.write(f'LAST|Stokwiki|"{item["page_title"]}"\n')
                # Link Commons category to this new item with P1268
                f.write(f'{item["commons_qid"]}|P1268|LAST\n')
                # Add blank line between items for readability
                f.write('\n')

        print(f"\nQuickStatements saved to: {output_file}", flush=True)

        # Show sample
        print(f"\nSample (first 5 items):", flush=True)
        for item in statements[:5]:
            print(f"  {item['word']:20s} → {item['page_title']:30s} (Commons: {item['commons_qid']})", flush=True)

        # Write detailed list
        detail_file = 'create_tokword_quickstatements_details.txt'
        with open(detail_file, 'w', encoding='utf-8') as f:
            f.write("QuickStatements to CREATE new Toki Pona word Wikidata items\n")
            f.write("="*70 + "\n\n")
            f.write(f"Total items to create: {len(statements)}\n\n")
            f.write(f"{'Word':<20} {'Tok.Wikipedia Page':<40} {'Commons QID':<15}\n")
            f.write("-"*70 + "\n")
            for item in statements:
                f.write(f"{item['word']:<20} {item['page_title']:<40} {item['commons_qid']:<15}\n")

        print(f"Detailed list saved to: {detail_file}", flush=True)
    else:
        print("No items found matching criteria!", flush=True)

    print(f"\n✓ Done!", flush=True)

if __name__ == "__main__":
    main()
