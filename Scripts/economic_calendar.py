import os
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

import requests


TE_CALENDAR_URL = "https://api.tradingeconomics.com/calendar"

# Para testes, o Trading Economics documenta uso com guest:guest.
# Em produção, prefira usar sua própria chave em TE_API_KEY.
DEFAULT_TE_API_KEY = "guest:guest"

TARGET_COUNTRIES = {
    "Brazil": "🇧🇷",
    "United States": "🇺🇸",
}

IMPORTANCE_EMOJI = {
    1: "🐂",
    2: "🐂🐂",
    3: "🐂🐂🐂",
}


def _get_api_key() -> str:
    return os.environ.get("TE_API_KEY", DEFAULT_TE_API_KEY)


def _fmt_value(value: Optional[str]) -> str:
    if value is None:
        return "-"
    text = str(value).strip()
    return text if text else "-"


def _parse_dt(dt_str: str) -> Optional[datetime]:
    """
    Trading Economics retorna datas em UTC em formato ISO.
    Ex.: 2016-12-02T13:30:00
    """
    if not dt_str:
        return None

    try:
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    except ValueError:
        try:
            return datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
        except ValueError:
            return None


def _to_brazil_time(dt_utc: Optional[datetime]) -> Optional[datetime]:
    if dt_utc is None:
        return None

    brasil_tz = timezone(timedelta(hours=-3))
    return dt_utc.astimezone(brasil_tz)


def _build_params() -> Dict[str, str]:
    """
    Filtra:
    - Brasil e EUA
    - importância 2 e 3
    """
    return {
        "c": _get_api_key(),
        "importance": "2,3",
        "countries": ",".join(TARGET_COUNTRIES.keys()),
        "f": "json",
    }


def _fetch_calendar() -> List[dict]:
    response = requests.get(
        TE_CALENDAR_URL,
        params=_build_params(),
        timeout=20,
        headers={"User-Agent": "Mozilla/5.0"},
    )
    response.raise_for_status()
    data = response.json()

    if isinstance(data, list):
        return data

    return []


def _is_today_brazil(dt_utc: Optional[datetime]) -> bool:
    if dt_utc is None:
        return False

    dt_br = _to_brazil_time(dt_utc)
    now_br = datetime.now(timezone(timedelta(hours=-3)))
    return dt_br.date() == now_br.date()


def _normalize_event(event: dict) -> Optional[dict]:
    country = event.get("Country")
    importance = event.get("Importance")

    if country not in TARGET_COUNTRIES:
        return None

    if importance not in (2, 3):
        return None

    dt_utc = _parse_dt(event.get("Date", ""))

    if not _is_today_brazil(dt_utc):
        return None

    dt_br = _to_brazil_time(dt_utc)

    return {
        "country": country,
        "flag": TARGET_COUNTRIES[country],
        "time_br": dt_br.strftime("%H:%M") if dt_br else "--:--",
        "event": _fmt_value(event.get("Event")),
        "category": _fmt_value(event.get("Category")),
        "importance": importance,
        "bulls": IMPORTANCE_EMOJI.get(importance, "🐂"),
        "actual": _fmt_value(event.get("Actual")),
        "forecast": _fmt_value(event.get("Forecast")),
        "previous": _fmt_value(event.get("Previous")),
    }


def _sort_events(events: List[dict]) -> List[dict]:
    return sorted(events, key=lambda x: (x["time_br"], -x["importance"], x["country"], x["event"]))


def economic_calendar(limit: int = 6) -> str:
    report = "🗓️ <b>Economic Agenda</b>\n\n"

    try:
        raw_events = _fetch_calendar()

        parsed_events = []
        for event in raw_events:
            normalized = _normalize_event(event)
            if normalized:
                parsed_events.append(normalized)

        parsed_events = _sort_events(parsed_events)

        if not parsed_events:
            report += "Sem eventos de média/alta importância para hoje."
            return report

        for item in parsed_events[:limit]:
            report += (
                f"{item['flag']} {item['time_br']} {item['event']}\n"
                f"Impacto: {item['bulls']}\n"
                f"Prev: {item['forecast']} | Ant: {item['previous']}"
            )

            if item["actual"] != "-":
                report += f" | Atual: {item['actual']}"

            report += "\n\n"

        return report.strip()

    except Exception as exc:
        print(f"[economic_calendar] erro: {exc}")
        report += "Erro ao carregar agenda econômica."
        return report


if __name__ == "__main__":
    print("Starting Economic Calendar script")
    print(economic_calendar())
