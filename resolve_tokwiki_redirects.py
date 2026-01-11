"""
Resolve redirects on tok.wikipedia.org and update the CSV with final targets
"""
import io
import sys
import time
import requests
import csv

# Fix Windows encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

TOK_API = "https://tok.wikipedia.org/w/api.php"
HEADERS = {
    'User-Agent': 'TokiPonaRedirectResolver/1.0 (resolving redirects for wiki coverage analysis)'
}

def resolve_redirect(page_title):
    """
    Check if a page is a redirect and return the final target.
    Returns (is_redirect, final_title, redirect_chain)
    """
    params = {
        'action': 'query',
        'titles': page_title,
        'redirects': 1,  # Follow redirects
        'format': 'json'
    }

    try:
        response = requests.get(TOK_API, params=params, headers=HEADERS, timeout=10)
        data = response.json()

        if 'query' not in data:
            return False, page_title, []

        # Check if there were redirects followed
        redirects = data['query'].get('redirects', [])

        if not redirects:
            # Not a redirect
            return False, page_title, []

        # Build redirect chain
        redirect_chain = [(r['from'], r['to']) for r in redirects]
        final_title = redirects[-1]['to']

        return True, final_title, redirect_chain

    except Exception as e:
        print(f"    Error resolving {page_title}: {e}", flush=True)
        return False, page_title, []

def main():
    input_file = 'tokipona_wiki_coverage.csv'
    output_file = 'tokipona_wiki_coverage.csv'
    backup_file = 'tokipona_wiki_coverage_before_redirects.csv'

    print("Reading CSV...", flush=True)

    # Read all rows
    rows = []
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    print(f"Loaded {len(rows)} rows", flush=True)

    # Backup original
    print(f"Creating backup: {backup_file}", flush=True)
    with open(backup_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    # Process rows with tok.wikipedia articles
    redirect_count = 0
    checked_count = 0
    redirect_info = []

    for i, row in enumerate(rows):
        if row['tok_exists'] != 'Yes':
            continue

        word = row['word']
        checked_count += 1

        print(f"\n[{checked_count}] Checking: {word}", flush=True)

        is_redirect, final_title, redirect_chain = resolve_redirect(word)

        if is_redirect:
            print(f"  → REDIRECT: {word} → {final_title}", flush=True)
            redirect_count += 1

            # Update the row
            row['tok_url'] = f"https://tok.wikipedia.org/wiki/{final_title.replace(' ', '_')}"

            # Store redirect info for summary
            redirect_info.append({
                'word': word,
                'final': final_title,
                'chain': ' → '.join([word] + [to for from_, to in redirect_chain])
            })
        else:
            print(f"  ✓ Not a redirect", flush=True)

        time.sleep(0.5)  # Rate limit

    # Write updated CSV
    print(f"\n{'='*60}", flush=True)
    print(f"Writing updated CSV...", flush=True)
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"✓ Done!", flush=True)
    print(f"\nSummary:", flush=True)
    print(f"  Checked: {checked_count} articles on tok.wikipedia.org", flush=True)
    print(f"  Redirects resolved: {redirect_count}", flush=True)
    print(f"  Direct articles: {checked_count - redirect_count}", flush=True)

    if redirect_info:
        print(f"\nRedirects found:", flush=True)
        for info in redirect_info:
            print(f"  {info['chain']}", flush=True)

    # Write redirect summary to file
    if redirect_info:
        summary_file = 'tokwiki_redirects_resolved.txt'
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"Tok Wikipedia Redirects Resolved\n")
            f.write(f"{'='*60}\n\n")
            f.write(f"Total redirects: {redirect_count}\n\n")
            for info in redirect_info:
                f.write(f"{info['chain']}\n")
        print(f"\nDetailed redirect list saved to: {summary_file}", flush=True)

if __name__ == "__main__":
    main()
