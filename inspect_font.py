import sys
import io
from fontTools.ttLib import TTFont

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

font_path = sys.argv[1]
font = TTFont(font_path)

print(f"Inspecting: {font_path}")
print("=" * 70)

# Get cmap
cmap = font.getBestCmap()

print(f"\nTotal glyphs in cmap: {len(cmap)}")
print("\nFirst 50 codepoints:")
for i, (codepoint, glyph_name) in enumerate(sorted(cmap.items())[:50]):
    print(f"  U+{codepoint:04X} -> {glyph_name}")

print("\nCodepoints in F1900-F19FF range:")
found_in_range = False
for codepoint, glyph_name in sorted(cmap.items()):
    if 0xF1900 <= codepoint <= 0xF19FF:
        print(f"  U+{codepoint:04X} -> {glyph_name}")
        found_in_range = True

if not found_in_range:
    print("  (none found)")

print("\nAll codepoints starting with F:")
for codepoint, glyph_name in sorted(cmap.items()):
    if codepoint >= 0xF0000:
        print(f"  U+{codepoint:05X} -> {glyph_name}")
