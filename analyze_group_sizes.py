import xml.etree.ElementTree as ET
import re
import io
import sys

# Fix Unicode encoding on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Parse the SVG
tree = ET.parse('Sitelen Pona Sound Symbols.svg')
root = tree.getroot()

ns = {'svg': 'http://www.w3.org/2000/svg'}

def get_path_bounds(d):
    """Extract bounding box from path d attribute"""
    xs, ys = [], []

    # Extract all coordinate pairs
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

    # Check all paths
    for path in group.findall('.//svg:path', ns):
        d = path.get('d', '')
        bounds = get_path_bounds(d)
        if bounds:
            px1, py1, px2, py2 = bounds
            min_x = min(min_x, px1)
            min_y = min(min_y, py1)
            max_x = max(max_x, px2)
            max_y = max(max_y, py2)

    # Check all ellipses
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

# Find all top-level groups
print(f"{'Syllable':<20} {'Width':>8} {'Height':>8} {'Content Bounds'}")
print("=" * 70)

widths, heights = [], []

for child in root:
    if child.tag.endswith('g') and child.get('transform'):
        gid = child.get('id', '')

        # Get content bounds
        bounds = get_group_bounds(child, ns)

        if bounds:
            min_x, min_y, max_x, max_y = bounds
            width = max_x - min_x
            height = max_y - min_y

            widths.append(width)
            heights.append(height)

            print(f"{gid:<20} {width:8.1f} {height:8.1f} ({min_x:.0f},{min_y:.0f}) to ({max_x:.0f},{max_y:.0f})")

if widths and heights:
    print(f"\n{'STATISTICS'}")
    print("=" * 70)
    print(f"Average width:  {sum(widths)/len(widths):.1f}")
    print(f"Average height: {sum(heights)/len(heights):.1f}")
    print(f"Min width:      {min(widths):.1f}")
    print(f"Max width:      {max(widths):.1f}")
    print(f"Min height:     {min(heights):.1f}")
    print(f"Max height:     {max(heights):.1f}")

    print(f"\nRecommended padding: ~10-20 pixels around each symbol")
