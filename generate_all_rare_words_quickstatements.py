"""
Generate QuickStatements to CREATE Wikidata items for ALL rare Toki Pona words
"""
import csv
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def load_sonapona_words():
    """Load all words that exist on sona.pona.la"""
    sonapona_words = set()
    with open('sonapona_no_wikidata.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            page_title = row['Page Title'].strip().lower()
            sonapona_words.add(page_title)
    return sonapona_words

def extract_word_from_category(category):
    """Extract word from category name like 'Category:Mulapisu (toki pona)' -> 'mulapisu'"""
    if category.startswith('Category:'):
        category = category[9:]
    if category.endswith(' (toki pona)'):
        category = category[:-12]  # " (toki pona)" is 12 characters
    return category.strip().lower()

def load_coverage_rare_words():
    """Load rare words from tokipona_wiki_coverage.csv (have wikidata concept links)"""
    words = {}
    with open('tokipona_wiki_coverage.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            category = row.get('category', '').strip()
            wikidata_id = row.get('wikidata_id', '').strip()

            if 'rare words' in category and not wikidata_id:
                word = row['word'].lower()
                words[word] = {
                    'tok_wikidata_id': row.get('tok_wikidata_id', '').strip()
                }
    return words

def main():
    output_file = 'create_all_rare_words_quickstatements.txt'

    print("Loading data...", flush=True)

    # Load sonapona words
    sonapona_words = load_sonapona_words()
    print(f"  Loaded {len(sonapona_words)} sona.pona.la words", flush=True)

    # Load coverage data (for concept links)
    coverage_data = load_coverage_rare_words()
    print(f"  Loaded {len(coverage_data)} coverage rare words with concept links", flush=True)

    # Load ALL rare words from redlinked_rare_words.csv
    all_words = []
    with open('redlinked_rare_words.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        current_category = None

        for row in reader:
            category = row['Category'].strip()
            file_name = row['Used By File'].strip()

            if category:  # New category
                current_category = category
                word = extract_word_from_category(category)

                # Get image file (strip 'File:' prefix)
                image = file_name.replace('File:', '') if file_name.startswith('File:') else None

                # Check if has sonapona
                has_sonapona = word in sonapona_words

                # Get concept link from coverage data if available
                tok_wikidata_id = coverage_data.get(word, {}).get('tok_wikidata_id', '')

                all_words.append({
                    'word': word,
                    'category': category,
                    'image': image,
                    'has_sonapona': has_sonapona,
                    'tok_wikidata_id': tok_wikidata_id
                })

    print(f"\nTotal rare words: {len(all_words)}", flush=True)
    with_sonapona = sum(1 for w in all_words if w['has_sonapona'])
    with_image = sum(1 for w in all_words if w['image'])
    with_concept = sum(1 for w in all_words if w['tok_wikidata_id'])
    print(f"  With sona.pona.la: {with_sonapona}", flush=True)
    print(f"  With image: {with_image}", flush=True)
    print(f"  With concept link: {with_concept}", flush=True)

    # Sort by word name
    all_words.sort(key=lambda x: x['word'])

    # Write QuickStatements
    with open(output_file, 'w', encoding='utf-8') as f:
        for item in all_words:
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
            f.write(f'LAST|P373|"{item["category"]}"\n')
            # Add P18 (image) if available
            if item['image']:
                f.write(f'LAST|P18|"{item["image"]}"\n')
            # Add P11250 (sona.pona.la wiki) if exists
            if item['has_sonapona']:
                f.write(f'LAST|P11250|"{item["word"]}"\n')
            # Add P1268 (represents) to link to concept if available
            if item['tok_wikidata_id']:
                f.write(f'LAST|P1268|{item["tok_wikidata_id"]}\n')
            # Add blank line between items
            f.write('\n')

    print(f"\nQuickStatements saved to: {output_file}", flush=True)

    # Write detailed list
    detail_file = 'create_all_rare_words_quickstatements_details.txt'
    with open(detail_file, 'w', encoding='utf-8') as f:
        f.write("QuickStatements to CREATE Wikidata items for ALL rare Toki Pona words\n")
        f.write("="*120 + "\n\n")
        f.write(f"Total items to create: {len(all_words)}\n")
        f.write(f"  With sona.pona.la: {with_sonapona}\n")
        f.write(f"  With image: {with_image}\n")
        f.write(f"  With concept link: {with_concept}\n\n")
        f.write(f"{'Word':<25} {'Commons Category':<55} {'SP':<4} {'Img':<4} {'Concept':<12}\n")
        f.write("-"*120 + "\n")
        for item in all_words:
            sp = 'Yes' if item['has_sonapona'] else 'No'
            img = 'Yes' if item['image'] else 'No'
            concept = item['tok_wikidata_id'] if item['tok_wikidata_id'] else 'N/A'
            f.write(f"{item['word']:<25} {item['category']:<55} {sp:<4} {img:<4} {concept:<12}\n")

    print(f"Detailed list saved to: {detail_file}", flush=True)

    # Show first 20 and last 10
    print(f"\nFirst 20 rare words:", flush=True)
    for item in all_words[:20]:
        sp_mark = '✓SP' if item['has_sonapona'] else '✗SP'
        img_mark = '✓IMG' if item['image'] else '✗IMG'
        concept = f"→{item['tok_wikidata_id']}" if item['tok_wikidata_id'] else ''
        print(f"  {item['word']:20s} {sp_mark} {img_mark:4s} {concept}", flush=True)

    print(f"\nLast 10 rare words:", flush=True)
    for item in all_words[-10:]:
        sp_mark = '✓SP' if item['has_sonapona'] else '✗SP'
        img_mark = '✓IMG' if item['image'] else '✗IMG'
        concept = f"→{item['tok_wikidata_id']}" if item['tok_wikidata_id'] else ''
        print(f"  {item['word']:20s} {sp_mark} {img_mark:4s} {concept}", flush=True)

    print(f"\n✓ Done! Generated {len(all_words)} QuickStatements for rare words", flush=True)

if __name__ == "__main__":
    main()
