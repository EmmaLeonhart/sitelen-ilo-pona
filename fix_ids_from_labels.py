import xml.etree.ElementTree as ET
import io
import sys

# Fix Unicode encoding on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Register namespaces
ET.register_namespace('', 'http://www.w3.org/2000/svg')
ET.register_namespace('sodipodi', 'http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd')
ET.register_namespace('inkscape', 'http://www.inkscape.org/namespaces/inkscape')

# Parse the SVG
tree = ET.parse('Sitelen Pona Sound Symbols.svg')
root = tree.getroot()

print("Fixing IDs to match inkscape:label and normalizing capitalization:\n")
print(f"{'Old ID':<20} {'Label':<20} → {'New ID':<20}")
print("=" * 65)

changed = 0

for child in root:
    if child.tag.endswith('g'):
        old_id = child.get('id', '')
        label = child.get('{http://www.inkscape.org/namespaces/inkscape}label', '')

        if old_id:
            # If there's a label, use it (lowercase). Otherwise just lowercase the id
            if label:
                new_id = label.lower()
            else:
                new_id = old_id.lower()

            if new_id != old_id:
                child.set('id', new_id)
                print(f"{old_id:<20} {label:<20} → {new_id:<20}")
                changed += 1

# Save
tree.write('Sitelen Pona Sound Symbols.svg', encoding='UTF-8', xml_declaration=True)

print(f"\n✓ Changed {changed} IDs")
print("✓ SVG saved")
