import html
import re
from datetime import datetime
from typing import Dict, List, Optional

import requests


URLS = {
    "Brazil": {
        "url": "https://www.myfxbook.com/pt/forex-economic-calendar/brazil",
        "flag": "🇧🇷",
        "currency": "BRL",
    },
    "United States": {
        "url": "https://www.myfxbook.com/forex-economic-calendar/united-states",
        "flag": "🇺🇸",
        "currency": "USD",
    },
}

IMPACT_MAP = {
    "High": "🐂🐂🐂",
    "Medium": "🐂🐂",
    "Alto": "🐂🐂🐂",
    "Médio": "🐂🐂",
}

MONTH_MAP = {
    "jan": 1, "fev": 2, "mar": 3, "abr": 4, "mai": 5, "jun": 6,
    "jul": 7, "ago": 8, "set": 9, "out": 10, "nov": 11, "dez": 12,
    "jan.": 1, "feb": 2, "mar.": 3, "apr": 4, "may": 5, "jun.": 6,
    "jul.": 7, "aug": 8, "sep": 9, "oct": 10, "nov.": 11, "dec": 12,
}


def _download(url: str) -> str:
    response = requests.get(
        url,
        timeout=20,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
        },
    )
    response.raise_for_status()
    return response.text


def _strip_tags_keep_lines(text: str) -> List[str]:
    text = html.unescape(text)
    text = text.replace("\r", "\n")
    text = re.sub(r"</(div|p|li|tr|td|h1|h2|h3|br|span)>", "\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace("\xa0", " ")
    lines = [re.sub(r"\s+", " ", line).strip() for line in text.split("\n")]
    return [line for line in lines if line]


def _parse_date_from_line(line: str) -> Optional[datetime]:
    line_low = line.lower()

    m_pt = re.search(r"(\d{1,2})\s+de\s+([a-zç\.]+)\s+de\s+(\d{4})", line_low)
    if m_pt:
        day = int(m_pt.group(1))
        month = MONTH_MAP.get(m_pt.group(2))
        year = int(m_pt.group(3))
        if month:
            return datetime(year, month, day)

    m_en = re.search(r"([a-z]{3,4})\s+(\d{1,2}),\s+(\d{4})", line_low)
    if m_en:
        month = MONTH_MAP.get(m_en.group(1))
        day = int(m_en.group(2))
        year = int(m_en.group(3))
        if month:
            return datetime(year, month, day)

    return None


def _extract_time(line: str) -> Optional[str]:
    match = re.search(r"(\d{2}:\d{2})", line)
    return match.group(1) if match else None


def _is_time_line(line: str) -> bool:
    return bool(_extract_time(line))


def _is_impact_line(line: str) -> bool:
    return line in IMPACT_MAP


def _looks_like_value(line: str) -> bool:
    if line in {"-", "No data", "Sem dados"}:
        return True
    return bool(re.search(r"\d", line))


def _extract_event_name(block: List[str], currency: str) -> Optional[str]:
    for line in block:
        if line.startswith(currency + " "):
            name = line.replace(currency, "", 1).strip()
            if name:
                return name
    return None


def _extract_impact(block: List[str]) -> Optional[str]:
    for line in block:
        if _is_impact_line(line):
            return line
    return None


def _extract_values_after_impact(block: List[str], impact_line: str) -> List[str]:
    values = []
    seen_impact = False

    for line in block:
        if line == impact_line:
            seen_impact = True
            continue

        if seen_impact and _looks_like_value(line):
            values.append(line)

    return values


def _collect_country_events(country_name: str, max_events: int = 4) -> List[Dict]:
    meta = URLS[country_name]
    raw_html = _download(meta["url"])
    lines = _strip_tags_keep_lines(raw_html)

    today = datetime.now().date()
    current_date = None
    events: List[Dict] = []

    for i, line in enumerate(lines):
        parsed_date = _parse_date_from_line(line)
        if parsed_date:
            current_date = parsed_date.date()
            continue

        if current_date != today:
            continue

        if not _is_time_line(line):
            continue

        time_str = _extract_time(line) or "--:--"
        block = lines[i:i + 12]

        event_name = _extract_event_name(block, meta["currency"])
        impact_line = _extract_impact(block)

        if not event_name or not impact_line:
            continue

        values = _extract_values_after_impact(block, impact_line)

        previous = values[0] if len(values) > 0 else "-"
        forecast = values[1] if len(values) > 1 else "-"
        actual = values[2] if len(values) > 2 else "-"

        events.append({
            "country": country_name,
            "flag": meta["flag"],
            "time": time_str,
            "event": event_name,
            "impact": impact_line,
            "bulls": IMPACT_MAP[impact_line],
            "previous": previous,
            "forecast": forecast,
            "actual": actual,
        })

    events.sort(key=lambda x: (x["time"], -len(x["bulls"])))
    return events[:max_events]


def _build_report_from_events(events: List[Dict], limit_total: int = 6) -> str:
    report = "🗓️ <b>Economic Agenda</b>\n\n"

    if not events:
        report += (
            "Sem agenda filtrada disponível no momento.\n"
            "Calendários:\n"
            "• Myfxbook Brasil\n"
            "• Myfxbook United States"
        )
        return report

    for item in events[:limit_total]:
        report += (
            f"{item['flag']} {item['time']} {item['event']}\n"
            f"Impacto: {item['bulls']}\n"
            f"Prev: {item['forecast']} | Ant: {item['previous']}"
        )

        if item["actual"] not in {"-", "No data", "Sem dados"}:
            report += f" | Atual: {item['actual']}"

        report += "\n\n"

    return report.strip()


def economic_calendar(limit_total: int = 6) -> str:
    try:
        all_events: List[Dict] = []
        all_events.extend(_collect_country_events("Brazil", max_events=3))
        all_events.extend(_collect_country_events("United States", max_events=4))
        all_events.sort(key=lambda x: (x["time"], -len(x["bulls"])))

        return _build_report_from_events(all_events, limit_total=limit_total)

    except Exception as exc:
        print(f"[economic_calendar] erro: {exc}")
        return (
            "🗓️ <b>Economic Agenda</b>\n\n"
            "Agenda indisponível no momento.\n"
            "Fontes de consulta:\n"
            "• Myfxbook Brasil\n"
            "• Myfxbook United States"
        )


if __name__ == "__main__":
    print("Starting Economic Calendar script")
    print(economic_calendar())
