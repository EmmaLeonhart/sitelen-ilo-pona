"""
Build a downloadable .otf font from the sitelen kalama pona glyph files.

Reads FontForge .glyph files from ..sfdir/ and produces
sitelen-kalama-pona.otf using fontTools.

Each syllable is mapped to a Unicode PUA codepoint starting at U+E100.

Usage:
    python build_font.py
"""

import re
import sys
from pathlib import Path

from fontTools.fontBuilder import FontBuilder
from fontTools.misc.psCharStrings import T2CharString

SCRIPT_DIR = Path(__file__).parent
ROOT_DIR = SCRIPT_DIR.parent
SFDIR = ROOT_DIR / '..sfdir'

ASCENT = 800
DESCENT = 200
UPM = ASCENT + DESCENT  # 1000

# All toki pona syllables in order
CONSONANTS = ['', 'm', 'n', 'p', 't', 'k', 'w', 'j', 'l', 's']
VOWELS = ['a', 'an', 'e', 'en', 'i', 'in', 'o', 'on', 'u', 'un']

SYLLABLES = []
for c in CONSONANTS:
    for v in VOWELS:
        SYLLABLES.append(c + v)

PUA_BASE = 0xE100


def parse_splineset(lines):
    """Parse FontForge SplineSet into a list of contours.

    Each contour is a list of (op, *coords) in absolute coordinates.
    """
    contours = []
    current = []
    for line in lines:
        line = line.strip()
        if not line or line == 'EndSplineSet':
            break
        tokens = line.split()

        if len(tokens) >= 3 and tokens[-2] == 'm':
            if current:
                contours.append(current)
                current = []
            current.append(('m', float(tokens[0]), float(tokens[1])))
        elif len(tokens) >= 3 and tokens[-2] == 'l':
            current.append(('l', float(tokens[0]), float(tokens[1])))
        elif len(tokens) >= 7 and tokens[-2] == 'c':
            current.append(('c',
                            float(tokens[0]), float(tokens[1]),
                            float(tokens[2]), float(tokens[3]),
                            float(tokens[4]), float(tokens[5])))

    if current:
        contours.append(current)
    return contours


def contours_to_charstring(contours, width):
    """Convert contours to a T2CharString program (relative coordinates)."""
    program = []
    # Width is encoded as first value if different from default
    program.append(width)
    cx, cy = 0, 0

    for contour in contours:
        for seg in contour:
            if seg[0] == 'm':
                dx = round(seg[1] - cx)
                dy = round(seg[2] - cy)
                program.extend([dx, dy, 'rmoveto'])
                cx, cy = seg[1], seg[2]
            elif seg[0] == 'l':
                dx = round(seg[1] - cx)
                dy = round(seg[2] - cy)
                program.extend([dx, dy, 'rlineto'])
                cx, cy = seg[1], seg[2]
            elif seg[0] == 'c':
                dx1 = round(seg[1] - cx)
                dy1 = round(seg[2] - cy)
                dx2 = round(seg[3] - seg[1])
                dy2 = round(seg[4] - seg[2])
                dx3 = round(seg[5] - seg[3])
                dy3 = round(seg[6] - seg[4])
                program.extend([dx1, dy1, dx2, dy2, dx3, dy3, 'rrcurveto'])
                cx, cy = seg[5], seg[6]

    program.append('endchar')

    cs = T2CharString()
    cs.program = program
    return cs


def load_glyph(syllable):
    """Load a glyph file and return (width, contours) or None."""
    glyph_name = syllable if syllable and syllable[0] in 'mnptkwjls' else syllable
    glyph_file = SFDIR / f'{glyph_name}.sitelen_kalama_pona.glyph'

    if not glyph_file.exists():
        return None

    content = glyph_file.read_text(encoding='utf-8')

    width_match = re.search(r'Width:\s+(\d+)', content)
    width = int(width_match.group(1)) if width_match else 1000

    spline_match = re.search(r'SplineSet\n(.*?)EndSplineSet', content, re.DOTALL)
    if not spline_match:
        return None

    spline_lines = spline_match.group(1).strip().split('\n')
    contours = parse_splineset(spline_lines)
    return width, contours


def make_notdef_charstring():
    """Create a simple .notdef rectangle charstring."""
    cs = T2CharString()
    cs.program = [
        500,  # width
        50, 0, 'rmoveto',
        400, 0, 'rlineto',
        0, 700, 'rlineto',
        -400, 0, 'rlineto',
        'endchar',
    ]
    return cs


def main():
    print('Building sitelen kalama pona font...')

    glyph_data = {}
    cmap = {}

    for i, syllable in enumerate(SYLLABLES):
        glyph_name = f'skp.{syllable}'
        result = load_glyph(syllable)
        if result is None:
            print(f'  Skipping {syllable} (no glyph file)')
            continue
        glyph_data[glyph_name] = result
        cmap[PUA_BASE + i] = glyph_name
        print(f'  Loaded {syllable} -> U+{PUA_BASE + i:04X}')

    if not glyph_data:
        print('No glyphs loaded!', file=sys.stderr)
        sys.exit(1)

    glyph_order = ['.notdef'] + sorted(glyph_data.keys())

    fb = FontBuilder(UPM, isTTF=False)
    fb.setupGlyphOrder(glyph_order)
    fb.setupCharacterMap(cmap)

    # Build charstrings
    charstrings = {'.notdef': make_notdef_charstring()}
    for glyph_name, (width, contours) in glyph_data.items():
        charstrings[glyph_name] = contours_to_charstring(contours, width)

    fb.setupCFF(
        'SitelenKalamaPona-Regular',
        {'FullName': 'Sitelen Kalama Pona', 'FamilyName': 'Sitelen Kalama Pona'},
        charstrings,
        {},
    )

    metrics = {'.notdef': (500, 0)}
    for glyph_name, (width, _) in glyph_data.items():
        metrics[glyph_name] = (width, 0)

    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=ASCENT, descent=-DESCENT)
    fb.setupOS2(
        sTypoAscender=ASCENT,
        sTypoDescender=-DESCENT,
        sTypoLineGap=0,
        usWinAscent=ASCENT,
        usWinDescent=DESCENT,
        sxHeight=500,
        sCapHeight=700,
        fsType=0,
    )
    fb.setupNameTable({
        'familyName': 'Sitelen Kalama Pona',
        'styleName': 'Regular',
    })
    fb.setupPost()

    otf_path = ROOT_DIR / 'fonts' / 'sitelen-kalama-pona.otf'
    fb.font.save(str(otf_path))
    print(f'\nWrote {otf_path}')

    # Also save as woff2
    try:
        fb.font.flavor = 'woff2'
        woff2_path = ROOT_DIR / 'fonts' / 'sitelen-kalama-pona.woff2'
        fb.font.save(str(woff2_path))
        print(f'Wrote {woff2_path}')
    except Exception as exc:
        print(f'WOFF2 export skipped: {exc}')

    print(f'\nCodepoint mapping ({len(glyph_data)} syllables):')
    for i, syllable in enumerate(SYLLABLES):
        glyph_name = f'skp.{syllable}'
        if glyph_name in glyph_data:
            print(f'  U+{PUA_BASE + i:04X}  {syllable}')


if __name__ == '__main__':
    main()
