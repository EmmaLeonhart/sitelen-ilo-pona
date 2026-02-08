import os
import glob

SFDIR = os.path.join(os.path.dirname(__file__), '..sfdir')

consonants = ['x', 'm', 'n', 'p', 't', 'k', 'w', 'j', 'l', 's']
vowels = ['a', 'an', 'e', 'en', 'i', 'in', 'o', 'on', 'u', 'un']

# Build syllable names: x = null onset (just the vowel), others = consonant + vowel
syllables = []
for c in consonants:
    for v in vowels:
        if c == 'x':
            syllables.append(v)
        else:
            syllables.append(c + v)

# Should be 100 syllables
assert len(syllables) == 100, f"Expected 100 syllables, got {len(syllables)}"

# Verify first and last match what user already renamed
assert syllables[0] == 'a', f"First should be 'a', got '{syllables[0]}'"
assert syllables[99] == 'sun', f"Last should be 'sun', got '{syllables[99]}'"

print(f"Generated {len(syllables)} syllable names")
print(f"First: {syllables[0]}, Last: {syllables[99]}")

# Find all _Name_Me glyph files
name_me_files = glob.glob(os.path.join(SFDIR, '_Name_Me.*.glyph'))
print(f"Found {len(name_me_files)} _Name_Me glyph files to rename")

renamed = 0
for filepath in sorted(name_me_files):
    filename = os.path.basename(filepath)
    # Extract encoding number from filename like _Name_Me.65703.glyph
    encoding = int(filename.split('.')[1])
    index = encoding - 65702

    if index < 0 or index >= 100:
        print(f"  SKIP: {filename} - index {index} out of range")
        continue

    syllable = syllables[index]
    new_name = f"{syllable}.sitelen_kalama_pona"

    # Read the file and update StartChar line
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    old_startchar = f"StartChar: NameMe.{encoding}"
    new_startchar = f"StartChar: {new_name}"
    content = content.replace(old_startchar, new_startchar)

    # Write updated content to new filename
    new_filepath = os.path.join(SFDIR, f"{new_name}.glyph")
    with open(new_filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    # Remove old file
    os.remove(filepath)
    renamed += 1
    print(f"  {filename} -> {new_name}.glyph  ({syllable})")

print(f"\nDone! Renamed {renamed} glyphs.")
