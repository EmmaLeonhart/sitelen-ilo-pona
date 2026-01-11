"""Quick test of the lowercase conversion"""
import io
import sys
import re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def extract_word_from_title(title):
    """Extract the toki pona word from a category title by removing (toki pona) suffix."""
    # Remove "Category:" prefix if present
    if title.startswith('Category:'):
        title = title[9:]

    # Remove " (toki pona)" or " (Toki Pona)" suffix
    title = re.sub(r'\s*\([Tt]oki [Pp]ona\)\s*$', '', title)

    # Also remove file extension if it's a file
    title = re.sub(r'\.(svg|png|jpg|jpeg)$', '', title, flags=re.IGNORECASE)

    title = title.strip()

    # Lowercase the first letter (toki pona convention)
    if title:
        title = title[0].lower() + title[1:]

    return title

# Test cases
test_titles = [
    "Category:Anpa lawa (toki pona)",
    "Category:Ijo akesi (toki pona)",
    "Category:Sitelen pona (toki pona)",
    "Category:Toki pona (toki pona)"
]

for title in test_titles:
    word = extract_word_from_title(title)
    print(f"{title} → '{word}'")
