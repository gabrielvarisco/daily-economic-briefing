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

    df = data["Close"]

    # remove ativos sem dados
    df = df.dropna(axis=1, how="all")

    return df


def build_analysis(df):

    today = df.iloc[-1]
    yesterday = df.iloc[-2]

    daily_return = ((today / yesterday) - 1) * 100

    weekly_return = pd.Series(index=df.columns, dtype=float)

    if len(df) > 6:
        weekly_return = ((today / df.iloc[-6]) - 1) * 100

    vol = df.pct_change().rolling(21).std() * np.sqrt(252) * 100
    vol = vol.iloc[-1]

    report = "📊 VARISCO QUANT REPORT\n\n"

    report += "🌎 MERCADO\n\n"

    for asset in df.columns:

        price = today.get(asset, np.nan)
        d_ret = daily_return.get(asset, np.nan)
        w_ret = weekly_return.get(asset, np.nan)
        v = vol.get(asset, np.nan)

        report += f"{asset}\n"

        report += f"Preço: {price:.2f}\n" if not np.isnan(price) else "Preço: -\n"
        report += f"Dia: {d_ret:.2f}%\n" if not np.isnan(d_ret) else "Dia: -\n"
        report += f"Semana: {w_ret:.2f}%\n" if not np.isnan(w_ret) else "Semana: -\n"
        report += f"Vol 21d: {v:.2f}%\n\n" if not np.isnan(v) else "Vol 21d: -\n\n"

    report += "🔥 MAIORES ALTAS DO DIA\n"

    for asset in daily_return.sort_values(ascending=False).head(5).index:
        report += f"{asset}: {daily_return[asset]:.2f}%\n"

    report += "\n🔻 MAIORES QUEDAS DO DIA\n"

    for asset in daily_return.sort_values().head(5).index:
        report += f"{asset}: {daily_return[asset]:.2f}%\n"

    report += "\n⚡ MAIOR VOLATILIDADE (21d)\n"

    vol_clean = vol.dropna()

    for asset in vol_clean.sort_values(ascending=False).head(5).index:
        report += f"{asset}: {vol_clean[asset]:.2f}%\n"

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
