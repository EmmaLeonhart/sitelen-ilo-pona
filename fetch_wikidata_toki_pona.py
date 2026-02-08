import csv
import io
import sys
import urllib.parse
import urllib.request
from pathlib import Path

SPARQL_URL = "https://query.wikidata.org/sparql"
USER_AGENT = "SitelenBot/1.0 (https://github.com/immanuelle-leonhart/Sitelen)"

QUERY_TOK_LABELS = """\
SELECT ?item ?tokLabel WHERE {
  ?item rdfs:label ?tokLabel .
  FILTER(LANG(?tokLabel) = "tok")
}
"""

QUERY_TP_WIKIPEDIA = """\
SELECT ?item ?tpTitle WHERE {
  ?tpArticle schema:about ?item ;
             schema:isPartOf <https://tokipona.wikipedia.org/> ;
             schema:name ?tpTitle .
}
"""


def run_query(query):
    params = {"query": query}
    url = SPARQL_URL + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept": "text/csv",
    })
    with urllib.request.urlopen(req, timeout=120) as resp:
        return resp.read().decode("utf-8")


def main():
    out_path = Path(__file__).parent / "wikidata_toki_pona.csv"

    print("Fetching toki pona labels...")
    try:
        labels_csv = run_query(QUERY_TOK_LABELS)
    except Exception as exc:
        print(f"Failed to fetch tok labels: {exc}", file=sys.stderr)
        sys.exit(1)

    print("Fetching toki pona Wikipedia articles...")
    try:
        wp_csv = run_query(QUERY_TP_WIKIPEDIA)
    except Exception as exc:
        print(f"Failed to fetch tp Wikipedia articles: {exc}", file=sys.stderr)
        sys.exit(1)

    # Parse labels: item -> tokLabel
    items = {}  # qid -> {tokLabel, tpTitle}
    for row in csv.DictReader(io.StringIO(labels_csv)):
        qid = row["item"]
        items.setdefault(qid, {"tokLabel": "", "tpTitle": ""})
        items[qid]["tokLabel"] = row["tokLabel"]

    # Parse Wikipedia articles: item -> tpTitle
    for row in csv.DictReader(io.StringIO(wp_csv)):
        qid = row["item"]
        items.setdefault(qid, {"tokLabel": "", "tpTitle": ""})
        items[qid]["tpTitle"] = row["tpTitle"]

    # Write merged CSV
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["item", "tokLabel", "tpTitle"])
        for qid in sorted(items):
            writer.writerow([qid, items[qid]["tokLabel"], items[qid]["tpTitle"]])

    print(f"Wrote {len(items)} items to {out_path}")


if __name__ == "__main__":
    main()
