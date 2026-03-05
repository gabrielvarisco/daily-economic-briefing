import yfinance as yf
import pandas as pd
import numpy as np
import requests
import os
from config import ALL_TICKERS

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


def get_data():

    data = yf.download(
        ALL_TICKERS,
        period="6mo",
        interval="1d",
        auto_adjust=True,
        threads=True
    )

    return data["Close"]


def build_analysis(df):

    today = df.iloc[-1]
    yesterday = df.iloc[-2]

    df = df.dropna(axis=1, how="all")
    
    daily_return = ((today / yesterday) - 1) * 100
    weekly_return = ((today / df.iloc[-6]) - 1) * 100

    vol = df.pct_change().rolling(21).std().iloc[-1] * np.sqrt(252) * 100

    report = "📊 VARISCO QUANT REPORT\n\n"

    report += "🌎 MERCADO\n\n"

    for asset in today.index:
        report += f"{asset}\n"
        report += f"Preço: {today[asset]:.2f}\n"
        report += f"Dia: {daily_return[asset]:.2f}%\n"
        report += f"Semana: {weekly_return[asset]:.2f}%\n"
        report += f"Vol 21d: {vol[asset]:.2f}%\n\n"

    report += "🔥 MAIORES ALTAS DO DIA\n"

    for asset in daily_return.sort_values(ascending=False).head(5).index:
        report += f"{asset}: {daily_return[asset]:.2f}%\n"

    report += "\n🔻 MAIORES QUEDAS DO DIA\n"

    for asset in daily_return.sort_values().head(5).index:
        report += f"{asset}: {daily_return[asset]:.2f}%\n"

    report += "\n⚡ MAIOR VOLATILIDADE (21d)\n"

    for asset in vol.sort_values(ascending=False).head(5).index:
        report += f"{asset}: {vol[asset]:.2f}%\n"

    return report


def send_telegram(message):

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }

    requests.post(url, data=payload)


if __name__ == "__main__":

    df = get_data()

    report = build_analysis(df)

    send_telegram(report)
