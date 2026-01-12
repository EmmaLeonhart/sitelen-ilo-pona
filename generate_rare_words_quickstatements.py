"""
Generate QuickStatements to CREATE Wikidata items for rare Toki Pona words
"""
import csv
import sys
import io
import os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def get_image_file(word, commons_title):
    """Get the main image file for a word from the CSV"""
    # Parse redlinked_rare_words.csv to find the first file for this category
    csv_path = 'redlinked_rare_words.csv'
    if not os.path.exists(csv_path):
        return None

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['Category'] == commons_title:
                # Get the first file (not the continuation rows with empty Category)
                file_name = row['Used By File'].strip()
                if file_name.startswith('File:'):
                    return file_name.replace('File:', '')
    return None

def main():
    input_file = 'tokipona_wiki_coverage.csv'
    output_file = 'create_rare_words_quickstatements.txt'

    print("Reading CSV...", flush=True)

    statements = []

    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            # Get rare words that don't have wikidata_id but DO have tok_wikidata_id
            category = row.get('category', '').strip()
            wikidata_id = row.get('wikidata_id', '').strip()
            tok_wikidata_id = row.get('tok_wikidata_id', '').strip()

            if 'rare words' in category and not wikidata_id:
                word = row['word']
                commons_title = row['commons_title']
                sona_exists = row.get('sona_exists', '').strip()

                # Get the image file
                image_file = get_image_file(word, commons_title)

                statements.append({
                    'word': word,
                    'commons_title': commons_title,
                    'tok_wikidata_id': tok_wikidata_id,
                    'sona_exists': sona_exists,
                    'image_file': image_file
                })

    print(f"Found {len(statements)} rare words to create", flush=True)

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
                # Add P31 (instance of) - Toki Pona word
                f.write(f'LAST|P31|Q137374997\n')
                # Add P373 (Commons category)
                f.write(f'LAST|P373|"{item["commons_title"]}"\n')
                # Add P18 (image) if available
                if item['image_file']:
                    f.write(f'LAST|P18|"{item["image_file"]}"\n')
                # Add P11250 (sona.pona.la wiki) if exists
                if item['sona_exists'] == 'Yes':
                    f.write(f'LAST|P11250|"{item["word"]}"\n')
                # Add P1268 (represents) to link to concept
                if item['tok_wikidata_id']:
                    f.write(f'LAST|P1268|{item["tok_wikidata_id"]}\n')
                # Add blank line between items
                f.write('\n')

        print(f"\nQuickStatements saved to: {output_file}", flush=True)

        # Write detailed list
        detail_file = 'create_rare_words_quickstatements_details.txt'
        with open(detail_file, 'w', encoding='utf-8') as f:
            f.write("QuickStatements to CREATE Wikidata items for rare Toki Pona words\n")
            f.write("="*100 + "\n\n")
            f.write(f"Total items to create: {len(statements)}\n\n")
            f.write(f"{'Word':<20} {'Commons Category':<50} {'Represents':<12} {'Image'}\n")
            f.write("-"*100 + "\n")
            for item in statements:
                img = item['image_file'] if item['image_file'] else 'N/A'
                f.write(f"{item['word']:<20} {item['commons_title']:<50} {item['tok_wikidata_id']:<12} {img}\n")

        print(f"Detailed list saved to: {detail_file}", flush=True)

        # Show all items
        print(f"\nAll {len(statements)} rare words to create:", flush=True)
        for item in statements:
            img_status = '✓ IMG' if item['image_file'] else '✗ IMG'
            sona_status = '✓ SP' if item['sona_exists'] == 'Yes' else '✗ SP'
            print(f"  {item['word']:20s} → P1268|{item['tok_wikidata_id']:<15s} {img_status} {sona_status}", flush=True)
    else:
        print("No items found matching criteria!", flush=True)

    print(f"\n✓ Done!", flush=True)

if __name__ == "__main__":
    main()
