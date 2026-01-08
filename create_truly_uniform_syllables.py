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
    """Calculate bounding box of all content in a group (recursive)"""
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

# First pass: find the maximum dimensions
max_width = 0
max_height = 0
groups_data = []

for child in list(root):
    if child.tag.endswith('g') and child.get('transform') and child.get('id'):
        gid = child.get('id', '')

        # Get the transform
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
                'width': width,
                'height': height,
                'tx': tx,
                'ty': ty
            })

# Set uniform dimensions (use max width and height + padding)
PADDING = 15
UNIFORM_WIDTH = max_width + (2 * PADDING)
UNIFORM_HEIGHT = max_height + (2 * PADDING)

# Create output directory
output_dir = "uniform_syllables"
os.makedirs(output_dir, exist_ok=True)

print(f"Creating truly uniform syllables in '{output_dir}/' directory:\n")
print(f"Uniform size: {UNIFORM_WIDTH:.0f}×{UNIFORM_HEIGHT:.0f}px\n")
print(f"{'Syllable':<20} {'Original':<15} {'Uniform':<15}")
print("=" * 60)

# Second pass: create uniform-size, centered SVGs
for data in groups_data:
    gid = data['id']
    child = data['element']
    min_x, min_y, max_x, max_y = data['bounds']
    orig_width = data['width']
    orig_height = data['height']
    tx = data['tx']
    ty = data['ty']

    # Apply transform to get actual visual bounds
    actual_min_x = min_x + tx
    actual_min_y = min_y + ty
    actual_max_x = max_x + tx
    actual_max_y = max_y + ty

    # Calculate center of content
    content_center_x = (actual_min_x + actual_max_x) / 2
    content_center_y = (actual_min_y + actual_max_y) / 2

    # Calculate viewBox to center content in uniform canvas
    viewbox_min_x = content_center_x - (UNIFORM_WIDTH / 2)
    viewbox_min_y = content_center_y - (UNIFORM_HEIGHT / 2)

    # Create new SVG
    new_svg = ET.Element('svg', {
        'version': '1.1',
        'xmlns': 'http://www.w3.org/2000/svg',
        'xmlns:sodipodi': 'http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd',
        'xmlns:inkscape': 'http://www.inkscape.org/namespaces/inkscape',
        'width': f"{UNIFORM_WIDTH}px",
        'height': f"{UNIFORM_HEIGHT}px",
        'viewBox': f"{viewbox_min_x} {viewbox_min_y} {UNIFORM_WIDTH} {UNIFORM_HEIGHT}",
        'style': 'shape-rendering:geometricPrecision; text-rendering:geometricPrecision; image-rendering:optimizeQuality; fill-rule:evenodd; clip-rule:evenodd'
    })

    # Deep copy the group
    group_copy = copy.deepcopy(child)
    new_svg.append(group_copy)

    # Write to file
    filename = f"sitelen kalama pona - {gid}.svg"
    filepath = os.path.join(output_dir, filename)

    new_tree = ET.ElementTree(new_svg)
    new_tree.write(filepath, encoding='UTF-8', xml_declaration=True)

    print(f"{gid:<20} {orig_width:.0f}×{orig_height:.0f}      {UNIFORM_WIDTH:.0f}×{UNIFORM_HEIGHT:.0f}")

print(f"\n✓ Successfully created {len(groups_data)} uniform syllable SVGs")
print(f"✓ All files are {UNIFORM_WIDTH:.0f}×{UNIFORM_HEIGHT:.0f}px, centered both horizontally and vertically")
