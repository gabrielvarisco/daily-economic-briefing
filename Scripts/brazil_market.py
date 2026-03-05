import yfinance as yf
import pandas as pd
import numpy as np
import requests
import os

TICKERS = [
    "PETR4.SA",
    "VALE3.SA",
    "ITUB4.SA",
    "BBAS3.SA",
    "ABEV3.SA",
    "PRIO3.SA",
    "CMIG4.SA",
    "CSAN3.SA",
    "ITSA4.SA",
    "SAPR4.SA",
    "SIMH3.SA",
    "KLBN4.SA",
    "RAPT4.SA",
    "USDBRL=X",
]

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


def get_data():

    data = yf.download(
        TICKERS,
        period="6mo",
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

    daily = ((today / yesterday) - 1) * 100

    report = "🇧🇷 B3 MARKET REPORT\n\n"

    for asset in df.columns:

        price = today[asset]
        ret = daily[asset]

        report += f"{asset}\n"
        report += f"Preço: {price:.2f}\n"
        report += f"Dia: {ret:.2f}%\n\n"

    report += "🔥 Maiores Altas\n"

    for asset in daily.sort_values(ascending=False).head(5).index:
        report += f"{asset}: {daily[asset]:.2f}%\n"

    report += "\n🔻 Maiores Quedas\n"

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
