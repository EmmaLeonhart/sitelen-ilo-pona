"""
Generate P18 (image) QuickStatements for newly created Wikidata items
Uses the pattern: Sitelen-word1-word2.svg (with hyphens replacing spaces)
"""
import csv
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def word_to_svg_filename(word, is_rare_word=False):
    """
    Convert word to SVG filename with Sitelen Seli Kiwen font prefix
    Examples:
    - "akesi kon" → "Sitelen-seli-kiwen-akesi-kon.svg"
    - "mama mije" → "Sitelen-seli-kiwen-mama-mije.svg"
    - "kutopoma" → "Sitelen-seli-kiwen-kutopoma.svg"
    """
    # Replace spaces with hyphens
    svg_name = word.replace(' ', '-')
    return f"Sitelen-seli-kiwen-{svg_name}.svg"

def main():
    input_file = 'tokipona_wiki_coverage.csv'
    output_file = 'add_p18_images_quickstatements.txt'

    print("Reading CSV to find newly created items...", flush=True)

    statements = []

    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            wikidata_id = row.get('wikidata_id', '').strip()
            tok_wikidata_id = row.get('tok_wikidata_id', '').strip()
            word = row['word']
            category = row['category']

            # We want items that have wikidata_id (Commons Wikidata)
            # These are the word items we just created
            if wikidata_id and not tok_wikidata_id:
                # Determine if rare word or compound word
                is_rare_word = 'rare words' in category

                svg_filename = word_to_svg_filename(word, is_rare_word)

                statements.append({
                    'qid': wikidata_id,
                    'word': word,
                    'svg': svg_filename,
                    'category': category
                })

    print(f"Found {len(statements)} items to add P18 images", flush=True)

    if statements:
        # Write QuickStatements V2 format
        with open(output_file, 'w', encoding='utf-8') as f:
            for item in statements:
                # Add P18 (image) statement
                f.write(f'{item["qid"]}|P18|"{item["svg"]}"\n')

        print(f"\nQuickStatements saved to: {output_file}", flush=True)

        # Summary by category
        rare_words = sum(1 for s in statements if 'rare words' in s['category'])
        ligatures = sum(1 for s in statements if 'ligatures' in s['category'])
        base_category = sum(1 for s in statements if 'rare words' not in s['category'] and 'ligatures' not in s['category'])

        print(f"\nSummary by type:", flush=True)
        print(f"  Rare words: {rare_words}", flush=True)
        print(f"  Ligatures/compound words: {ligatures}", flush=True)
        print(f"  Base category items: {base_category}", flush=True)

        # Write detailed list
        detail_file = 'add_p18_images_details.txt'
        with open(detail_file, 'w', encoding='utf-8') as f:
            f.write("P18 (image) QuickStatements for newly created Wikidata items\n")
            f.write("="*80 + "\n\n")
            f.write(f"Total items: {len(statements)}\n\n")
            f.write(f"{'QID':<15} {'Word':<30} {'SVG Filename':<40}\n")
            f.write("-"*80 + "\n")
            for item in statements:
                f.write(f"{item['qid']:<15} {item['word']:<30} {item['svg']:<40}\n")

        print(f"Detailed list saved to: {detail_file}", flush=True)

        # Show first 20 examples
        print(f"\nFirst 20 items:", flush=True)
        for item in statements[:20]:
            print(f"  {item['qid']} | {item['word']:30s} → {item['svg']}", flush=True)
    else:
        print("No items found! Make sure to sync the CSV first with get_tokwiki_wikidata.py", flush=True)

    print(f"\n✓ Done!", flush=True)

if __name__ == "__main__":
    main()
