import csv
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Load CSV
with open('tokipona_wiki_coverage.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

# Find entries with both wikidata_id and tok_wikidata_id
statements = []
for row in rows:
    word = row['word']
    word_qid = row.get('wikidata_id', '').strip()
    tok_qid = row.get('tok_wikidata_id', '').strip()

    if word_qid and tok_qid:
        # word_qid P460 tok_qid
        statements.append((word, word_qid, tok_qid))

print(f"Found {len(statements)} entries with both word QID and tok_wikidata_id")

# Write QuickStatements
with open('p460_quickstatements.txt', 'w', encoding='utf-8') as f:
    for word, word_qid, tok_qid in statements:
        f.write(f"{word_qid}|P460|{tok_qid}\n")

print(f"Saved to p460_quickstatements.txt")

# Also write detailed version for reference
with open('p460_quickstatements_details.txt', 'w', encoding='utf-8') as f:
    for word, word_qid, tok_qid in statements:
        f.write(f"{word}\t{word_qid}\tP460\t{tok_qid}\n")

print(f"Saved details to p460_quickstatements_details.txt")

# Show first 20 as sample
print("\nSample (first 20):")
for word, word_qid, tok_qid in statements[:20]:
    print(f"  {word}: {word_qid} -> P460 -> {tok_qid}")
