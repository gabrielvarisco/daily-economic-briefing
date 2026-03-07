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

    if not token or not chat_id:
        print("Telegram token ou chat id não encontrado")
        return

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


def download_data(ticker, period="3mo"):

    try:

        data = yf.download(
            ticker,
            period=period,
            interval="1d",
            progress=False,
            auto_adjust=True
        )

        if data.empty:
            return None

        return data

    except Exception as e:

        print(f"Erro baixando {ticker}: {e}")
        return None


def analyze_stock(ticker):

    data = download_data(ticker, "3mo")

    if data is None:
        return None

    close = data["Close"]

    price = get_last_value(close)

    prev = get_last_value(close.iloc[-2:])

    change = ((price - prev) / prev) * 100

    mm20 = get_last_value(close.rolling(20).mean())
    mm50 = get_last_value(close.rolling(50).mean())

    mm20_signal = "↑" if price > mm20 else "↓"
    mm50_signal = "↑" if price > mm50 else "↓"

    return {
        "ticker": ticker.replace(".SA", ""),
        "price": round(price, 2),
        "change": round(change, 2),
        "mm20": mm20_signal,
        "mm50": mm50_signal
    }


def analyze_ibov():

    data = download_data(BRAZIL_INDEX, "1y")

    close = data["Close"]

    price = get_last_value(close)

    mm200_series = close.rolling(200).mean()

    mm200 = get_last_value(mm200_series)

    regime = "Bull" if price > mm200 else "Bear"

    return price, mm200, regime


def analyze_dollar():

    data = download_data(BRAZIL_DOLLAR, "3mo")

    close = data["Close"]

    price = get_last_value(close)

    mm20 = get_last_value(close.rolling(20).mean())
    mm50 = get_last_value(close.rolling(50).mean())

    if price > mm20 and price > mm50:
        trend = "Alta forte"

    elif price > mm20:
        trend = "Alta"

    elif price < mm20 and price < mm50:
        trend = "Baixa forte"

    else:
        trend = "Neutra"

    return round(price, 2), round(mm20, 2), round(mm50, 2), trend


def analyze_di():

    data = download_data(BRAZIL_DI, "3mo")

    close = data["Close"]

    price = get_last_value(close)

    mm20 = get_last_value(close.rolling(20).mean())

    trend = "Alta" if price > mm20 else "Baixa"

    return round(price, 2), trend


def brazil_market():

    report = "🇧🇷 <b>Brazil Market</b>\n\n"

    ibov, mm200, regime = analyze_ibov()

    report += f"IBOV: {round(ibov,0)}\n"
    report += f"MM200: {round(mm200,0)}\n"
    report += f"Regime: {regime}\n\n"

    dollar, mm20_d, mm50_d, dollar_trend = analyze_dollar()

    report += f"Dólar: {dollar}\n"
    report += f"MM20: {mm20_d}\n"
    report += f"MM50: {mm50_d}\n"
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
                f"{stock['change']}% "
                f"MM20{stock['mm20']} "
                f"MM50{stock['mm50']}\n"
            )

    return report


if __name__ == "__main__":

    print("Starting Brazil Market script")

    report = brazil_market()

    print(report)

    send_telegram(report)
