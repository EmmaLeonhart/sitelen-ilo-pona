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

# Create output directory
output_dir = "individual_syllables"
os.makedirs(output_dir, exist_ok=True)

# Padding around each symbol
PADDING = 15

print(f"Extracting individual syllables to '{output_dir}/' directory:\n")
print(f"{'Syllable':<20} {'File':<40} {'Size'}")
print("=" * 80)

extracted = 0

# Process each top-level group
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

        # Get content bounds
        bounds = get_group_bounds(child, ns)

        if not bounds:
            print(f"{gid:<20} Skipped - no content found")
            continue

        min_x, min_y, max_x, max_y = bounds

        # Apply the transform to get actual visual bounds
        actual_min_x = min_x + tx
        actual_min_y = min_y + ty
        actual_max_x = max_x + tx
        actual_max_y = max_y + ty

        # Add padding
        actual_min_x -= PADDING
        actual_min_y -= PADDING
        actual_max_x += PADDING
        actual_max_y += PADDING

        width = actual_max_x - actual_min_x
        height = actual_max_y - actual_min_y

        # Create new SVG for this syllable
        new_svg = ET.Element('svg', {
            'version': '1.1',
            'xmlns': 'http://www.w3.org/2000/svg',
            'xmlns:sodipodi': 'http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd',
            'xmlns:inkscape': 'http://www.inkscape.org/namespaces/inkscape',
            'width': f"{width}px",
            'height': f"{height}px",
            'viewBox': f"{actual_min_x} {actual_min_y} {width} {height}",
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

        extracted += 1

        print(f"{gid:<20} {filename:<40} {width:.0f}×{height:.0f}")

print(f"\n✓ Successfully extracted {extracted} syllable SVGs to '{output_dir}/' directory")
