"""
Test the category checking logic
"""
import requests
from bs4 import BeautifulSoup

def test_category(category_name):
    url = f"https://commons.wikimedia.org/wiki/Category:{category_name.replace(' ', '_')}"
    headers = {
        'User-Agent': 'SitelenSeliKiwenBot/1.0 (checking category existence; contact: wikimedia commons user)'
    }
    print(f"\nTesting: {category_name}")
    print(f"URL: {url}")

    response = requests.get(url, allow_redirects=True, timeout=10, headers=headers)
    print(f"Status code: {response.status_code}")
    print(f"Final URL: {response.url}")

    soup = BeautifulSoup(response.text, 'html.parser')

    # Check for various indicators
    print(f"Contains 'action=edit': {'action=edit' in response.url}")
    print(f"Contains 'redlink=1': {'redlink=1' in response.url}")
    print(f"Contains 'There is currently no text': {'There is currently no text in this page' in response.text}")

    # Check for category-specific elements
    catlinks = soup.find('div', id='mw-normal-catlinks')
    print(f"Has catlinks div: {catlinks is not None}")

    # Check for the "create category" message
    noarticletext = soup.find('div', class_='noarticletext')
    print(f"Has noarticletext div: {noarticletext is not None}")

    # Look for category members
    mw_category = soup.find('div', id='mw-pages')
    print(f"Has category pages div: {mw_category is not None}")

    # Check for "Category:XYZ does not exist" message
    mw_content = soup.find('div', id='mw-content-text')
    if mw_content:
        # Look for the message about category creation
        firstHeading = soup.find('h1', id='firstHeading')
        print(f"First heading: {firstHeading.text if firstHeading else 'None'}")

        # Check if there's content in the category
        category_content = soup.find('div', class_='mw-category-generated')
        print(f"Has category-generated div: {category_content is not None}")

        # Look for empty category message
        empty_msg = soup.find('p', string=lambda t: t and 'This category is empty' in t)
        print(f"Has 'empty category' message: {empty_msg is not None}")

        # Check for actual members
        if category_content:
            # Look for the gallery or list of files
            members = category_content.find_all('li')
            print(f"Number of category members: {len(members)}")

            # Look for subcategories
            subcats = soup.find('div', id='mw-subcategories')
            print(f"Has subcategories section: {subcats is not None}")

            # Look for pages/files section
            pages = soup.find('div', id='mw-pages')
            print(f"Has pages section: {pages is not None}")

    # Check for "Category is empty" text in the content
    print(f"Contains 'category is empty': {'This category is empty' in response.text.lower() or 'category currently contains no pages' in response.text.lower()}")

    return response

# Test with a category we know exists
print("="*60)
print("Testing EXISTING category")
test_category("Sitelen_seli_kiwen_svgs")

print("\n" + "="*60)
print("Testing REDLINKED category")
test_category("Aasun_(toki_pona)")
