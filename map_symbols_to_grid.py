import xml.etree.ElementTree as ET
import re
import io
import sys

# Fix Unicode encoding on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Parse the SVG
tree = ET.parse('Sitelen Pona Sound Symbols.svg')
root = tree.getroot()

# Define namespaces
ns = {
    'svg': 'http://www.w3.org/2000/svg',
    'sodipodi': 'http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd'
}

# Extract text positions and labels
texts = []
for text_elem in root.findall('.//svg:text', ns):
    x = float(text_elem.get('x', 0))
    y = float(text_elem.get('y', 0))
    tspan = text_elem.find('.//svg:tspan', ns)
    if tspan is not None and tspan.text:
        label = tspan.text.strip()
        texts.append({'label': label, 'x': x, 'y': y})

# Sort and categorize
vowels = []
consonants = []

for t in texts:
    label = t['label']
    if label in ['a', 'i', 'u', 'e', 'o']:
        vowels.append(t)
    else:
        consonants.append(t)

# Sort vowels by x position (left to right)
vowels.sort(key=lambda t: t['x'])

# Sort consonants by y position (top to bottom)
consonants.sort(key=lambda t: t['y'])

print("VOWELS (X-axis):")
for i, v in enumerate(vowels):
    print(f"  {v['label']}: x ≈ {v['x']:.0f}")

print("\nCONSONANTS (Y-axis):")
for i, c in enumerate(consonants):
    print(f"  {c['label']}: y ≈ {c['y']:.0f}")

# Now look at groups with IDs starting with 'g1'
# These seem to be the main graphical symbol groups
groups = root.findall('.//svg:g[@id]', ns)
symbol_groups = []

for g in groups:
    gid = g.get('id', '')
    if gid.startswith('g1') and '-' not in gid:  # Main groups, not subgroups
        transform = g.get('transform', '')
        match = re.search(r'translate\(([-\d.]+),\s*([-\d.]+)\)', transform)
        if match:
            tx = float(match.group(1))
            ty = float(match.group(2))
            symbol_groups.append({
                'id': gid,
                'tx': tx,
                'ty': ty
            })

# Looking at the pattern, I notice:
# X transforms seem to be: 0, 10, 28, 44 (possibly corresponding to columns/vowels)
# Y transforms vary more widely (corresponding to rows/consonants)

# Let's look at the actual geometric shapes to find their centers
print("\n\nFINDING SYMBOL CENTERS:")

# Find all ellipses and paths with substantial content
shapes = []
for elem in root.iter():
    if elem.tag.endswith('ellipse'):
        cx = float(elem.get('cx', 0))
        cy = float(elem.get('cy', 0))
        shapes.append({'type': 'ellipse', 'cx': cx, 'cy': cy, 'id': elem.get('id', '')})
    elif elem.tag.endswith('path'):
        # Parse path d attribute to estimate center
        d = elem.get('d', '')
        # Extract m commands (move to) which often indicate start positions
        matches = re.findall(r'm\s+([\d.]+),\s*([\d.]+)', d, re.IGNORECASE)
        if matches:
            avg_x = sum(float(m[0]) for m in matches) / len(matches)
            avg_y = sum(float(m[1]) for m in matches) / len(matches)
            pid = elem.get('id', '')
            if pid:  # Only include paths with IDs
                shapes.append({'type': 'path', 'cx': avg_x, 'cy': avg_y, 'id': pid})

# Define grid spacing based on text positions
# Vowel x-positions: 196.58, 349.31, 496.39, 633.57, 810.34
# Consonant y-positions: 166.88, 308.30, 463.86, 585.48, 719.83, 814.59, 922.07, 1030.96, 1138.44, 1265.72

# Column spacing (approximate):
# a: ~150-250
# i: ~300-400
# u: ~450-550
# e: ~600-700
# o: ~750-900

# Row spacing (approximate):
# M: ~50-220
# N: ~220-380
# P: ~380-520
# T: ~520-650
# K: ~650-770
# S: ~770-870
# w: ~870-980
# y: ~980-1090
# l: ~1090-1200
# x: ~1200+

def map_x_to_vowel(x):
    if x < 250:
        return 'a'
    elif x < 400:
        return 'i'
    elif x < 550:
        return 'u'
    elif x < 700:
        return 'e'
    else:
        return 'o'

def map_y_to_consonant(y):
    if y < 220:
        return 'M'
    elif y < 380:
        return 'N'
    elif y < 520:
        return 'P'
    elif y < 650:
        return 'T'
    elif y < 770:
        return 'K'
    elif y < 870:
        return 'S'
    elif y < 980:
        return 'w'
    elif y < 1090:
        return 'y'
    elif y < 1200:
        return 'l'
    else:
        return 'x'

# Map ellipses
print("\nELLIPSES:")
for shape in shapes:
    if shape['type'] == 'ellipse':
        v = map_x_to_vowel(shape['cx'])
        c = map_y_to_consonant(shape['cy'])
        print(f"  {shape['id']:20} at ({shape['cx']:6.1f}, {shape['cy']:6.1f}) → {c}{v}")

# Group shapes by approximate grid position
from collections import defaultdict
grid_map = defaultdict(list)

for shape in shapes:
    if shape['cx'] > 100:  # Filter out shapes far to the left (labels, etc.)
        v = map_x_to_vowel(shape['cx'])
        c = map_y_to_consonant(shape['cy'])
        syllable = f"{c}{v}"
        grid_map[syllable].append(shape)

print("\n\nSYMBOLS GROUPED BY GRID POSITION:")
for syllable in sorted(grid_map.keys()):
    count = len(grid_map[syllable])
    print(f"  {syllable}: {count} symbol(s)")

print("\n\nDone!")
