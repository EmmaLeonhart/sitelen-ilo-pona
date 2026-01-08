import os
import re
import sys
import io
from pathlib import Path

# Fix Unicode encoding on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Base directory
base_dir = Path(r"C:\Users\Immanuelle\Documents\Github\Sitelen\uniform_syllables")

# Source file
source_file = base_dir / "sitelen kalama pona - ma.svg"

# Target files: all m-series and n-series except ma itself
m_series_targets = ['man', 'me', 'men', 'mi', 'min', 'mo', 'mon', 'mu', 'mun']
n_series_targets = ['na', 'nan', 'ne', 'nen', 'ni', 'nin', 'no', 'non', 'nu', 'nun']

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

def add_ma_reference_to_file(target_filepath, ma_content, series_letter):
    """Add ma reference content to a target file, positioned off-screen"""
    with open(target_filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    reference_id = f"{series_letter}-reference"

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
    # Position based on series: m=1000, n=1500
    x_offset = 1000 if series_letter == 'm' else 1500

    off_screen_group = f'''  <g id="{reference_id}" transform="translate({x_offset},0)">
    <!-- ma.svg reference for {series_letter}-series -->
{ma_content}
  </g>
'''

    # Insert before the closing </svg> tag
    new_content = content[:closing_tag_pos] + off_screen_group + content[closing_tag_pos:]

    with open(target_filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

    return True

def main():
    print("Copying ma.svg content off-screen to m-series and n-series files...")
    print("=" * 70)

    # Read the source file
    if not source_file.exists():
        print(f"ERROR: Source file not found: {source_file}")
        return

    ma_content = extract_svg_content(source_file)
    if ma_content is None:
        print(f"ERROR: Could not extract content from {source_file}")
        return

    print(f"Source: {source_file.name}\n")

    total_processed = 0
    total_skipped = 0

    # Process m-series
    print("Processing m-series:")
    print(f"  Targets: {', '.join(m_series_targets)}")
    for syllable in m_series_targets:
        target_filepath = base_dir / f"sitelen kalama pona - {syllable}.svg"
        if not target_filepath.exists():
            print(f"  WARNING: Target file not found: {target_filepath.name}")
            continue

        success = add_ma_reference_to_file(target_filepath, ma_content, 'm')
        if success:
            print(f"  ✓ Added m-reference to {target_filepath.name}")
            total_processed += 1
        else:
            total_skipped += 1

    # Process n-series
    print("\nProcessing n-series:")
    print(f"  Targets: {', '.join(n_series_targets)}")
    for syllable in n_series_targets:
        target_filepath = base_dir / f"sitelen kalama pona - {syllable}.svg"
        if not target_filepath.exists():
            print(f"  WARNING: Target file not found: {target_filepath.name}")
            continue

        success = add_ma_reference_to_file(target_filepath, ma_content, 'n')
        if success:
            print(f"  ✓ Added n-reference to {target_filepath.name}")
            total_processed += 1
        else:
            total_skipped += 1

    print("\n" + "=" * 70)
    print(f"DONE! Processed: {total_processed} files, Skipped: {total_skipped} files")

if __name__ == "__main__":
    main()
