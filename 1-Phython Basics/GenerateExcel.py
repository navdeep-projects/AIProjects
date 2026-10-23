import re
from Importpyodbc import SearchService

def get_keyword_context(text, keyword):
    """Extract sentences, URLs and div blocks where keyword appears with purpose analysis."""

    # extract URLs containing keyword from raw HTML
    urls = re.findall(r'https?://[^\s"<>]+', text)
    url_matches = [(url, "URL Reference") for url in urls if keyword.lower() in url.lower()]

    # extract div blocks containing keyword from raw HTML
    div_matches = []
    for div in re.findall(r'<div[^>]*>.*?</div>', text, re.IGNORECASE | re.DOTALL):
        if keyword.lower() in div.lower():
            clean_div = re.sub(r'<[^>]+>', ' ', div)
            clean_div = re.sub(r'\s+', ' ', clean_div).strip()
            if clean_div:
                div_matches.append((clean_div[:300], "DIV Block"))

    # extract plain sentences containing keyword
    clean_text = re.sub(r'<[^>]+>', ' ', text)
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    sentences = re.split(r'(?<=[.!?])\s+|\n+', clean_text)

    purpose_keywords = {
        "visa":        "Visa application process",
        "apply":       "Application submission",
        "appointment": "Appointment scheduling",
        "document":    "Document requirement",
        "passport":    "Passport related",
        "fee":         "Fee payment",
        "reject":      "Application rejection",
        "approv":      "Application approval",
        "submit":      "Submission process",
        "confirm":     "Confirmation notice",
        "attach":      "Attachment reference",
        "embassy":     "Embassy related",
        "interview":   "Interview scheduling",
        "expire":      "Expiry notification",
        "renew":       "Renewal process",
        "cancel":      "Cancellation notice",
        "status":      "Status update",
        "notif":       "Notification",
        "remind":      "Reminder",
        "welcome":     "Welcome message",
        "image":       "Image/Logo reference",
        "logo":        "Image/Logo reference",
        "asset":       "Asset reference",
        "http":        "URL Reference",
    }

    sentence_matches = []
    for sentence in sentences:
        if keyword.lower() in sentence.lower():
            purpose = "General reference"
            for pk, label in purpose_keywords.items():
                if pk.lower() in sentence.lower():
                    purpose = label
                    break
            sentence_matches.append((sentence.strip(), purpose))

    # merge all, avoid duplicates
    seen = set()
    result = []
    for item, purpose in url_matches + div_matches + sentence_matches:
        if item not in seen:
            seen.add(item)
            result.append((item, purpose))

    return result if result else [(clean_text[:300], "General reference")]

