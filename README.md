# Sitelen — Toki Pona Fonts

Fonts for [Toki Pona](https://tokipona.org), the constructed minimalist language.
This repository contains two fonts:

- **Sitelen Kalama Pona** — a phonetic syllable font (sound symbols)
- **Sitelen Seli Kiwen** — a word symbol font (logographs)

![Sitelen Pona Sound Symbols](Sitelen%20Pona%20Sound%20Symbols.svg)

---

## Download

The font files are in the [`fonts/`](fonts/) directory:

| File | Format | Description |
|------|--------|-------------|
| [`sitelen-kalama-pona.otf`](fonts/sitelen-kalama-pona.otf) | OTF | Sitelen Kalama Pona — desktop use |
| [`sitelen-kalama-pona.woff2`](fonts/sitelen-kalama-pona.woff2) | WOFF2 | Sitelen Kalama Pona — web use |
| (original repo) | - | [Sitelen Seli Kiwen](https://github.com/kreativekorp/sitelen-seli-kiwen) |

---

## Installation

### Desktop (OTF)

1. Download [`fonts/sitelen-kalama-pona.otf`](fonts/sitelen-kalama-pona.otf)
2. Double-click the file and choose **Install Font** (macOS/Windows), or copy it to `~/.local/share/fonts/` and run `fc-cache` (Linux)

### Web (WOFF2)

```css
@font-face {
    font-family: 'Sitelen Kalama Pona';
    src: url('sitelen-kalama-pona.woff2') format('woff2');
}

@font-face {
    font-family: 'Sitelen Seli Kiwen';
    src: url('sitelen-seli-kiwen.woff2') format('woff2');
}
```

---

## Sitelen Kalama Pona

A phonetic abugida covering all 100 Toki Pona syllables. Each glyph is mapped to a Unicode Private Use Area (PUA) codepoint starting at U+E100.

### Codepoint Map

| Codepoint | Syllable | Codepoint | Syllable | Codepoint | Syllable | Codepoint | Syllable | Codepoint | Syllable |
|-----------|----------|-----------|----------|-----------|----------|-----------|----------|-----------|----------|
| U+E100 | a | U+E10A | ma | U+E114 | na | U+E11E | pa | U+E128 | ta |
| U+E101 | an | U+E10B | man | U+E115 | nan | U+E11F | pan | U+E129 | tan |
| U+E102 | e | U+E10C | me | U+E116 | ne | U+E120 | pe | U+E12A | te |
| U+E103 | en | U+E10D | men | U+E117 | nen | U+E121 | pen | U+E12B | ten |
| U+E104 | i | U+E10E | mi | U+E118 | ni | U+E122 | pi | U+E12C | ti |
| U+E105 | in | U+E10F | min | U+E119 | nin | U+E123 | pin | U+E12D | tin |
| U+E106 | o | U+E110 | mo | U+E11A | no | U+E124 | po | U+E12E | to |
| U+E107 | on | U+E111 | mon | U+E11B | non | U+E125 | pon | U+E12F | ton |
| U+E108 | u | U+E112 | mu | U+E11C | nu | U+E126 | pu | U+E130 | tu |
| U+E109 | un | U+E113 | mun | U+E11D | nun | U+E127 | pun | U+E131 | tun |

| Codepoint | Syllable | Codepoint | Syllable | Codepoint | Syllable | Codepoint | Syllable | Codepoint | Syllable |
|-----------|----------|-----------|----------|-----------|----------|-----------|----------|-----------|----------|
| U+E132 | ka | U+E13C | wa | U+E146 | ja | U+E150 | la | U+E15A | sa |
| U+E133 | kan | U+E13D | wan | U+E147 | jan | U+E151 | lan | U+E15B | san |
| U+E134 | ke | U+E13E | we | U+E148 | je | U+E152 | le | U+E15C | se |
| U+E135 | ken | U+E13F | wen | U+E149 | jen | U+E153 | len | U+E15D | sen |
| U+E136 | ki | U+E140 | wi | U+E14A | ji | U+E154 | li | U+E15E | si |
| U+E137 | kin | U+E141 | win | U+E14B | jin | U+E155 | lin | U+E15F | sin |
| U+E138 | ko | U+E142 | wo | U+E14C | jo | U+E156 | lo | U+E160 | so |
| U+E139 | kon | U+E143 | won | U+E14D | jon | U+E157 | lon | U+E161 | son |
| U+E13A | ku | U+E144 | wu | U+E14E | ju | U+E158 | lu | U+E162 | su |
| U+E13B | kun | U+E145 | wun | U+E14F | jun | U+E159 | lun | U+E163 | sun |

---

## Sitelen Seli Kiwen

A logographic font containing word symbols for Toki Pona vocabulary. Created by [KreativeKorp](https://github.com/kreativekorp).

- [Original Repository & Downloads](https://github.com/kreativekorp/sitelen-seli-kiwen)

Individual word glyphs are in [`sitelen_seli_kiwen_svgs/`](sitelen_seli_kiwen_svgs/) as standalone SVG files for use in generating composite SVGs.

---

## Repository Structure

```
fonts/                        Font files (OTF and WOFF2)
scripts/                      Build and generation scripts
  build_font.py               Rebuild sitelen-kalama-pona.otf from source glyphs
  generate_sitelen_kalama_pona.py  Generate composed SVG images
  batch_generate_svgs.py      Batch-generate SVGs for Wikipedia titles
  extract_sitelen_seli_kiwen.py   Extract glyphs from sitelen-seli-kiwen.woff2
  overwrite_svgs_from_font.py     Regenerate syllable SVGs from source
  fetch_wikidata_toki_pona.py     Fetch page list from tok.wikipedia.org
  process_wikidata_toki_pona.py   Filter titles for batch generation
data/                         Wikipedia data (CSV/TXT)
sitelen_seli_kiwen_svgs/      Individual word glyph SVGs (~541 files)
uniform_syllables/            Syllable glyph SVGs (100 files)
output/                       Generated composite SVGs (~6,500 files)
```

### Building from Source

The sitelen-kalama-pona font is built from FontForge glyph files in `..sfdir/`:

```bash
pip install fonttools
python scripts/build_font.py
```

This outputs `fonts/sitelen-kalama-pona.otf` and `fonts/sitelen-kalama-pona.woff2`.

---

## License

This project is released under the [SIL Open Font License 1.1](LICENSE) (OFL-1.1).
You are free to use, study, modify, and redistribute these fonts, including
embedding them in documents or software, as long as the fonts are not sold
standalone. See [LICENSE](LICENSE) for full terms.
