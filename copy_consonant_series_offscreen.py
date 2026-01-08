import os
import re
import sys
import io
from pathlib import Path

# Fix Unicode encoding on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Base directory
base_dir = Path(r"C:\Users\Immanuelle\Documents\Github\Sitelen\uniform_syllables")

# Define which consonant series to process
# Format: 'source_syllable': [list of target syllables]
consonant_series = {
    'ma': ['man', 'me', 'men', 'mi', 'min', 'mo', 'mon', 'mu', 'mun'],
    'na': ['nan', 'ne', 'nen', 'ni', 'nin', 'no', 'non', 'nu', 'nun']
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

def add_reference_to_file(target_filepath, reference_content, reference_id, consonant):
    """Add reference content to a target file, positioned off-screen"""
    with open(target_filepath, 'r', encoding='utf-8') as f:
        content = f.read()

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
    # Position based on consonant: m=1000, n=1500
    x_offset = 1000 if consonant == 'm' else 1500

    off_screen_group = f'''  <g id="{reference_id}" transform="translate({x_offset},0)">
    <!-- {consonant}-series reference -->
{reference_content}
  </g>
'''

    # Insert before the closing </svg> tag
    new_content = content[:closing_tag_pos] + off_screen_group + content[closing_tag_pos:]

    with open(target_filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

    return True

def main():
    print("Starting to copy consonant series content off-screen...")
    print("=" * 70)

    total_processed = 0
    total_skipped = 0

    for source_syllable, target_syllables in consonant_series.items():
        # Determine consonant letter
        consonant = source_syllable[0]

        # Get source file
        source_filepath = base_dir / f"sitelen kalama pona - {source_syllable}.svg"

        if not source_filepath.exists():
            print(f"\nWARNING: Source file not found: {source_filepath.name}")
            continue

        # Extract content
        source_content = extract_svg_content(source_filepath)
        if source_content is None:
            print(f"\nERROR: Could not extract content from {source_filepath.name}")
            continue

        print(f"\nProcessing {consonant}-series (source: {source_syllable}.svg)")
        print(f"  Targets: {', '.join(target_syllables)}")

        # Process each target file
        for syllable in target_syllables:
            target_filepath = base_dir / f"sitelen kalama pona - {syllable}.svg"

            if not target_filepath.exists():
                print(f"  WARNING: Target file not found: {target_filepath.name}")
                continue

            reference_id = f"{consonant}-reference"
            success = add_reference_to_file(target_filepath, source_content, reference_id, consonant)
            if success:
                print(f"  ✓ Added {reference_id} to {target_filepath.name}")
                total_processed += 1
            else:
                total_skipped += 1

    print("\n" + "=" * 70)
    print(f"DONE! Processed: {total_processed} files, Skipped: {total_skipped} files")

if __name__ == "__main__":
    main()
