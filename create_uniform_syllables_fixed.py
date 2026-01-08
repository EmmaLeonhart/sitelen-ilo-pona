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

# First pass: find the maximum width
max_width = 0
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

            groups_data.append({
                'id': gid,
                'element': child,
                'bounds': bounds,
                'width': width,
                'height': height,
                'tx': tx,
                'ty': ty
            })

# Set uniform width (use max width + padding)
PADDING = 15
UNIFORM_WIDTH = max_width + (2 * PADDING)

# Create output directory
output_dir = "uniform_syllables"
os.makedirs(output_dir, exist_ok=True)

print(f"Creating uniform-width syllables in '{output_dir}/' directory:\n")
print(f"Uniform width: {UNIFORM_WIDTH:.0f}px\n")
print(f"{'Syllable':<20} {'Original':<12} {'Uniform':<12} {'Centered'}")
print("=" * 80)

# Second pass: create uniform-width, centered SVGs
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

    # Add vertical padding
    actual_min_y -= PADDING
    actual_max_y += PADDING
    height = actual_max_y - actual_min_y

    # Calculate centering offset
    content_center_x = (actual_min_x + actual_max_x) / 2
    uniform_center_x = UNIFORM_WIDTH / 2

    # Adjust viewBox to center the content horizontally
    viewbox_min_x = content_center_x - uniform_center_x
    viewbox_max_x = content_center_x + uniform_center_x

    # Create new SVG
    new_svg = ET.Element('svg', {
        'version': '1.1',
        'xmlns': 'http://www.w3.org/2000/svg',
        'xmlns:sodipodi': 'http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd',
        'xmlns:inkscape': 'http://www.inkscape.org/namespaces/inkscape',
        'width': f"{UNIFORM_WIDTH}px",
        'height': f"{height}px",
        'viewBox': f"{viewbox_min_x} {actual_min_y} {UNIFORM_WIDTH} {height}",
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

    print(f"{gid:<20} {orig_width:.0f}×{orig_height:.0f}   {UNIFORM_WIDTH:.0f}×{height:.0f}   ✓")

print(f"\n✓ Successfully created {len(groups_data)} uniform-width syllable SVGs")
print(f"✓ All files are {UNIFORM_WIDTH:.0f}px wide, centered horizontally")
