import xml.etree.ElementTree as ET
import re
import io
import sys
import os
import copy

# Fix Unicode encoding on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Register namespaces
ET.register_namespace('', 'http://www.w3.org/2000/svg')
ET.register_namespace('sodipodi', 'http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd')
ET.register_namespace('inkscape', 'http://www.inkscape.org/namespaces/inkscape')

# Parse the original SVG
tree = ET.parse('Sitelen Pona Sound Symbols.svg')
root = tree.getroot()

ns = {'svg': 'http://www.w3.org/2000/svg'}

def get_path_bounds(d):
    xs, ys = [], []
    coords = re.findall(r'[-\d.]+\s+[-\d.]+', d)
    for coord in coords:
        parts = coord.split()
        if len(parts) >= 2:
            try:
                xs.append(float(parts[0]))
                ys.append(float(parts[1]))
            except:
                pass
    if xs and ys:
        return min(xs), min(ys), max(xs), max(ys)
    return None

def get_group_bounds(group, ns):
    min_x, min_y = float('inf'), float('inf')
    max_x, max_y = float('-inf'), float('-inf')

    for path in group.findall('.//svg:path', ns):
        d = path.get('d', '')
        bounds = get_path_bounds(d)
        if bounds:
            px1, py1, px2, py2 = bounds
            min_x = min(min_x, px1)
            min_y = min(min_y, py1)
            max_x = max(max_x, px2)
            max_y = max(max_y, py2)

    for ellipse in group.findall('.//svg:ellipse', ns):
        cx = float(ellipse.get('cx', 0))
        cy = float(ellipse.get('cy', 0))
        rx = float(ellipse.get('rx', 0))
        ry = float(ellipse.get('ry', 0))
        min_x = min(min_x, cx - rx)
        min_y = min(min_y, cy - ry)
        max_x = max(max_x, cx + rx)
        max_y = max(max_y, cy + ry)

    if min_x != float('inf'):
        return min_x, min_y, max_x, max_y
    return None

# First pass: find max dimensions
max_width = 0
max_height = 0
groups_data = []

for child in list(root):
    if child.tag.endswith('g') and child.get('transform') and child.get('id'):
        gid = child.get('id', '')
        transform = child.get('transform', '')
        match = re.search(r'translate\(([-\d.]+)[,\s]+([-\d.]+)\)', transform)
        if not match:
            continue

        tx = float(match.group(1))
        ty = float(match.group(2))
        bounds = get_group_bounds(child, ns)

        if bounds:
            min_x, min_y, max_x, max_y = bounds
            width = max_x - min_x
            height = max_y - min_y
            max_width = max(max_width, width)
            max_height = max(max_height, height)

            groups_data.append({
                'id': gid,
                'element': child,
                'bounds': bounds,
                'tx': tx,
                'ty': ty
            })

# Fixed canvas size
PADDING = 15
CANVAS_WIDTH = max_width + (2 * PADDING)
CANVAS_HEIGHT = max_height + (2 * PADDING)

output_dir = "uniform_syllables"
os.makedirs(output_dir, exist_ok=True)

print(f"Creating fixed-size canvas syllables:\n")
print(f"Canvas size: {CANVAS_WIDTH:.0f}×{CANVAS_HEIGHT:.0f}px\n")
print(f"{'Syllable':<20} ViewBox")
print("=" * 70)

for data in groups_data:
    gid = data['id']
    child = data['element']
    min_x, min_y, max_x, max_y = data['bounds']
    tx = data['tx']
    ty = data['ty']

    # Actual visual position after transform
    actual_center_x = ((min_x + max_x) / 2) + tx
    actual_center_y = ((min_y + max_y) / 2) + ty

    # ViewBox: center the content in the fixed canvas
    # ViewBox always starts at (center - canvas/2), so symbol is in middle
    viewbox_x = actual_center_x - (CANVAS_WIDTH / 2)
    viewbox_y = actual_center_y - (CANVAS_HEIGHT / 2)

    # Create SVG
    new_svg = ET.Element('svg')
    new_svg.set('version', '1.1')
    new_svg.set('xmlns', 'http://www.w3.org/2000/svg')
    new_svg.set('width', f"{CANVAS_WIDTH}px")
    new_svg.set('height', f"{CANVAS_HEIGHT}px")
    new_svg.set('viewBox', f"{viewbox_x} {viewbox_y} {CANVAS_WIDTH} {CANVAS_HEIGHT}")

    # Deep copy group
    group_copy = copy.deepcopy(child)
    new_svg.append(group_copy)

    # Write
    filename = f"sitelen kalama pona - {gid}.svg"
    filepath = os.path.join(output_dir, filename)

    new_tree = ET.ElementTree(new_svg)
    new_tree.write(filepath, encoding='UTF-8', xml_declaration=True)

    print(f"{gid:<20} ({viewbox_x:.1f}, {viewbox_y:.1f}, {CANVAS_WIDTH:.0f}, {CANVAS_HEIGHT:.0f})")

print(f"\n✓ Created {len(groups_data)} syllables")
print(f"✓ All {CANVAS_WIDTH:.0f}×{CANVAS_HEIGHT:.0f}px")
print(f"✓ Each symbol centered in canvas")
