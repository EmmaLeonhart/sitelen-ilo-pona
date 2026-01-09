import sys
import io
from fontTools.ttLib import TTFont
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

font_path = sys.argv[1]
font = TTFont(font_path)

glyph_set = font.getGlyphSet()
all_glyph_names = sorted(list(glyph_set.keys()))

print(f"Font: {Path(font_path).name}")
print(f"Total glyphs: {len(all_glyph_names)}")
print("\nAll glyph names:")
print("=" * 70)

for name in all_glyph_names:
    print(name)
