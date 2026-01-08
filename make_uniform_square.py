import xml.etree.ElementTree as ET
import io
import sys
import os
import glob

# Fix Unicode encoding on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Register namespaces
ET.register_namespace('', 'http://www.w3.org/2000/svg')
ET.register_namespace('sodipodi', 'http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd')
ET.register_namespace('inkscape', 'http://www.inkscape.org/namespaces/inkscape')

# First pass: find max dimensions
max_dimension = 0
syllable_data = []

svg_dir = "uniform_syllables"
for filepath in glob.glob(os.path.join(svg_dir, "*.svg")):
    tree = ET.parse(filepath)
    root = tree.getroot()

    width = float(root.get('width', 0))
    height = float(root.get('height', 0))
    viewBox = root.get('viewBox', '')

    max_dimension = max(max_dimension, width, height)

    syllable_data.append({
        'filepath': filepath,
        'tree': tree,
        'root': root,
        'width': width,
        'height': height,
        'viewBox': viewBox
    })

print(f"Maximum dimension found: {max_dimension:.1f}")
print(f"Making all syllables {max_dimension:.1f}×{max_dimension:.1f}px (square)\n")
print(f"{'Syllable':<30} {'Original':<15} → {'Square'}")
print("=" * 70)

# Second pass: make all square and centered
for data in syllable_data:
    root = data['root']
    orig_width = data['width']
    orig_height = data['height']
    viewBox_parts = data['viewBox'].split()

    if len(viewBox_parts) == 4:
        vb_x = float(viewBox_parts[0])
        vb_y = float(viewBox_parts[1])
        vb_width = float(viewBox_parts[2])
        vb_height = float(viewBox_parts[3])

        # Calculate center of current content
        content_center_x = vb_x + (vb_width / 2)
        content_center_y = vb_y + (vb_height / 2)

        # New viewBox: centered on content, but square canvas
        new_vb_x = content_center_x - (max_dimension / 2)
        new_vb_y = content_center_y - (max_dimension / 2)

        # Update SVG attributes
        root.set('width', str(max_dimension))
        root.set('height', str(max_dimension))
        root.set('viewBox', f"{new_vb_x} {new_vb_y} {max_dimension} {max_dimension}")

        # Write back
        data['tree'].write(data['filepath'], encoding='UTF-8', xml_declaration=True)

        filename = os.path.basename(data['filepath'])
        print(f"{filename:<30} {orig_width:.0f}×{orig_height:.0f}     → {max_dimension:.0f}×{max_dimension:.0f}")

print(f"\n✓ All {len(syllable_data)} syllables are now {max_dimension:.0f}×{max_dimension:.0f}px")
print("✓ Each symbol centered in its square canvas")
