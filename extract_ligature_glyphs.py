import sys
import io
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Toki Pona words we want to extract
toki_pona_words = [
    'a', 'akesi', 'ala', 'alasa', 'ale', 'ali', 'anpa', 'ante', 'anu', 'apeja', 'awen',
    'e', 'en', 'epiku', 'esun', 'ijo', 'ike', 'ilo', 'insa', 'jaki', 'jan', 'jasima',
    'jelo', 'jo', 'kala', 'kalama', 'kama', 'kasi', 'ken', 'kepeken', 'kijetesantakalu',
    'kili', 'kin', 'kipisi', 'kiwen', 'ko', 'kokosila', 'kon', 'ku', 'kule', 'kulupu',
    'kute', 'la', 'lanpan', 'lape', 'laso', 'lawa', 'leko', 'len', 'lete', 'li', 'lili',
    'linja', 'lipu', 'loje', 'lon', 'luka', 'lukin', 'lupa', 'ma', 'majuna', 'mama',
    'mani', 'meli', 'meso', 'mi', 'mije', 'misikeke', 'moku', 'moli', 'monsi', 'monsuta',
    'mu', 'mun', 'musi', 'mute', 'n', 'namako', 'nanpa', 'nasa', 'nasin', 'nena', 'ni',
    'nimi', 'noka', 'o', 'oko', 'olin', 'ona', 'open', 'pakala', 'pake', 'pali', 'palisa',
    'pan', 'pana', 'pi', 'pilin', 'pimeja', 'pini', 'pipi', 'poka', 'poki', 'pona',
    'powe', 'pu', 'sama', 'seli', 'selo', 'seme', 'sewi', 'sijelo', 'sike', 'sin', 'sina',
    'sinpin', 'sitelen', 'soko', 'sona', 'soweli', 'suli', 'suno', 'supa', 'suwi', 'tan',
    'taso', 'tawa', 'telo', 'tenpo', 'toki', 'tomo', 'tonsi', 'tu', 'unpa', 'uta', 'utala',
    'walo', 'wan', 'waso', 'wawa', 'weka', 'wile'
]

def extract_ligature_mappings(font):
    """Extract word -> glyph_name mappings from GSUB ligature table"""
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
                                for glyph in components:
                                    if glyph in reverse_cmap:
                                        char = chr(reverse_cmap[glyph])
                                        latin_chars.append(char)

                                if latin_chars:
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

def process_font(font_path, output_dir_name):
    """Process a font file and extract Toki Pona glyphs using ligature mappings"""
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

    for word in toki_pona_words:
        output_file = output_dir / f"{output_dir_name}-{word}.svg"

        # Check if this word has a ligature mapping
        if word in ligature_mappings:
            glyph_name = ligature_mappings[word]
            print(f"Extracting: {word:20} (glyph: {glyph_name:30}) -> {output_file.name}")
            if extract_glyph_by_name(font, glyph_name, output_file):
                extracted += 1
            else:
                skipped += 1
        else:
            print(f"  ⚠ {word:20} -> No ligature mapping found")
            skipped += 1

    print(f"\n{'=' * 70}")
    print(f"Summary for {font_path.name}:")
    print(f"  ✓ Extracted: {extracted}")
    print(f"  ⚠ Skipped: {skipped}")
    print(f"{'=' * 70}\n")

def main():
    print("=" * 70)
    print("Toki Pona Font Glyph Extractor (via ligature mappings)")
    print("=" * 70)

    if len(sys.argv) < 2:
        print("\nUsage: python extract_ligature_glyphs.py <font_file> [output_dir_name]")
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
