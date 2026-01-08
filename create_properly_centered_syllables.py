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
    """Extract bounding box from path d attribute"""
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
    """Calculate bounding box of all content in a group"""
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

# First pass: find max width
max_width = 0
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

            groups_data.append({
                'id': gid,
                'element': child,
                'bounds': bounds,
                'tx': tx,
                'ty': ty
            })

# Uniform width with padding
PADDING = 15
UNIFORM_WIDTH = max_width + (2 * PADDING)

output_dir = "uniform_syllables"
os.makedirs(output_dir, exist_ok=True)

print(f"Creating properly centered syllables:\n")
print(f"Uniform width: {UNIFORM_WIDTH:.0f}px\n")
print(f"{'Syllable':<20} {'Size':<15} {'ViewBox Y':<15}")
print("=" * 55)

for data in groups_data:
    gid = data['id']
    child = data['element']
    min_x, min_y, max_x, max_y = data['bounds']
    tx = data['tx']
    ty = data['ty']

    # Actual visual position after transform
    actual_min_x = min_x + tx
    actual_max_x = max_x + tx
    actual_min_y = min_y + ty
    actual_max_y = max_y + ty

    # Content center X
    content_center_x = (actual_min_x + actual_max_x) / 2

    # ViewBox positioning:
    # Y: starts at PADDING pixels above the content top
    viewbox_min_y = actual_min_y - PADDING
    # X: centered so content is in the middle of uniform width
    viewbox_min_x = content_center_x - (UNIFORM_WIDTH / 2)

    # Height: content height + padding on both sides
    height = (actual_max_y - actual_min_y) + (2 * PADDING)

    # Create SVG
    new_svg = ET.Element('svg')
    new_svg.set('version', '1.1')
    new_svg.set('xmlns', 'http://www.w3.org/2000/svg')
    new_svg.set('width', f"{UNIFORM_WIDTH}px")
    new_svg.set('height', f"{height}px")
    new_svg.set('viewBox', f"{viewbox_min_x} {viewbox_min_y} {UNIFORM_WIDTH} {height}")

    # Deep copy group
    group_copy = copy.deepcopy(child)
    new_svg.append(group_copy)

    # Write
    filename = f"sitelen kalama pona - {gid}.svg"
    filepath = os.path.join(output_dir, filename)

    new_tree = ET.ElementTree(new_svg)
    new_tree.write(filepath, encoding='UTF-8', xml_declaration=True)

    print(f"{gid:<20} {UNIFORM_WIDTH:.0f}×{height:.0f}  Y={viewbox_min_y:.1f}")

print(f"\n✓ Created {len(groups_data)} syllables")
print(f"✓ All {UNIFORM_WIDTH:.0f}px wide")
print(f"✓ Each centered horizontally with {PADDING}px padding from content edges")
