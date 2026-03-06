import yfinance as yf
import pandas as pd
import numpy as np
import requests
import os
import sys

# permite importar arquivos da raiz do projeto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tickers.brazil_stocks import BRAZIL_TICKERS


def calculate_volatility(df):

    returns = df["Close"].pct_change()
    vol = returns.rolling(21).std() * np.sqrt(252)

    return vol.iloc[-1]


def analyze_ticker(ticker):

    df = yf.download(
        ticker,
        period="3mo",
        interval="1d",
        progress=False
    )

    if df.empty or len(df) < 50:
        return None

    price = df["Close"].iloc[-1]

    daily_return = (
        df["Close"].iloc[-1] /
        df["Close"].iloc[-2] - 1
    ) * 100

    weekly_return = (
        df["Close"].iloc[-1] /
        df["Close"].iloc[-6] - 1
    ) * 100

    vol = calculate_volatility(df)

    df["MM20"] = df["Close"].rolling(20).mean()
    df["MM50"] = df["Close"].rolling(50).mean()

    mm20 = df["MM20"].iloc[-1]
    mm50 = df["MM50"].iloc[-1]

    if price > mm20 and price > mm50:
        trend = "Alta forte (acima MM20 e MM50)"

    elif price > mm50:
        trend = "Alta moderada (acima MM50)"

    else:
        trend = "Baixa / correção"

    return {
        "ticker": ticker,
        "price": price,
        "daily": daily_return,
        "weekly": weekly_return,
        "vol": vol,
        "trend": trend
    }


def brazil_market():

    report = "🇧🇷 BRAZIL STOCK MARKET\n\n"

    for ticker in BRAZIL_TICKERS:

        data = analyze_ticker(ticker)

        if data is None:
            continue

        report += (
            f"{data['ticker']}\n"
            f"Preço: {data['price']:.2f}\n"
            f"Dia: {data['daily']:.2f}%\n"
            f"Semana: {data['weekly']:.2f}%\n"
            f"Vol 21d: {data['vol']:.2%}\n"
            f"Tendência: {data['trend']}\n\n"
        )

    return report


def send_telegram(message):

    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("CHAT_ID")

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": message
    }

    requests.post(url, data=payload)


if __name__ == "__main__":

    report = brazil_market()

    send_telegram(report)
