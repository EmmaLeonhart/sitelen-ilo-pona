"""
Generate a gallery HTML page for the Wikidata-generated sitelen kalama pona SVGs.

Produces gallery.html with a searchable grid of all output/ SVGs.
"""

from pathlib import Path
from urllib.parse import quote

ROOT_DIR = Path(__file__).parent.parent
OUTPUT_DIR = ROOT_DIR / 'output'
OUTPUT_FILE = ROOT_DIR / 'gallery.html'

PREFIX = 'sitelen kalama pona - '

def display_label(raw_label):
    """Strip the leading ', ' from bare proper nouns for display."""
    if raw_label.startswith(', '):
        return raw_label[2:]
    return raw_label

def main():
    svgs = sorted(
        f for f in OUTPUT_DIR.glob('sitelen kalama pona - *.svg')
        if not f.name.endswith('.wiki.txt')
    )

    cards = []
    for svg_file in svgs:
        raw_label = svg_file.stem.replace(PREFIX, '')
        label = display_label(raw_label)
        rel_path = 'output/' + quote(svg_file.name, safe=' ,()-')
        cards.append((label, rel_path))

    card_html = '\n'.join(
        f'    <div class="card"><img loading="lazy" src="{p}" alt="{l}"><span>{l}</span></div>'
        for l, p in cards
    )

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Sitelen Kalama Pona — Wikidata SVG Gallery</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 0; background: #f8f9fa; color: #1a1a1b; }}
    header {{ padding: 1.5rem 2rem; border-bottom: 1px solid #ddd; display: flex; align-items: center; gap: 2rem; flex-wrap: wrap; }}
    header h1 {{ margin: 0; font-size: 1.4rem; }}
    nav a {{ color: #0066cc; text-decoration: none; font-weight: bold; margin-right: 1rem; }}
    nav a:hover {{ text-decoration: underline; }}
    #search {{ padding: 0.4rem 0.8rem; border: 1px solid #ccc; border-radius: 6px; font-size: 1rem; width: 240px; }}
    #count {{ color: #666; font-size: 0.9rem; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); gap: 0.75rem; padding: 1.5rem 2rem; }}
    .card {{ background: white; padding: 0.75rem; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); text-align: center; }}
    .card img {{ width: 100%; height: 80px; object-fit: contain; margin-bottom: 0.4rem; }}
    .card span {{ font-size: 0.72rem; color: #555; display: block; word-break: break-word; }}
    .hidden {{ display: none !important; }}
  </style>
</head>
<body>
  <header>
    <div>
      <nav><a href="index.html">← Home</a> <a href="docs/">Font Docs</a></nav>
      <h1>Wikidata SVG Gallery</h1>
    </div>
    <input id="search" type="search" placeholder="Filter…" oninput="filter(this.value)">
    <span id="count">{len(cards)} items</span>
  </header>
  <div class="grid" id="grid">
{card_html}
  </div>
  <script>
    const cards = document.querySelectorAll('.card');
    function filter(q) {{
      q = q.toLowerCase();
      let n = 0;
      cards.forEach(c => {{
        const show = !q || c.querySelector('span').textContent.toLowerCase().includes(q);
        c.classList.toggle('hidden', !show);
        if (show) n++;
      }});
      document.getElementById('count').textContent = n + ' items';
    }}
  </script>
</body>
</html>'''

    OUTPUT_FILE.write_text(html, encoding='utf-8')
    print(f'Wrote gallery ({len(cards)} items) to {OUTPUT_FILE}')

if __name__ == '__main__':
    main()
