"""
Generate sitelen kalama pona composed SVG images.

Takes a toki pona phrase with a proper name like "jan sewi Amatelasu"
and generates an SVG combining word symbols and sound symbols.

Uses pre-extracted SVGs from sitelen_seli_kiwen_svgs/ and uniform_syllables/.

Usage:
    python generate_sitelen_kalama_pona.py "jan sewi Amatelasu"
    python generate_sitelen_kalama_pona.py "tomo sewi Isukusima"
"""

import sys
import io
import re
import xml.etree.ElementTree as ET
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SCRIPT_DIR = Path(__file__).parent
SYLLABLES_DIR = SCRIPT_DIR / 'uniform_syllables'
WORD_SVGS_DIR = SCRIPT_DIR / 'sitelen_seli_kiwen_svgs'

# Special Commons filenames that don't follow the standard pattern
SPECIAL_COMMONS = {
    'tomo sewi': 'Tomo_sewi_old.svg',
}

CONSONANTS = set('mnptkwjls')
TARGET_HEIGHT = 1000
SPACING = 80


def get_available_compounds():
    """Scan sitelen_seli_kiwen_svgs/ for compound SVG files (those with hyphens)."""
    compounds = set()
    for f in WORD_SVGS_DIR.glob('Sitelen seli kiwen - *-*.svg'):
        name = f.stem.replace('Sitelen seli kiwen - ', '')
        compounds.add(name)
    return compounds


def read_svg_paths(svg_file):
    """Read path data and viewBox from an SVG file. Returns (paths, viewBox)."""
    if not svg_file.exists():
        return None, None

    tree = ET.parse(str(svg_file))
    root = tree.getroot()
    ns = {'svg': 'http://www.w3.org/2000/svg'}

    viewBox = root.get('viewBox', '0 0 1000 1000')
    vb = [float(x) for x in viewBox.split()]

    path_els = root.findall('.//svg:path', ns)
    if not path_els:
        path_els = root.findall('.//path')
    if not path_els:
        return None, None

    paths = []
    for path_el in path_els:
        d = path_el.get('d')
        if not d:
            continue
        transform = path_el.get('transform', '')
        paths.append({'d': d, 'transform': transform})

    if not paths:
        return None, None

    return paths, vb


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
            i += 1
    return syllables


def syllable_to_svg_name(syllable):
    """Convert a syllable to its SVG filename prefix.
    Null onset gets 'x' prefix.
    """
    if syllable[0] not in CONSONANTS:
        return 'x' + syllable
    return syllable


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


def match_compounds(word_tokens, compound_set):
    """Greedily match word tokens into compounds where possible."""
    result = []
    i = 0
    while i < len(word_tokens):
        matched = False
        for length in range(min(4, len(word_tokens) - i), 1, -1):
            candidate = '-'.join(word_tokens[i:i + length])
            if candidate in compound_set:
                result.append(candidate)
                i += length
                matched = True
                break
        if not matched:
            result.append(word_tokens[i])
            i += 1
    return result


def word_commons_url(word):
    """Generate the Wikimedia Commons URL for a word glyph."""
    if word.replace('-', ' ') in SPECIAL_COMMONS:
        filename = SPECIAL_COMMONS[word.replace('-', ' ')]
    else:
        filename = f"Sitelen_seli_kiwen_-_{word}.svg"
    return f"https://commons.wikimedia.org/wiki/File:{filename}"


def syllable_commons_url(syllable):
    """Generate the Wikimedia Commons URL for a syllable glyph."""
    svg_name = syllable_to_svg_name(syllable)
    return f"https://commons.wikimedia.org/wiki/File:Sitelen_kalama_pona_-_{svg_name}.svg"


