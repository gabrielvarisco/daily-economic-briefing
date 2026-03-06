import yfinance as yf
import pandas as pd
import numpy as np
import requests
import os
import sys

# permite importar arquivos da raiz do projeto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tickers.brazil_stocks import BRAZIL_TICKERS


def calculate_volatility(close):

    returns = close.pct_change()
    vol = returns.rolling(21).std() * np.sqrt(252)

    return vol.iloc[-1]


def analyze_ticker(ticker):

    print(f"Analyzing {ticker}")

    df = yf.download(
        ticker,
        period="3mo",
        interval="1d",
        progress=False
    )

    if df.empty or len(df) < 50:
        print(f"No data for {ticker}")
        return None

    # força Close a ser série simples
    close = df["Close"].squeeze()

    price = float(close.iloc[-1])

    daily_return = (
        close.iloc[-1] / close.iloc[-2] - 1
    ) * 100

    weekly_return = (
        close.iloc[-1] / close.iloc[-6] - 1
    ) * 100

    vol = calculate_volatility(close)

    mm20 = close.rolling(20).mean().iloc[-1]
    mm50 = close.rolling(50).mean().iloc[-1]

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

    valid = 0

    for ticker in BRAZIL_TICKERS:

        data = analyze_ticker(ticker)

        if data is None:
            continue

        valid += 1

        report += (
            f"{data['ticker']}\n"
            f"Preço: {data['price']:.2f}\n"
            f"Dia: {data['daily']:.2f}%\n"
            f"Semana: {data['weekly']:.2f}%\n"
            f"Vol 21d: {data['vol']:.2%}\n"
            f"Tendência: {data['trend']}\n\n"
        )

    if valid == 0:
        report += "Nenhum dado retornado."

    return report


def send_telegram(message):

    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("CHAT_ID")

    if not token or not chat_id:
        print("ERRO: TELEGRAM_TOKEN ou CHAT_ID não encontrados.")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": message
    }

    print("Sending message to Telegram...")

    r = requests.post(url, data=payload, timeout=20)

    print("Telegram response:", r.text)


if __name__ == "__main__":

    print("Starting Brazil Market script")

    report = brazil_market()

    print(report)

    send_telegram(report)

    print("Script finished")
