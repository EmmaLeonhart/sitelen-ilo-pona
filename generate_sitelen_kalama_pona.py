"""
Generate sitelen kalama pona composed SVG images.

Takes a toki pona phrase with a proper name like "jan sewi Amatelasu"
and generates an SVG combining word symbols and sound symbols.

Usage:
    python generate_sitelen_kalama_pona.py "jan sewi Amatelasu"
    python generate_sitelen_kalama_pona.py "tomo sewi Isukusima"

Requires: fontTools (pip install fonttools)
"""

import sys
import io
import os
import re
import xml.etree.ElementTree as ET
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen

SCRIPT_DIR = Path(__file__).parent
SYLLABLES_DIR = SCRIPT_DIR / 'uniform_syllables'
FONT_PATH = SCRIPT_DIR / 'sitelen-seli-kiwen.woff2'
LIGATURE_FONT_PATH = SCRIPT_DIR / 'linja-pona-precomposed.woff2'

# Word -> hex code mapping for F19xx codepoints (individual words)
WORD_CODEPOINTS = {
    'a': 0xF1900, 'akesi': 0xF1901, 'ala': 0xF1902, 'alasa': 0xF1903,
    'ale': 0xF1904, 'ali': 0xF1904, 'anpa': 0xF1905, 'ante': 0xF1906,
    'anu': 0xF1907, 'awen': 0xF1908, 'e': 0xF1909, 'en': 0xF190A,
    'esun': 0xF190B, 'ijo': 0xF190C, 'ike': 0xF190D, 'ilo': 0xF190E,
    'insa': 0xF190F, 'jaki': 0xF1910, 'jan': 0xF1911, 'jelo': 0xF1912,
    'jo': 0xF1913, 'kala': 0xF1914, 'kalama': 0xF1915, 'kama': 0xF1916,
    'kasi': 0xF1917, 'ken': 0xF1918, 'kepeken': 0xF1919, 'kili': 0xF191A,
    'kiwen': 0xF191B, 'ko': 0xF191C, 'kon': 0xF191D, 'kule': 0xF191E,
    'kulupu': 0xF191F, 'kute': 0xF1920, 'la': 0xF1921, 'lape': 0xF1922,
    'laso': 0xF1923, 'lawa': 0xF1924, 'len': 0xF1925, 'lete': 0xF1926,
    'li': 0xF1927, 'lili': 0xF1928, 'linja': 0xF1929, 'lipu': 0xF192A,
    'loje': 0xF192B, 'lon': 0xF192C, 'luka': 0xF192D, 'lukin': 0xF192E,
    'lupa': 0xF192F, 'ma': 0xF1930, 'mama': 0xF1931, 'mani': 0xF1932,
    'meli': 0xF1933, 'mi': 0xF1934, 'mije': 0xF1935, 'moku': 0xF1936,
    'moli': 0xF1937, 'monsi': 0xF1938, 'mu': 0xF1939, 'mun': 0xF193A,
    'musi': 0xF193B, 'mute': 0xF193C, 'nanpa': 0xF193D, 'nasa': 0xF193E,
    'nasin': 0xF193F, 'nena': 0xF1940, 'ni': 0xF1941, 'nimi': 0xF1942,
    'noka': 0xF1943, 'o': 0xF1944, 'olin': 0xF1945, 'ona': 0xF1946,
    'open': 0xF1947, 'pakala': 0xF1948, 'pali': 0xF1949, 'palisa': 0xF194A,
    'pan': 0xF194B, 'pana': 0xF194C, 'pi': 0xF194D, 'pilin': 0xF194E,
    'pimeja': 0xF194F, 'pini': 0xF1950, 'pipi': 0xF1951, 'poka': 0xF1952,
    'poki': 0xF1953, 'pona': 0xF1954, 'pu': 0xF1955, 'sama': 0xF1956,
    'seli': 0xF1957, 'selo': 0xF1958, 'seme': 0xF1959, 'sewi': 0xF195A,
    'sijelo': 0xF195B, 'sike': 0xF195C, 'sin': 0xF195D, 'sina': 0xF195E,
    'sinpin': 0xF195F, 'sitelen': 0xF1960, 'sona': 0xF1961, 'soweli': 0xF1962,
    'suli': 0xF1963, 'suno': 0xF1964, 'supa': 0xF1965, 'suwi': 0xF1966,
    'tan': 0xF1967, 'taso': 0xF1968, 'tawa': 0xF1969, 'telo': 0xF196A,
    'tenpo': 0xF196B, 'toki': 0xF196C, 'tomo': 0xF196D, 'tu': 0xF196E,
    'unpa': 0xF196F, 'uta': 0xF1970, 'utala': 0xF1971, 'walo': 0xF1972,
    'wan': 0xF1973, 'waso': 0xF1974, 'wawa': 0xF1975, 'weka': 0xF1976,
    'wile': 0xF1977, 'namako': 0xF1978, 'kin': 0xF1979, 'oko': 0xF197A,
    'kipisi': 0xF197B, 'leko': 0xF197C, 'monsuta': 0xF197D, 'tonsi': 0xF197E,
    'jasima': 0xF197F, 'kijetesantakalu': 0xF1980, 'soko': 0xF1981,
    'meso': 0xF1982, 'epiku': 0xF1983, 'kokosila': 0xF1984, 'lanpan': 0xF1985,
    'n': 0xF1986, 'misikeke': 0xF1987, 'ku': 0xF1988,
    'pake': 0xF19A0, 'apeja': 0xF19A1, 'majuna': 0xF19A2, 'powe': 0xF19A3,
}

