import yfinance as yf
import pandas as pd
import numpy as np
import requests
import os
from datetime import datetime
from config import ALL_TICKERS, BR_STOCKS, MACRO, CRYPTO

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


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

    df = df.dropna(axis=1)

    today = df.iloc[-1]
    yesterday = df.iloc[-2]

    daily_return = ((today / yesterday) - 1) * 100
    weekly_return = ((today / df.iloc[-6]) - 1) * 100

    vol = df.pct_change().rolling(21).std().iloc[-1] * np.sqrt(252) * 100

    ma200 = df.rolling(200).mean().iloc[-1]

    today_date = datetime.now().strftime("%d %b %Y")

    report = f"📊 VARISCO QUANT REPORT\n{today_date}\n\n"

    # MACRO
    report += "🌎 Macro\n"

    for asset in MACRO:
        if asset in today.index:
            price = today[asset]
            change = daily_return[asset]

            report += f"{asset} {price:.2f} ({change:+.2f}%)\n"

    report += "\n"

    # BRASIL
    report += "🇧🇷 Ações Brasil\n"

    for asset in BR_STOCKS:
        if asset in today.index:
            price = today[asset]
            change = daily_return[asset]

            report += f"{asset.replace('.SA','')} {price:.2f} ({change:+.2f}%)\n"

    report += "\n"

    # CRYPTO
    report += "🪙 Crypto\n"

    for asset in CRYPTO:
        if asset in today.index:
            price = today[asset]
            change = daily_return[asset]

            report += f"{asset.replace('-USD','')} {price:.2f} ({change:+.2f}%)\n"

    report += "\n"

    # TOP MOVERS
    report += "🔥 Maiores Altas\n"

    for asset in daily_return.sort_values(ascending=False).head(5).index:
        change = daily_return[asset]
        report += f"{asset.replace('.SA','')} {change:+.2f}%\n"

    report += "\n"

    report += "🔻 Maiores Quedas\n"

    for asset in daily_return.sort_values().head(5).index:
        change = daily_return[asset]
        report += f"{asset.replace('.SA','')} {change:+.2f}%\n"

    report += "\n"

    # VOLATILIDADE
    report += "⚡ Volatilidade 21d (anualizada)\n"

    for asset in vol.sort_values(ascending=False).head(5).index:
        report += f"{asset.replace('.SA','')} {vol[asset]:.2f}%\n"

    report += "\n"

    # TENDENCIA
    report += "📈 Tendência (MA200)\n"

    for asset in today.index:

        if asset in ma200.index:

            if today[asset] > ma200[asset]:

                report += f"{asset.replace('.SA','')} 🟢 acima MA200\n"

            else:

                report += f"{asset.replace('.SA','')} 🔴 abaixo MA200\n"

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
