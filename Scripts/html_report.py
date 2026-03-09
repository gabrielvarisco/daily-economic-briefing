import os
import re
from datetime import datetime
from typing import Dict, List, Tuple


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REPORTS_DIR = os.path.join(BASE_DIR, "reports")


SECTION_TITLES = {
    "market_take": "🧠 Market Take",
    "day_over_day": "📌 Since Last Snapshot",
    "macro": "🌍 Macro Global",
    "brazil": "🇧🇷 Brazil Market",
    "usa": "🇺🇸 USA Market",
    "crypto": "₿ Crypto Market",
    "quant": "📈 Quant Summary",
    "news": "📰 News Market",
}


def _ensure_reports_dir():
    os.makedirs(REPORTS_DIR, exist_ok=True)


def _today():
    return datetime.utcnow().strftime("%Y-%m-%d")


def _today_filename():
    return os.path.join(REPORTS_DIR, f"daily_report_{_today()}.html")


def _index_filename():
    return os.path.join(REPORTS_DIR, "index.html")


def _escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _convert_html(text: str) -> str:
    text = text.replace("<b>", "__B__").replace("</b>", "__B_END__")
    text = _escape(text)
    text = text.replace("__B__", "<b>").replace("__B_END__", "</b>")
    return text.replace("\n", "<br>")


def _card(title: str, body: str) -> str:
    body = _convert_html(body)

    return f"""
<section class="card">
<div class="card-title">{title}</div>
<div class="card-body">{body}</div>
</section>
"""


def _extract_regime(text: str) -> str:
    m = re.search(r"Regime:\s*<b>(.*?)</b>", text or "")
    return m.group(1) if m else "-"


def _extract_summary(text: str) -> str:
    text = re.sub("<.*?>", "", text)
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    for l in lines:
        if l.lower().startswith("regime"):
            continue
        if len(l) > 20:
            return l[:160]
    return "-"


def _list_reports():
    files = [
        f for f in os.listdir(REPORTS_DIR)
        if re.match(r"daily_report_\d{4}-\d{2}-\d{2}\.html", f)
    ]
    files.sort(reverse=True)
    return files


def _build_report_html(sections: Dict[str, str]) -> str:

    cards = []

    for key in SECTION_TITLES:

        if key not in sections:
            continue

        cards.append(_card(SECTION_TITLES[key], sections[key]))

    cards = "\n".join(cards)

    return f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Daily Economic Briefing</title>

<style>

body {{
background:#0e1117;
color:#e6edf3;
font-family:Arial;
margin:0;
}}

.container {{
max-width:1200px;
margin:auto;
padding:30px;
}}

.hero {{
margin-bottom:30px;
}}

.hero h1 {{
margin:0;
font-size:36px;
}}

.grid {{
display:grid;
grid-template-columns:repeat(auto-fit,minmax(340px,1fr));
gap:20px;
}}

.card {{
background:#161b22;
border:1px solid #30363d;
border-radius:12px;
overflow:hidden;
}}

.card-title {{
padding:12px 16px;
font-weight:bold;
background:#0d1117;
border-bottom:1px solid #30363d;
}}

.card-body {{
padding:16px;
font-size:14px;
}}

a {{
color:#58a6ff;
}}

</style>
</head>

<body>

<div class="container">

<div class="hero">
<h1>Daily Economic Briefing</h1>
<p>Market intelligence dashboard</p>
<p><a href="index.html">← Back to history</a></p>
</div>

<div class="grid">

{cards}

</div>

</div>

</body>
</html>
"""


def _build_index_html() -> str:

    reports = _list_reports()

    latest_regime = "-"
    latest_summary = "-"
    latest_date = "-"

    if reports:

        latest_file = reports[0]
        latest_date = latest_file.replace("daily_report_", "").replace(".html", "")

        with open(os.path.join(REPORTS_DIR, latest_file), encoding="utf-8") as f:
            html = f.read()

        latest_regime = _extract_regime(html)
        latest_summary = _extract_summary(html)

    rows = []

    for r in reports:

        date = r.replace("daily_report_", "").replace(".html", "")

        rows.append(
            f"""
<tr>
<td>{date}</td>
<td><a href="{r}">Open report</a></td>
</tr>
"""
        )

    rows = "\n".join(rows)

    return f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Daily Market Dashboard</title>

<style>

body {{
background:#0e1117;
color:#e6edf3;
font-family:Arial;
margin:0;
}}

.container {{
max-width:1100px;
margin:auto;
padding:40px;
}}

h1 {{
margin-top:0;
}}

.dashboard {{
display:grid;
grid-template-columns:repeat(auto-fit,minmax(250px,1fr));
gap:20px;
margin-bottom:40px;
}}

.widget {{
background:#161b22;
padding:20px;
border-radius:10px;
border:1px solid #30363d;
}}

table {{
width:100%;
border-collapse:collapse;
}}

td {{
padding:10px;
border-bottom:1px solid #30363d;
}}

a {{
color:#58a6ff;
}}

</style>
</head>

<body>

<div class="container">

<h1>Daily Market Dashboard</h1>

<div class="dashboard">

<div class="widget">
<b>Latest Report</b><br><br>
{latest_date}
</div>

<div class="widget">
<b>Market Regime</b><br><br>
{latest_regime}
</div>

<div class="widget">
<b>Market Summary</b><br><br>
{latest_summary}
</div>

</div>

<h2>Report History</h2>

<table>

{rows}

</table>

</div>

</body>
</html>
"""


def generate_index_page():

    index_path = _index_filename()

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(_build_index_html())

    return index_path


def generate_html_report(sections: Dict[str, str]) -> Tuple[str, str]:

    _ensure_reports_dir()

    report_path = _today_filename()

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(_build_report_html(sections))

    index_path = generate_index_page()

    return report_path, index_path
