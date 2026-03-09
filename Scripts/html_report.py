import os
from datetime import datetime
from typing import Dict


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


def _ensure_reports_dir() -> None:
    os.makedirs(REPORTS_DIR, exist_ok=True)


def _today_filename() -> str:
    today = datetime.utcnow().strftime("%Y-%m-%d")
    return os.path.join(REPORTS_DIR, f"daily_report_{today}.html")


def _escape_html(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _telegram_html_to_simple_html(text: str) -> str:
    """
    Converte o texto vindo do bot para HTML simples de página.
    Preserva <b> e <i>, escapa o resto e transforma quebras em <br>.
    """
    placeholders = {
        "__B_OPEN__": "<b>",
        "__B_CLOSE__": "</b>",
        "__I_OPEN__": "<i>",
        "__I_CLOSE__": "</i>",
    }

    safe = text or ""
    safe = safe.replace("<b>", placeholders["__B_OPEN__"])
    safe = safe.replace("</b>", placeholders["__B_CLOSE__"])
    safe = safe.replace("<i>", placeholders["__I_OPEN__"])
    safe = safe.replace("</i>", placeholders["__I_CLOSE__"])

    safe = _escape_html(safe)

    for key, value in placeholders.items():
        safe = safe.replace(_escape_html(key), value)

    return safe.replace("\n", "<br>\n")


def _section_card(title: str, body: str) -> str:
    body_html = _telegram_html_to_simple_html(body)

    return f"""
    <section class="card">
      <div class="card-header">{title}</div>
      <div class="card-body">{body_html}</div>
    </section>
    """


def _build_full_html(sections: Dict[str, str]) -> str:
    generated_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    ordered_keys = [
        "market_take",
        "day_over_day",
        "macro",
        "brazil",
        "usa",
        "crypto",
        "quant",
        "news",
    ]

    cards_html = []

    for key in ordered_keys:
        content = sections.get(key)
        if not content:
            continue

        title = SECTION_TITLES.get(key, key)
        cards_html.append(_section_card(title, content))

    joined_cards = "\n".join(cards_html)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Daily Economic Briefing</title>
  <style>
    :root {{
      --bg: #0b1020;
      --panel: #121a2b;
      --panel-2: #172033;
      --text: #e8eefc;
      --muted: #9fb0d3;
      --border: #25304a;
      --accent: #7aa2ff;
      --accent-2: #4ee1a0;
      --shadow: rgba(0, 0, 0, 0.30);
    }}

    * {{
      box-sizing: border-box;
    }}

    body {{
      margin: 0;
      font-family: Arial, Helvetica, sans-serif;
      background: linear-gradient(180deg, #0b1020 0%, #0d1324 100%);
      color: var(--text);
      line-height: 1.55;
    }}

    .container {{
      max-width: 1200px;
      margin: 0 auto;
      padding: 32px 20px 56px;
    }}

    .hero {{
      background: linear-gradient(135deg, #15213a 0%, #10192c 100%);
      border: 1px solid var(--border);
      border-radius: 18px;
      padding: 28px 28px 22px;
      box-shadow: 0 8px 24px var(--shadow);
      margin-bottom: 24px;
    }}

    .title {{
      margin: 0 0 8px;
      font-size: 34px;
      font-weight: 700;
      letter-spacing: -0.02em;
    }}

    .subtitle {{
      margin: 0;
      color: var(--muted);
      font-size: 15px;
    }}

    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
      gap: 18px;
      align-items: start;
    }}

    .card {{
      background: linear-gradient(180deg, var(--panel) 0%, var(--panel-2) 100%);
      border: 1px solid var(--border);
      border-radius: 16px;
      overflow: hidden;
      box-shadow: 0 8px 20px var(--shadow);
    }}

    .card-header {{
      padding: 14px 18px;
      border-bottom: 1px solid var(--border);
      font-size: 15px;
      font-weight: 700;
      color: var(--accent);
      background: rgba(255, 255, 255, 0.02);
    }}

    .card-body {{
      padding: 18px;
      font-size: 14px;
      white-space: normal;
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

    .badge-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 14px;
    }}

    .badge {{
      border: 1px solid var(--border);
      background: rgba(255, 255, 255, 0.03);
      color: var(--muted);
      border-radius: 999px;
      padding: 8px 12px;
      font-size: 12px;
    }}

    @media (max-width: 700px) {{
      .title {{
        font-size: 28px;
      }}

      .container {{
        padding: 20px 14px 40px;
      }}

      .hero {{
        padding: 22px 18px 18px;
      }}
    }}
  </style>
</head>
<body>
  <div class="container">
    <header class="hero">
      <h1 class="title">Daily Economic Briefing</h1>
      <p class="subtitle">Relatório diário de mercados com leitura executiva, cross-asset e histórico.</p>
      <div class="badge-row">
        <div class="badge">Generated: {generated_at}</div>
        <div class="badge">Markets: Brazil • USA • Crypto • Macro</div>
        <div class="badge">Format: HTML Daily Report</div>
      </div>
    </header>

    <main class="grid">
      {joined_cards}
    </main>

    <div class="footer">
      Generated automatically by your market briefing system.
    </div>
  </div>
</body>
</html>
"""


def generate_html_report(sections: Dict[str, str]) -> str:
    _ensure_reports_dir()

    filepath = _today_filename()
    html_content = _build_full_html(sections)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html_content)

    return filepath