# Special Commons filenames that don't follow the standard pattern
SPECIAL_COMMONS = {
    'tomo sewi': 'Tomo_sewi_old.svg',
}

CONSONANTS = set('mnptkwjls')
TARGET_HEIGHT = 1000
SPACING = 80


def load_ligatures():
    """Load ligature name list from linja-pona-precomposed GSUB (for knowing which compounds exist)."""
    if not LIGATURE_FONT_PATH.exists():
        return {}
    font = TTFont(str(LIGATURE_FONT_PATH))
    if 'GSUB' not in font:
        return {}

    gsub = font['GSUB']
    cmap = font.getBestCmap()
    reverse_cmap = {v: k for k, v in cmap.items()}
    ligatures = {}

    for fr in gsub.table.FeatureList.FeatureRecord:
        if fr.FeatureTag != 'liga':
            continue
        for li in fr.Feature.LookupListIndex:
            lookup = gsub.table.LookupList.Lookup[li]
            if lookup.LookupType != 4:
                continue
            for st in lookup.SubTable:
                if not hasattr(st, 'ligatures'):
                    continue
                for first_glyph, lig_set in st.ligatures.items():
                    for lig in lig_set:
                        components = [first_glyph] + lig.Component
                        chars = []
                        for g in components:
                            if g in reverse_cmap:
                                chars.append(chr(reverse_cmap[g]))
                            else:
                                chars.append(f'[{g}]')
                        text = ''.join(chars)
                        # Only keep clean toki pona ligatures
                        if re.match(r'^[a-z]+-[a-z]+(-[a-z]+)?$', text):
                            ligatures[text] = lig.LigGlyph
    font.close()
    return ligatures


def extract_glyph_path(font, codepoint):
    """Extract SVG path data and bounds for a glyph by codepoint."""
    glyph_set = font.getGlyphSet()
    cmap = font.getBestCmap()
    if codepoint not in cmap:
        return None, None
    glyph_name = cmap[codepoint]
    glyph = glyph_set[glyph_name]

    # Get path
    pen = SVGPathPen(glyph_set)
    glyph.draw(pen)
    path_data = pen.getCommands()

    # Get bounds
    bounds_pen = BoundsPen(glyph_set)
    glyph.draw(bounds_pen)
    bounds = bounds_pen.bounds  # (xMin, yMin, xMax, yMax)

    return path_data, bounds


def extract_glyph_by_name(font, glyph_name):
    """Extract SVG path data and bounds for a glyph by its name."""
    glyph_set = font.getGlyphSet()
    if glyph_name not in glyph_set:
        return None, None
    glyph = glyph_set[glyph_name]

    pen = SVGPathPen(glyph_set)
    glyph.draw(pen)
    path_data = pen.getCommands()

    bounds_pen = BoundsPen(glyph_set)
    glyph.draw(bounds_pen)
    bounds = bounds_pen.bounds

    return path_data, bounds


