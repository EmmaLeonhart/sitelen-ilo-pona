import os
import re
import sys
import io
from pathlib import Path

# Fix Unicode encoding on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Base directory
base_dir = Path(r"C:\Users\Immanuelle\Documents\Github\Sitelen\uniform_syllables")

# All vowel variants (excluding -o itself)
vowel_variants = ['a', 'an', 'e', 'en', 'i', 'in', 'on', 'u', 'un']

# Consonants to process (excluding k which is already complete)
consonants = ['l', 'm', 'n', 'p', 's', 't', 'w', 'x', 'y']

# X-offset mapping for each consonant to avoid conflicts
# x-reference=500, m-reference=1000, n-reference=1500
x_offsets = {
    'l': 2000,
    'm': 2500,
    'n': 3000,
    'p': 3500,
    's': 4000,
    't': 4500,
    'w': 5000,
    'x': 5500,
    'y': 6000
}

def extract_svg_content(filepath):
    """Extract the main content from an SVG file (everything between <svg> and </svg>)"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find all content between opening <svg> tag and closing </svg>
    match = re.search(r'<svg[^>]*>(.*)</svg>', content, re.DOTALL)
    if match:
        inner_content = match.group(1)
        return inner_content
    return None

def add_consonant_o_reference(target_filepath, o_content, consonant, x_offset):
    """Add consonant-o reference content to a target file, positioned off-screen"""
    with open(target_filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    reference_id = f"{consonant}o-reference"

    # Check if reference already exists
    if f'id="{reference_id}"' in content:
        print(f"  Skipping {target_filepath.name} - already has {reference_id}")
        return False

    # Find the closing </svg> tag
    closing_tag_pos = content.rfind('</svg>')
    if closing_tag_pos == -1:
        print(f"  ERROR: Could not find closing </svg> tag in {target_filepath.name}")
        return False

    # Create the off-screen reference group
    off_screen_group = f'''  <g id="{reference_id}" transform="translate({x_offset},0)">
    <!-- {consonant}o.svg reference -->
{o_content}
  </g>
'''

    # Insert before the closing </svg> tag
    new_content = content[:closing_tag_pos] + off_screen_group + content[closing_tag_pos:]

    with open(target_filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

    return True

def main():
    print("Copying o-series content to all consonant vowel variants...")
    print("=" * 70)

    total_processed = 0
    total_skipped = 0

    for consonant in consonants:
        # Source file: consonant + 'o'
        source_syllable = consonant + 'o'
        source_filepath = base_dir / f"sitelen kalama pona - {source_syllable}.svg"

        if not source_filepath.exists():
            print(f"\nWARNING: Source file not found: {source_filepath.name}")
            continue

        # Extract content
        o_content = extract_svg_content(source_filepath)
        if o_content is None:
            print(f"\nERROR: Could not extract content from {source_filepath.name}")
            continue

        # Build target list (all vowel variants for this consonant)
        targets = [consonant + vowel for vowel in vowel_variants]

        print(f"\nProcessing {consonant}-series (source: {source_syllable}.svg)")
        print(f"  Targets: {', '.join(targets)}")

        x_offset = x_offsets[consonant]

        # Process each target file
        for syllable in targets:
            target_filepath = base_dir / f"sitelen kalama pona - {syllable}.svg"

            if not target_filepath.exists():
                print(f"  WARNING: Target file not found: {target_filepath.name}")
                continue

            success = add_consonant_o_reference(target_filepath, o_content, consonant, x_offset)
            if success:
                print(f"  ✓ Added {consonant}o-reference to {target_filepath.name}")
                total_processed += 1
            else:
                total_skipped += 1

    print("\n" + "=" * 70)
    print(f"DONE! Processed: {total_processed} files, Skipped: {total_skipped} files")

if __name__ == "__main__":
    main()
