import yfinance as yf
import pandas as pd
import numpy as np

TICKERS = [
    "SPY",
    "QQQ",
    "TLT",
    "DX-Y.NYB"   # DXY
]


def market_regime():

    data = yf.download(
        TICKERS,
        period="6mo",
        interval="1d",
        auto_adjust=True,
        threads=True
    )

    df = data["Close"]

    today = df.iloc[-1]
    month = df.iloc[-21]

    returns = ((today / month) - 1) * 100

    spy = returns["SPY"]
    qqq = returns["QQQ"]
    tlt = returns["TLT"]
    dxy = returns["DX-Y.NYB"]

    report = "🧠 MARKET REGIME\n\n"

    report += f"SPY 1M: {spy:.2f}%\n"
    report += f"QQQ 1M: {qqq:.2f}%\n"
    report += f"TLT 1M: {tlt:.2f}%\n"
    report += f"DXY 1M: {dxy:.2f}%\n\n"

    # regime logic

    if spy > 0 and qqq > 0 and tlt < 0:
        regime = "🔥 RISK ON"

    elif spy < 0 and qqq < 0 and tlt > 0:
        regime = "⚠️ RISK OFF"

    elif dxy > 2 and spy < 0:
        regime = "🌪 DOLLAR STRESS"

    else:
        regime = "⚖️ NEUTRAL"

    report += f"Regime: {regime}"

    return report
