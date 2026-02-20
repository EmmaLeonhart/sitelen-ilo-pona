"""Extract all glyphs from sitelen-seli-kiwen.woff2 into individual SVG files.

Uses uharfbuzz to discover compound word glyphs via ZWJ shaping.
Outputs files named to match Wikimedia Commons conventions:
  - Individual: 'Sitelen seli kiwen - jan.svg'
  - Compound:   'Sitelen seli kiwen - jan-sewi.svg'
"""
import sys, io, os, tempfile
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
import uharfbuzz as hb

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SCRIPT_DIR = Path(__file__).parent
ROOT_DIR = SCRIPT_DIR.parent
FONT_PATH = ROOT_DIR / 'fonts' / 'sitelen-seli-kiwen.woff2'
OUTPUT_DIR = ROOT_DIR / 'sitelen_seli_kiwen_svgs'

# Word -> F19xx codepoint
WORDS = {
    'a': 0xF1900, 'akesi': 0xF1901, 'ala': 0xF1902, 'alasa': 0xF1903,
    'ale': 0xF1904, 'anpa': 0xF1905, 'ante': 0xF1906, 'anu': 0xF1907,
    'awen': 0xF1908, 'e': 0xF1909, 'en': 0xF190A, 'esun': 0xF190B,
    'ijo': 0xF190C, 'ike': 0xF190D, 'ilo': 0xF190E, 'insa': 0xF190F,
    'jaki': 0xF1910, 'jan': 0xF1911, 'jelo': 0xF1912, 'jo': 0xF1913,
    'kala': 0xF1914, 'kalama': 0xF1915, 'kama': 0xF1916, 'kasi': 0xF1917,
    'ken': 0xF1918, 'kepeken': 0xF1919, 'kili': 0xF191A, 'kiwen': 0xF191B,
    'ko': 0xF191C, 'kon': 0xF191D, 'kule': 0xF191E, 'kulupu': 0xF191F,
    'kute': 0xF1920, 'la': 0xF1921, 'lape': 0xF1922, 'laso': 0xF1923,
    'lawa': 0xF1924, 'len': 0xF1925, 'lete': 0xF1926, 'li': 0xF1927,
    'lili': 0xF1928, 'linja': 0xF1929, 'lipu': 0xF192A, 'loje': 0xF192B,
    'lon': 0xF192C, 'luka': 0xF192D, 'lukin': 0xF192E, 'lupa': 0xF192F,
    'ma': 0xF1930, 'mama': 0xF1931, 'mani': 0xF1932, 'meli': 0xF1933,
    'mi': 0xF1934, 'mije': 0xF1935, 'moku': 0xF1936, 'moli': 0xF1937,
    'monsi': 0xF1938, 'mu': 0xF1939, 'mun': 0xF193A, 'musi': 0xF193B,
    'mute': 0xF193C, 'nanpa': 0xF193D, 'nasa': 0xF193E, 'nasin': 0xF193F,
    'nena': 0xF1940, 'ni': 0xF1941, 'nimi': 0xF1942, 'noka': 0xF1943,
    'o': 0xF1944, 'olin': 0xF1945, 'ona': 0xF1946, 'open': 0xF1947,
    'pakala': 0xF1948, 'pali': 0xF1949, 'palisa': 0xF194A, 'pan': 0xF194B,
    'pana': 0xF194C, 'pi': 0xF194D, 'pilin': 0xF194E, 'pimeja': 0xF194F,
    'pini': 0xF1950, 'pipi': 0xF1951, 'poka': 0xF1952, 'poki': 0xF1953,
    'pona': 0xF1954, 'pu': 0xF1955, 'sama': 0xF1956, 'seli': 0xF1957,
    'selo': 0xF1958, 'seme': 0xF1959, 'sewi': 0xF195A, 'sijelo': 0xF195B,
    'sike': 0xF195C, 'sin': 0xF195D, 'sina': 0xF195E, 'sinpin': 0xF195F,
    'sitelen': 0xF1960, 'sona': 0xF1961, 'soweli': 0xF1962, 'suli': 0xF1963,
    'suno': 0xF1964, 'supa': 0xF1965, 'suwi': 0xF1966, 'tan': 0xF1967,
    'taso': 0xF1968, 'tawa': 0xF1969, 'telo': 0xF196A, 'tenpo': 0xF196B,
    'toki': 0xF196C, 'tomo': 0xF196D, 'tu': 0xF196E, 'unpa': 0xF196F,
    'uta': 0xF1970, 'utala': 0xF1971, 'walo': 0xF1972, 'wan': 0xF1973,
    'waso': 0xF1974, 'wawa': 0xF1975, 'weka': 0xF1976, 'wile': 0xF1977,
    'namako': 0xF1978, 'kin': 0xF1979, 'oko': 0xF197A, 'kipisi': 0xF197B,
    'leko': 0xF197C, 'monsuta': 0xF197D, 'tonsi': 0xF197E, 'jasima': 0xF197F,
    'kijetesantakalu': 0xF1980, 'soko': 0xF1981, 'meso': 0xF1982,
    'epiku': 0xF1983, 'kokosila': 0xF1984, 'lanpan': 0xF1985, 'n': 0xF1986,
    'misikeke': 0xF1987, 'ku': 0xF1988,
    'pake': 0xF19A0, 'apeja': 0xF19A1, 'majuna': 0xF19A2, 'powe': 0xF19A3,
}

