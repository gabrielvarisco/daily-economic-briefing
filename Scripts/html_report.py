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
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _convert_html(text: str) -> str:
    safe = text or ""

    placeholders = {
        "__B_OPEN__": "<b>",
        "__B_CLOSE__": "</b>",
        "__I_OPEN__": "<i>",
        "__I_CLOSE__": "</i>",
    }

    safe = safe.replace("<b>", placeholders["__B_OPEN__"])
    safe = safe.replace("</b>", placeholders["__B_CLOSE__"])
    safe = safe.replace("<i>", placeholders["__I_OPEN__"])
    safe = safe.replace("</i>", placeholders["__I_CLOSE__"])

    safe = _escape(safe)

    for key, value in placeholders.items():
        safe = safe.replace(_escape(key), value)

    return safe.replace("\n", "<br>")


def _normalize_title_for_strip(title: str) -> str:
    title = re.sub(r"<[^>]+>", "", title or "")
    title = re.sub(r"^[^\wÀ-ÿA-Za-z]+", "", title).strip()
    return title


def _strip_duplicate_title(title: str, body: str) -> str:
    if not body:
        return ""

    cleaned = body.strip()

    variants = [
        title.strip(),
        _normalize_title_for_strip(title),
    ]

    body_variants = [cleaned]

    plain_body = re.sub(r"<[^>]+>", "", cleaned).strip()
    body_variants.append(plain_body)

    for variant in variants:
        if not variant:
            continue

        for candidate in body_variants:
            if candidate.startswith(variant):
                return cleaned[len(cleaned) - len(candidate[len(variant):].lstrip()):]

    # remove casos como "🧠 <b>Market Take</b>"
    plain_title = _normalize_title_for_strip(title)
    cleaned_plain = re.sub(r"<[^>]+>", "", cleaned).strip()
    cleaned_plain = re.sub(r"^[^\wÀ-ÿA-Za-z]+", "", cleaned_plain).strip()

    if plain_title and cleaned_plain.startswith(plain_title):
        pattern = r"^\s*[^\wÀ-ÿA-Za-z]*\s*(?:<b>)?\s*" + re.escape(plain_title) + r"\s*(?:</b>)?\s*"
        cleaned = re.sub(pattern, "", cleaned, count=1, flags=re.IGNORECASE)

    return cleaned.strip()


def _card(title: str, body: str, extra_class: str = "") -> str:
    body = _strip_duplicate_title(title, body)
    body = _convert_html(body)

    return f"""
<section class="card {extra_class}">
  <div class="card-title">{title}</div>
  <div class="card-body">{body}</div>
</section>
"""


def _extract_regime(text: str) -> str:
    m = re.search(r"Regime:\s*<b>(.*?)</b>", text or "")
    return m.group(1).strip() if m else "-"


def _extract_summary(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text or "")
    lines = [l.strip() for l in text.splitlines() if l.strip()]

    for line in lines:
        if line.lower().startswith("regime:"):
            continue
        if len(line) > 20:
            return line[:180]

    return "-"


def _extract_metric(section_text: str, pattern: str) -> str:
    match = re.search(pattern, section_text or "", re.MULTILINE)
    return match.group(1).strip() if match else "-"


def _summary_cards(sections: Dict[str, str]) -> str:
    market_take = sections.get("market_take", "")
    brazil = sections.get("brazil", "")
    usa = sections.get("usa", "")
    crypto = sections.get("crypto", "")
    macro = sections.get("macro", "")

    regime = _extract_regime(market_take)
    ibov_change = _extract_metric(brazil, r"IBOV\s+[0-9\.,]+\s+([\-0-9\.]+%)")
    spy_change = _extract_metric(usa, r"S&P500\s+[0-9\.,]+\s+([\-0-9\.]+%)")
    btc_change = _extract_metric(crypto, r"BTC\s+\$[0-9\.,]+\s+([\-0-9\.]+%)\s+\(24h\)")
    vix_change = _extract_metric(macro, r"VIX:\s+[0-9\.,]+\s+\([🟢🔴⚪]\s+([\-0-9\.]+%)\)")

    cards = [
        ("Regime", regime),
        ("IBOV", ibov_change),
        ("S&P500", spy_change),
        ("BTC 24h", btc_change),
        ("VIX", vix_change),
    ]

    html_parts = []
    for label, value in cards:
        html_parts.append(
            f"""
<div class="metric-card">
  <div class="metric-label">{label}</div>
  <div class="metric-value">{value}</div>
</div>
"""
        )

    return "\n".join(html_parts)