def generate_html(results, filename="search_results.html"):
    rows_html = ""
    for r in results:
        if r['column_name'].lower() in ('body', 'attachmentpath'):
            contexts = get_keyword_context(r['key_value'], r['key_name'])
            keyword = r['key_name']
            context_items = ""
            for c, purpose in contexts:
                css = "url" if purpose == "URL Reference" else "div" if purpose == "DIV Block" else ""
                highlighted = re.sub("(?i)(" + re.escape(keyword) + ")", r"<mark>\1</mark>", c)
                context_items += f'<li><span class="purpose-tag {css}">{purpose}</span> {highlighted}</li>'
            detail = f'<ul class="context-list">{context_items}</ul>'
        else:
            kv = r['key_value'][:120] + ('...' if len(r['key_value']) > 120 else '')
            detail = f'<span class="plain-val">{kv}</span>'

        rows_html += (
            f"<tr>"
            f"<td><span class='kw-badge'>{r['key_name']}</span></td>"
            f"<td>{r['table_name']}</td>"
            f"<td>{r['id']}</td>"
            f"<td>{r['culture_code']}</td>"
            f"<td>{r['column_name']}</td>"
            f"<td class='detail-cell'>{detail}</td>"
            f"</tr>\n"
        )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Search Results</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 30px; background: #f4f6f9; }}
        h2 {{ color: #2c3e50; }}
        .toolbar {{ margin-bottom: 12px; display:flex; align-items:center; gap:10px; }}
        input {{ padding: 8px; width: 300px; border: 1px solid #ccc; border-radius: 4px; }}
        table {{ width: 100%; border-collapse: collapse; background: white; box-shadow: 0 2px 6px rgba(0,0,0,0.1); }}
        th {{ background: #2c3e50; color: white; padding: 12px; text-align: left; }}
        td {{ padding: 10px 12px; border-bottom: 1px solid #e0e0e0; vertical-align:top; }}
        tr:hover {{ background: #eaf4fb; }}
        .kw-badge {{ background:#2980b9; color:white; padding:3px 10px; border-radius:12px; font-size:13px; white-space:nowrap; }}
        .context-list {{ margin:0; padding-left:18px; font-size:13px; color:#333; line-height:1.8; }}
        .context-list li {{ margin-bottom:4px; }}
        mark {{ background:#fff176; font-weight:bold; padding:0 2px; border-radius:2px; }}
        .plain-val {{ font-size:13px; color:#555; }}
        .purpose-tag {{ display:inline-block; background:#e67e22; color:white; font-size:11px; padding:1px 7px; border-radius:10px; margin-right:6px; white-space:nowrap; }}
        .purpose-tag.url {{ background:#2980b9; }}
        .purpose-tag.div {{ background:#8e44ad; }}
        .badge {{ background: #2980b9; color: white; padding: 2px 8px; border-radius: 10px; font-size: 12px; }}
        .export-btn {{ padding: 9px 18px; background: #27ae60; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; font-weight: bold; }}
        .export-btn:hover {{ background: #1e8449; }}
        .bottom-bar {{ margin-top: 16px; display: flex; justify-content: space-between; align-items: center; }}
        .detail-cell {{ max-width: 600px; }}
    </style>
</head>
<body>
    <h2>Cross Data Search Results</h2>
    <div class="toolbar">
        <input type="text" id="searchInput" onkeyup="filterTable()" placeholder="Filter by keyword, table, column...">
        <button class="export-btn" onclick="exportToExcel()">&#11015; Export to Excel</button>
    </div>
    <table id="resultsTable">
        <thead>
            <tr>
                <th>Search Keyword</th>
                <th>Table Name</th>
                <th>Id</th>
                <th>Culture Code</th>
                <th>Column Name</th>
                <th>Where It Is Used</th>
            </tr>
        </thead>
        <tbody>
            {rows_html}
        </tbody>
    </table>
    <div class="bottom-bar">
        <div id="total">Total records: <span class="badge">{len(results)}</span></div>
        <button class="export-btn" onclick="exportToExcel()">&#11015; Export to Excel</button>
    </div>

    <script src="https://cdn.sheetjs.com/xlsx-latest/package/dist/xlsx.full.min.js"></script>
    <script>
        function filterTable() {{
            const filter = document.getElementById("searchInput").value.toLowerCase();
            const rows = document.querySelectorAll("#resultsTable tbody tr");
            let count = 0;
            rows.forEach(row => {{
                const match = row.innerText.toLowerCase().includes(filter);
                row.style.display = match ? "" : "none";
                if (match) count++;
            }});
            document.getElementById("total").innerHTML = `Showing: <span class="badge">${{count}}</span>`;
        }}

        function exportToExcel() {{
            const table = document.getElementById("resultsTable");
            const visibleRows = [...table.querySelectorAll("tr")].filter(r => r.style.display !== "none");
            const data = visibleRows.map(r =>
                [...r.querySelectorAll("th,td")].map(c => c.innerText)
            );
            const ws = XLSX.utils.aoa_to_sheet(data);
            ws["!cols"] = [{{ wch: 18 }}, {{ wch: 30 }}, {{ wch: 20 }}, {{ wch: 80 }}];
            const wb = XLSX.utils.book_new();
            XLSX.utils.book_append_sheet(wb, ws, "Results");
            XLSX.writeFile(wb, "search_results.xlsx");
        }}
    </script>
</body>
</html>"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"HTML report saved to {filename}")

if __name__ == "__main__":
    import webbrowser, os
    svc = SearchService()
    results = svc.search_all_tables()
    filename = "search_results.html"
    generate_html(results, filename)
    filepath = os.path.abspath(filename)
    url = f"file:///{filepath}"
    # print(f"\nReport URL: {url}")
    webbrowser.open(url)
