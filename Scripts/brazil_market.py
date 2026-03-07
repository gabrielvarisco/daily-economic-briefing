import os
import sys
import requests
import yfinance as yf
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tickers.brazil_stocks import BRAZIL_TICKERS, BRAZIL_INDEX, BRAZIL_DOLLAR


def send_telegram(message):

    token = os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("CHAT_ID")

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }

    requests.post(url, json=payload)


def get_last_value(series):

    value = series.iloc[-1]

    if isinstance(value, pd.Series):
        value = value.iloc[0]

    return float(value)


def analyze_stock(ticker):

    data = yf.download(ticker, period="3mo", interval="1d", progress=False)

    if data.empty:
        return None

    close = data["Close"]

    price = get_last_value(close)

    prev = get_last_value(close.iloc[-2])

    daily_change = ((price - prev) / prev) * 100

    mm20 = get_last_value(close.rolling(20).mean())
    mm50 = get_last_value(close.rolling(50).mean())

    mm20_status = "↑" if price > mm20 else "↓"
    mm50_status = "↑" if price > mm50 else "↓"

    return {
        "ticker": ticker.replace(".SA", ""),
        "price": round(price, 2),
        "daily_change": round(daily_change, 2),
        "mm20": mm20_status,
        "mm50": mm50_status
    }


def analyze_ibov():

    data = yf.download(BRAZIL_INDEX, period="1y", interval="1d", progress=False)

    close = data["Close"]

    price = get_last_value(close)

    mm200_series = close.rolling(200).mean()
    mm200 = get_last_value(mm200_series)

    regime = "Bull (IBOV > MM200)" if price > mm200 else "Bear (IBOV < MM200)"

    return round(price, 0), round(mm200, 0), regime


def analyze_dollar():

    data = yf.download(BRAZIL_DOLLAR, period="3mo", interval="1d", progress=False)

    close = data["Close"]

    price = get_last_value(close)

    mm20 = get_last_value(close.rolling(20).mean())
    mm50 = get_last_value(close.rolling(50).mean())

    if price > mm20 and price > mm50:
        trend = "Alta forte (acima MM20 e MM50)"
    elif price > mm20:
        trend = "Alta (acima MM20)"
    elif price < mm20 and price < mm50:
        trend = "Baixa forte (abaixo MM20 e MM50)"
    elif price < mm20:
        trend = "Baixa (abaixo MM20)"
    else:
        trend = "Neutro"

    return round(price, 2), round(mm20, 2), round(mm50, 2), trend


def brazil_market():

    report = "🇧🇷 <b>Brazil Market</b>\n\n"

    ibov, mm200, regime = analyze_ibov()

    report += f"IBOV: {ibov}\n"
    report += f"MM200: {mm200}\n"
    report += f"Regime: {regime}\n\n"

    dollar, mm20, mm50, trend = analyze_dollar()

    report += f"Dólar: {dollar}\n"
    report += f"MM20: {mm20}\n"
    report += f"MM50: {mm50}\n"
    report += f"Trend: {trend}\n\n"

    report += "Ações:\n"

    for ticker in BRAZIL_TICKERS:

        stock = analyze_stock(ticker)

        if stock:

            report += (
                f"{stock['ticker']} "
                f"{stock['price']} "
                f"{stock['daily_change']}% "
                f"MM20{stock['mm20']} "
                f"MM50{stock['mm50']}\n"
            )

    return report


if __name__ == "__main__":

    print("Starting Brazil Market script")

    report = brazil_market()

    print(report)

    send_telegram(report)
