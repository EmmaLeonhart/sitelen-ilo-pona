import sys
import io
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen

# Fix Unicode encoding on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Unicode mappings - word to hex code (without F19 prefix)
unicode_mappings = {
    'a': '00', 'akesi': '01', 'ala': '02', 'alasa': '03', 'ale': '04', 'ali': '04',
    'anpa': '05', 'ante': '06', 'anu': '07', 'awen': '08', 'e': '09', 'en': '0A',
    'esun': '0B', 'ijo': '0C', 'ike': '0D', 'ilo': '0E', 'insa': '0F', 'jaki': '10',
    'jan': '11', 'jelo': '12', 'jo': '13', 'kala': '14', 'kalama': '15', 'kama': '16',
    'kasi': '17', 'ken': '18', 'kepeken': '19', 'kili': '1A', 'kiwen': '1B', 'ko': '1C',
    'kon': '1D', 'kule': '1E', 'kulupu': '1F', 'kute': '20', 'la': '21', 'lape': '22',
    'laso': '23', 'lawa': '24', 'len': '25', 'lete': '26', 'li': '27', 'lili': '28',
    'linja': '29', 'lipu': '2A', 'loje': '2B', 'lon': '2C', 'luka': '2D', 'lukin': '2E',
    'lupa': '2F', 'ma': '30', 'mama': '31', 'mani': '32', 'meli': '33', 'mi': '34',
    'mije': '35', 'moku': '36', 'moli': '37', 'monsi': '38', 'mu': '39', 'mun': '3A',
    'musi': '3B', 'mute': '3C', 'nanpa': '3D', 'nasa': '3E', 'nasin': '3F', 'nena': '40',
    'ni': '41', 'nimi': '42', 'noka': '43', 'o': '44', 'olin': '45', 'ona': '46',
    'open': '47', 'pakala': '48', 'pali': '49', 'palisa': '4A', 'pan': '4B', 'pana': '4C',
    'pi': '4D', 'pilin': '4E', 'pimeja': '4F', 'pini': '50', 'pipi': '51', 'poka': '52',
    'poki': '53', 'pona': '54', 'pu': '55', 'sama': '56', 'seli': '57', 'selo': '58',
    'seme': '59', 'sewi': '5A', 'sijelo': '5B', 'sike': '5C', 'sin': '5D', 'sina': '5E',
    'sinpin': '5F', 'sitelen': '60', 'sona': '61', 'soweli': '62', 'suli': '63', 'suno': '64',
    'supa': '65', 'suwi': '66', 'tan': '67', 'taso': '68', 'tawa': '69', 'telo': '6A',
    'tenpo': '6B', 'toki': '6C', 'tomo': '6D', 'tu': '6E', 'unpa': '6F', 'uta': '70',
    'utala': '71', 'walo': '72', 'wan': '73', 'waso': '74', 'wawa': '75', 'weka': '76',
    'wile': '77', 'namako': '78', 'kin': '79', 'oko': '7A', 'kipisi': '7B', 'leko': '7C',
    'monsuta': '7D', 'tonsi': '7E', 'jasima': '7F', 'kijetesantakalu': '80', 'soko': '81',
    'meso': '82', 'epiku': '83', 'kokosila': '84', 'lanpan': '85', 'n': '86', 'misikeke': '87',
    'ku': '88', 'pake': 'A0', 'apeja': 'A1', 'majuna': 'A2', 'powe': 'A3'
}

# Toki Pona words (all unique words from unicode_mappings)
toki_pona_words = list(unicode_mappings.keys())

def extract_glyph_by_name(font, glyph_name, output_path):
    """Extract a single glyph by name and save as SVG"""
    try:
        # Get the glyph set
        glyph_set = font.getGlyphSet()

        # Check if glyph exists
        if glyph_name not in glyph_set:
            return False

        # Get the glyph
        glyph = glyph_set[glyph_name]

        # Create SVG pen
        pen = SVGPathPen(glyph_set)

        # Draw the glyph
        glyph.draw(pen)

        # Get the SVG path
        path_data = pen.getCommands()

        if not path_data or path_data.strip() == '':
            # Empty glyph
            return False

        # Get glyph metrics
        width = glyph.width

        # Get font metrics for proper viewBox
        units_per_em = font['head'].unitsPerEm
        ascent = font['hhea'].ascent
        descent = font['hhea'].descent

        # Create SVG with proper viewBox
        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 {-ascent} {width} {ascent - descent}">
  <path d="{path_data}" transform="scale(1,-1)" fill="currentColor"/>
</svg>
'''

        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)

        return True

    except Exception as e:
        return False

def process_font(font_path, output_dir_name):
    """Process a font file and extract Toki Pona glyphs by name"""
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

    # Get glyph set to see what's available
    glyph_set = font.getGlyphSet()
    all_glyph_names = list(glyph_set.keys())

    print(f"Font has {len(all_glyph_names)} total glyphs")
    print(f"Searching for Toki Pona word glyphs...\n")

    # Create output directory
    output_dir = Path("font_glyphs") / output_dir_name
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Output directory: {output_dir}\n")

    # Try various naming patterns
    extracted = 0
    skipped = 0

    for word in toki_pona_words:
        output_file = output_dir / f"{output_dir_name}-{word}.svg"

        # Try different glyph name patterns
        possible_names = [
            word,                    # exact match: "jan"
            word.capitalize(),       # capitalized: "Jan"
            f"sp.{word}",           # prefixed: "sp.jan"
            f"sitelen.{word}",      # prefixed: "sitelen.jan"
            f"pona.{word}",         # prefixed: "pona.jan"
            f"tp_{word}",           # underscore: "tp_jan"
            f"{word}.sp",           # suffixed: "jan.sp"
        ]

        # Add Unicode hex name pattern if this word has a mapping
        if word in unicode_mappings:
            hex_code = unicode_mappings[word]
            possible_names.append(f"uniF19{hex_code}")  # e.g., "uniF1911" for jan

        found = False
        for glyph_name in possible_names:
            if glyph_name in all_glyph_names:
                print(f"Extracting: {word:20} (glyph: {glyph_name:30}) -> {output_file.name}")
                if extract_glyph_by_name(font, glyph_name, output_file):
                    extracted += 1
                    found = True
                    break

        if not found:
            print(f"  ⚠ {word:20} -> No glyph found")
            skipped += 1

    print(f"\n{'=' * 70}")
    print(f"Summary for {font_path.name}:")
    print(f"  ✓ Extracted: {extracted}")
    print(f"  ⚠ Skipped: {skipped}")
    print(f"{'=' * 70}\n")

def main():
    print("=" * 70)
    print("Toki Pona Font Glyph Extractor (by glyph name)")
    print("=" * 70)

    if len(sys.argv) < 2:
        print("\nUsage: python extract_font_glyphs_by_name.py <font_file> [output_dir_name]")
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
