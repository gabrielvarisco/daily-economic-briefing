import os
import sys
from typing import Dict, List, Optional

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from Scripts.asset_analyzer import analyze_asset
from tickers.brazil_stocks import BRAZIL_TICKERS, BRAZIL_INDEX, BRAZIL_DOLLAR
from tickers.usa_stocks import (
    USA_INDEX_TICKERS,
    USA_SECTOR_TICKERS,
    USA_STOCK_TICKERS,
    USA_MACRO_TICKERS,
)


CRYPTO_PROXY_TICKERS = [
    "BTC-USD",
    "ETH-USD",
    "SOL-USD",
]

LABELS = {
    BRAZIL_INDEX: "IBOV",
    BRAZIL_DOLLAR: "USDBRL",
    "SPY": "S&P500",
    "QQQ": "Nasdaq",
    "DIA": "Dow",
    "IWM": "Russell",
    "XLK": "Tech",
    "XLF": "Financials",
    "XLE": "Energy",
    "XLV": "Health",
    "^VIX": "VIX",
    "TLT": "Treasuries",
    "DX-Y.NYB": "DXY",
    "^TNX": "US10Y",
    "BTC-USD": "BTC",
    "ETH-USD": "ETH",
    "SOL-USD": "SOL",
}

EXCLUDED_FROM_GAINERS_LOSERS = {
    "^VIX",   # distorce bastante a leitura
}

EXCLUDED_FROM_BREADTH = {
    "^VIX",      # não é ativo de risco tradicional
    "^TNX",      # yield
    "DX-Y.NYB",  # dollar index
    BRAZIL_DOLLAR,
}


def _fmt(value: Optional[float], digits: int = 2) -> str:
    if value is None:
        return "-"
    return f"{value:.{digits}f}"


def _collect_universe() -> List[str]:
    universe: List[str] = []

    universe.extend([BRAZIL_INDEX, BRAZIL_DOLLAR])
    universe.extend(BRAZIL_TICKERS)
    universe.extend(USA_INDEX_TICKERS)
    universe.extend(USA_SECTOR_TICKERS)
    universe.extend(USA_STOCK_TICKERS)
    universe.extend(USA_MACRO_TICKERS)
    universe.extend(CRYPTO_PROXY_TICKERS)

    deduped = []
    seen = set()

    for ticker in universe:
        if ticker in seen:
            continue
        seen.add(ticker)
        deduped.append(ticker)

    return deduped


def _classify_asset(ticker: str) -> str:
    if ticker in BRAZIL_TICKERS or ticker in {BRAZIL_INDEX, BRAZIL_DOLLAR}:
        return "Brazil"

    if ticker in USA_INDEX_TICKERS:
        return "USA Index"

    if ticker in USA_SECTOR_TICKERS:
        return "USA Sector"

    if ticker in USA_STOCK_TICKERS:
        return "USA Stock"

    if ticker in USA_MACRO_TICKERS:
        return "Macro"

    if ticker in CRYPTO_PROXY_TICKERS:
        return "Crypto"

    return "Other"


def _analyze_universe() -> List[Dict]:
    results = []

    for ticker in _collect_universe():
        asset = analyze_asset(
            ticker=ticker,
            period="1y",
            interval="1d",
            label=LABELS.get(ticker, ticker.replace(".SA", "")),
        )

        if not asset:
            continue

        asset["asset_class"] = _classify_asset(ticker)
        results.append(asset)

    return results


def _sort_assets(
    assets: List[Dict],
    metric: str,
    reverse: bool = True,
) -> List[Dict]:
    filtered = [a for a in assets if a.get(metric) is not None]

    return sorted(
        filtered,
        key=lambda x: x.get(metric, float("-inf") if reverse else float("inf")),
        reverse=reverse,
    )


def _positive_gainers(assets: List[Dict], top_n: int = 5) -> List[Dict]:
    filtered = [
        a for a in assets
        if a.get("daily_change") is not None
        and a["daily_change"] > 0
        and a.get("ticker") not in EXCLUDED_FROM_GAINERS_LOSERS
    ]
    return _sort_assets(filtered, "daily_change", reverse=True)[:top_n]


