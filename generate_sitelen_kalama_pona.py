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
CARTOUCHE_SVG = SCRIPT_DIR / 'Jan_Sinpo_We_(Jimbo_Wales_in_Sitelen_Pona).svg'


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


def read_svg_paths_by_label(svg_file, labels):
    """Read path data by inkscape:label. Returns (paths_by_label, viewBox)."""
    if not svg_file.exists():
        return None, None

    tree = ET.parse(str(svg_file))
    root = tree.getroot()
    ns = {
        'svg': 'http://www.w3.org/2000/svg',
        'inkscape': 'http://www.inkscape.org/namespaces/inkscape',
    }

    viewBox = root.get('viewBox', '0 0 1000 1000')
    vb = [float(x) for x in viewBox.split()]

    paths_by_label = {label: [] for label in labels}
    for path_el in root.findall('.//svg:path', ns) + root.findall('.//path'):
        label = path_el.get(f'{{{ns["inkscape"]}}}label')
        if label not in paths_by_label:
            continue
        d = path_el.get('d')
        if not d:
            continue
        transform = path_el.get('transform', '')
        paths_by_label[label].append({'d': d, 'transform': transform})

    return paths_by_label, vb


def _path_bbox(d):
    """Approximate bbox for an SVG path (handles common commands safely)."""
    if not d:
        return None
    tokens = re.findall(r'[a-zA-Z]|[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?', d)
    if not tokens:
        return None

    idx = 0
    cmd = None
    x = y = 0.0
    start_x = start_y = 0.0
    last_cx = last_cy = None
    min_x = min_y = float('inf')
    max_x = max_y = float('-inf')

    def update(px, py):
        nonlocal min_x, min_y, max_x, max_y
        min_x = min(min_x, px)
        min_y = min(min_y, py)
        max_x = max(max_x, px)
        max_y = max(max_y, py)

    def read_numbers(n):
        nonlocal idx
        if idx + n > len(tokens):
            return None
        vals = tokens[idx:idx + n]
        if any(re.match(r'[a-zA-Z]', v) for v in vals):
            return None
        idx += n
        return [float(v) for v in vals]

    while idx < len(tokens):
        if re.match(r'[a-zA-Z]', tokens[idx]):
            cmd = tokens[idx]
            idx += 1
        if cmd is None:
            break

        c = cmd
        if c in ('Z', 'z'):
            x, y = start_x, start_y
            update(x, y)
            cmd = None
            continue

        if c in ('M', 'm', 'L', 'l', 'T', 't'):
            vals = read_numbers(2)
            if not vals:
                break
            dx, dy = vals
            if c.islower():
                x += dx
                y += dy
            else:
                x = dx
                y = dy
            if c in ('M', 'm'):
                start_x, start_y = x, y
                cmd = 'l' if c == 'm' else 'L'
            update(x, y)
        elif c in ('H', 'h'):
            vals = read_numbers(1)
            if not vals:
                break
            dx = vals[0]
            x = x + dx if c == 'h' else dx
            update(x, y)
        elif c in ('V', 'v'):
            vals = read_numbers(1)
            if not vals:
                break
            dy = vals[0]
            y = y + dy if c == 'v' else dy
            update(x, y)
        elif c in ('C', 'c'):
            vals = read_numbers(6)
            if not vals:
                break
            x1, y1, x2, y2, x3, y3 = vals
            if c.islower():
                x1 += x; y1 += y; x2 += x; y2 += y; x3 += x; y3 += y
            update(x1, y1)
            update(x2, y2)
            x, y = x3, y3
            update(x, y)
            last_cx, last_cy = x2, y2
        elif c in ('S', 's'):
            vals = read_numbers(4)
            if not vals:
                break
            x2, y2, x3, y3 = vals
            if last_cx is None:
                x1, y1 = x, y
            else:
                x1, y1 = 2 * x - last_cx, 2 * y - last_cy
            if c.islower():
                x2 += x; y2 += y; x3 += x; y3 += y
            update(x1, y1)
            update(x2, y2)
            x, y = x3, y3
            update(x, y)
            last_cx, last_cy = x2, y2
        elif c in ('Q', 'q'):
            vals = read_numbers(4)
            if not vals:
                break
            x1, y1, x2, y2 = vals
            if c.islower():
                x1 += x; y1 += y; x2 += x; y2 += y
            update(x1, y1)
            x, y = x2, y2
            update(x, y)
            last_cx, last_cy = x1, y1
        elif c in ('A', 'a'):
            vals = read_numbers(7)
            if not vals:
                break
            x2, y2 = vals[5], vals[6]
            if c.islower():
                x2 += x; y2 += y
            x, y = x2, y2
            update(x, y)
        else:
            cmd = None

    if min_x == float('inf'):
        return None
    return min_x, min_y, max_x, max_y


