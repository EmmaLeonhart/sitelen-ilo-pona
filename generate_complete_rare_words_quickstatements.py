"""
Generate QuickStatements for ALL rare Toki Pona words:
1. CREATE statements for 11 rare words without Wikidata items
2. ADD property statements for 291 rare words with existing Wikidata items
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

def get_image_for_word(word, redlinked_data):
    """Get image file for a word from redlinked data"""
    return redlinked_data.get(word.lower(), {}).get('image')

def load_redlinked_images():
    """Load image files from redlinked_rare_words.csv"""
    images = {}
    with open('redlinked_rare_words.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            category = row['Category'].strip()
            file_name = row['Used By File'].strip()

            if category:
                # Extract word from category
                word = category.replace('Category:', '').replace(' (toki pona)', '').strip().lower()
                # Get image file
                image = file_name.replace('File:', '') if file_name.startswith('File:') else None
                images[word] = {'image': image}
    return images

def main():
    output_file = 'complete_rare_words_quickstatements.txt'

    print("Loading data...", flush=True)

    # Load sonapona words
    sonapona_words = load_sonapona_words()
    print(f"  Loaded {len(sonapona_words)} sona.pona.la words", flush=True)

    # Load image data from redlinked file
    redlinked_images = load_redlinked_images()
    print(f"  Loaded {len(redlinked_images)} rare word images", flush=True)

    # Load all rare words from coverage CSV
    create_statements = []  # Words without Wikidata items
    add_statements = []     # Words with Wikidata items needing properties

    with open('tokipona_wiki_coverage.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            category = row.get('category', '').strip()

            if 'rare words' not in category:
                continue

            word = row['word'].lower()
            wikidata_id = row.get('wikidata_id', '').strip()
            commons_title = row['commons_title']
            sona_exists = row.get('sona_exists', '').strip()
            tok_wikidata_id = row.get('tok_wikidata_id', '').strip()

            # Get image
            image = get_image_for_word(word, redlinked_images)

            # Check if has sonapona
            has_sonapona = word in sonapona_words

            item = {
                'word': word,
                'wikidata_id': wikidata_id,
                'commons_title': commons_title,
                'image': image,
                'has_sonapona': has_sonapona,
                'tok_wikidata_id': tok_wikidata_id
            }

            if wikidata_id:
                add_statements.append(item)
            else:
                create_statements.append(item)

    print(f"\nTotal rare words: {len(create_statements) + len(add_statements)}", flush=True)
    print(f"  CREATE new items: {len(create_statements)}", flush=True)
    print(f"  ADD properties to existing: {len(add_statements)}", flush=True)

    # Sort both lists
    create_statements.sort(key=lambda x: x['word'])
    add_statements.sort(key=lambda x: x['word'])

    # Write QuickStatements
    with open(output_file, 'w', encoding='utf-8') as f:
        # PART 1: CREATE new items
        if create_statements:
            f.write('# ========================================\n')
            f.write(f'# PART 1: CREATE {len(create_statements)} new rare word items\n')
            f.write('# ========================================\n\n')

            for item in create_statements:
                f.write('CREATE\n')
                f.write(f'LAST|Lmul|"{item["word"]}"\n')
                f.write(f'LAST|Ltok|"{item["word"]}"\n')
                f.write(f'LAST|Len|"{item["word"]}"\n')
                f.write(f'LAST|P31|Q137374997\n')
                f.write(f'LAST|P373|"{item["commons_title"]}"\n')
                if item['image']:
                    f.write(f'LAST|P18|"{item["image"]}"\n')
                if item['has_sonapona']:
                    f.write(f'LAST|P11250|"{item["word"]}"\n')
                if item['tok_wikidata_id']:
                    f.write(f'LAST|P1268|{item["tok_wikidata_id"]}\n')
                f.write('\n')

        # PART 2: ADD properties to existing items
        if add_statements:
            f.write('# ========================================\n')
            f.write(f'# PART 2: ADD properties to {len(add_statements)} existing rare word items\n')
            f.write('# ========================================\n\n')

            for item in add_statements:
                # Add P18 (image) if available
                if item['image']:
                    f.write(f'{item["wikidata_id"]}|P18|"{item["image"]}"\n')
                # Add P11250 (sonapona) if exists
                if item['has_sonapona']:
                    f.write(f'{item["wikidata_id"]}|P11250|"{item["word"]}"\n')
                # Add P1268 (represents) if concept link exists
                if item['tok_wikidata_id']:
                    f.write(f'{item["wikidata_id"]}|P1268|{item["tok_wikidata_id"]}\n')

    print(f"\nQuickStatements saved to: {output_file}", flush=True)

    # Write detailed report
    detail_file = 'complete_rare_words_quickstatements_details.txt'
    with open(detail_file, 'w', encoding='utf-8') as f:
        f.write("Complete QuickStatements for ALL rare Toki Pona words\n")
        f.write("="*120 + "\n\n")

        f.write(f"SUMMARY:\n")
        f.write(f"  Total rare words: {len(create_statements) + len(add_statements)}\n")
        f.write(f"  - CREATE new items: {len(create_statements)}\n")
        f.write(f"  - ADD properties: {len(add_statements)}\n\n")

        # Stats for properties
        create_with_img = sum(1 for i in create_statements if i['image'])
        create_with_sp = sum(1 for i in create_statements if i['has_sonapona'])
        create_with_concept = sum(1 for i in create_statements if i['tok_wikidata_id'])

        add_with_img = sum(1 for i in add_statements if i['image'])
        add_with_sp = sum(1 for i in add_statements if i['has_sonapona'])
        add_with_concept = sum(1 for i in add_statements if i['tok_wikidata_id'])

        f.write(f"CREATE group properties:\n")
        f.write(f"  - With P18 (image): {create_with_img}\n")
        f.write(f"  - With P11250 (sonapona): {create_with_sp}\n")
        f.write(f"  - With P1268 (concept): {create_with_concept}\n\n")

        f.write(f"ADD group properties:\n")
        f.write(f"  - With P18 (image): {add_with_img}\n")
        f.write(f"  - With P11250 (sonapona): {add_with_sp}\n")
        f.write(f"  - With P1268 (concept): {add_with_concept}\n\n")

        f.write("="*120 + "\n\n")

        # CREATE list
        if create_statements:
            f.write(f"PART 1: CREATE {len(create_statements)} new items\n")
            f.write("-"*120 + "\n")
            f.write(f"{'Word':<25} {'Commons Category':<55} {'IMG':<4} {'SP':<4} {'Concept':<12}\n")
            f.write("-"*120 + "\n")
            for item in create_statements:
                img = 'Yes' if item['image'] else 'No'
                sp = 'Yes' if item['has_sonapona'] else 'No'
                concept = item['tok_wikidata_id'] if item['tok_wikidata_id'] else 'N/A'
                f.write(f"{item['word']:<25} {item['commons_title']:<55} {img:<4} {sp:<4} {concept:<12}\n")
            f.write("\n\n")

        # ADD list
        if add_statements:
            f.write(f"PART 2: ADD properties to {len(add_statements)} existing items\n")
            f.write("-"*120 + "\n")
            f.write(f"{'Word':<25} {'QID':<15} {'IMG':<4} {'SP':<4} {'Concept':<12}\n")
            f.write("-"*120 + "\n")
            for item in add_statements:
                img = 'Yes' if item['image'] else 'No'
                sp = 'Yes' if item['has_sonapona'] else 'No'
                concept = item['tok_wikidata_id'] if item['tok_wikidata_id'] else 'N/A'
                f.write(f"{item['word']:<25} {item['wikidata_id']:<15} {img:<4} {sp:<4} {concept:<12}\n")

    print(f"Detailed report saved to: {detail_file}", flush=True)

    # Show samples
    print(f"\n=== PART 1: CREATE {len(create_statements)} new items ===", flush=True)
    for item in create_statements:
        img = '✓IMG' if item['image'] else '✗IMG'
        sp = '✓SP' if item['has_sonapona'] else '✗SP'
        concept = f"→{item['tok_wikidata_id']}" if item['tok_wikidata_id'] else ''
        print(f"  {item['word']:20s} {img} {sp} {concept}", flush=True)

    print(f"\n=== PART 2: ADD properties to {len(add_statements)} existing items ===", flush=True)
    print(f"First 20:", flush=True)
    for item in add_statements[:20]:
        img = '✓IMG' if item['image'] else '✗IMG'
        sp = '✓SP' if item['has_sonapona'] else '✗SP'
        concept = f"→{item['tok_wikidata_id']}" if item['tok_wikidata_id'] else ''
        print(f"  {item['wikidata_id']:12s} {item['word']:20s} {img} {sp} {concept}", flush=True)

    print(f"\n✓ Done! Generated QuickStatements for {len(create_statements) + len(add_statements)} rare words", flush=True)

if __name__ == "__main__":
    main()
