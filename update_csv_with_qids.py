"""
Update CSV with QIDs from the word-QID mapping file
"""
import csv
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Read word-QID mapping
word_to_qid = {}
with open('word_qid_mapping.txt', 'r', encoding='utf-8') as f:
    for line in f:
        parts = line.strip().split()
        if len(parts) == 2:
            word = parts[0]
            qid = parts[1]
            word_to_qid[word] = qid

print(f"Loaded {len(word_to_qid)} word-QID mappings", flush=True)

# Read CSV
with open('tokipona_wiki_coverage.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

# Update CSV with QIDs
updated = 0
for row in rows:
    word = row['word']
    if word in word_to_qid and not row.get('wikidata_id', '').strip():
        qid = word_to_qid[word]
        row['wikidata_id'] = qid
        row['wikidata_url'] = f"https://www.wikidata.org/wiki/{qid}"
        updated += 1
        print(f"  {word} → {qid}", flush=True)

# Write updated CSV
with open('tokipona_wiki_coverage.csv', 'w', encoding='utf-8', newline='') as f:
    fieldnames = rows[0].keys()
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"\n✓ Updated {updated} items in CSV", flush=True)
