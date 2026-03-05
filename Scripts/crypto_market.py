import requests

def crypto_market():

    url = "https://api.coingecko.com/api/v3/global"
    data = requests.get(url).json()

    market_cap = data["data"]["total_market_cap"]["usd"]
    btc_dominance = data["data"]["market_cap_percentage"]["btc"]

    btc = requests.get(
        "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_change=true"
    ).json()

    eth = requests.get(
        "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd&include_24hr_change=true"
    ).json()

    btc_price = btc["bitcoin"]["usd"]
    btc_change = btc["bitcoin"]["usd_24h_change"]

    eth_price = eth["ethereum"]["usd"]
    eth_change = eth["ethereum"]["usd_24h_change"]

    message = "₿ CRYPTO MARKET\n\n"

    btc_emoji = "🟢" if btc_change > 0 else "🔴"
    eth_emoji = "🟢" if eth_change > 0 else "🔴"

    message += f"BTC: ${btc_price:,.0f} ({btc_emoji} {btc_change:.2f}%)\n"
    message += f"ETH: ${eth_price:,.0f} ({eth_emoji} {eth_change:.2f}%)\n\n"

    message += f"BTC Dominance: {btc_dominance:.2f}%\n"
    message += f"Market Cap: ${market_cap/1e12:.2f}T\n"

    return message
