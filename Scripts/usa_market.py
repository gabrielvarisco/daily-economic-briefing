import os
import sys
from typing import Optional

import requests

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from Scripts.asset_analyzer import analyze_asset
from tickers.usa_stocks import (
    USA_INDEX_TICKERS,
    USA_SECTOR_TICKERS,
    USA_STOCK_TICKERS,
    USA_MACRO_TICKERS,
)


USA_LABELS = {
    "SPY": "S&P500",
    "QQQ": "Nasdaq",
    "DIA": "Dow",
    "IWM": "Russell",
    "XLK": "Tech",
    "XLF": "Financials",
    "XLE": "Energy",
    "XLV": "Health",
    "^VIX": "VIX",
    "TLT": "Treasuries",
    "DX-Y.NYB": "DXY",
}


def send_telegram(message: str) -> None:
    token = os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("CHAT_ID")

    if not token or not chat_id:
        print("[usa_market] TELEGRAM_TOKEN ou CHAT_ID não configurados.")
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
        print(f"[usa_market] erro ao enviar mensagem para o Telegram: {exc}")


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


def _analyze_with_label(ticker: str, period: str = "1y") -> Optional[dict]:
    return analyze_asset(
        ticker=ticker,
        period=period,
        interval="1d",
        label=USA_LABELS.get(ticker, ticker),
    )


def usa_market() -> str:
    report = "🇺🇸 <b>USA Market</b>\n\n"

    report += "<b>Índices</b>\n\n"
    valid_indices = 0

    for ticker in USA_INDEX_TICKERS:
        asset = _analyze_with_label(ticker, period="1y")
        if not asset:
            continue

        valid_indices += 1
        report += _fmt_asset_line(asset, show_mm200=True) + "\n\n"

    if valid_indices == 0:
        report += "Sem dados de índices no momento.\n\n"

    report += "<b>Setores</b>\n\n"
    valid_sectors = 0

    for ticker in USA_SECTOR_TICKERS:
        asset = _analyze_with_label(ticker, period="1y")
        if not asset:
            continue

        valid_sectors += 1
        report += _fmt_asset_line(asset, show_mm200=False) + "\n\n"

    if valid_sectors == 0:
        report += "Sem dados de setores no momento.\n\n"

    report += "<b>Big Techs</b>\n\n"
    valid_stocks = 0

    for ticker in USA_STOCK_TICKERS:
        asset = _analyze_with_label(ticker, period="1y")
        if not asset:
            continue

        valid_stocks += 1
        report += _fmt_asset_line(asset, show_mm200=False) + "\n\n"

    if valid_stocks == 0:
        report += "Sem dados de ações no momento.\n\n"

    report += "<b>Macro / Risco</b>\n\n"
    valid_macro = 0

    for ticker in USA_MACRO_TICKERS:
        asset = _analyze_with_label(ticker, period="1y")
        if not asset:
            continue

        valid_macro += 1
        report += _fmt_asset_line(asset, show_mm200=False) + "\n\n"

    if valid_macro == 0:
        report += "Sem dados macro no momento.\n\n"

    return report.strip()


if __name__ == "__main__":
    print("Starting USA Market script")

    report = usa_market()

    print(report)

    send_telegram(report)
