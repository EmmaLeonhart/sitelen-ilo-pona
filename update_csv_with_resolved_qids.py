import csv
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Load the resolved QIDs
qid_map = {}
with open('missing_qids_resolved.txt', 'r', encoding='utf-8') as f:
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) >= 2 and parts[1] != 'NOT_FOUND':
            word = parts[0]
            qid = parts[1]
            qid_map[word] = qid

print(f"Loaded {len(qid_map)} resolved QIDs")

# Load and update CSV
with open('tokipona_wiki_coverage.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    rows = list(reader)

updated_count = 0
for row in rows:
    word = row['word']
    if not row.get('wikidata_id', '').strip() and word in qid_map:
        row['wikidata_id'] = qid_map[word]
        row['wikidata_url'] = f"https://www.wikidata.org/wiki/{qid_map[word]}"
        updated_count += 1
        print(f"Updated: {word} -> {qid_map[word]}")

# Write updated CSV
with open('tokipona_wiki_coverage.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"\nUpdated {updated_count} entries in tokipona_wiki_coverage.csv")

# Verify
with open('tokipona_wiki_coverage.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    has_qid = sum(1 for r in rows if r.get('wikidata_id', '').strip())
    print(f"Total entries with wikidata_id now: {has_qid}/{len(rows)}")
