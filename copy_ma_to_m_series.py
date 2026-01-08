import os
import sys
import io
from pathlib import Path

# Fix Unicode encoding on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Base directory
base_dir = Path(r"C:\Users\Immanuelle\Documents\Github\Sitelen\uniform_syllables")

# Source file
source_file = base_dir / "sitelen kalama pona - ma.svg"

# Target m-series files (NOT ma, just the other m-series)
m_series_targets = ['man', 'me', 'men', 'mi', 'min', 'mo', 'mon', 'mu', 'mun']

def main():
    print("Copying ma.svg content to all other m-series files...")
    print("=" * 70)

    # Read the source file
    if not source_file.exists():
        print(f"ERROR: Source file not found: {source_file}")
        return

    with open(source_file, 'r', encoding='utf-8') as f:
        ma_content = f.read()

    print(f"Source: {source_file.name}")
    print(f"Targets: {', '.join(m_series_targets)}\n")

    total_processed = 0

    # Copy to each target file
    for syllable in m_series_targets:
        target_filepath = base_dir / f"sitelen kalama pona - {syllable}.svg"

        if not target_filepath.exists():
            print(f"  WARNING: Target file not found: {target_filepath.name}")
            continue

        # Write the ma.svg content to the target file
        with open(target_filepath, 'w', encoding='utf-8') as f:
            f.write(ma_content)

        print(f"  ✓ Copied to {target_filepath.name}")
        total_processed += 1

    print("\n" + "=" * 70)
    print(f"DONE! Copied ma.svg to {total_processed} files")

if __name__ == "__main__":
    main()
