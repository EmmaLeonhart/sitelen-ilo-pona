"""
Analyze wiki coverage by category type
"""
import csv

def analyze_category(csv_file):
    categories_data = {
        'Category:Sitelen Pona ligatures': {
            'name': 'Ligatures',
            'total': 0,
            'wikidata': 0,
            'sona': 0,
            'tok': 0,
            'wiktionary': 0
        },
        'Category:Toki Pona logograms by word': {
            'name': 'Logograms',
            'total': 0,
            'wikidata': 0,
            'sona': 0,
            'tok': 0,
            'wiktionary': 0
        },
        'Category:Toki pona rare words': {
            'name': 'Rare Words',
            'total': 0,
            'wikidata': 0,
            'sona': 0,
            'tok': 0,
            'wiktionary': 0
        }
    }

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cat = row['category']
            if cat in categories_data:
                categories_data[cat]['total'] += 1
                if row['wikidata_id']:
                    categories_data[cat]['wikidata'] += 1
                if row['sona_exists'] == 'Yes':
                    categories_data[cat]['sona'] += 1
                if row['tok_exists'] == 'Yes':
                    categories_data[cat]['tok'] += 1
                if row['wiktionary_exists'] == 'Yes':
                    categories_data[cat]['wiktionary'] += 1

    # Print results
    print("\n" + "="*70)
    print("TOKI PONA WIKI COVERAGE BY CATEGORY")
    print("="*70 + "\n")

    for cat, data in categories_data.items():
        if data['total'] == 0:
            continue

        name = data['name']
        total = data['total']

        print(f"{name.upper()}")
        print("-" * 70)
        print(f"Total items: {total}")
        print(f"\nCoverage:")
        print(f"  Wikidata:         {data['wikidata']:4d} / {total:4d}  ({data['wikidata']*100//total:3d}%)")
        print(f"  sona.pona.la:     {data['sona']:4d} / {total:4d}  ({data['sona']*100//total:3d}%)")
        print(f"  tok.wikipedia:    {data['tok']:4d} / {total:4d}  ({data['tok']*100//total:3d}%)")
        print(f"  en.wiktionary:    {data['wiktionary']:4d} / {total:4d}  ({data['wiktionary']*100//total:3d}%)")
        print()

    # Summary for ligatures and rare words combined
    ligatures = categories_data['Category:Sitelen Pona ligatures']
    rare = categories_data['Category:Toki pona rare words']

    combined_total = ligatures['total'] + rare['total']
    combined_wikidata = ligatures['wikidata'] + rare['wikidata']
    combined_sona = ligatures['sona'] + rare['sona']
    combined_tok = ligatures['tok'] + rare['tok']
    combined_wiktionary = ligatures['wiktionary'] + rare['wiktionary']

    print("="*70)
    print("COMBINED: LIGATURES + RARE WORDS")
    print("="*70)
    print(f"Total items: {combined_total}")
    print(f"\nCoverage:")
    print(f"  Wikidata:         {combined_wikidata:4d} / {combined_total:4d}  ({combined_wikidata*100//combined_total:3d}%)")
    print(f"  sona.pona.la:     {combined_sona:4d} / {combined_total:4d}  ({combined_sona*100//combined_total:3d}%)")
    print(f"  tok.wikipedia:    {combined_tok:4d} / {combined_total:4d}  ({combined_tok*100//combined_total:3d}%)")
    print(f"  en.wiktionary:    {combined_wiktionary:4d} / {combined_total:4d}  ({combined_wiktionary*100//combined_total:3d}%)")
    print()

if __name__ == "__main__":
    analyze_category('tokipona_wiki_coverage.csv')
