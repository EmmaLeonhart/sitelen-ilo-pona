"""
Generate P1268 QuickStatements ONLY for the 14 newly created items
"""
import csv

# The 14 newly created items
new_items = ['esun', 'jaki', 'ken', 'kijetesantakalu', 'ko', 'kon',
             'linja', 'lon', 'namako', 'nena', 'pilin', 'seli', 'sike', 'supa']

with open('tokipona_wiki_coverage.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)

    statements = []

    for row in reader:
        word = row['word']
        if word in new_items:
            wikidata_id = row['wikidata_id']
            tok_wikidata_id = row['tok_wikidata_id']

            if wikidata_id and tok_wikidata_id:
                statements.append(f"{wikidata_id}|P1268|{tok_wikidata_id}")
                print(f"{word:20s} | {wikidata_id}|P1268|{tok_wikidata_id}")

with open('represents_new14_quickstatements.txt', 'w', encoding='utf-8') as f:
    for stmt in statements:
        f.write(stmt + '\n')

print(f"\nWrote {len(statements)} statements to represents_new14_quickstatements.txt")