ZWJ = 0x200D


def extract_glyph_svg_by_name(font, glyph_set, glyph_name):
    """Extract a glyph by its internal name as SVG."""
    if glyph_name not in glyph_set:
        return None
    glyph = glyph_set[glyph_name]

    pen = SVGPathPen(glyph_set)
    glyph.draw(pen)
    path_data = pen.getCommands()
    if not path_data:
        return None

    ascent = font['hhea'].ascent
    descent = font['hhea'].descent

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 {-ascent} {glyph.width} {ascent - descent}">
  <path d="{path_data}" transform="scale(1,-1)" fill="currentColor"/>
</svg>
'''
    return svg


def find_compounds_via_harfbuzz(font_path, ttfont):
    """Use harfbuzz to find all 2-word ZWJ compounds."""
    # Save as TTF for harfbuzz (it can't read WOFF2 cmap properly)
    tmp = tempfile.NamedTemporaryFile(suffix='.ttf', delete=False)
    tmp_path = tmp.name
    tmp.close()
    ttfont_copy = TTFont(str(font_path))
    ttfont_copy.flavor = None
    ttfont_copy.save(tmp_path)
    ttfont_copy.close()

    with open(tmp_path, 'rb') as f:
        font_data = f.read()
    os.unlink(tmp_path)

    blob = hb.Blob(font_data)
    face = hb.Face(blob)
    hb_font = hb.Font(face)
    glyph_order = ttfont.getGlyphOrder()
    word_list = sorted(WORDS.keys())

    compounds = {}
    for w1 in word_list:
        for w2 in word_list:
            buf = hb.Buffer()
            buf.add_codepoints([WORDS[w1], ZWJ, WORDS[w2]])
            buf.guess_segment_properties()
            hb.shape(hb_font, buf, {'calt': True, 'liga': True, 'rlig': True})
            infos = buf.glyph_infos
            if len(infos) == 1:
                gid = infos[0].codepoint
                gname = glyph_order[gid]
                compounds[f'{w1}-{w2}'] = gname

    return compounds


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    font = TTFont(str(FONT_PATH))
    glyph_set = font.getGlyphSet()
    cmap = font.getBestCmap()

    # 1. Extract individual words
    count = 0
    for word, cp in sorted(WORDS.items()):
        if cp not in cmap:
            print(f'  SKIP: {word} (not in cmap)')
            continue
        glyph_name = cmap[cp]
        svg = extract_glyph_svg_by_name(font, glyph_set, glyph_name)
        if svg:
            filename = f'Sitelen seli kiwen - {word}.svg'
            (OUTPUT_DIR / filename).write_text(svg, encoding='utf-8')
            count += 1
            print(f'  {word}')
        else:
            print(f'  SKIP: {word} (no path data)')

    print(f'\nExtracted {count} individual word SVGs')

    # 2. Find and extract compound glyphs via harfbuzz ZWJ shaping
    print('\nDiscovering compound glyphs via harfbuzz...')
    compounds = find_compounds_via_harfbuzz(FONT_PATH, font)
    print(f'Found {len(compounds)} compounds')

    compound_count = 0
    for name, glyph_name in sorted(compounds.items()):
        svg = extract_glyph_svg_by_name(font, glyph_set, glyph_name)
        if svg:
            filename = f'Sitelen seli kiwen - {name}.svg'
            (OUTPUT_DIR / filename).write_text(svg, encoding='utf-8')
            compound_count += 1
            print(f'  {name}')

    print(f'\nExtracted {compound_count} compound SVGs')
    print(f'Total: {count + compound_count} SVGs saved to: {OUTPUT_DIR}')
    font.close()


if __name__ == '__main__':
    main()
