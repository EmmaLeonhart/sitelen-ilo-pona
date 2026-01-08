import os
import re
import sys
import io
from pathlib import Path

# Fix Unicode encoding on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Base directory
base_dir = Path(r"C:\Users\Immanuelle\Documents\Github\Sitelen\uniform_syllables")

# Define vowel patterns and corresponding consonants
vowel_patterns = {
    'a': ['la', 'ma', 'na', 'pa', 'sa', 'ta', 'wa', 'xa', 'ya'],
    'an': ['lan', 'man', 'nan', 'pan', 'san', 'tan', 'wan', 'xan', 'yan'],
    'e': ['le', 'me', 'ne', 'pe', 'se', 'te', 'we', 'xe', 'ye'],
    'en': ['len', 'men', 'nen', 'pen', 'sen', 'ten', 'wen', 'xen', 'yen'],
    'i': ['li', 'mi', 'ni', 'pi', 'si', 'ti', 'wi', 'xi', 'yi'],
    'in': ['lin', 'min', 'nin', 'pin', 'sin', 'tin', 'win', 'xin', 'yin'],
    'o': ['lo', 'mo', 'no', 'po', 'so', 'to', 'wo', 'xo', 'yo'],
    'on': ['lon', 'mon', 'non', 'pon', 'son', 'ton', 'won', 'xon', 'yon'],
    'u': ['lu', 'mu', 'nu', 'pu', 'su', 'tu', 'wu', 'xu', 'yu'],
    'un': ['lun', 'mun', 'nun', 'pun', 'sun', 'tun', 'wun', 'xun', 'yun']
}

def extract_svg_content(filepath):
    """Extract the main content from an SVG file (everything between <svg> and </svg>)"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find all content between opening <svg> tag and closing </svg>
    # We want everything except the closing </svg> tag
    match = re.search(r'<svg[^>]*>(.*)</svg>', content, re.DOTALL)
    if match:
        inner_content = match.group(1)
        # Get the opening svg tag too for reference
        svg_tag_match = re.search(r'<svg[^>]*>', content)
        svg_tag = svg_tag_match.group(0) if svg_tag_match else ""
        return inner_content, svg_tag
    return None, None

def add_k_content_to_file(target_filepath, k_content, vowel_name):
    """Add k-series content to a target file, positioned off-screen"""
    with open(target_filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if k-reference already exists
    if 'id="k-reference"' in content or 'id="x-reference"' in content:
        print(f"  Skipping {target_filepath.name} - already has k/x-reference")
        return False

    # Find the closing </svg> tag
    closing_tag_pos = content.rfind('</svg>')
    if closing_tag_pos == -1:
        print(f"  ERROR: Could not find closing </svg> tag in {target_filepath.name}")
        return False

    # Create the off-screen reference group
    # Position it way outside the viewbox (typical viewBox is around -50 to 50, so use x=500)
    off_screen_group = f'''  <g id="x-reference" transform="translate(500,0)">
    <!-- k-series reference for vowel {vowel_name} -->
{k_content}
  </g>
'''

    # Insert before the closing </svg> tag
    new_content = content[:closing_tag_pos] + off_screen_group + content[closing_tag_pos:]

    with open(target_filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

    return True

def main():
    print("Starting to copy k-series content to corresponding vowel files...")
    print("=" * 70)

    total_processed = 0
    total_skipped = 0

    for vowel, target_syllables in vowel_patterns.items():
        # Determine the k-series source file
        k_syllable = 'k' + vowel
        k_filepath = base_dir / f"sitelen kalama pona - {k_syllable}.svg"

        if not k_filepath.exists():
            print(f"\nWARNING: k-series file not found: {k_filepath.name}")
            continue

        # Extract k-series content
        k_content, k_svg_tag = extract_svg_content(k_filepath)
        if k_content is None:
            print(f"\nERROR: Could not extract content from {k_filepath.name}")
            continue

        print(f"\nProcessing vowel pattern '{vowel}' (source: {k_syllable}.svg)")
        print(f"  Targets: {', '.join(target_syllables)}")

        # Process each target file
        for syllable in target_syllables:
            target_filepath = base_dir / f"sitelen kalama pona - {syllable}.svg"

            if not target_filepath.exists():
                print(f"  WARNING: Target file not found: {target_filepath.name}")
                continue

            success = add_k_content_to_file(target_filepath, k_content, vowel)
            if success:
                print(f"  ✓ Added k-reference to {target_filepath.name}")
                total_processed += 1
            else:
                total_skipped += 1

    print("\n" + "=" * 70)
    print(f"DONE! Processed: {total_processed} files, Skipped: {total_skipped} files")

if __name__ == "__main__":
    main()
