import csv

def generate_html_section(categories, section_title, section_id, color):
    """Generate HTML for one category section"""
    sorted_categories = sorted(categories)

    html = f"""
    <div class="section" id="{section_id}">
        <h2 style="color: {color};">{section_title} ({len(sorted_categories)} categories)</h2>

        <div class="button-container">
            <button onclick="openAllInSection('{section_id}')">Open All {section_title}</button>
            <button onclick="openFirstNInSection('{section_id}', 50)">Open First 50</button>
        </div>

        <div class="category-list">
"""

    for category in sorted_categories:
        display_name = category.replace('Category:', '')
        category_url = f"https://commons.wikimedia.org/wiki/{category.replace(' ', '_')}"

        html += f"""            <div class="category-item">
                <span class="category-name">{display_name}</span> -
                <a href="{category_url}" class="category-link" target="_blank">Create on Commons</a>
            </div>
"""

    html += """        </div>
    </div>
"""
    return html

def main():
    # Read all three CSVs
    rare_words = set()
    ligatures = set()
    anomalies = set()

    with open('redlinked_rare_words.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['Category']:
                rare_words.add(row['Category'])

    with open('redlinked_ligatures.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['Category']:
                ligatures.add(row['Category'])

    with open('redlinked_anomalies.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['Category']:
                anomalies.add(row['Category'])

    # Generate combined HTML
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sitelen Seli Kiwen - Categorized Redlinked Categories</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1400px;
            margin: 20px auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        h1 {
            color: #333;
            border-bottom: 3px solid #0645ad;
            padding-bottom: 10px;
        }
        h2 {
            margin-top: 30px;
            padding: 15px;
            background-color: white;
            border-radius: 5px;
            border-left: 5px solid;
        }
        .stats {
            background-color: #e8f4f8;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .nav-buttons {
            margin: 20px 0;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        .nav-buttons button {
            background-color: #444;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
        }
        .nav-buttons button:hover {
            background-color: #666;
        }
        .section {
            margin-bottom: 40px;
        }
        .button-container {
            margin: 15px 0;
        }
        button {
            background-color: #0645ad;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            margin-right: 10px;
        }
        button:hover {
            background-color: #0b0080;
        }
        .category-list {
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            column-count: 2;
            column-gap: 20px;
        }
        .category-item {
            padding: 8px 0;
            border-bottom: 1px solid #eee;
            break-inside: avoid;
        }
        .category-item:last-child {
            border-bottom: none;
        }
        .category-link {
            color: #0645ad;
            text-decoration: none;
            font-size: 14px;
        }
        .category-link:hover {
            text-decoration: underline;
        }
        .category-name {
            font-weight: bold;
            color: #d73333;
        }
        .explanation {
            background-color: #fff3cd;
            border: 1px solid #ffc107;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 20px;
        }
        .explanation h3 {
            margin-top: 0;
            color: #856404;
        }
        .explanation ul {
            margin: 10px 0;
        }
    </style>
    <script>
        function openAllInSection(sectionId) {
            const section = document.getElementById(sectionId);
            const links = section.querySelectorAll('.category-link');
            links.forEach(link => {
                window.open(link.href, '_blank');
            });
        }

        function openFirstNInSection(sectionId, n) {
            const section = document.getElementById(sectionId);
            const links = section.querySelectorAll('.category-link');
            for (let i = 0; i < Math.min(n, links.length); i++) {
                window.open(links[i].href, '_blank');
            }
        }

        function scrollToSection(sectionId) {
            document.getElementById(sectionId).scrollIntoView({ behavior: 'smooth' });
        }
    </script>
</head>
<body>
    <h1>Sitelen Seli Kiwen - Categorized Redlinked Categories</h1>

    <div class="stats">
        <strong>Total redlinked categories:</strong> """ + str(len(rare_words) + len(ligatures) + len(anomalies)) + """<br>
        <strong>Source category:</strong> <a href="https://commons.wikimedia.org/wiki/Category:Sitelen_seli_kiwen_svgs" target="_blank">Category:Sitelen_seli_kiwen_svgs</a>
    </div>

    <div class="explanation">
        <h3>Category Types:</h3>
        <ul>
            <li><strong>Rare Words (""" + str(len(rare_words)) + """):</strong> Single toki pona words that don't have categories yet (e.g., "Amelin (toki pona)")</li>
            <li><strong>Ligatures (""" + str(len(ligatures)) + """):</strong> Multi-word combinations with spaces (e.g., "Anpa lawa (toki pona)")</li>
            <li><strong>Anomalies (""" + str(len(anomalies)) + """):</strong> Words with unusual patterns like camelCase or numbers</li>
        </ul>
    </div>

    <div class="nav-buttons">
        <button onclick="scrollToSection('rare-words')">Jump to Rare Words</button>
        <button onclick="scrollToSection('ligatures')">Jump to Ligatures</button>
        <button onclick="scrollToSection('anomalies')">Jump to Anomalies</button>
    </div>
"""

    # Add sections
    html_content += generate_html_section(rare_words, "Rare Words", "rare-words", "#2c5aa0")
    html_content += generate_html_section(ligatures, "Ligatures", "ligatures", "#0d7d3d")
    html_content += generate_html_section(anomalies, "Anomalies", "anomalies", "#c7254e")

    html_content += """
</body>
</html>
"""

    # Write HTML file
    output_file = 'redlinked_categories_categorized.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"HTML file generated: {output_file}")
    print(f"  Rare words: {len(rare_words)}")
    print(f"  Ligatures: {len(ligatures)}")
    print(f"  Anomalies: {len(anomalies)}")
    print(f"  Total: {len(rare_words) + len(ligatures) + len(anomalies)}")

if __name__ == '__main__':
    main()
