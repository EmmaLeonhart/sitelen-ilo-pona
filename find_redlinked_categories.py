import requests
import csv
import time

API_URL = "https://commons.wikimedia.org/w/api.php"

# Proper User-Agent header as required by Wikimedia
HEADERS = {
    'User-Agent': 'SitelenSeliKiwenBot/1.0 (https://github.com/user/sitelen; user@example.com) Python/requests'
}

def get_category_members(category_name):
    """Get all files in a category"""
    members = []
    params = {
        'action': 'query',
        'list': 'categorymembers',
        'cmtitle': category_name,
        'cmlimit': 'max',
        'format': 'json'
    }

    while True:
        response = requests.get(API_URL, params=params, headers=HEADERS)
        data = response.json()

        if 'query' in data and 'categorymembers' in data['query']:
            members.extend(data['query']['categorymembers'])

        if 'continue' not in data:
            break
        params['cmcontinue'] = data['continue']['cmcontinue']
        time.sleep(0.5)

    return members

def get_page_categories(page_title):
    """Get all categories for a given page"""
    params = {
        'action': 'query',
        'titles': page_title,
        'prop': 'categories',
        'cllimit': 'max',
        'format': 'json'
    }

    response = requests.get(API_URL, params=params, headers=HEADERS)
    data = response.json()

    pages = data['query']['pages']
    page_id = list(pages.keys())[0]

    if 'categories' in pages[page_id]:
        return [cat['title'] for cat in pages[page_id]['categories']]
    return []

def check_category_exists(category_title):
    """Check if a category exists (has content)"""
    params = {
        'action': 'query',
        'titles': category_title,
        'format': 'json'
    }

    response = requests.get(API_URL, params=params, headers=HEADERS)
    data = response.json()

    pages = data['query']['pages']
    page_id = list(pages.keys())[0]

    # If page_id is negative, the page doesn't exist
    return int(page_id) > 0 and 'missing' not in pages[page_id]

def main():
    print("Fetching files from Category:Sitelen_seli_kiwen_svgs...")
    members = get_category_members('Category:Sitelen_seli_kiwen_svgs')
    print(f"Found {len(members)} files")

    redlinked_categories = {}

    for i, member in enumerate(members, 1):
        page_title = member['title']
        print(f"[{i}/{len(members)}] Checking {page_title}...")

        categories = get_page_categories(page_title)

        for category in categories:
            if category not in redlinked_categories:
                exists = check_category_exists(category)
                if not exists:
                    print(f"  Found redlink: {category}")
                    redlinked_categories[category] = []
                time.sleep(0.5)  # Rate limiting

            if category in redlinked_categories:
                redlinked_categories[category].append(page_title)

        time.sleep(0.5)  # Rate limiting

    # Write to CSV
    csv_file = 'redlinked_categories.csv'
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Category', 'Used By File'])

        for category, files in sorted(redlinked_categories.items()):
            for file in files:
                writer.writerow([category, file])

    print(f"\nFound {len(redlinked_categories)} redlinked categories")
    print(f"Results saved to {csv_file}")

    # Print summary
    print("\nRedlinked categories:")
    for category in sorted(redlinked_categories.keys()):
        print(f"  {category} (used by {len(redlinked_categories[category])} files)")

if __name__ == '__main__':
    main()
