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
    # Vowels are: a, i, u, e, o
    if label in ['a', 'i', 'u', 'e', 'o']:
        vowels.append(t)
    # Consonants are everything else
    else:
        consonants.append(t)

# Sort vowels by x position (left to right)
vowels.sort(key=lambda t: t['x'])

# Sort consonants by y position (top to bottom)
consonants.sort(key=lambda t: t['y'])

print("VOWELS (X-axis, left to right):")
for i, v in enumerate(vowels):
    print(f"  {i}: {v['label']} at x={v['x']:.2f}")

print("\nCONSONANTS (Y-axis, top to bottom):")
for i, c in enumerate(consonants):
    print(f"  {i}: {c['label']} at y={c['y']:.2f}")

# Now extract graphical groups with transforms
print("\n\nGRAPHICAL GROUPS:")

groups = root.findall('.//svg:g[@transform]', ns)
main_transforms = []

for g in groups:
    transform = g.get('transform', '')
    match = re.search(r'translate\(([-\d.]+),\s*([-\d.]+)\)', transform)
    if match:
        tx = float(match.group(1))
        ty = float(match.group(2))

        # Only consider top-level groups (direct children with IDs like g1782, g1783, etc.)
        if g.get('id') and g.get('id').startswith('g1'):
            main_transforms.append({
                'id': g.get('id'),
                'tx': tx,
                'ty': ty
            })

# Sort by position
main_transforms.sort(key=lambda g: (g['ty'], g['tx']))

print("\nMain groups sorted by position:")
for mt in main_transforms:
    print(f"  {mt['id']}: translate({mt['tx']}, {mt['ty']})")

# Attempt to map groups to grid positions
print("\n\nATTEMPTING TO MAP GROUPS TO GRID:")
print("(Adjusting for transforms)\n")

# Define approximate grid positions based on text positions
# Vowel columns (approximate centers between text positions)
vowel_centers = []
for i in range(len(vowels)):
    vowel_centers.append({
        'letter': vowels[i]['label'],
        'x': vowels[i]['x']
    })

# Consonant rows (approximate centers)
consonant_centers = []
for i in range(len(consonants)):
    consonant_centers.append({
        'letter': consonants[i]['label'],
        'y': consonants[i]['y']
    })

# Map each main group to closest vowel-consonant combination
for mt in main_transforms:
    # Adjust for the transform offset
    adjusted_y = mt['ty'] + 116  # Most have -116, -74, etc offsets
    adjusted_x = mt['tx']

    # Find closest vowel
    closest_vowel = None
    min_vowel_dist = float('inf')
    for vc in vowel_centers:
        dist = abs(vc['x'] - adjusted_x)
        if dist < min_vowel_dist:
            min_vowel_dist = dist
            closest_vowel = vc['letter']

    # Find closest consonant
    closest_consonant = None
    min_consonant_dist = float('inf')
    for cc in consonant_centers:
        dist = abs(cc['y'] - adjusted_y)
        if dist < min_consonant_dist:
            min_consonant_dist = dist
            closest_consonant = cc['letter']

    syllable = f"{closest_consonant}{closest_vowel}" if closest_consonant and closest_vowel else "?"
    print(f"  {mt['id']}: ({mt['tx']:6.1f}, {mt['ty']:6.1f}) → adjusted ({adjusted_x:6.1f}, {adjusted_y:6.1f}) → {syllable}")

print("\n\nDone!")
