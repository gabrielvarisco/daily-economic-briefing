import os
import sys
from typing import Optional

import requests

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from Scripts.asset_analyzer import analyze_asset
from tickers.brazil_stocks import BRAZIL_TICKERS, BRAZIL_INDEX, BRAZIL_DOLLAR


def send_telegram(message: str) -> None:
    token = os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("CHAT_ID")

    if not token or not chat_id:
        print("[brazil_market] TELEGRAM_TOKEN ou CHAT_ID não configurados.")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
    }

    try:
        response = requests.post(url, json=payload, timeout=15)
        response.raise_for_status()
    except requests.RequestException as exc:
        print(f"[brazil_market] erro ao enviar mensagem para o Telegram: {exc}")


def _fmt_number(value: Optional[float], digits: int = 2) -> str:
    if value is None:
        return "-"
    return f"{value:.{digits}f}"


def _fmt_asset_line(asset: dict, show_mm200: bool = False) -> str:
    line = (
        f"{asset['label']} {_fmt_number(asset['price'])} {_fmt_number(asset['daily_change'])}%\n"
        f"Vol{_fmt_number(asset['vol_21d'])}% "
        f"MM20{asset.get('ma20_status', '-')} "
        f"MM50{asset.get('ma50_status', '-')}"
    )

    if show_mm200:
        line += f" MM200{asset.get('ma200_status', '-')}"

    return line


def analyze_ibov() -> Optional[dict]:
    return analyze_asset(
        ticker=BRAZIL_INDEX,
        period="1y",
        interval="1d",
        label="IBOV",
    )


def analyze_dollar() -> Optional[dict]:
    return analyze_asset(
        ticker=BRAZIL_DOLLAR,
        period="6mo",
        interval="1d",
        label="Dólar",
    )


def analyze_stock(ticker: str) -> Optional[dict]:
    return analyze_asset(
        ticker=ticker,
        period="6mo",
        interval="1d",
        label=ticker.replace(".SA", ""),
    )


def brazil_market() -> str:
    report = "🇧🇷 <b>Brazil Market</b>\n\n"

    ibov = analyze_ibov()
    if ibov:
        report += _fmt_asset_line(ibov, show_mm200=True) + "\n\n"
    else:
        report += "IBOV: sem dados disponíveis\n\n"

    dollar = analyze_dollar()
    if dollar:
        report += _fmt_asset_line(dollar, show_mm200=False) + "\n\n"
    else:
        report += "Dólar: sem dados disponíveis\n\n"

    report += "Ações:\n\n"

    valid_count = 0

    for ticker in BRAZIL_TICKERS:
        stock = analyze_stock(ticker)

        if not stock:
            continue

        valid_count += 1
        report += _fmt_asset_line(stock, show_mm200=False) + "\n\n"

    if valid_count == 0:
        report += "Nenhuma ação com dados disponíveis no momento.\n"

    return report.strip()


if __name__ == "__main__":
    print("Starting Brazil Market script")

    report = brazil_market()

    print(report)

    send_telegram(report)
