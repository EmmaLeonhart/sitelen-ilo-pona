import csv
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def qid_from_uri(uri: str) -> str:
    if not uri:
        return ""
    return uri.rsplit("/", 1)[-1]


def read_rows_from_xml(path: Path):
    text = path.read_text(encoding="utf-8", errors="ignore")

    # Robust line-based parsing to tolerate malformed XML.
    current = None
    item = ""
    tok = ""
    tp = ""
    in_result = False

    def flush():
        nonlocal item, tok, tp, in_result
        if in_result and (item or tok or tp):
            yield {"item": item, "tokLabel": tok, "tpTitle": tp}
        item = ""
        tok = ""
        tp = ""
        in_result = False

    for line in text.splitlines():
        if "<result" in line:
            in_result = True
            item = ""
            tok = ""
            tp = ""
            current = None
        if "binding name='item'" in line or 'binding name="item"' in line:
            current = "item"
        elif "binding name='tokLabel'" in line or 'binding name="tokLabel"' in line:
            current = "tokLabel"
        elif "binding name='tpTitle'" in line or 'binding name="tpTitle"' in line:
            current = "tpTitle"

        if "<uri>" in line and "</uri>" in line and current == "item":
            item = line.split("<uri>", 1)[1].split("</uri>", 1)[0].strip()
        if "<literal" in line and "</literal>" in line:
            value = line.split(">", 1)[1].split("</literal>", 1)[0]
            if current == "tokLabel":
                tok = value.strip()
            elif current == "tpTitle":
                tp = value.strip()

        if "</result>" in line:
            yield from flush()

    # Flush any trailing partial result
    yield from flush()


def read_rows_from_csv(path: Path):
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row


def main():
    root = Path(__file__).parent
    src = root / "wikidata_toki_pona.csv"
    out_csv = root / "wikidata_toki_pona_processed.csv"
    name_list = root / "wikidata_toki_pona_names.txt"

    if not src.exists():
        print(f"Missing input: {src}", file=sys.stderr)
        sys.exit(1)

    head = src.read_text(encoding="utf-8", errors="ignore").lstrip()
    if head.startswith("<"):
        rows_iter = read_rows_from_xml(src)
    else:
        rows_iter = read_rows_from_csv(src)

    rows = []
    name_set = []
    seen = set()

    for r in rows_iter:
        qid = qid_from_uri(r.get("item", ""))
        tok = r.get("tokLabel", "") or ""
        tp = r.get("tpTitle", "") or ""
        name = tok if tok else tp
        name = name.replace("_", " ").strip()
        if not name:
            continue
        rows.append(
            {
                "qid": qid,
                "tok_label": tok,
                "tp_title": tp,
                "name": name,
            }
        )
        if name not in seen:
            seen.add(name)
            name_set.append(name)

    with out_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["qid", "tok_label", "tp_title", "name"])
        writer.writeheader()
        writer.writerows(rows)

    with name_list.open("w", encoding="utf-8") as f:
        for name in name_set:
            f.write(name + "\n")

    print(f"Wrote {out_csv}")
    print(f"Wrote {name_list} ({len(name_set)} unique names)")


if __name__ == "__main__":
    main()
