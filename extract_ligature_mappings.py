import sys
import io
from fontTools.ttLib import TTFont

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

font_path = sys.argv[1]
font = TTFont(font_path)

print(f"Font: {font_path}")
print("=" * 70)

# Check if GSUB table exists
if 'GSUB' not in font:
    print("No GSUB table found (no ligatures)")
    sys.exit(0)

gsub = font['GSUB']

print(f"\nGSUB Version: {gsub.table.Version}")
print(f"Feature count: {len(gsub.table.FeatureList.FeatureRecord)}")

# List all features
print("\nFeatures:")
for feature_record in gsub.table.FeatureList.FeatureRecord:
    print(f"  - {feature_record.FeatureTag}")

# Get cmap for reverse lookup
cmap = font.getBestCmap()
reverse_cmap = {v: k for k, v in cmap.items()}

# Look for ligature substitution lookups
print("\nLigature substitutions:")
print("=" * 70)

for feature_record in gsub.table.FeatureList.FeatureRecord:
    feature = feature_record.Feature
    print(f"\nFeature: {feature_record.FeatureTag}")

    for lookup_index in feature.LookupListIndex:
        lookup = gsub.table.LookupList.Lookup[lookup_index]
        print(f"  Lookup Type: {lookup.LookupType}")

        # Type 4 is ligature substitution
        if lookup.LookupType == 4:
            for subtable in lookup.SubTable:
                if hasattr(subtable, 'ligatures'):
                    for first_glyph, ligature_set in subtable.ligatures.items():
                        for ligature in ligature_set:
                            components = [first_glyph] + ligature.Component
                            result = ligature.LigGlyph

                            # Try to get Latin text for components
                            latin_chars = []
                            for glyph in components:
                                if glyph in reverse_cmap:
                                    char = chr(reverse_cmap[glyph])
                                    latin_chars.append(char)
                                else:
                                    latin_chars.append(f"[{glyph}]")

                            latin_text = ''.join(latin_chars)
                            print(f"    {latin_text:30} -> {result}")
