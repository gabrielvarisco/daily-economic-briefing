import yfinance as yf
import pandas as pd
import numpy as np
import requests
import os

TICKERS = [
    "BTC-USD",
    "ETH-USD",
    "SOL-USD",
    "BNB-USD",
    "LINK-USD",
    "UNI7083-USD"
]

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


def get_data():

    data = yf.download(
        TICKERS,
        period="3mo",
        interval="1d",
        auto_adjust=True,
        threads=True
    )

    df = data["Close"]

    df = df.dropna(axis=1, how="all")

    return df


def build_report(df):

    today = df.iloc[-1]
    yesterday = df.iloc[-2]
    week = df.iloc[-7]

    daily = ((today / yesterday) - 1) * 100
    weekly = ((today / week) - 1) * 100

    vol = df.pct_change().rolling(21).std().iloc[-1] * np.sqrt(365) * 100

    report = "🪙 CRYPTO MARKET REPORT\n\n"

    for asset in df.columns:

        report += f"{asset}\n"
        report += f"Preço: {today[asset]:.2f}\n"
        report += f"24h: {daily[asset]:.2f}%\n"
        report += f"7d: {weekly[asset]:.2f}%\n"
        report += f"Vol: {vol[asset]:.2f}%\n\n"

    report += "🚀 Maiores Altas (24h)\n"

    for asset in daily.sort_values(ascending=False).head(5).index:
        report += f"{asset}: {daily[asset]:.2f}%\n"

    report += "\n🔻 Maiores Quedas (24h)\n"

    for asset in daily.sort_values().head(5).index:
        report += f"{asset}: {daily[asset]:.2f}%\n"

    return report


def send(msg):

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": msg
    }

    requests.post(url, data=payload)


if __name__ == "__main__":

    df = get_data()

    report = build_report(df)

    send(report)
