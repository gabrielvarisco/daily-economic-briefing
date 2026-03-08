import os
from typing import Optional

import requests


COINGECKO_URL = "https://api.coingecko.com/api/v3"

CRYPTO_ASSETS = [
    "bitcoin",
    "ethereum",
    "solana",
]

CRYPTO_LABELS = {
    "bitcoin": "BTC",
    "ethereum": "ETH",
    "solana": "SOL",
}


def send_telegram(message: str) -> None:
    token = os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("CHAT_ID")

    if not token or not chat_id:
        print("[crypto_market] TELEGRAM_TOKEN ou CHAT_ID não configurados.")
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
        print(f"[crypto_market] erro ao enviar mensagem para o Telegram: {exc}")


def _fetch_market_data():
    url = f"{COINGECKO_URL}/coins/markets"

    params = {
        "vs_currency": "usd",
        "ids": ",".join(CRYPTO_ASSETS),
        "order": "market_cap_desc",
        "per_page": 10,
        "page": 1,
        "sparkline": False,
        "price_change_percentage": "24h,7d",
    }

    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()

    return response.json()


def _fetch_global_data():
    url = f"{COINGECKO_URL}/global"

    response = requests.get(url, timeout=20)
    response.raise_for_status()

    return response.json()["data"]


def _fmt(value: Optional[float], digits: int = 2) -> str:
    if value is None:
        return "-"
    return f"{value:.{digits}f}"


def crypto_market() -> str:
    report = "₿ <b>Crypto Market</b>\n\n"

    try:
        market_data = _fetch_market_data()

        for coin in market_data:
            symbol = CRYPTO_LABELS.get(coin["id"], coin["symbol"].upper())

            price = coin.get("current_price")
            change_24h = coin.get("price_change_percentage_24h")
            change_7d = coin.get("price_change_percentage_7d_in_currency")

            report += (
                f"{symbol} ${_fmt(price)} "
                f"{_fmt(change_24h)}% (24h) "
                f"{_fmt(change_7d)}% (7d)\n"
            )

        report += "\n"

        global_data = _fetch_global_data()

        total_market_cap = global_data["total_market_cap"]["usd"]
        btc_dominance = global_data["market_cap_percentage"]["btc"]

        report += f"Total Market Cap: ${total_market_cap:,.0f}\n"
        report += f"BTC Dominance: {_fmt(btc_dominance)}%\n"

    except Exception as exc:
        print(f"[crypto_market] erro: {exc}")
        report += "Erro ao carregar dados de crypto."

    return report


if __name__ == "__main__":
    print("Starting Crypto Market script")

    report = crypto_market()

    print(report)

    send_telegram(report)
