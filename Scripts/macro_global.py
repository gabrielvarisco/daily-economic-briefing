import os
import sys
from typing import Optional

import requests

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from Scripts.asset_analyzer import analyze_asset


MACRO_TICKERS = {
    "DX-Y.NYB": "Dollar Index (DXY)",
    "^TNX": "US 10Y Yield",
    "SPY": "S&P 500",
    "^VIX": "VIX",
    "GLD": "Gold",
    "USO": "Oil (WTI)",
}


def send_telegram(message: str) -> None:
    token = os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("CHAT_ID")

    if not token or not chat_id:
        print("[macro_global] TELEGRAM_TOKEN ou CHAT_ID não configurados.")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }

    try:
        response = requests.post(url, json=payload, timeout=15)
        response.raise_for_status()
    except requests.RequestException as exc:
        print(f"[macro_global] erro ao enviar mensagem para o Telegram: {exc}")


def _fmt_number(value: Optional[float], digits: int = 2) -> str:
    if value is None:
        return "-"
    return f"{value:.{digits}f}"


def _direction_emoji(change: Optional[float]) -> str:
    if change is None:
        return "⚪"
    return "🟢" if change > 0 else "🔴"


def _analyze_macro_asset(ticker: str, label: str) -> Optional[dict]:
    return analyze_asset(
        ticker=ticker,
        period="1y",
        interval="1d",
        label=label,
    )


def macro_global() -> str:
    report = "🌍 <b>Macro Global</b>\n\n"

    valid_count = 0

    for ticker, label in MACRO_TICKERS.items():
        asset = _analyze_macro_asset(ticker, label)

        if not asset:
            report += f"{label}: erro\n"
            continue

        valid_count += 1
        change = asset.get("daily_change")
        emoji = _direction_emoji(change)

        report += (
            f"{label}: {_fmt_number(asset.get('price'))} "
            f"({emoji} {_fmt_number(change)}%)\n"
        )

    if valid_count == 0:
        report += "Sem dados macro disponíveis no momento."

    return report.strip()


if __name__ == "__main__":
    print("Starting Macro Global script")

    report = macro_global()

    print(report)

    send_telegram(report)
