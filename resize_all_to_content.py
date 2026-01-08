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

output_dir = "uniform_syllables"
os.makedirs(output_dir, exist_ok=True)

print(f"Resizing all syllables to content bounds:\n")
print(f"{'Syllable':<20} {'Size':<15}")
print("=" * 40)

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

        if not bounds:
            continue

        min_x, min_y, max_x, max_y = bounds

        # Actual position after transform
        actual_min_x = min_x + tx
        actual_min_y = min_y + ty
        actual_max_x = max_x + tx
        actual_max_y = max_y + ty

        # Content dimensions
        width = actual_max_x - actual_min_x
        height = actual_max_y - actual_min_y

        # Create SVG with viewBox exactly at content bounds
        new_svg = ET.Element('svg')
        new_svg.set('version', '1.1')
        new_svg.set('xmlns', 'http://www.w3.org/2000/svg')
        new_svg.set('width', str(width))
        new_svg.set('height', str(height))
        new_svg.set('viewBox', f"{actual_min_x} {actual_min_y} {width} {height}")

        # Deep copy group
        group_copy = copy.deepcopy(child)
        new_svg.append(group_copy)

        # Write
        filename = f"sitelen kalama pona - {gid}.svg"
        filepath = os.path.join(output_dir, filename)

        new_tree = ET.ElementTree(new_svg)
        new_tree.write(filepath, encoding='UTF-8', xml_declaration=True)

        print(f"{gid:<20} {width:.1f}×{height:.1f}")

print(f"\n✓ All syllables resized to content bounds")
