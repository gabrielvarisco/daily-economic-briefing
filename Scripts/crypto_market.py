import os
from typing import Optional

import requests


COINGECKO_URL = "https://api.coingecko.com/api/v3"

CRYPTO_ASSETS = [
    "bitcoin",
    "ethereum",
    "solana",
    "chainlink",
    "raydium",
    "binancecoin",
    "uniswap",
    "aave",
]

CRYPTO_LABELS = {
    "bitcoin": "BTC",
    "ethereum": "ETH",
    "solana": "SOL",
    "chainlink": "LINK",
    "raydium": "RAY",
    "binancecoin": "BNB",
    "uniswap": "UNI",
    "aave": "AAVE",
}

TOTAL3_CHART_URL = "https://www.tradingview.com/symbols/TOTAL3/"


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
        "disable_web_page_preview": True,
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
        "per_page": 20,
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


def _fmt_billions(value: Optional[float]) -> str:
    if value is None:
        return "-"
    return f"{value / 1_000_000_000:.2f}B"


def _build_coin_line(coin: dict) -> str:
    symbol = CRYPTO_LABELS.get(coin["id"], coin.get("symbol", "").upper())

    price = coin.get("current_price")
    change_24h = coin.get("price_change_percentage_24h")
    change_7d = coin.get("price_change_percentage_7d_in_currency")

    return (
        f"{symbol} ${_fmt(price)} "
        f"{_fmt(change_24h)}% (24h) "
        f"{_fmt(change_7d)}% (7d)"
    )


def crypto_market() -> str:
    report = "₿ <b>Crypto Market</b>\n\n"

    try:
        market_data = _fetch_market_data()
        global_data = _fetch_global_data()

        coins_by_id = {coin["id"]: coin for coin in market_data}

        majors = ["bitcoin", "ethereum", "solana"]
        defi_alt = ["chainlink", "raydium", "binancecoin", "uniswap", "aave"]

        report += "<b>Majors</b>\n"
        for coin_id in majors:
            coin = coins_by_id.get(coin_id)
            if coin:
                report += _build_coin_line(coin) + "\n"

        report += "\n<b>Alt / DeFi</b>\n"
        for coin_id in defi_alt:
            coin = coins_by_id.get(coin_id)
            if coin:
                report += _build_coin_line(coin) + "\n"

        report += "\n"

        total_market_cap = global_data.get("total_market_cap", {}).get("usd")
        btc_dominance = global_data.get("market_cap_percentage", {}).get("btc")

        btc_market_cap = coins_by_id.get("bitcoin", {}).get("market_cap")
        eth_market_cap = coins_by_id.get("ethereum", {}).get("market_cap")

        total3_estimate = None
        if (
            total_market_cap is not None
            and btc_market_cap is not None
            and eth_market_cap is not None
        ):
            total3_estimate = total_market_cap - btc_market_cap - eth_market_cap

        report += f"Total Market Cap: ${total_market_cap:,.0f}\n" if total_market_cap is not None else "Total Market Cap: -\n"
        report += f"BTC Dominance: {_fmt(btc_dominance)}%\n"
        report += f"TOTAL3 aprox.: ${_fmt_billions(total3_estimate)}\n"
        report += f'TOTAL3 chart: <a href="{TOTAL3_CHART_URL}">TradingView</a>\n'

    except Exception as exc:
        print(f"[crypto_market] erro: {exc}")
        report += "Erro ao carregar dados de crypto."

    return report.strip()


if __name__ == "__main__":
    print("Starting Crypto Market script")

    report = crypto_market()

    print(report)

    send_telegram(report)
