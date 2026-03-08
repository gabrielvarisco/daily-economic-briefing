import os
from datetime import datetime, timedelta, timezone
from typing import List, Optional

import requests


DEFAULT_TE_API_KEY = "guest:guest"
BRAZIL_TZ = timezone(timedelta(hours=-3))

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


def _fmt_value(value) -> str:
    if value is None:
        return "-"
    text = str(value).strip()
    return text if text else "-"


def _safe_int(value) -> Optional[int]:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _parse_dt(dt_str: str) -> Optional[datetime]:
    if not dt_str:
        return None

    candidates = [
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%d %H:%M:%S",
    ]

    clean = dt_str.replace("Z", "").strip()

    for fmt in candidates:
        try:
            return datetime.strptime(clean, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue

    try:
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    except ValueError:
        return None


def _to_brazil_time(dt_utc: Optional[datetime]) -> Optional[datetime]:
    if dt_utc is None:
        return None
    return dt_utc.astimezone(BRAZIL_TZ)


def _request_json(url: str, params: dict) -> List[dict]:
    response = requests.get(
        url,
        params=params,
        timeout=20,
        headers={"User-Agent": "Mozilla/5.0"},
    )
    response.raise_for_status()

    data = response.json()
    if isinstance(data, list):
        return data

    raise ValueError(f"Resposta inesperada da API: {type(data).__name__}")


def _fetch_calendar() -> List[dict]:
    api_key = _get_api_key()

    attempts = [
        (
            "country-endpoint",
            "https://api.tradingeconomics.com/calendar/country/Brazil,United States",
            {"c": api_key, "importance": "2,3", "f": "json"},
        ),
        (
            "snapshot-endpoint",
            "https://api.tradingeconomics.com/calendar",
            {"c": api_key, "importance": "2,3", "f": "json"},
        ),
    ]

    last_error = None

    for name, url, params in attempts:
        try:
            data = _request_json(url, params)
            print(f"[economic_calendar] fetch ok via {name}: {len(data)} eventos brutos")
            return data
        except Exception as exc:
            last_error = exc
            print(f"[economic_calendar] falha via {name}: {exc}")

    raise RuntimeError(f"não foi possível carregar agenda econômica: {last_error}")


def _is_today_brazil(dt_utc: Optional[datetime]) -> bool:
    if dt_utc is None:
        return False

    dt_br = _to_brazil_time(dt_utc)
    now_br = datetime.now(BRAZIL_TZ)
    return dt_br.date() == now_br.date()


def _normalize_event(event: dict) -> Optional[dict]:
    country = _fmt_value(event.get("Country"))
    importance = _safe_int(event.get("Importance"))
    dt_utc = _parse_dt(_fmt_value(event.get("Date")))

    if country not in TARGET_COUNTRIES:
        return None

    if importance not in (2, 3):
        return None

    if not _is_today_brazil(dt_utc):
        return None

    dt_br = _to_brazil_time(dt_utc)

    return {
        "country": country,
        "flag": TARGET_COUNTRIES[country],
        "time_br": dt_br.strftime("%H:%M") if dt_br else "--:--",
        "event": _fmt_value(event.get("Event")),
        "importance": importance,
        "bulls": IMPORTANCE_EMOJI.get(importance, "🐂"),
        "actual": _fmt_value(event.get("Actual")),
        "forecast": _fmt_value(event.get("Forecast")),
        "previous": _fmt_value(event.get("Previous")),
    }


def economic_calendar(limit: int = 6) -> str:
    report = "🗓️ <b>Economic Agenda</b>\n\n"

    try:
        raw_events = _fetch_calendar()

        parsed_events = []
        for event in raw_events:
            normalized = _normalize_event(event)
            if normalized:
                parsed_events.append(normalized)

        parsed_events.sort(
            key=lambda x: (x["time_br"], -x["importance"], x["country"], x["event"])
        )

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
        print(f"[economic_calendar] erro final: {exc}")
        report += "Erro ao carregar agenda econômica."
        return report


if __name__ == "__main__":
    print("Starting Economic Calendar script")
    print(economic_calendar())
