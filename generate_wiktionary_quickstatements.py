"""
Generate Senwiktionary sitelink QuickStatements for en.wiktionary links
Format: QID|Senwiktionary|"Appendix:Toki_Pona/WORD"
"""
import csv
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def main():
    input_file = 'tokipona_wiki_coverage.csv'
    output_file = 'add_wiktionary_quickstatements.txt'

    print("Reading CSV...", flush=True)

    statements = []

    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            # Check if item has wiktionary coverage
            wikt_exists = row.get('wiktionary_exists', '').strip() == 'Yes'
            wikt_url = row.get('wiktionary_url', '').strip()
            wikidata_id = row.get('wikidata_id', '').strip()

            if wikt_exists and wikt_url and wikidata_id:
                # Extract page name from URL
                # Format: https://en.wiktionary.org/wiki/Appendix:Toki_Pona/WORD
                if 'Appendix:Toki_Pona/' in wikt_url:
                    # Get the full "Appendix:Toki_Pona/WORD" part
                    page_title = wikt_url.split('/wiki/')[-1]

                    statements.append({
                        'qid': wikidata_id,
                        'word': row['word'],
                        'page_title': page_title
                    })

    print(f"Found {len(statements)} items with wiktionary coverage", flush=True)

    if statements:
        # Write QuickStatements V2 format
        with open(output_file, 'w', encoding='utf-8') as f:
            for item in statements:
                # Add Senwiktionary sitelink
                f.write(f'{item["qid"]}|Senwiktionary|"{item["page_title"]}"\n')

        print(f"\nQuickStatements saved to: {output_file}", flush=True)

        # Write detailed list
        detail_file = 'add_wiktionary_details.txt'
        with open(detail_file, 'w', encoding='utf-8') as f:
            f.write("Senwiktionary sitelink QuickStatements for en.wiktionary links\n")
            f.write("="*80 + "\n\n")
            f.write(f"Total items: {len(statements)}\n\n")
            f.write(f"{'QID':<15} {'Word':<30} {'Page Title':<50}\n")
            f.write("-"*80 + "\n")
            for item in statements:
                f.write(f"{item['qid']:<15} {item['word']:<30} {item['page_title']:<50}\n")

        print(f"Detailed list saved to: {detail_file}", flush=True)

        # Show first 20 examples
        print(f"\nFirst 20 items:", flush=True)
        for item in statements[:20]:
            print(f"  {item['qid']} | {item['word']:30s} → {item['page_title']}", flush=True)
    else:
        print("No items found with wiktionary coverage!", flush=True)

    print(f"\n✓ Done!", flush=True)

if __name__ == "__main__":
    main()