def generate(text):
    """Generate a composed SVG for the given toki pona phrase."""
    print(f'Input: {text}')

    word_tokens, sound_name = parse_input(text)
    print(f'  Words: {word_tokens}')
    print(f'  Sound name: {sound_name}')

    # Find available compounds from extracted SVGs
    compound_set = get_available_compounds()
    print(f'  Available compounds: {len(compound_set)}')

    # Match compounds greedily
    matched_words = match_compounds(word_tokens, compound_set)
    print(f'  Matched words: {matched_words}')

    # Parse syllables
    syllables = parse_syllables(sound_name) if sound_name else []
    print(f'  Syllables: {syllables}')

    pieces = []
    sources = []
    x_cursor = 0

    # Read word SVGs
    for word in matched_words:
        svg_file = WORD_SVGS_DIR / f'Sitelen seli kiwen - {word}.svg'
        paths, vb = read_svg_paths(svg_file)

        if paths and vb:
            vb_x, vb_y, vb_w, vb_h = vb
            scale = TARGET_HEIGHT / vb_h if vb_h > 0 else 1
            pieces.append({
                'type': 'word',
                'paths': paths,
                'viewbox': vb,
                'scale': scale,
                'x_offset': x_cursor,
            })
            x_cursor += vb_w * scale + SPACING
            sources.append(f'{word}: {word_commons_url(word)}')
            print(f'  Loaded word SVG: {word}')
        else:
            print(f'  Warning: could not load SVG for "{word}"')

    # Read syllable SVGs
    for syl in syllables:
        svg_name = syllable_to_svg_name(syl)
        svg_file = SYLLABLES_DIR / f'sitelen kalama pona - {svg_name}.svg'
        paths, vb = read_svg_paths(svg_file)

        if paths and vb:
            vb_x, vb_y, vb_w, vb_h = vb
            scale = TARGET_HEIGHT / vb_h if vb_h > 0 else 1
            pieces.append({
                'type': 'syllable',
                'paths': paths,
                'viewbox': vb,
                'scale': scale,
                'x_offset': x_cursor,
            })
            x_cursor += vb_w * scale + SPACING
            sources.append(f'{syl}: {syllable_commons_url(syl)}')
            print(f'  Loaded syllable: {syl}')
        else:
            print(f'  Warning: could not load syllable "{syl}"')

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

    def strip_flip_transform(transform):
        if not transform:
            return ''
        return re.sub(r'scale\(\s*1\s*,\s*-1\s*\)', '', transform).strip()

    for piece in pieces:
        vb_x, vb_y, vb_w, vb_h = piece['viewbox']
        s = piece['scale']
        tx = piece['x_offset'] - vb_x * s
        ty = -vb_y * s

        for path in piece['paths']:
            transform = path.get('transform', '')
            has_flip = 'scale(1,-1)' in transform.replace(' ', '')
            inner_transform = strip_flip_transform(transform) if has_flip else transform
            inner_transform = inner_transform.strip()

            if has_flip:
                # Word SVGs from font: viewBox like "0 -1000 900 1200", path has scale(1,-1)
                # The path is in font coordinates (Y-up). scale(1,-1) flips it.
                # viewBox origin is (0, -ascent). We need to map this into our output space.
                outer = f'translate({tx:.2f},{ty:.2f}) scale({s:.4f},{-s:.4f})'
            else:
                # Syllable SVGs: viewBox like "0 0 1000 1000", no flip
                outer = f'translate({tx:.2f},{ty:.2f}) scale({s:.4f},{s:.4f})'

            if inner_transform:
                svg_parts.append(
                    f'  <g transform="{outer}">'
                    f'<path d="{path["d"]}" transform="{inner_transform}" fill="#000000" />'
                    f'</g>'
                )
            else:
                svg_parts.append(
                    f'  <path d="{path["d"]}"'
                    f' transform="{outer}"'
                    f' fill="#000000" />'
                )

    svg_parts.append('</svg>')
    svg_content = '\n'.join(svg_parts) + '\n'

    output_dir = SCRIPT_DIR / 'output'
    output_dir.mkdir(exist_ok=True)
    output_name = f'sitelen kalama pona - {text}.svg'
    output_path = output_dir / output_name
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