def _paths_bbox(paths):
    bbox = None
    for p in paths:
        b = _path_bbox(p.get('d', ''))
        if not b:
            continue
        if bbox is None:
            bbox = list(b)
        else:
            bbox[0] = min(bbox[0], b[0])
            bbox[1] = min(bbox[1], b[1])
            bbox[2] = max(bbox[2], b[2])
            bbox[3] = max(bbox[3], b[3])
    if bbox is None:
        return None
    return tuple(bbox)


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

    word_pieces = []
    syllable_pieces = []
    cartouche_pieces = []
    sources = []
    x_cursor = 0

    # Read word SVGs
    for word in matched_words:
        svg_file = WORD_SVGS_DIR / f'Sitelen seli kiwen - {word}.svg'
        paths, vb = read_svg_paths(svg_file)

        if paths and vb:
            vb_x, vb_y, vb_w, vb_h = vb
            scale = (TARGET_HEIGHT / vb_h if vb_h > 0 else 1) * 0.8
            word_pieces.append({
                'type': 'word',
                'paths': paths,
                'viewbox': vb,
                'scale': scale,
                'x_offset': x_cursor,
                'y_offset': 0,
            })
            x_cursor += vb_w * scale + SPACING
            sources.append(f'{word}: {word_commons_url(word)}')
            print(f'  Loaded word SVG: {word}')
        else:
            print(f'  Warning: could not load SVG for "{word}"')

    # Read syllable SVGs and compute cartouche layout
    syllable_items = []
    for syl in syllables:
        svg_name = syllable_to_svg_name(syl)
        svg_file = SYLLABLES_DIR / f'sitelen kalama pona - {svg_name}.svg'
        paths, vb = read_svg_paths(svg_file)

        if paths and vb:
            vb_x, vb_y, vb_w, vb_h = vb
            scale = (TARGET_HEIGHT / vb_h if vb_h > 0 else 1) * 1.2
            syllable_items.append({
                'syllable': syl,
                'paths': paths,
                'viewbox': vb,
                'scale': scale,
            })
            sources.append(f'{syl}: {syllable_commons_url(syl)}')
            print(f'  Loaded syllable: {syl}')
        else:
            print(f'  Warning: could not load syllable "{syl}"')

    if syllable_items:
        cartouche_labels = {'left', 'center', 'right'}
        cartouche_paths_by_label, cartouche_vb = read_svg_paths_by_label(
            CARTOUCHE_SVG,
            cartouche_labels,
        )
        if not cartouche_paths_by_label or not cartouche_vb:
            raise FileNotFoundError(
                f'Cartouche SVG not found or invalid: {CARTOUCHE_SVG}'
            )

        if any(not cartouche_paths_by_label[label] for label in cartouche_labels):
            raise ValueError('Cartouche SVG is missing left/center/right labels.')

        c_vb_x, c_vb_y, c_vb_w, c_vb_h = cartouche_vb
        cartouche_scale = TARGET_HEIGHT / c_vb_h if c_vb_h > 0 else 1
        center_bbox = _paths_bbox(cartouche_paths_by_label['center'])
        if not center_bbox:
            raise ValueError('Failed to compute cartouche center bounds.')
        cartouche_bar_height = (center_bbox[3] - center_bbox[1]) * cartouche_scale

        # Update syllable scaling to fit cartouche height
        syllable_widths = []
        for item in syllable_items:
            vb_x, vb_y, vb_w, vb_h = item['viewbox']
            item['scale'] = (TARGET_HEIGHT / vb_h if vb_h > 0 else 1) * 0.8
            syllable_widths.append(vb_w * item['scale'])

        syllable_start_x = x_cursor

        syllable_total_width = sum(syllable_widths)
        if len(syllable_widths) > 1:
            syllable_total_width += SPACING * (len(syllable_widths) - 1)

        left_bbox = _paths_bbox(cartouche_paths_by_label['left'])
        right_bbox = _paths_bbox(cartouche_paths_by_label['right'])
        if not left_bbox or not right_bbox:
            raise ValueError('Failed to compute cartouche side bounds.')

        left_w = (left_bbox[2] - left_bbox[0]) * cartouche_scale
        right_w = (right_bbox[2] - right_bbox[0]) * cartouche_scale
        center_w = (center_bbox[2] - center_bbox[0]) * cartouche_scale

        seg_w = center_w
        cartouche_inner_width = seg_w * len(syllable_widths)
        cartouche_total_width = left_w + cartouche_inner_width + right_w

        left_x = syllable_start_x
        middle_x = left_x + left_w
        right_x = middle_x + cartouche_inner_width

        # Left/right keep native proportions (scale_x == scale_y)
        cartouche_pieces.append({
            'paths': cartouche_paths_by_label['left'],
            'viewbox': cartouche_vb,
            'scale_x': cartouche_scale,
            'scale_y': cartouche_scale,
            'x_offset': left_x - left_bbox[0] * cartouche_scale,
            'y_offset': 0,
        })

        # Center repeats per syllable, no stretching
        for i in range(len(syllable_widths)):
            seg_x = middle_x + i * seg_w
            center_x = seg_x + (seg_w - center_w) / 2
            cartouche_pieces.append({
                'paths': cartouche_paths_by_label['center'],
                'viewbox': cartouche_vb,
                'scale_x': cartouche_scale,
                'scale_y': cartouche_scale,
                'x_offset': center_x - center_bbox[0] * cartouche_scale,
                'y_offset': 0,
            })

        cartouche_pieces.append({
            'paths': cartouche_paths_by_label['right'],
            'viewbox': cartouche_vb,
            'scale_x': cartouche_scale,
            'scale_y': cartouche_scale,
            'x_offset': right_x - right_bbox[0] * cartouche_scale,
            'y_offset': 0,
        })

        # Place syllables inside cartouche
        for i, (item, width) in enumerate(zip(syllable_items, syllable_widths)):
            seg_x = middle_x + i * seg_w
            x_cursor = seg_x + (seg_w - width) / 2
            vb_x, vb_y, vb_w, vb_h = item['viewbox']
            y_offset = (TARGET_HEIGHT - vb_h * item['scale']) / 2
            syllable_pieces.append({
                'type': 'syllable',
                'paths': item['paths'],
                'viewbox': item['viewbox'],
                'scale': item['scale'],
                'x_offset': x_cursor,
                'y_offset': y_offset,
            })

        # Move cursor to the end of cartouche block
        x_cursor = syllable_start_x + cartouche_total_width + SPACING

    # Build SVG
    has_content = bool(word_pieces or syllable_pieces or cartouche_pieces)
    total_width = x_cursor - SPACING if has_content else 0

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

    # Render word glyphs
    for piece in word_pieces:
        vb_x, vb_y, vb_w, vb_h = piece['viewbox']
        s = piece['scale']
        tx = piece['x_offset'] - vb_x * s
        ty = -vb_y * s + piece['y_offset']

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

    # Render cartouche pieces behind syllables
    for piece in cartouche_pieces:
        vb_x, vb_y, vb_w, vb_h = piece['viewbox']
        sx = piece['scale_x']
        sy = piece['scale_y']
        tx = piece['x_offset'] - vb_x * sx
        ty = piece['y_offset'] - vb_y * sy

        for path in piece['paths']:
            inner_transform = (path.get('transform') or '').strip()
            if inner_transform:
                svg_parts.append(
                    f'  <g transform="translate({tx:.2f},{ty:.2f}) scale({sx:.4f},{sy:.4f})">'
                    f'<path d="{path["d"]}" transform="{inner_transform}" fill="#000000" />'
                    f'</g>'
                )
            else:
                svg_parts.append(
                    f'  <path d="{path["d"]}"'
                    f' transform="translate({tx:.2f},{ty:.2f}) scale({sx:.4f},{sy:.4f})"'
                    f' fill="#000000" />'
                )

    # Render syllable glyphs
    for piece in syllable_pieces:
        vb_x, vb_y, vb_w, vb_h = piece['viewbox']
        s = piece['scale']
        tx = piece['x_offset'] - vb_x * s
        ty = -vb_y * s + piece['y_offset']

        for path in piece['paths']:
            transform = path.get('transform', '')
            has_flip = 'scale(1,-1)' in transform.replace(' ', '')
            inner_transform = strip_flip_transform(transform) if has_flip else transform
            inner_transform = inner_transform.strip()

            if has_flip:
                outer = f'translate({tx:.2f},{ty:.2f}) scale({s:.4f},{-s:.4f})'
            else:
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
