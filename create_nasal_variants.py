import xml.etree.ElementTree as ET
import io
import sys
import os
import glob
import copy

# Fix Unicode encoding on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Register namespaces
ET.register_namespace('', 'http://www.w3.org/2000/svg')
ET.register_namespace('sodipodi', 'http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd')
ET.register_namespace('inkscape', 'http://www.inkscape.org/namespaces/inkscape')

# Parse the lun file to extract the nasal marker
lun_tree = ET.parse('uniform_syllables/sitelen kalama pona - lun.svg')
lun_root = lun_tree.getroot()

ns = {
    'svg': 'http://www.w3.org/2000/svg',
    'inkscape': 'http://www.inkscape.org/namespaces/inkscape'
}

# Find the nasal path (it's at root level, not nested in groups)
nasal_path = None
for elem in lun_root.iter():
    if elem.tag.endswith('path') and elem.get('{http://www.inkscape.org/namespaces/inkscape}label') == 'nasal':
        nasal_path = elem
        break

if nasal_path is None:
    print("Error: Could not find nasal path in lun.svg")
    sys.exit(1)

print("Found nasal marker path")
print(f"Creating -n variants for all syllables...\n")
print(f"{'Original':<30} → {'Nasal variant'}")
print("=" * 65)

created = 0

# Process all syllable files except lun (which already has it)
svg_dir = "uniform_syllables"
for filepath in sorted(glob.glob(os.path.join(svg_dir, "sitelen kalama pona - *.svg"))):
    filename = os.path.basename(filepath)

    # Skip lun since it already has the nasal marker
    if filename == "sitelen kalama pona - lun.svg":
        continue

    # Parse the syllable file
    tree = ET.parse(filepath)
    root = tree.getroot()

    # Extract syllable name from filename
    # "sitelen kalama pona - ma.svg" -> "ma"
    syllable = filename.replace("sitelen kalama pona - ", "").replace(".svg", "")

    # Create new filename with -n suffix
    new_syllable = syllable + "n"
    new_filename = f"sitelen kalama pona - {new_syllable}.svg"
    new_filepath = os.path.join(svg_dir, new_filename)

    # Deep copy the nasal path and add it to this SVG
    nasal_copy = copy.deepcopy(nasal_path)
    root.append(nasal_copy)

    # Update the docname attribute if present
    for elem in root.iter():
        if elem.tag.endswith('namedview'):
            elem.set('{http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd}docname', new_filename)

    # Write the new file
    tree.write(new_filepath, encoding='UTF-8', xml_declaration=True)

    print(f"{filename:<30} → {new_filename}")
    created += 1

print(f"\n✓ Created {created} nasal variants")
print(f"✓ Total syllables: {created + 50} (50 regular + {created} nasal)")