def _negative_losers(assets: List[Dict], top_n: int = 5) -> List[Dict]:
    filtered = [
        a for a in assets
        if a.get("daily_change") is not None
        and a["daily_change"] < 0
        and a.get("ticker") not in EXCLUDED_FROM_GAINERS_LOSERS
    ]
    return _sort_assets(filtered, "daily_change", reverse=False)[:top_n]


def _positive_weekly_momentum(assets: List[Dict], top_n: int = 5) -> List[Dict]:
    filtered = [
        a for a in assets
        if a.get("weekly_change") is not None
        and a["weekly_change"] > 0
        and a.get("ticker") not in EXCLUDED_FROM_GAINERS_LOSERS
    ]
    return _sort_assets(filtered, "weekly_change", reverse=True)[:top_n]


def _top_volatility(assets: List[Dict], top_n: int = 5) -> List[Dict]:
    filtered = [
        a for a in assets
        if a.get("vol_21d") is not None
    ]
    return _sort_assets(filtered, "vol_21d", reverse=True)[:top_n]


def _breadth_summary(assets: List[Dict]) -> Dict[str, str]:
    valid_assets = [
        a for a in assets
        if a.get("daily_change") is not None
        and a.get("ticker") not in EXCLUDED_FROM_BREADTH
    ]

    if not valid_assets:
        return {
            "up_down": "-",
            "mm20": "-",
            "mm50": "-",
            "risk_regime": "Indefinido",
        }

    up_count = sum(1 for a in valid_assets if a["daily_change"] > 0)
    down_count = sum(1 for a in valid_assets if a["daily_change"] < 0)

    mm20_up = sum(1 for a in valid_assets if a.get("ma20_status") == "↑")
    mm50_up = sum(1 for a in valid_assets if a.get("ma50_status") == "↑")

    total = len(valid_assets)

    mm20_pct = (mm20_up / total) * 100 if total else 0
    mm50_pct = (mm50_up / total) * 100 if total else 0

    risk_regime = "Neutro"
    if mm20_pct >= 65 and mm50_pct >= 60:
        risk_regime = "Risk-on"
    elif mm20_pct <= 35 and mm50_pct <= 40:
        risk_regime = "Risk-off"

    return {
        "up_down": f"{up_count}/{down_count}",
        "mm20": f"{mm20_up}/{total}",
        "mm50": f"{mm50_up}/{total}",
        "risk_regime": risk_regime,
    }


def _format_asset_line(asset: Dict, metric: str) -> str:
    return f"{asset['label']} {_fmt(asset.get(metric))}% [{asset['asset_class']}]"


def quant_summary() -> str:
    assets = _analyze_universe()

    if not assets:
        return "📈 <b>Quant Summary</b>\n\nSem dados disponíveis."

    gainers = _positive_gainers(assets, top_n=5)
    losers = _negative_losers(assets, top_n=5)
    momentum = _positive_weekly_momentum(assets, top_n=5)
    volatility = _top_volatility(assets, top_n=5)
    breadth = _breadth_summary(assets)

    report = "📈 <b>Quant Summary</b>\n\n"

    report += "<b>Breadth & Regime</b>\n"
    report += f"Up/Down: {breadth['up_down']}\n"
    report += f"Acima MM20: {breadth['mm20']}\n"
    report += f"Acima MM50: {breadth['mm50']}\n"
    report += f"Regime: {breadth['risk_regime']}\n\n"

    report += "<b>Leaders</b>\n"
    if gainers:
        for asset in gainers:
            report += _format_asset_line(asset, "daily_change") + "\n"
    else:
        report += "Sem gainers relevantes hoje.\n"

    report += "\n<b>Laggards</b>\n"
    if losers:
        for asset in losers:
            report += _format_asset_line(asset, "daily_change") + "\n"
    else:
        report += "Sem losers relevantes hoje.\n"

    report += "\n<b>Weekly Momentum</b>\n"
    if momentum:
        for asset in momentum:
            report += _format_asset_line(asset, "weekly_change") + "\n"
    else:
        report += "Sem momentum positivo relevante na semana.\n"

    report += "\n<b>Volatility Watch</b>\n"
    if volatility:
        for asset in volatility:
            report += _format_asset_line(asset, "vol_21d") + "\n"
    else:
        report += "Sem dados de volatilidade.\n"

    return report.strip()


if __name__ == "__main__":
    print("Starting Quant Summary script")
    print(quant_summary())
