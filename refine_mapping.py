import io
import sys

# Fix Unicode encoding on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Actual vowel positions from the SVG text
vowel_positions = {
    'a': 197,
    'i': 349,
    'u': 496,
    'e': 634,
    'o': 810
}

# Actual consonant positions
consonant_positions = {
    'M': 167,
    'N': 308,
    'P': 464,
    'T': 585,
    'K': 720,
    'S': 815,
    'w': 922,
    'y': 1031,
    'l': 1138,
    'x': 1266
}

# Calculate better boundaries (midpoints between positions)
vowel_boundaries = {
    'a': (0, (197 + 349) / 2),       # 0 - 273
    'i': ((197 + 349) / 2, (349 + 496) / 2),   # 273 - 422.5
    'u': ((349 + 496) / 2, (496 + 634) / 2),   # 422.5 - 565
    'e': ((496 + 634) / 2, (634 + 810) / 2),   # 565 - 722
    'o': ((634 + 810) / 2, 9999)     # 722 - infinity
}

consonant_boundaries = {
    'M': (0, (167 + 308) / 2),       # 0 - 237.5
    'N': ((167 + 308) / 2, (308 + 464) / 2),   # 237.5 - 386
    'P': ((308 + 464) / 2, (464 + 585) / 2),   # 386 - 524.5
    'T': ((464 + 585) / 2, (585 + 720) / 2),   # 524.5 - 652.5
    'K': ((585 + 720) / 2, (720 + 815) / 2),   # 652.5 - 767.5
    'S': ((720 + 815) / 2, (815 + 922) / 2),   # 767.5 - 868.5
    'w': ((815 + 922) / 2, (922 + 1031) / 2),  # 868.5 - 976.5
    'y': ((922 + 1031) / 2, (1031 + 1138) / 2), # 976.5 - 1084.5
    'l': ((1031 + 1138) / 2, (1138 + 1266) / 2), # 1084.5 - 1202
    'x': ((1138 + 1266) / 2, 9999)   # 1202 - infinity
}

def map_x_to_vowel_refined(x):
    for vowel, (min_x, max_x) in vowel_boundaries.items():
        if min_x <= x < max_x:
            return vowel
    return '?'

def map_y_to_consonant_refined(y):
    for consonant, (min_y, max_y) in consonant_boundaries.items():
        if min_y <= y < max_y:
            return consonant
    return '?'

# Test on the duplicates
print("REFINED MAPPING FOR DUPLICATE GROUPS:")
print("=" * 70)

duplicates = [
    ("Pe_1", 682, 412),
    ("Pe_2", 552, 412),
    ("Pe_3", 623, 445),
    ("Pe_4", 689, 412),
    ("Po_1", 805, 413),
    ("Po_2", 722, 419),
    ("Po_3", 906, 438),
    ("Po_4", 754, 447),
    ("Ko_1", 788, 697),
    ("Ko_2", 782, 692),
    ("Ko_3", 794, 755),
    ("To_1", 796, 555),
    ("To_2", 792, 598),
    ("yo_1", 763, 1086),
    ("yo_2", 774, 1040),
]

from collections import defaultdict
refined_map = defaultdict(list)

for old_name, x, y in duplicates:
    vowel = map_x_to_vowel_refined(x)
    consonant = map_y_to_consonant_refined(y)
    new_syllable = f"{consonant}{vowel}"

    refined_map[new_syllable].append((old_name, x, y))

    print(f"{old_name:10} at ({x:4}, {y:4}) → vowel boundary check:")
    print(f"           X={x:6.1f} → {vowel} (boundaries: ", end="")
    for v, (min_x, max_x) in vowel_boundaries.items():
        if v == vowel:
            print(f"{min_x:.1f}-{max_x:.1f})", end="")
            break
    print(f" ... NEW: {new_syllable}")

print("\n\nREFINED GROUPING:")
for syllable in sorted(refined_map.keys()):
    groups = refined_map[syllable]
    print(f"\n{syllable}: {len(groups)} group(s)")
    for old_name, x, y in groups:
        print(f"  {old_name:10} at ({x:4}, {y:4})")

# Count how many are still duplicates
still_duplicates = [s for s, g in refined_map.items() if len(g) > 1]
print(f"\n\nSTILL DUPLICATES AFTER REFINEMENT: {len(still_duplicates)}")
print(f"RESOLVED (now unique): {len(duplicates) - sum(len(g) for s, g in refined_map.items() if len(g) > 1)}")