def _build_report_html(sections: Dict[str, str]) -> str:
    summary_html = _summary_cards(sections)
    generated_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    cards = []
    for key in SECTION_TITLES:
        if key not in sections:
            continue

        extra_class = "wide-card" if key in {"market_take", "news"} else ""
        cards.append(_card(SECTION_TITLES[key], sections[key], extra_class=extra_class))

    cards_html = "\n".join(cards)

    return f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Daily Economic Briefing</title>

<style>
:root {{
  --bg: #0b1220;
  --panel: #131c2e;
  --panel-2: #182338;
  --border: #2a3957;
  --text: #e8eefc;
  --muted: #9eb0d1;
  --accent: #74a7ff;
  --accent-2: #59d0a7;
}}

* {{
  box-sizing: border-box;
}}

body {{
  margin: 0;
  background: linear-gradient(180deg, #0b1220 0%, #0d1425 100%);
  color: var(--text);
  font-family: Arial, Helvetica, sans-serif;
}}

.container {{
  max-width: 1320px;
  margin: 0 auto;
  padding: 32px 20px 56px;
}}

.hero {{
  background: linear-gradient(135deg, #16223b 0%, #11192a 100%);
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: 30px;
  margin-bottom: 24px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.25);
}}

.hero h1 {{
  margin: 0 0 8px;
  font-size: 38px;
}}

.hero p {{
  margin: 0;
  color: var(--muted);
}}

.hero-top {{
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
  flex-wrap: wrap;
}}

.top-link a {{
  color: var(--accent);
  text-decoration: none;
  font-weight: 700;
}}

.metrics-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 14px;
  margin: 24px 0 28px;
}}

.metric-card {{
  background: linear-gradient(180deg, var(--panel) 0%, var(--panel-2) 100%);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 16px;
  min-height: 96px;
}}

.metric-label {{
  font-size: 12px;
  color: var(--muted);
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}}

.metric-value {{
  font-size: 24px;
  font-weight: 700;
  line-height: 1.2;
}}

.grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(380px, 1fr));
  gap: 18px;
}}

.card {{
  background: linear-gradient(180deg, var(--panel) 0%, var(--panel-2) 100%);
  border: 1px solid var(--border);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 8px 20px rgba(0,0,0,0.18);
}}

.wide-card {{
  grid-column: 1 / -1;
}}

.card-title {{
  padding: 14px 18px;
  font-weight: 700;
  color: var(--accent);
  border-bottom: 1px solid var(--border);
  background: rgba(255,255,255,0.02);
}}

.card-body {{
  padding: 18px;
  font-size: 14px;
  line-height: 1.65;
  word-break: break-word;
}}

.card-body b {{
  color: #ffffff;
}}

.card-body i {{
  color: var(--muted);
}}

.footer {{
  margin-top: 28px;
  color: var(--muted);
  font-size: 13px;
  text-align: center;
}}

@media (max-width: 700px) {{
  .hero h1 {{
    font-size: 30px;
  }}

  .container {{
    padding: 20px 14px 40px;
  }}

  .grid {{
    grid-template-columns: 1fr;
  }}
}}
</style>
</head>

<body>
<div class="container">

  <div class="hero">
    <div class="hero-top">
      <div>
        <h1>Daily Economic Briefing</h1>
        <p>Market intelligence dashboard</p>
      </div>
      <div class="top-link">
        <a href="index.html">← Back to history</a>
      </div>
    </div>

    <div class="metrics-grid">
      {summary_html}
    </div>

    <p>Generated: {generated_at}</p>
  </div>

  <div class="grid">
    {cards_html}
  </div>

  <div class="footer">
    Generated automatically by your market briefing system.
  </div>

</div>
</body>
</html>
"""


def _list_reports() -> List[str]:
    _ensure_reports_dir()

    files = [
        f for f in os.listdir(REPORTS_DIR)
        if re.match(r"daily_report_\d{4}-\d{2}-\d{2}\.html$", f)
    ]
    files.sort(reverse=True)
    return files


def _extract_report_data(filepath: str) -> Tuple[str, str]:
    regime = "-"
    summary = "-"

    try:
        with open(filepath, encoding="utf-8") as f:
            html = f.read()

        regime = _extract_regime(html)
        summary = _extract_summary(html)
    except Exception:
        pass

    return regime, summary


def _build_index_html() -> str:
    reports = _list_reports()

    latest_date = "-"
    latest_regime = "-"
    latest_summary = "-"

    if reports:
        latest_file = reports[0]
        latest_date = latest_file.replace("daily_report_", "").replace(".html", "")
        latest_regime, latest_summary = _extract_report_data(os.path.join(REPORTS_DIR, latest_file))

    rows = []

    for report in reports:
        date = report.replace("daily_report_", "").replace(".html", "")
        regime, summary = _extract_report_data(os.path.join(REPORTS_DIR, report))

        rows.append(
            f"""
