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
    "BTC-USD": "BTC",
    "ETH-USD": "ETH",
    "SOL-USD": "SOL",
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


def _analyze_universe() -> List[Dict]:
    results = []

    for ticker in _collect_universe():
        asset = analyze_asset(
            ticker=ticker,
            period="1y",
            interval="1d",
            label=LABELS.get(ticker, ticker.replace(".SA", "")),
        )

        if asset:
            results.append(asset)

    return results


def _top_by_metric(
    assets: List[Dict],
    metric: str,
    top_n: int = 5,
    reverse: bool = True,
    exclude_missing: bool = True,
) -> List[Dict]:
    filtered = assets

    if exclude_missing:
        filtered = [a for a in assets if a.get(metric) is not None]

    return sorted(
        filtered,
        key=lambda x: x.get(metric, float("-inf") if reverse else float("inf")),
        reverse=reverse,
    )[:top_n]


def _breadth_summary(assets: List[Dict]) -> Dict[str, str]:
    valid_assets = [a for a in assets if a.get("daily_change") is not None]

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


def quant_summary() -> str:
    assets = _analyze_universe()

    if not assets:
        return "📈 <b>Quant Summary</b>\n\nSem dados disponíveis."

    top_gainers = _top_by_metric(assets, "daily_change", top_n=5, reverse=True)
    top_losers = _top_by_metric(assets, "daily_change", top_n=5, reverse=False)
    top_vol = _top_by_metric(assets, "vol_21d", top_n=5, reverse=True)
    top_week = _top_by_metric(assets, "weekly_change", top_n=5, reverse=True)

    breadth = _breadth_summary(assets)

    report = "📈 <b>Quant Summary</b>\n\n"

    report += "<b>Market Breadth</b>\n"
    report += f"Up/Down: {breadth['up_down']}\n"
    report += f"Acima MM20: {breadth['mm20']}\n"
    report += f"Acima MM50: {breadth['mm50']}\n"
    report += f"Regime: {breadth['risk_regime']}\n\n"

    report += "<b>Top Gainers (Dia)</b>\n"
    for asset in top_gainers:
        report += f"{asset['label']} {_fmt(asset['daily_change'])}%\n"

    report += "\n<b>Top Losers (Dia)</b>\n"
    for asset in top_losers:
        report += f"{asset['label']} {_fmt(asset['daily_change'])}%\n"

    report += "\n<b>Top Momentum (Semana)</b>\n"
    for asset in top_week:
        report += f"{asset['label']} {_fmt(asset['weekly_change'])}%\n"

    report += "\n<b>Top Volatilidade 21d</b>\n"
    for asset in top_vol:
        report += f"{asset['label']} {_fmt(asset['vol_21d'])}%\n"

    return report.strip()


if __name__ == "__main__":
    print("Starting Quant Summary script")
    print(quant_summary())
