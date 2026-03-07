import os
import sys
import requests
import yfinance as yf
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tickers.brazil_stocks import BRAZIL_TICKERS, BRAZIL_INDEX, BRAZIL_DOLLAR, BRAZIL_DI


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

    if data.empty or len(data) < 50:
        return None

    close = data["Close"]

    price = get_last_value(close)
    yesterday = get_last_value(close.iloc[-2])

    mm20 = get_last_value(close.rolling(20).mean())
    mm50 = get_last_value(close.rolling(50).mean())

    daily_change = ((price - yesterday) / yesterday) * 100

    mm20_status = "MM20↑" if price > mm20 else "MM20↓"
    mm50_status = "MM50↑" if price > mm50 else "MM50↓"

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
    mm200 = get_last_value(close.rolling(200).mean())

    regime = "Bull" if price > mm200 else "Bear"

    return price, mm200, regime


def analyze_dollar():

    data = yf.download(BRAZIL_DOLLAR, period="1mo", interval="1d", progress=False)

    close = data["Close"]

    price = get_last_value(close)
    week = get_last_value(close.iloc[-5])

    change = ((price - week) / week) * 100

    trend = "Alta" if change > 0 else "Baixa"

    return round(price, 2), trend


def analyze_di():

    data = yf.download(BRAZIL_DI, period="1mo", interval="1d", progress=False)

    close = data["Close"]

    price = get_last_value(close)
    week = get_last_value(close.iloc[-5])

    change = ((price - week) / week) * 100

    trend = "Alta" if change > 0 else "Baixa"

    return round(price, 2), trend


def brazil_market():

    report = "🇧🇷 <b>Brazil Market</b>\n\n"

    ibov, mm200, regime = analyze_ibov()

    report += f"IBOV: {round(ibov,0)}\n"
    report += f"MM200: {round(mm200,0)}\n"
    report += f"Regime: {regime}\n\n"

    dollar, dollar_trend = analyze_dollar()

    report += f"Dólar: {dollar}\n"
    report += f"Trend: {dollar_trend}\n\n"

    di, di_trend = analyze_di()

    report += f"Juros DI: {di}\n"
    report += f"Trend: {di_trend}\n\n"

    report += "Ações:\n"

    for ticker in BRAZIL_TICKERS:

        stock = analyze_stock(ticker)

        if stock:

            report += (
                f"{stock['ticker']} "
                f"{stock['price']} "
                f"{stock['daily_change']}% "
                f"{stock['mm20']} "
                f"{stock['mm50']}\n"
            )

    return report


if __name__ == "__main__":

    print("Starting Brazil Market script")

    report = brazil_market()

    print(report)

    send_telegram(report)