<tr>
  <td>{date}</td>
  <td>{regime}</td>
  <td>{_escape(summary)}</td>
  <td><a href="{report}">Open report</a></td>
</tr>
"""
        )

    rows_html = "\n".join(rows)
    generated_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    return f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Daily Market Dashboard</title>

<style>
:root {{
  --bg: #0b1220;
  --panel: #131c2e;
  --panel-2: #182338;
  --border: #2a3957;
  --text: #e8eefc;
  --muted: #9eb0d1;
  --accent: #74a7ff;
}}

* {{
  box-sizing: border-box;
}}

body {{
  margin: 0;
  background: linear-gradient(180deg, #0b1220 0%, #0d1425 100%);
  color: var(--text);
  font-family: Arial, Helvetica, sans-serif;
}}

.container {{
  max-width: 1220px;
  margin: 0 auto;
  padding: 32px 20px 56px;
}}

.hero {{
  background: linear-gradient(135deg, #16223b 0%, #11192a 100%);
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: 30px;
  margin-bottom: 24px;
}}

.hero h1 {{
  margin: 0 0 8px;
  font-size: 38px;
}}

.hero p {{
  margin: 0;
  color: var(--muted);
}}

.dashboard {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
  margin: 24px 0 28px;
}}

.widget {{
  background: linear-gradient(180deg, var(--panel) 0%, var(--panel-2) 100%);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 18px;
}}

.widget-label {{
  color: var(--muted);
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-bottom: 10px;
}}

.widget-value {{
  font-size: 24px;
  font-weight: 700;
}}

.widget-text {{
  font-size: 14px;
  line-height: 1.5;
}}

.panel {{
  background: linear-gradient(180deg, var(--panel) 0%, var(--panel-2) 100%);
  border: 1px solid var(--border);
  border-radius: 16px;
  overflow: hidden;
}}

.table-title {{
  padding: 16px 18px;
  font-weight: 700;
  color: var(--accent);
  border-bottom: 1px solid var(--border);
}}

table {{
  width: 100%;
  border-collapse: collapse;
}}

th, td {{
  padding: 14px 16px;
  border-bottom: 1px solid var(--border);
  text-align: left;
  vertical-align: top;
  font-size: 14px;
}}

th {{
  color: var(--accent);
  background: rgba(255,255,255,0.02);
}}

a {{
  color: var(--accent);
  text-decoration: none;
  font-weight: 700;
}}

.footer {{
  margin-top: 24px;
  color: var(--muted);
  font-size: 13px;
  text-align: center;
}}

@media (max-width: 900px) {{
  th:nth-child(3),
  td:nth-child(3) {{
    display: none;
  }}
}}

@media (max-width: 700px) {{
  .hero h1 {{
    font-size: 30px;
  }}

  .container {{
    padding: 20px 14px 40px;
  }}
}}
</style>
</head>

<body>
<div class="container">

  <div class="hero">
    <h1>Daily Market Dashboard</h1>
    <p>Historical archive of the market briefing system</p>

    <div class="dashboard">
      <div class="widget">
        <div class="widget-label">Latest Report</div>
        <div class="widget-value">{latest_date}</div>
      </div>

      <div class="widget">
        <div class="widget-label">Market Regime</div>
        <div class="widget-value">{latest_regime}</div>
      </div>

      <div class="widget">
        <div class="widget-label">Market Summary</div>
        <div class="widget-text">{_escape(latest_summary)}</div>
      </div>
    </div>

    <p>Updated: {generated_at}</p>
  </div>

  <div class="panel">
    <div class="table-title">Report History</div>
    <table>
      <thead>
        <tr>
          <th>Date</th>
          <th>Regime</th>
          <th>Summary</th>
          <th>Link</th>
        </tr>
      </thead>
      <tbody>
        {rows_html}
      </tbody>
    </table>
  </div>

  <div class="footer">
    Daily report archive.
  </div>

</div>
</body>
</html>
"""


def generate_index_page():
    _ensure_reports_dir()

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
