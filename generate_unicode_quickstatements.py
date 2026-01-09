import requests
import sys
import io

# Fix Unicode encoding on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

WIKIDATA_SPARQL = "https://query.wikidata.org/sparql"

# Unicode mappings from the user's list
unicode_mappings = {
    'a': '00', 'akesi': '01', 'ala': '02', 'alasa': '03', 'ale': '04', 'ali': '04',
    'anpa': '05', 'ante': '06', 'anu': '07', 'awen': '08', 'e': '09', 'en': '0A',
    'esun': '0B', 'ijo': '0C', 'ike': '0D', 'ilo': '0E', 'insa': '0F', 'jaki': '10',
    'jan': '11', 'jelo': '12', 'jo': '13', 'kala': '14', 'kalama': '15', 'kama': '16',
    'kasi': '17', 'ken': '18', 'kepeken': '19', 'kili': '1A', 'kiwen': '1B', 'ko': '1C',
    'kon': '1D', 'kule': '1E', 'kulupu': '1F', 'kute': '20', 'la': '21', 'lape': '22',
    'laso': '23', 'lawa': '24', 'len': '25', 'lete': '26', 'li': '27', 'lili': '28',
    'linja': '29', 'lipu': '2A', 'loje': '2B', 'lon': '2C', 'luka': '2D', 'lukin': '2E',
    'lupa': '2F', 'ma': '30', 'mama': '31', 'mani': '32', 'meli': '33', 'mi': '34',
    'mije': '35', 'moku': '36', 'moli': '37', 'monsi': '38', 'mu': '39', 'mun': '3A',
    'musi': '3B', 'mute': '3C', 'nanpa': '3D', 'nasa': '3E', 'nasin': '3F', 'nena': '40',
    'ni': '41', 'nimi': '42', 'noka': '43', 'o': '44', 'olin': '45', 'ona': '46',
    'open': '47', 'pakala': '48', 'pali': '49', 'palisa': '4A', 'pan': '4B', 'pana': '4C',
    'pi': '4D', 'pilin': '4E', 'pimeja': '4F', 'pini': '50', 'pipi': '51', 'poka': '52',
    'poki': '53', 'pona': '54', 'pu': '55', 'sama': '56', 'seli': '57', 'selo': '58',
    'seme': '59', 'sewi': '5A', 'sijelo': '5B', 'sike': '5C', 'sin': '5D', 'sina': '5E',
    'sinpin': '5F', 'sitelen': '60', 'sona': '61', 'soweli': '62', 'suli': '63', 'suno': '64',
    'supa': '65', 'suwi': '66', 'tan': '67', 'taso': '68', 'tawa': '69', 'telo': '6A',
    'tenpo': '6B', 'toki': '6C', 'tomo': '6D', 'tu': '6E', 'unpa': '6F', 'uta': '70',
    'utala': '71', 'walo': '72', 'wan': '73', 'waso': '74', 'wawa': '75', 'weka': '76',
    'wile': '77', 'namako': '78', 'kin': '79', 'oko': '7A', 'kipisi': '7B', 'leko': '7C',
    'monsuta': '7D', 'tonsi': '7E', 'jasima': '7F', 'kijetesantakalu': '80', 'soko': '81',
    'meso': '82', 'epiku': '83', 'kokosila': '84', 'lanpan': '85', 'n': '86', 'misikeke': '87',
    'ku': '88', 'pake': 'A0', 'apeja': 'A1', 'majuna': 'A2', 'powe': 'A3'
}

def get_wikidata_qids():
    """Query Wikidata for all Toki Pona words and get their QIDs"""
    print("Querying Wikidata for Toki Pona words...")

    # Get all words that are instances of Toki Pona word (Q137374997)
    sparql_query = """
    SELECT DISTINCT ?item ?itemLabel WHERE {
      ?item wdt:P31 wd:Q137374997 .
      SERVICE wikibase:label { bd:serviceParam wikibase:language "tok,en". }
    }
    """

    try:
        response = requests.get(
            WIKIDATA_SPARQL,
            params={'query': sparql_query, 'format': 'json'},
            headers={'User-Agent': 'TokiPona-Unicode-QuickStatements/1.0'}
        )

        if response.status_code != 200:
            print(f"ERROR: Got status code {response.status_code}")
            return {}

        data = response.json()

        word_to_qid = {}
        for result in data['results']['bindings']:
            label = result['itemLabel']['value']
            qid = result['item']['value'].split('/')[-1]

            # Only include single words
            if ' ' not in label and label.islower():
                word_to_qid[label] = qid

        print(f"Found {len(word_to_qid)} Toki Pona words on Wikidata\n")
        return word_to_qid

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return {}

def generate_quickstatements():
    """Generate QuickStatements for adding Unicode code points"""
    print("=" * 70)
    print("Generating QuickStatements for Unicode Code Points")
    print("=" * 70)
    print()

    # Get QIDs from Wikidata
    word_to_qid = get_wikidata_qids()

    # Generate QuickStatements
    statements = []
    not_found = []

    for word, hex_code in sorted(unicode_mappings.items()):
        unicode_point = f"F19{hex_code}"

        if word in word_to_qid:
            qid = word_to_qid[word]
            # Format: Q137722416|P4213|"F19A3"|P361|Q3685891
            statement = f'{qid}|P4213|"{unicode_point}"|P361|Q3685891'
            statements.append(statement)
            print(f"✓ {word:20} -> {qid:12} Unicode: {unicode_point}")
        else:
            not_found.append((word, unicode_point))
            print(f"✗ {word:20} -> NOT FOUND   Unicode: {unicode_point}")

    # Save to file
    output_file = 'unicode_quickstatements.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        for statement in statements:
            f.write(statement + '\n')

    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total words in Unicode list: {len(unicode_mappings)}")
    print(f"Found on Wikidata: {len(statements)}")
    print(f"Not found on Wikidata: {len(not_found)}")
    print()
    print(f"✓ Saved QuickStatements to: {output_file}")
    print()

    if not_found:
        print("Words NOT found on Wikidata:")
        for word, unicode_point in not_found:
            print(f"  • {word} (Unicode: F19{unicode_point})")
        print()

if __name__ == "__main__":
    generate_quickstatements()
