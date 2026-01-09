import sys
import io
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def extract_ligature_mappings(font):
    """Extract ALL word -> glyph_name mappings from GSUB ligature table"""
    mappings = {}

    if 'GSUB' not in font:
        return mappings

    gsub = font['GSUB']
    cmap = font.getBestCmap()
    reverse_cmap = {v: k for k, v in cmap.items()}

    for feature_record in gsub.table.FeatureList.FeatureRecord:
        feature = feature_record.Feature

        for lookup_index in feature.LookupListIndex:
            lookup = gsub.table.LookupList.Lookup[lookup_index]

            # Type 4 is ligature substitution
            if lookup.LookupType == 4:
                for subtable in lookup.SubTable:
                    if hasattr(subtable, 'ligatures'):
                        for first_glyph, ligature_set in subtable.ligatures.items():
                            for ligature in ligature_set:
                                components = [first_glyph] + ligature.Component
                                result = ligature.LigGlyph

                                # Build Latin text from components
                                latin_chars = []
                                all_latin = True
                                for glyph in components:
                                    if glyph in reverse_cmap:
                                        char = chr(reverse_cmap[glyph])
                                        # Only include if it's a letter, digit, hyphen, or space
                                        if char.isalnum() or char in '-_ ':
                                            latin_chars.append(char)
                                        else:
                                            all_latin = False
                                            break
                                    else:
                                        all_latin = False
                                        break

                                if all_latin and latin_chars:
                                    latin_text = ''.join(latin_chars)
                                    mappings[latin_text] = result

    return mappings

def extract_glyph_by_name(font, glyph_name, output_path):
    """Extract a single glyph by name and save as SVG"""
    try:
        glyph_set = font.getGlyphSet()

        if glyph_name not in glyph_set:
            return False

        glyph = glyph_set[glyph_name]
        pen = SVGPathPen(glyph_set)
        glyph.draw(pen)
        path_data = pen.getCommands()

        if not path_data or path_data.strip() == '':
            return False

        width = glyph.width
        units_per_em = font['head'].unitsPerEm
        ascent = font['hhea'].ascent
        descent = font['hhea'].descent

        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 {-ascent} {width} {ascent - descent}">
  <path d="{path_data}" transform="scale(1,-1)" fill="currentColor"/>
</svg>
'''

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)

        return True

    except Exception as e:
        return False

def sanitize_filename(text):
    """Convert ligature text to safe filename"""
    # Replace spaces and special chars with hyphens
    safe = text.replace(' ', '-').replace('_', '-')
    # Remove any remaining unsafe characters
    safe = ''.join(c for c in safe if c.isalnum() or c == '-')
    return safe

def process_font(font_path, output_dir_name):
    """Process a font file and extract ALL Toki Pona glyphs using ligature mappings"""
    font_path = Path(font_path)

    if not font_path.exists():
        print(f"ERROR: Font file not found: {font_path}")
        return

    print(f"\n{'=' * 70}")
    print(f"Processing: {font_path.name}")
    print(f"{'=' * 70}\n")

    # Load font
    try:
        font = TTFont(font_path)
    except Exception as e:
        print(f"ERROR: Could not load font: {e}")
        return

    # Extract ligature mappings
    print("Extracting ligature mappings...")
    ligature_mappings = extract_ligature_mappings(font)
    print(f"Found {len(ligature_mappings)} ligature mappings\n")

    # Create output directory
    output_dir = Path("font_glyphs") / output_dir_name
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Output directory: {output_dir}\n")

    extracted = 0
    skipped = 0

    for text, glyph_name in sorted(ligature_mappings.items()):
        safe_name = sanitize_filename(text)
        output_file = output_dir / f"{output_dir_name}-{safe_name}.svg"

        if extract_glyph_by_name(font, glyph_name, output_file):
            extracted += 1
            if extracted % 100 == 0:
                print(f"  Extracted {extracted}/{len(ligature_mappings)}...")
        else:
            skipped += 1

    print(f"\n{'=' * 70}")
    print(f"Summary for {font_path.name}:")
    print(f"  ✓ Extracted: {extracted}")
    print(f"  ⚠ Skipped: {skipped}")
    print(f"{'=' * 70}\n")

def main():
    print("=" * 70)
    print("Toki Pona Font Glyph Extractor (ALL ligature mappings)")
    print("=" * 70)

    if len(sys.argv) < 2:
        print("\nUsage: python extract_all_ligatures.py <font_file> [output_dir_name]")
        sys.exit(1)

    font_path = sys.argv[1]

    if len(sys.argv) >= 3:
        output_dir_name = sys.argv[2]
    else:
        output_dir_name = Path(font_path).stem

    process_font(font_path, output_dir_name)
    print("Done!")

if __name__ == "__main__":
    main()
