import re
import html
from datetime import datetime
from typing import List, Dict, Optional

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


def _clean_text(text: str) -> str:
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _strip_tags_keep_lines(text: str) -> List[str]:
    text = html.unescape(text)
    text = text.replace("\r", "\n")
    text = re.sub(r"</(div|p|li|tr|td|h1|h2|h3|br)>", "\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace("\xa0", " ")
    lines = [re.sub(r"\s+", " ", line).strip() for line in text.split("\n")]
    return [line for line in lines if line]


def _parse_date_from_line(line: str) -> Optional[datetime]:
    line_low = line.lower()

    # pt: "segunda-feira, 09 de mar de 2026"
    m_pt = re.search(r"(\d{2})\s+de\s+([a-zç\.]+)\s+de\s+(\d{4})", line_low)
    if m_pt:
        day = int(m_pt.group(1))
        month = MONTH_MAP.get(m_pt.group(2))
        year = int(m_pt.group(3))
        if month:
            return datetime(year, month, day)

    # en: "Monday, Mar 09, 2026"
    m_en = re.search(r"([a-z]{3,4})\s+(\d{2}),\s+(\d{4})", line_low)
    if m_en:
        month = MONTH_MAP.get(m_en.group(1))
        day = int(m_en.group(2))
        year = int(m_en.group(3))
        if month:
            return datetime(year, month, day)

    return None


def _is_time_line(line: str) -> bool:
    return bool(re.match(r"^\d{2}\s+[A-Za-zç]{3}\s+\d{2}:\d{2}$", line)) or bool(
        re.match(r"^[A-Z][a-z]{2}\s+\d{2},\s+\d{2}:\d{2}$", line)
    )


def _extract_time(line: str) -> Optional[str]:
    m = re.search(r"(\d{2}:\d{2})", line)
    return m.group(1) if m else None


def _is_impact(line: str) -> bool:
    return line in {"High", "Medium", "Alto", "Médio"}


def _looks_like_value(line: str) -> bool:
    if line in {"-", "No data", "Sem dados"}:
        return True
    if re.search(r"\d", line):
        return True
    return False


def _collect_country_events(country_name: str, max_events: int = 4) -> List[Dict]:
    meta = URLS[country_name]
    raw_html = _download(meta["url"])
    lines = _strip_tags_keep_lines(raw_html)

    today = datetime.now().date()
    current_date = None
    events: List[Dict] = []

    i = 0
    while i < len(lines):
        line = lines[i]

        parsed_date = _parse_date_from_line(line)
        if parsed_date:
            current_date = parsed_date.date()
            i += 1
            continue

        if current_date != today:
            i += 1
            continue

        if _is_time_line(line):
            time_str = _extract_time(line)
            block = lines[i:i + 10]

            currency_line = next((x for x in block if x.startswith(meta["currency"] + " ")), None)
            impact_line = next((x for x in block if _is_impact(x)), None)

            if not currency_line or not impact_line:
                i += 1
                continue

            event_name = currency_line.replace(meta["currency"], "", 1).strip()

            values_after_impact = []
            seen_impact = False
            for x in block:
                if x == impact_line:
                    seen_impact = True
                    continue
                if seen_impact and _looks_like_value(x):
                    values_after_impact.append(x)

            previous = values_after_impact[0] if len(values_after_impact) > 0 else "-"
            forecast = values_after_impact[1] if len(values_after_impact) > 1 else "-"
            actual = values_after_impact[2] if len(values_after_impact) > 2 else "-"

            if impact_line not in IMPACT_MAP:
                i += 1
                continue

            events.append({
                "country": country_name,
                "flag": meta["flag"],
                "time": time_str or "--:--",
                "event": event_name,
                "impact": impact_line,
                "bulls": IMPACT_MAP[impact_line],
                "previous": previous,
                "forecast": forecast,
                "actual": actual,
            })

            i += 1
            continue

        i += 1

    events.sort(key=lambda x: (x["time"], -len(x["bulls"])))
    return events[:max_events]


def economic_calendar(limit_total: int = 6) -> str:
    report = "🗓️ <b>Economic Agenda</b>\n\n"

    try:
        all_events: List[Dict] = []
        all_events.extend(_collect_country_events("Brazil", max_events=3))
        all_events.extend(_collect_country_events("United States", max_events=4))

        all_events.sort(key=lambda x: (x["time"], -len(x["bulls"])))

        if not all_events:
            return report + "Sem eventos de média/alta importância para hoje."

        for item in all_events[:limit_total]:
            report += (
                f"{item['flag']} {item['time']} {item['event']}\n"
                f"Impacto: {item['bulls']}\n"
                f"Prev: {item['forecast']} | Ant: {item['previous']}"
            )

            if item["actual"] not in {"-", "No data", "Sem dados"}:
                report += f" | Atual: {item['actual']}"

            report += "\n\n"

        return report.strip()

    except Exception as exc:
        print(f"[economic_calendar] erro: {exc}")
        return report + "Erro ao carregar agenda econômica."


if __name__ == "__main__":
    print("Starting Economic Calendar script")
    print(economic_calendar())
