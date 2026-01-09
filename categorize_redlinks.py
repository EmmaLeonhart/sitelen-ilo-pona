import csv
import re

def is_camel_case(word):
    """Check if a word has camelCase or PascalCase (multiple capital letters in unusual positions)"""
    # Check for patterns like "AkesiKon", "AAANUSEMEmailMahjong", etc.
    # Look for capital letter followed by lowercase, then another capital
    return bool(re.search(r'[a-z][A-Z]', word)) or bool(re.search(r'[A-Z]{2,}[a-z]', word))

def categorize_category(category_name):
    """Categorize a category into rare words, ligatures, or anomalies"""
    # Remove "Category:" prefix
    name = category_name.replace('Category:', '')

    # Extract the word(s) before " (toki pona)"
    if ' (toki pona)' in name:
        word_part = name.replace(' (toki pona)', '')
    else:
        return 'anomaly'  # Doesn't follow expected pattern

    # Check if it contains a space (ligature)
    if ' ' in word_part:
        return 'ligature'

    # Check for camelCase or other anomalies
    if is_camel_case(word_part):
        return 'anomaly'

    # Check for unusual characters or patterns
    if any(char.isdigit() for char in word_part):
        return 'anomaly'

    # Otherwise it's a single rare word
    return 'rare_word'

def main():
    # Read the CSV
    categories_data = {}
    with open('redlinked_categories.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            category = row['Category']
            file_name = row['Used By File']

            if category not in categories_data:
                categories_data[category] = []
            categories_data[category].append(file_name)

    # Categorize
    rare_words = {}
    ligatures = {}
    anomalies = {}

    for category, files in categories_data.items():
        cat_type = categorize_category(category)

        if cat_type == 'rare_word':
            rare_words[category] = files
        elif cat_type == 'ligature':
            ligatures[category] = files
        else:
            anomalies[category] = files

    print(f"Categorization complete:")
    print(f"  Rare words: {len(rare_words)}")
    print(f"  Ligatures: {len(ligatures)}")
    print(f"  Anomalies: {len(anomalies)}")

    # Save to separate CSVs
    for category_type, data, filename in [
        ('rare_words', rare_words, 'redlinked_rare_words.csv'),
        ('ligatures', ligatures, 'redlinked_ligatures.csv'),
        ('anomalies', anomalies, 'redlinked_anomalies.csv')
    ]:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Category', 'Used By File', 'File Count'])
            for cat, files in sorted(data.items()):
                writer.writerow([cat, files[0], len(files)])
                for file in files[1:]:
                    writer.writerow(['', file, ''])
        print(f"Saved {filename}")

if __name__ == '__main__':
    main()
