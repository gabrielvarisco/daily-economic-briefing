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
        "text": message
    }

    requests.post(url, json=payload)


def get_last_value(series):

    value = series.iloc[-1]

    if isinstance(value, pd.Series):
        value = value.iloc[0]

    return float(value)


# ----------------------------
# STOCK ANALYSIS
# ----------------------------

def analyze_stock(ticker):

    data = yf.download(ticker, period="3mo", interval="1d", progress=False)

    if data.empty:
        return None

    close = data["Close"]

    price = get_last_value(close)
    yesterday = get_last_value(close.iloc[-2])

    daily_change = ((price - yesterday) / yesterday) * 100

    mm20 = close.rolling(20).mean().iloc[-1]
    mm50 = close.rolling(50).mean().iloc[-1]

    mm20 = float(mm20)
    mm50 = float(mm50)

    mm20_signal = "↑" if price > mm20 else "↓"
    mm50_signal = "↑" if price > mm50 else "↓"

    return {
        "ticker": ticker.replace(".SA", ""),
        "price": round(price, 2),
        "daily_change": round(daily_change, 2),
        "mm20": mm20_signal,
        "mm50": mm50_signal
    }


# ----------------------------
# IBOV
# ----------------------------

def analyze_ibov():

    data = yf.download(BRAZIL_INDEX, period="1y", interval="1d", progress=False)

    close = data["Close"]

    price = get_last_value(close)

    mm200 = close.rolling(200).mean().iloc[-1]
    mm200 = float(mm200)

    regime = "Bull" if price > mm200 else "Bear"

    return round(price, 0), round(mm200, 0), regime


# ----------------------------
# DOLLAR
# ----------------------------

def analyze_dollar():

    data = yf.download(BRAZIL_DOLLAR, period="3mo", interval="1d", progress=False)

    close = data["Close"]

    price = get_last_value(close)

    mm20 = close.rolling(20).mean().iloc[-1]
    mm50 = close.rolling(50).mean().iloc[-1]

    mm20 = float(mm20)
    mm50 = float(mm50)

    if price > mm20 and price > mm50:
        trend = "Alta forte"
    elif price > mm20:
        trend = "Alta"
    elif price < mm20 and price < mm50:
        trend = "Baixa forte"
    else:
        trend = "Neutro"

    return round(price, 2), round(mm20, 2), round(mm50, 2), trend


# ----------------------------
# DI FUTURES
# ----------------------------

def analyze_di():

    data = yf.download(BRAZIL_DI, period="1mo", interval="1d", progress=False)

    close = data["Close"]

    price = get_last_value(close)
    yesterday = get_last_value(close.iloc[-2])

    change = ((price - yesterday) / yesterday) * 100

    trend = "Alta" if change > 0 else "Baixa"

    return round(price, 2), trend


# ----------------------------
# MAIN REPORT
# ----------------------------

def brazil_market():

    report = "🇧🇷 Brazil Market\n\n"

    # IBOV
    ibov, mm200, regime = analyze_ibov()

    report += f"IBOV: {ibov}\n"
    report += f"MM200: {mm200}\n"
    report += f"Regime: {regime}\n\n"

    # DOLLAR
    dollar, d_mm20, d_mm50, dollar_trend = analyze_dollar()

    report += f"Dólar: {dollar}\n"
    report += f"MM20: {d_mm20}\n"
    report += f"MM50: {d_mm50}\n"
    report += f"Trend: {dollar_trend}\n\n"

    # DI
    di, di_trend = analyze_di()

    report += f"Juros DI: {di}\n"
    report += f"Trend: {di_trend}\n\n"

    # STOCKS
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


# ----------------------------
# RUN
# ----------------------------

if __name__ == "__main__":

    print("Starting Brazil Market script")

    report = brazil_market()

    print(report)

    send_telegram(report)
