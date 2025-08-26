from http.server import BaseHTTPRequestHandler
from bs4 import BeautifulSoup
from _shared import fetch_soup, find_row_cells_across_tables, render_html

URL = "https://www.cne-siar.gov.uk/bins-and-recycling/waste-recycling-collections-lewis-and-harris/non-recyclable-waste-grey-bin-purple-sticker/wednesday-collections"
TITLE = "BLACK Bin Collection Dates for Shader"
ICON  = "fa-trash-alt"
H1_COLOR = "#000"
BODY_BG = "#f7f9fc"
CARD_BG = "#fff"
LI_BG   = "#eef3f7"

TARGETS = ["Upper Shader", "Lower Shader"]

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            soup = fetch_soup(URL)
        except Exception as e:
            html = f"<p>Error fetching data: {e}</p>"
            self._send(200, html)
            return

        found, months = find_row_cells_across_tables(soup, TARGETS)

        if not months:
            html = render_html(
                TITLE, ICON, H1_COLOR, BODY_BG, CARD_BG, LI_BG,
                "<p>Could not find bin collection information on the page.</p>"
            )
            self._send(200, html)
            return

        area_sections = []
        for area in TARGETS:
            cells = found.get(area, [])
            if cells:
                month_blocks = []
                for month, dates_str in zip(months, cells):
                    dates = [d.strip() for d in dates_str.split(",") if d.strip()]
                    lis = "\n".join(f'<li><i class="fas fa-calendar-day"></i> {d}</li>' for d in dates) or "<li>-</li>"
                    month_blocks.append(f"<h3>{month}</h3>\n<ul>{lis}</ul>")
                area_sections.append(f"<h2>{area}</h2>\n{''.join(month_blocks)}")

        sections_html = (
            "\n".join(area_sections)
            if area_sections
            else "<p>No bin collection dates found for Upper/Lower Shader. Try refreshing later.</p>"
        )

        html = render_html(TITLE, ICON, H1_COLOR, BODY_BG, CARD_BG, LI_BG, sections_html)
        self._send(200, html)

    def _send(self, code: int, html: str):
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))
