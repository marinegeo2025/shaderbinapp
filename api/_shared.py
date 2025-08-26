# /api/_shared.py
from typing import List, Dict, Optional, Tuple
from bs4 import BeautifulSoup, Tag
import requests

HEADERS = {"User-Agent": "Mozilla/5.0"}

def fetch_soup(url: str, timeout: int = 12) -> BeautifulSoup:
    r = requests.get(url, timeout=timeout, headers=HEADERS)
    r.raise_for_status()
    return BeautifulSoup(r.text, "html.parser")

def find_row_cells_across_tables(
    soup: BeautifulSoup,
    targets: List[str],
) -> Tuple[Dict[str, List[str]], List[str]]:
    """
    Scan *every* table on the page.
    - Return a dict of {target -> [month_cells...]} for each matched target row.
    - Return 'months' from the header of the table where we first matched a target.
    Matching is case-insensitive and checks the first <td> text contains the target.
    """
    found: Dict[str, List[str]] = {}
    months: List[str] = []

    # Look at all tables; some pages group by "Week"/"Area"
    for table in soup.find_all("table"):
        # Build month headers for this table
        ths = table.find_all("th")
        if not ths:
            continue
        table_months = [th.get_text(strip=True) for th in ths][1:]  # skip 'Area' col

        # Iterate rows
        for tr in table.find_all("tr"):
            tds = tr.find_all("td")
            if not tds:
                continue
            area_text = tds[0].get_text(strip=True).lower()

            for target in targets:
                if target.lower() in area_text:
                    cells = [td.get_text(strip=True) for td in tds[1:]]
                    found[target] = cells
                    # lock months to the first table where we find a target
                    if not months:
                        months = table_months

        # Early exit if we already found all targets
        if all(t.lower() in [k.lower() for k in found.keys()] for t in targets):
            break

    return found, months

def render_html(
    title: str,
    icon: str,
    h1_color: str,
    body_bg: str,
    card_bg: str,
    li_bg: str,
    sections_html: str,
) -> str:
    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>{title}</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap" rel="stylesheet">
  <style>
    body {{
      font-family: 'Poppins', sans-serif;
      background: {body_bg};
      display: flex; justify-content: center; align-items: center;
      min-height: 100vh; margin: 0; padding: 24px;
    }}
    .container {{
      background: {card_bg}; padding: 25px; border-radius: 12px;
      box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
      width: 360px; max-width: 100%; text-align: center;
    }}
    h1 {{ color: {h1_color}; font-size: 24px; margin-bottom: 20px; }}
    h2 {{ font-size: 18px; color: #444; margin: 14px 0 10px; font-weight: 700; }}
    h3 {{ font-size: 16px; color: #555; margin: 10px 0 8px; font-weight: 600; }}
    ul {{ list-style: none; padding: 0; margin: 0 0 8px 0; }}
    li {{
      background: {li_bg}; margin: 6px 0; padding: 10px; border-radius: 6px;
      font-size: 15px; color: #333; font-weight: 500;
    }}
    .note {{ font-size: 12px; color: #666; margin-top: 10px; }}
    .back {{ display:inline-block; margin-top:16px; text-decoration:none; color:#0066cc; }}
  </style>
</head>
<body>
  <div class="container">
    <h1><i class="fas {icon}"></i> {title}</h1>
    {sections_html}
    <a class="back" href="/">← Back</a>
  </div>
</body>
</html>"""
