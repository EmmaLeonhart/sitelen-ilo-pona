"""Show current data for synced items"""
import csv

with open('tokipona_wiki_coverage.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)

    print("Items with both Commons Wikidata AND tok.wikipedia Wikidata:")
    print("="*100)

    for row in reader:
        if row['wikidata_id'] and row['tok_wikidata_id']:
            print(f"{row['word']:20s} | Commons: {row['wikidata_id']:12s} | TokWiki: {row['tok_wikidata_id']:12s} | Sona: {row['sona_exists']:3s} | Wiktionary: {row['wiktionary_exists']:3s}")
