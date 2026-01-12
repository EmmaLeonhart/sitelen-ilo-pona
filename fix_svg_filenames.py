"""
Fix SVG filenames in QuickStatements file
Change "word.svg" to "Sitelen-seli-kiwen-word.svg"
"""
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def main():
    input_file = 'create_ligature_items_with_concepts_quickstatements.txt'
    output_file = 'create_ligature_items_with_concepts_quickstatements.txt'

    print("Reading QuickStatements file...", flush=True)

    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    fixed_lines = []
    fixed_count = 0

    for line in lines:
        if line.startswith('LAST|P18|"') and line.endswith('.svg"\n'):
            # Extract the word from "word.svg"
            word = line[len('LAST|P18|"'):-len('.svg"\n')]
            # Replace spaces with hyphens for the filename
            filename = f"Sitelen-seli-kiwen-{word.replace(' ', '-')}.svg"
            fixed_line = f'LAST|P18|"{filename}"\n'
            fixed_lines.append(fixed_line)
            fixed_count += 1
        else:
            fixed_lines.append(line)

    print(f"Fixed {fixed_count} P18 lines", flush=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)

    print(f"✓ Updated file: {output_file}", flush=True)

    # Show examples
    print("\nFirst 5 fixed P18 lines:", flush=True)
    count = 0
    for line in fixed_lines:
        if line.startswith('LAST|P18|'):
            print(f"  {line.strip()}", flush=True)
            count += 1
            if count >= 5:
                break

if __name__ == "__main__":
    main()
