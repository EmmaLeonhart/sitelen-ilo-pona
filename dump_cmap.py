import sys
import io
from fontTools.ttLib import TTFont

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

font_path = sys.argv[1]
font = TTFont(font_path)

cmap = font.getBestCmap()

print(f"Font: {font_path}")
print(f"Total cmap entries: {len(cmap)}\n")

# Show all mappings
for codepoint, glyph_name in sorted(cmap.items()):
    print(f"U+{codepoint:04X} -> {glyph_name}")
