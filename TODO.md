# TODO

## Done

- [x] Reorganize repository into `fonts/`, `scripts/`, `data/` directories
- [x] Add `README.md` with download links, install instructions, and codepoint table
- [x] Add OFL-1.1 open source license

## Urgent

Oh sitelen seli kiwen is not a part of this project. Here’s the source for it https://github.com/kreativekorp/sitelen-seli-kiwen link it instead of having it downloadable on ohr repo. It is just used for generating svgs in our workflow. Don’t want to seem like I’m taking credit for something I’m not.

## Planned: Automated Wikidata Pipeline

The goal is a fully automated GitHub Actions pipeline that:

1. **Queries Wikidata via SPARQL** for all items that have a Toki Pona (`tok`) label
2. **Generates SVG images** (sitelen kalama pona) for each item's label
3. **Produces Wikimedia Commons page content** for each image (description, source, category)
4. **Produces QuickStatements** to add `P18` (image) claims on each Wikidata item
5. **Runs weekly** (cron) and on every push to `main`

### Implementation Steps

- [x] **`scripts/fetch_wikidata_sparql.py`** — Replaced SPARQL with more reliable Wikidata Search API (CirrusSearch) to avoid timeouts.
- [x] **`.github/workflows/generate-svgs.yml`** — Updated with correct branch and dependencies.
- [x] **Landing Page** — Added `index.html` and `gallery.html` for downloads and SVG viewing.
- [x] **Attribution** — Corrected font attribution and linked to original Sitelen Seli Kiwen repository.

- [ ] **License headers** — Add OFL license header to generated SVG files and Commons pages

- [ ] **Wikimedia Commons upload** — Consider using the Commons API or Pattypan to batch-upload
      generated SVGs. The existing `.wiki.txt` sidecar files already contain the page wikitext.

### SPARQL Query Sketch

```sparql
SELECT ?item ?label WHERE {
  ?item rdfs:label ?label .
  FILTER(LANG(?label) = "tok")
}
ORDER BY ?item
```

Endpoint: `https://query.wikidata.org/sparql`

### QuickStatements Format

```
Q<id>	P18	"Sitelen kalama pona - <filename>.svg"	S854	"<commons-url>"
```

### GitHub Actions Sketch

```yaml
name: Generate Sitelen SVGs
on:
  push:
    branches: [main]
  schedule:
    - cron: '0 0 * * 0'  # Every Sunday at midnight UTC

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install fonttools requests
      - run: python scripts/fetch_wikidata_sparql.py
      - run: python scripts/batch_generate_svgs.py
      - run: python scripts/generate_quickstatements.py
      - name: Commit new outputs
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add output/ data/
          git diff --cached --quiet || git commit -m "Auto-generate sitelen SVGs [skip ci]"
          git push
```
