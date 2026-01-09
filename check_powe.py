import requests
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

WIKIDATA_SPARQL = "https://query.wikidata.org/sparql"

# Check what's up with powe (Q137722416)
sparql_query = """
SELECT ?item ?itemLabel ?p31 ?p31Label WHERE {
  VALUES ?item { wd:Q137722416 }
  OPTIONAL { ?item wdt:P31 ?p31 . }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "tok,en". }
}
"""

response = requests.get(
    WIKIDATA_SPARQL,
    params={'query': sparql_query, 'format': 'json'},
    headers={'User-Agent': 'Powe-Debug/1.0'}
)

data = response.json()

print("Checking Q137722416 (powe):")
print("=" * 70)
for result in data['results']['bindings']:
    label = result.get('itemLabel', {}).get('value', 'NO LABEL')
    p31 = result.get('p31', {}).get('value', 'NO P31')
    p31_label = result.get('p31Label', {}).get('value', '')

    print(f"Label: {label}")
    print(f"P31 (instance of): {p31}")
    print(f"P31 Label: {p31_label}")
    print()

# Also check if it appears in our general query
print("Checking if powe appears in general Toki Pona word query...")
general_query = """
SELECT DISTINCT ?item ?itemLabel WHERE {
  ?item wdt:P31 wd:Q137374997 .
  FILTER(CONTAINS(LCASE(?itemLabel), "powe"))
  SERVICE wikibase:label { bd:serviceParam wikibase:language "tok,en". }
}
"""

response2 = requests.get(
    WIKIDATA_SPARQL,
    params={'query': general_query, 'format': 'json'},
    headers={'User-Agent': 'Powe-Debug/1.0'}
)

data2 = response2.json()
if data2['results']['bindings']:
    print("Found in general query:")
    for result in data2['results']['bindings']:
        qid = result['item']['value'].split('/')[-1]
        label = result['itemLabel']['value']
        print(f"  {qid}: {label}")
else:
    print("NOT found in general query for Toki Pona words")