def parse_syllables(name):
    """Parse a proper name into toki pona syllables.
    e.g., 'Amatelasu' -> ['a', 'ma', 'te', 'la', 'su']
    """
    name = name.lower()
    syllables = []
    i = 0
    while i < len(name):
        if name[i] in CONSONANTS:
            syl = name[i]
            i += 1
            if i < len(name) and name[i] in 'aeiou':
                syl += name[i]
                i += 1
                # Optional coda n (only if next char is NOT a vowel)
                if i < len(name) and name[i] == 'n' and (i + 1 >= len(name) or name[i + 1] not in 'aeiou'):
                    syl += 'n'
                    i += 1
            syllables.append(syl)
        elif name[i] in 'aeiou':
            syl = name[i]
            i += 1
            if i < len(name) and name[i] == 'n' and (i + 1 >= len(name) or name[i + 1] not in 'aeiou'):
                syl += 'n'
                i += 1
            syllables.append(syl)
        else:
            i += 1  # skip unknown characters
    return syllables


def syllable_to_svg_name(syllable):
    """Convert a syllable to its SVG filename in uniform_syllables/.
    Null onset gets 'x' prefix, 'j' stays as 'j'.
    """
    if syllable[0] not in CONSONANTS:
        return 'x' + syllable
    return syllable


def read_syllable_svg_path(syllable):
    """Read the path data from a syllable SVG file. Returns (path_data, viewBox)."""
    svg_name = syllable_to_svg_name(syllable)
    svg_path = SYLLABLES_DIR / f'sitelen kalama pona - {svg_name}.svg'
    if not svg_path.exists():
        print(f'  Warning: syllable SVG not found: {svg_path.name}')
        return None, None

    tree = ET.parse(str(svg_path))
    root = tree.getroot()
    ns = {'svg': 'http://www.w3.org/2000/svg'}

    viewBox = root.get('viewBox', '0 0 1000 1000')
    parts = viewBox.split()
    vb = [float(x) for x in parts]

    path_el = root.find('.//svg:path', ns)
    if path_el is None:
        path_el = root.find('.//path')
    if path_el is None:
        return None, None

    return path_el.get('d'), vb


def word_commons_url(word):
    """Generate the Wikimedia Commons URL for a word glyph."""
    if word in SPECIAL_COMMONS:
        filename = SPECIAL_COMMONS[word]
    else:
        filename = f"Sitelen_seli_kiwen_-_{word.replace(' ', '-')}.svg"
    return f"https://commons.wikimedia.org/wiki/File:{filename}"


def syllable_commons_url(syllable):
    """Generate the Wikimedia Commons URL for a syllable glyph."""
    svg_name = syllable_to_svg_name(syllable)
    return f"https://commons.wikimedia.org/wiki/File:Sitelen_kalama_pona_-_{svg_name}.svg"


def parse_input(text):
    """Parse input into word tokens and sound name.
    Lowercase tokens = word symbols, first uppercase token starts sound symbols.
    """
    tokens = text.split()
    words = []
    sound_name = None

    for i, token in enumerate(tokens):
        if token[0].isupper():
            sound_name = ''.join(tokens[i:])
            break
        words.append(token)

    return words, sound_name


def match_ligatures(word_tokens, ligature_set):
    """Greedily match word tokens into ligatures where possible."""
    result = []
    i = 0
    while i < len(word_tokens):
        matched = False
        for length in range(min(4, len(word_tokens) - i), 1, -1):
            candidate = '-'.join(word_tokens[i:i + length])
            if candidate in ligature_set:
                result.append(' '.join(word_tokens[i:i + length]))
                i += length
                matched = True
                break
        if not matched:
            result.append(word_tokens[i])
            i += 1
    return result


