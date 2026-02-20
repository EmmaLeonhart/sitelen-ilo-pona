import csv
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

API_URL = "https://tok.wikipedia.org/w/api.php"
USER_AGENT = "SitelenBot/1.0 (https://github.com/immanuelle-leonhart/Sitelen)"


def fetch_all_pages():
    """Fetch all mainspace pages from toki pona Wikipedia via allpages API."""
    pages = []
    params = {
        "action": "query",
        "list": "allpages",
        "apnamespace": "0",
        "aplimit": "500",
        "format": "json",
    }
    while True:
        url = API_URL + "?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        for p in data["query"]["allpages"]:
            pages.append({"pageid": p["pageid"], "title": p["title"]})

        if "continue" in data:
            params["apcontinue"] = data["continue"]["apcontinue"]
            print(f"  ...{len(pages)} pages so far")
        else:
            break

    return pages


def main():
    out_path = Path(__file__).parent.parent / "data" / "wikidata_toki_pona.csv"

    print("Fetching all pages from tok.wikipedia.org...")
    pages = fetch_all_pages()

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["pageid", "title"])
        for p in pages:
            writer.writerow([p["pageid"], p["title"]])

    print(f"Wrote {len(pages)} pages to {out_path}")


if __name__ == "__main__":
    main()
