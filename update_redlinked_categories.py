"""
Check which redlinked categories now exist on Wikimedia Commons and update the HTML file.
"""
import io
import sys
import time
import requests
from bs4 import BeautifulSoup
import re

# Fix Windows encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def check_category_exists(category_name):
    """Check if a category exists (has files) on Wikimedia Commons."""
    url = f"https://commons.wikimedia.org/wiki/Category:{category_name.replace(' ', '_')}"
    headers = {
        'User-Agent': 'SitelenSeliKiwenBot/1.0 (checking category existence; contact: wikimedia commons user)'
    }
    try:
        response = requests.get(url, allow_redirects=True, timeout=10, headers=headers)
        if response.status_code != 200:
            return False

        # Parse HTML to check for category members
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the category-generated div which contains the member list
        category_content = soup.find('div', class_='mw-category-generated')
        if not category_content:
            return False

        # Count members (files/pages in the category)
        members = category_content.find_all('li')

        # Category "exists" (is in use) if it has at least one member
        return len(members) > 0

    except Exception as e:
        print(f"Error checking {category_name}: {e}", flush=True)
        return False

def main():
    import sys
    input_file = "redlinked_categories_categorized.html"
    output_file = "redlinked_categories_categorized_updated.html"

    # Optional limit for testing
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else None

    print("Reading HTML file...")
    with open(input_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all category items
    category_items = soup.find_all('div', class_='category-item')
    if limit:
        category_items = category_items[:limit]
        print(f"Testing mode: checking first {limit} categories only", flush=True)
    print(f"Found {len(category_items)} total categories to check", flush=True)

    removed_count = 0
    rare_removed = 0
    ligature_removed = 0
    anomaly_removed = 0

    # Track which categories exist
    existing_categories = []

    for i, item in enumerate(category_items):
        # Extract category name
        category_span = item.find('span', class_='category-name')
        if not category_span:
            continue

        category_full_name = category_span.text.strip()

        # Extract just the category name for URL checking
        # Format is "CategoryName (toki pona)" or similar

        print(f"\n[{i+1}/{len(category_items)}] Checking: {category_full_name}", flush=True)

        # Check if category exists
        if check_category_exists(category_full_name):
            print(f"  ✓ EXISTS - will remove", flush=True)
            existing_categories.append(category_full_name)

            # Determine which section it's in by checking parent sections
            parent = item.parent
            while parent:
                if parent.get('id') == 'rare-words':
                    rare_removed += 1
                    break
                elif parent.get('id') == 'ligatures':
                    ligature_removed += 1
                    break
                elif parent.get('id') == 'anomalies':
                    anomaly_removed += 1
                    break
                parent = parent.parent

            # Remove the item
            item.decompose()
            removed_count += 1
        else:
            print(f"  ✗ Still redlinked", flush=True)

        # Be nice to the server
        time.sleep(1.5)

    print(f"\n{'='*60}", flush=True)
    print(f"Summary:", flush=True)
    print(f"  Total categories checked: {len(category_items)}", flush=True)
    print(f"  Categories that now exist: {removed_count}", flush=True)
    print(f"    - Rare words: {rare_removed}", flush=True)
    print(f"    - Ligatures: {ligature_removed}", flush=True)
    print(f"    - Anomalies: {anomaly_removed}", flush=True)
    print(f"  Categories still redlinked: {len(category_items) - removed_count}", flush=True)
    print(f"{'='*60}\n", flush=True)

    if existing_categories:
        print("Categories that now exist:", flush=True)
        for cat in existing_categories:
            print(f"  - {cat}", flush=True)

    # Update counts in the HTML
    # Find and update the stats div
    stats_div = soup.find('div', class_='stats')
    if stats_div:
        strong_tag = stats_div.find('strong', string='Total redlinked categories:')
        if strong_tag:
            # Update the text after the strong tag
            current_count = len(category_items) - removed_count
            # Replace the content
            for sibling in strong_tag.next_siblings:
                if isinstance(sibling, str):
                    sibling.replace_with(f' {current_count}')
                    break

    # Update section headers with new counts
    rare_section = soup.find('h2', string=re.compile(r'Rare Words \(\d+ categories\)'))
    if rare_section:
        current_rare = len(soup.find('div', id='rare-words').find_all('div', class_='category-item'))
        rare_section.string = f'Rare Words ({current_rare} categories)'

    ligature_section = soup.find('h2', string=re.compile(r'Ligatures \(\d+ categories\)'))
    if ligature_section:
        current_ligatures = len(soup.find('div', id='ligatures').find_all('div', class_='category-item'))
        ligature_section.string = f'Ligatures ({current_ligatures} categories)'

    anomaly_section = soup.find('h2', string=re.compile(r'Anomalies \(\d+ categories\)'))
    if anomaly_section:
        current_anomalies = len(soup.find('div', id='anomalies').find_all('div', class_='category-item'))
        anomaly_section.string = f'Anomalies ({current_anomalies} categories)'

    # Update explanation section
    explanation_ul = soup.find('div', class_='explanation').find('ul')
    if explanation_ul:
        lis = explanation_ul.find_all('li')
        current_rare = len(soup.find('div', id='rare-words').find_all('div', class_='category-item'))
        current_ligatures = len(soup.find('div', id='ligatures').find_all('div', class_='category-item'))
        current_anomalies = len(soup.find('div', id='anomalies').find_all('div', class_='category-item'))

        if len(lis) >= 1:
            lis[0].clear()
            lis[0].append(soup.new_tag('strong'))
            lis[0].strong.string = f'Rare Words ({current_rare}):'
            lis[0].append(' Single toki pona words that don\'t have categories yet (e.g., "Amelin (toki pona)")')
        if len(lis) >= 2:
            lis[1].clear()
            lis[1].append(soup.new_tag('strong'))
            lis[1].strong.string = f'Ligatures ({current_ligatures}):'
            lis[1].append(' Multi-word combinations with spaces (e.g., "Anpa lawa (toki pona)")')
        if len(lis) >= 3:
            lis[2].clear()
            lis[2].append(soup.new_tag('strong'))
            lis[2].strong.string = f'Anomalies ({current_anomalies}):'
            lis[2].append(' Words with unusual patterns like camelCase or numbers')

    # Write updated HTML
    print(f"\nWriting updated HTML to {output_file}...", flush=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(str(soup.prettify()))

    print(f"✓ Done! Updated HTML saved to {output_file}", flush=True)

if __name__ == "__main__":
    main()
