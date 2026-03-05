import yfinance as yf

def get_price(symbol):
    try:
        data = yf.Ticker(symbol)
        hist = data.history(period="2d")

        price = hist["Close"].iloc[-1]
        prev = hist["Close"].iloc[-2]

        change = ((price - prev) / prev) * 100

        return price, change
    except:
        return None, None


def macro_global():

    assets = {
        "Dollar Index (DXY)": "DX-Y.NYB",
        "US 10Y Yield": "^TNX",
        "S&P500 Futures": "ES=F",
        "VIX": "^VIX",
        "Gold": "GC=F",
        "Oil (WTI)": "CL=F",
        "Iron Ore": "TIO=F"
    }

    message = "🌍 MACRO GLOBAL\n\n"

    for name, symbol in assets.items():

        price, change = get_price(symbol)

        if price is None:
            message += f"{name}: erro\n"
            continue

        emoji = "🟢" if change > 0 else "🔴"

        message += f"{name}: {price:.2f} ({emoji} {change:.2f}%)\n"

    return message
