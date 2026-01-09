import csv

def generate_html_from_csv(csv_file, output_html):
    """Generate HTML file with category links from CSV"""

    # Read unique categories from CSV
    categories = set()
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            categories.add(row['Category'])

    # Sort categories for better organization
    sorted_categories = sorted(categories)

    # Generate HTML
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sitelen Seli Kiwen - Redlinked Categories</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 20px auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        h1 {
            color: #333;
            border-bottom: 3px solid #0645ad;
            padding-bottom: 10px;
        }
        .stats {
            background-color: #e8f4f8;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .button-container {
            margin: 20px 0;
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
        }
        .category-item {
            padding: 8px 0;
            border-bottom: 1px solid #eee;
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
    </style>
    <script>
        function openAllInTabs() {
            const links = document.querySelectorAll('.category-link');
            links.forEach(link => {
                window.open(link.href, '_blank');
            });
        }

        function openFirst50() {
            const links = document.querySelectorAll('.category-link');
            for (let i = 0; i < Math.min(50, links.length); i++) {
                window.open(links[i].href, '_blank');
            }
        }
    </script>
</head>
<body>
    <h1>Sitelen Seli Kiwen - Redlinked Categories on Commons</h1>

    <div class="stats">
        <strong>Total redlinked categories found:</strong> """ + str(len(sorted_categories)) + """<br>
        <strong>Source category:</strong> <a href="https://commons.wikimedia.org/wiki/Category:Sitelen_seli_kiwen_svgs" target="_blank">Category:Sitelen_seli_kiwen_svgs</a>
    </div>

    <div class="button-container">
        <button onclick="openAllInTabs()">Open All Categories in New Tabs</button>
        <button onclick="openFirst50()">Open First 50 Categories</button>
    </div>

    <div class="category-list">
"""

    # Add each category as a link
    for category in sorted_categories:
        # Remove "Category:" prefix for display
        display_name = category.replace('Category:', '')
        # Create the Commons URL
        category_url = f"https://commons.wikimedia.org/wiki/{category.replace(' ', '_')}"

        html_content += f"""        <div class="category-item">
            <span class="category-name">{display_name}</span> -
            <a href="{category_url}" class="category-link" target="_blank">Create on Commons</a>
        </div>
"""

    html_content += """    </div>
</body>
</html>
"""

    # Write HTML file
    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"HTML file generated: {output_html}")
    print(f"Total categories: {len(sorted_categories)}")

if __name__ == '__main__':
    csv_file = 'redlinked_categories.csv'
    output_html = 'redlinked_categories.html'

    generate_html_from_csv(csv_file, output_html)
