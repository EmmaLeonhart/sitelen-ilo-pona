"""
Generate P11250 QuickStatements for sona.pona.la wiki links
Format: QID|P11250|"sonapona:pagename"
"""
import csv
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def main():
    input_file = 'tokipona_wiki_coverage.csv'
    output_file = 'add_sonapona_quickstatements.txt'

    print("Reading CSV...", flush=True)

    statements = []

    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            # Check if item has sona.pona.la coverage
            sona_exists = row.get('sona_exists', '').strip() == 'Yes'
            sona_url = row.get('sona_url', '').strip()
            wikidata_id = row.get('wikidata_id', '').strip()

            if sona_exists and sona_url and wikidata_id:
                # Extract page name from URL
                # Format: https://sona.pona.la/wiki/PAGENAME
                if '/wiki/' in sona_url:
                    pagename = sona_url.split('/wiki/')[-1]

                    statements.append({
                        'qid': wikidata_id,
                        'word': row['word'],
                        'pagename': pagename
                    })

    print(f"Found {len(statements)} items with sona.pona.la coverage", flush=True)

    if statements:
        # Write QuickStatements V2 format
        with open(output_file, 'w', encoding='utf-8') as f:
            for item in statements:
                # Add P11250 (Miraheze article ID) with sonapona: prefix
                f.write(f'{item["qid"]}|P11250|"sonapona:{item["pagename"]}"\n')

        print(f"\nQuickStatements saved to: {output_file}", flush=True)

        # Write detailed list
        detail_file = 'add_sonapona_details.txt'
        with open(detail_file, 'w', encoding='utf-8') as f:
            f.write("P11250 QuickStatements for sona.pona.la wiki links\n")
            f.write("="*80 + "\n\n")
            f.write(f"Total items: {len(statements)}\n\n")
            f.write(f"{'QID':<15} {'Word':<30} {'sonapona:pagename':<40}\n")
            f.write("-"*80 + "\n")
            for item in statements:
                f.write(f"{item['qid']:<15} {item['word']:<30} sonapona:{item['pagename']:<40}\n")

        print(f"Detailed list saved to: {detail_file}", flush=True)

        # Show first 20 examples
        print(f"\nFirst 20 items:", flush=True)
        for item in statements[:20]:
            print(f"  {item['qid']} | {item['word']:30s} → sonapona:{item['pagename']}", flush=True)
    else:
        print("No items found with sona.pona.la coverage!", flush=True)

    print(f"\n✓ Done!", flush=True)

if __name__ == "__main__":
    main()
