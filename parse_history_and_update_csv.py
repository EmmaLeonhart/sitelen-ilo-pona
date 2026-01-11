"""
Parse Wikidata creation history and update CSV with QIDs
"""
import csv
import re
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Read the history log (pasted manually)
history_text = """13:57, 11 January 2026 diff hist  +906  N yutu (Q137763949)
13:57, 11 January 2026 diff hist  +922  N yupekosi (Q137763948)
13:57, 11 January 2026 diff hist  +922  N wuwojiti (Q137763947)"""

def parse_history_line(line):
    """Extract word and QID from history line"""
    # Pattern: word (QXXXXXX)
    match = re.search(r'N\s+(.+?)\s+\((Q\d+)\)', line)
    if match:
        word = match.group(1)
        qid = match.group(2)
        return word, qid
    return None, None

def main():
    # Read history from file
    with open('wikidata_creation_history.txt', 'r', encoding='utf-8') as f:
        history_lines = f.readlines()

    # Parse all QIDs
    word_to_qid = {}
    for line in history_lines:
        word, qid = parse_history_line(line)
        if word and qid:
            word_to_qid[word] = qid

    print(f"Parsed {len(word_to_qid)} items from history", flush=True)

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

    print(f"\n✓ Updated {updated} items", flush=True)

if __name__ == "__main__":
    main()
