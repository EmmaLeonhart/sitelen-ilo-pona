"""
Generate a gallery HTML page for the Sitelen fonts.

Produces gallery.html with a grid of syllable SVGs and a sample of word SVGs.
"""

from pathlib import Path
import re

ROOT_DIR = Path(__file__).parent.parent
SYLLABLES_DIR = ROOT_DIR / 'uniform_syllables'
WORDS_DIR = ROOT_DIR / 'sitelen_seli_kiwen_svgs'
OUTPUT_FILE = ROOT_DIR / 'gallery.html'

def main():
    html_parts = [
        '<!DOCTYPE html>',
        '<html lang="en">',
        '<head>',
        '    <meta charset="UTF-8">',
        '    <meta name="viewport" content="width=device-width, initial-scale=1.0">',
        '    <title>Sitelen - Font Gallery</title>',
        '    <style>',
        '        body { font-family: system-ui, -apple-system, sans-serif; line-height: 1.5; max-width: 1200px; margin: 0 auto; padding: 2rem; background: #f8f9fa; }',
        '        h1, h2 { color: #1a1a1b; }',
        '        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(100px, 1fr)); gap: 1rem; margin-bottom: 3rem; }',
        '        .card { background: white; padding: 1rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); text-align: center; }',
        '        .card img { width: 100%; height: auto; max-height: 80px; margin-bottom: 0.5rem; }',
        '        .card span { font-size: 0.8rem; color: #666; font-weight: bold; }',
        '        nav { margin-bottom: 2rem; }',
        '        nav a { margin-right: 1rem; color: #0066cc; text-decoration: none; font-weight: bold; }',
        '        nav a:hover { text-decoration: underline; }',
        '    </style>',
        '</head>',
        '<body>',
        '    <nav><a href="index.html">← Back to Downloads</a></nav>',
        '    <h1>Sitelen Font Gallery</h1>',
        '    ',
        '    <section>',
        '        <h2>Sitelen Kalama Pona (Syllables)</h2>',
        '        <div class="grid">'
    ]

    # Get syllable SVGs
    syllables = sorted(SYLLABLES_DIR.glob('sitelen kalama pona - *.svg'))
    for s_file in syllables:
        name = s_file.name.replace('sitelen kalama pona - ', '').replace('.svg', '')
        # Use relative path for the image src
        rel_path = f'uniform_syllables/{s_file.name}'
        html_parts.append(f'            <div class="card"><img src="{rel_path}" alt="{name}"><span>{name}</span></div>')
    
    html_parts.append('        </div>')
    html_parts.append('    </section>')

    html_parts.append('    <section>')
    html_parts.append('        <h2>Sitelen Seli Kiwen (Word Logographs - Sample)</h2>')
    html_parts.append('        <div class="grid">')

    # Get sample of word SVGs (they are many, so just show a sample or first 100)
    words = sorted(WORDS_DIR.glob('Sitelen seli kiwen - *.svg'))
    for w_file in words[:150]:  # Show first 150
        name = w_file.name.replace('Sitelen seli kiwen - ', '').replace('.svg', '')
        rel_path = f'sitelen_seli_kiwen_svgs/{w_file.name}'
        html_parts.append(f'            <div class="card"><img src="{rel_path}" alt="{name}"><span>{name}</span></div>')

    html_parts.append('        </div>')
    if len(words) > 150:
        html_parts.append(f'        <p>...and {len(words) - 150} more word glyphs.</p>')
    html_parts.append('    </section>')

    html_parts.append('</body>')
    html_parts.append('</html>')

    OUTPUT_FILE.write_text('\n'.join(html_parts), encoding='utf-8')
    print(f'Wrote gallery to {OUTPUT_FILE}')

if __name__ == '__main__':
    main()
