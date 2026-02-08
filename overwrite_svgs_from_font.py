import os
import re
import glob

SFDIR = os.path.join(os.path.dirname(__file__), '..sfdir')
OUTDIR = os.path.join(os.path.dirname(__file__), 'uniform_syllables')

ASCENT = 800  # from font.props

consonants = ['x', 'm', 'n', 'p', 't', 'k', 'w', 'j', 'l', 's']
vowels = ['a', 'an', 'e', 'en', 'i', 'in', 'o', 'on', 'u', 'un']

# Build mapping: glyph name -> svg filename syllable
# Null onset (x) gets "x" prefix in SVG filenames
# "j" becomes "y" in SVG filenames
syllable_to_svgname = {}
for c in consonants:
    for v in vowels:
        if c == 'x':
            glyph_name = v  # font glyph name has no consonant
            svg_syllable = 'x' + v  # SVG uses "x" prefix
        elif c == 'j':
            glyph_name = 'j' + v
            svg_syllable = 'y' + v  # SVG uses "y" instead of "j"
        else:
            glyph_name = c + v
            svg_syllable = c + v
        syllable_to_svgname[glyph_name] = svg_syllable


def parse_splineset(lines):
    """Parse FontForge SplineSet into SVG path data, flipping Y axis."""
    path_parts = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line or line == 'EndSplineSet':
            break

        tokens = line.split()

        if len(tokens) >= 3 and tokens[-2] == 'm':
            # Move to: x y m flag
            x = float(tokens[0])
            y = ASCENT - float(tokens[1])
            path_parts.append(f'M {x:.2f},{y:.2f}')

        elif len(tokens) >= 3 and tokens[-2] == 'l':
            # Line to: x y l flag
            x = float(tokens[0])
            y = ASCENT - float(tokens[1])
            path_parts.append(f'L {x:.2f},{y:.2f}')

        elif len(tokens) >= 7 and tokens[-2] == 'c':
            # Cubic bezier: cp1x cp1y cp2x cp2y x y c flag
            cp1x = float(tokens[0])
            cp1y = ASCENT - float(tokens[1])
            cp2x = float(tokens[2])
            cp2y = ASCENT - float(tokens[3])
            x = float(tokens[4])
            y = ASCENT - float(tokens[5])
            path_parts.append(f'C {cp1x:.2f},{cp1y:.2f} {cp2x:.2f},{cp2y:.2f} {x:.2f},{y:.2f}')

        i += 1

    # Close each subpath
    path_data = ' '.join(path_parts)
    # Add Z to close paths at each new M (except the first)
    # Split on M, add Z before each subsequent M
    segments = path_data.split('M ')
    result = ''
    for j, seg in enumerate(segments):
        if not seg.strip():
            continue
        if j > 1:  # close previous subpath
            result += ' Z '
        result += 'M ' + seg
    result += ' Z'
    return result


def glyph_to_svg(glyph_path, svg_syllable):
    """Convert a .glyph file to an SVG file."""
    with open(glyph_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract Width
    width_match = re.search(r'Width:\s+(\d+)', content)
    width = int(width_match.group(1)) if width_match else 1000

    # Extract SplineSet
    spline_match = re.search(r'SplineSet\n(.*?)EndSplineSet', content, re.DOTALL)
    if not spline_match:
        return None

    spline_lines = spline_match.group(1).strip().split('\n')
    path_data = parse_splineset(spline_lines)

    height = 1000  # ascent + descent
    svg_name = f'sitelen kalama pona - {svg_syllable}'

    svg = f'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg
   version="1.1"
   width="{width}"
   height="{height}"
   viewBox="0 0 {width} {height}"
   id="svg1"
   xmlns="http://www.w3.org/2000/svg">
  <path
     d="{path_data}"
     style="fill:#000000;fill-opacity:1;stroke:none"
     id="glyph" />
</svg>
'''
    return svg


# Process all glyphs
count = 0
for glyph_name, svg_syllable in sorted(syllable_to_svgname.items()):
    # Find glyph file
    glyph_filename = f'{glyph_name}.sitelen_kalama_pona.glyph'
    glyph_path = os.path.join(SFDIR, glyph_filename)

    if not os.path.exists(glyph_path):
        print(f'  MISSING glyph: {glyph_filename}')
        continue

    svg_filename = f'sitelen kalama pona - {svg_syllable}.svg'
    svg_path = os.path.join(OUTDIR, svg_filename)

    svg_content = glyph_to_svg(glyph_path, svg_syllable)
    if svg_content is None:
        print(f'  NO SPLINES: {glyph_name}')
        continue

    with open(svg_path, 'w', encoding='utf-8') as f:
        f.write(svg_content)

    count += 1
    print(f'  {glyph_name} -> {svg_filename}')

print(f'\nDone! Wrote {count} SVG files to {OUTDIR}')