def generate(text):
    """Generate a composed SVG for the given toki pona phrase."""
    print(f'Input: {text}')

    # Parse
    word_tokens, sound_name = parse_input(text)
    print(f'  Words: {word_tokens}')
    print(f'  Sound name: {sound_name}')

    # Load ligature names (from linja-pona-precomposed, just to know which compounds exist)
    ligatures = load_ligatures()
    print(f'  Loaded {len(ligatures)} known ligature names')

    # Match ligatures greedily
    matched_words = match_ligatures(word_tokens, ligatures)
    print(f'  Matched words: {matched_words}')

    # Parse syllables
    syllables = parse_syllables(sound_name) if sound_name else []
    print(f'  Syllables: {syllables}')

    # Load sitelen-seli-kiwen font for glyph extraction
    font = TTFont(str(FONT_PATH))

    pieces = []
    sources = []
    x_cursor = 0

    # Extract word glyphs from sitelen-seli-kiwen
    for word in matched_words:
        # For each word (single or compound), extract individual word glyphs
        # and place them together as one unit
        sub_words = word.split()
        word_pieces = []
        all_ok = True

        for sw in sub_words:
            if sw in WORD_CODEPOINTS:
                cp = WORD_CODEPOINTS[sw]
                path_data, bounds = extract_glyph_path(font, cp)
                if path_data and bounds:
                    word_pieces.append((sw, path_data, bounds))
                else:
                    print(f'  Warning: could not extract glyph for "{sw}"')
                    all_ok = False
            else:
                print(f'  Warning: unknown word "{sw}"')
                all_ok = False

        if not all_ok or not word_pieces:
            continue

        # For a compound, we stack the modifier on top of the head word
        # For now, place each word glyph sequentially as separate pieces
        for sw, path_data, bounds in word_pieces:
            xmin, ymin, xmax, ymax = bounds
            w = xmax - xmin
            h = ymax - ymin
            scale = TARGET_HEIGHT / h if h > 0 else 1
            pieces.append({
                'type': 'word',
                'path': path_data,
                'bounds': bounds,
                'scale': scale,
                'x_offset': x_cursor,
            })
            x_cursor += w * scale + SPACING

        source = word_commons_url(word)
        sources.append(f'{word}: {source}')
        print(f'  Extracted word glyph(s): {word}')

    # Extract syllable glyphs
    for syl in syllables:
        path_data, vb = read_syllable_svg_path(syl)
        if path_data and vb:
            vb_x, vb_y, vb_w, vb_h = vb
            scale = TARGET_HEIGHT / vb_h if vb_h > 0 else 1
            pieces.append({
                'type': 'syllable',
                'path': path_data,
                'viewbox': vb,
                'scale': scale,
                'x_offset': x_cursor,
            })
            x_cursor += vb_w * scale + SPACING
            sources.append(f'{syl}: {syllable_commons_url(syl)}')
            print(f'  Read syllable: {syl}')
        else:
            print(f'  Warning: could not read syllable "{syl}"')

    font.close()

    # Build SVG
    total_width = x_cursor - SPACING if pieces else 0

    comment_lines = [
        f'Representation of "{text}" in sitelen kalama pona',
        'Generated by generate_sitelen_kalama_pona.py',
        '',
        'Sources:',
    ] + [f'  {s}' for s in sources]
    comment = '\n'.join(comment_lines)

    svg_parts = [
        '<?xml version="1.0" encoding="UTF-8" standalone="no"?>',
        f'<!--\n{comment}\n-->',
        f'<svg version="1.1" width="{total_width:.0f}" height="{TARGET_HEIGHT}"',
        f'     viewBox="0 0 {total_width:.0f} {TARGET_HEIGHT}"',
        '     xmlns="http://www.w3.org/2000/svg">',
    ]

    for piece in pieces:
        if piece['type'] == 'word':
            xmin, ymin, xmax, ymax = piece['bounds']
            w = xmax - xmin
            h = ymax - ymin
            s = piece['scale']
            # Font glyphs have Y-up, SVG is Y-down: scale(1,-1) and translate
            tx = piece['x_offset'] - xmin * s
            ty = ymax * s  # after flip, ymax becomes the top
            svg_parts.append(
                f'  <path d="{piece["path"]}"'
                f' transform="translate({tx:.2f},{ty:.2f}) scale({s:.4f},{-s:.4f})"'
                f' fill="#000000" />'
            )
        elif piece['type'] == 'syllable':
            vb_x, vb_y, vb_w, vb_h = piece['viewbox']
            s = piece['scale']
            tx = piece['x_offset'] - vb_x * s
            ty = -vb_y * s
            svg_parts.append(
                f'  <path d="{piece["path"]}"'
                f' transform="translate({tx:.2f},{ty:.2f}) scale({s:.4f},{s:.4f})"'
                f' fill="#000000" />'
            )

    svg_parts.append('</svg>')
    svg_content = '\n'.join(svg_parts) + '\n'

    # Output
    output_name = f'sitelen kalama pona - {text}.svg'
    output_path = SYLLABLES_DIR / output_name
    with open(str(output_path), 'w', encoding='utf-8') as f:
        f.write(svg_content)

    print(f'\n  Output: {output_path}')
    return output_path


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python generate_sitelen_kalama_pona.py "jan sewi Amatelasu"')
        sys.exit(1)

    text = sys.argv[1]
    generate(text)
