import os
import sys
from typing import Optional

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from Scripts.asset_analyzer import analyze_asset
from tickers.brazil_stocks import BRAZIL_INDEX, BRAZIL_DOLLAR


def _fmt(value: Optional[float], digits: int = 2) -> str:
    if value is None:
        return "-"
    return f"{value:.{digits}f}"


def _get_asset(ticker: str, label: str, period: str = "1y") -> Optional[dict]:
    return analyze_asset(
        ticker=ticker,
        period=period,
        interval="1d",
        label=label,
    )


def _direction_word(value: Optional[float]) -> str:
    if value is None:
        return "estável"
    if value > 0:
        return "alta"
    if value < 0:
        return "queda"
    return "estável"


def _risk_regime(spy: Optional[dict], vix: Optional[dict], btc: Optional[dict]) -> str:
    score = 0

    if spy:
        if spy.get("daily_change", 0) > 0:
            score += 1
        if spy.get("ma20_status") == "↑":
            score += 1

    if btc:
        if btc.get("daily_change", 0) > 0:
            score += 1
        if btc.get("ma20_status") == "↑":
            score += 1

    if vix:
        if vix.get("daily_change", 0) > 0:
            score -= 2
        if vix.get("ma20_status") == "↑":
            score -= 1

    if score >= 2:
        return "Risk-on"
    if score <= -1:
        return "Risk-off"
    return "Neutro"


def market_take() -> str:
    spy = _get_asset("SPY", "S&P 500")
    qqq = _get_asset("QQQ", "Nasdaq")
    vix = _get_asset("^VIX", "VIX")
    btc = _get_asset("BTC-USD", "BTC")
    ibov = _get_asset(BRAZIL_INDEX, "IBOV")
    usdb = _get_asset(BRAZIL_DOLLAR, "USDBRL")
    tnx = _get_asset("^TNX", "US10Y")
    dxy = _get_asset("DX-Y.NYB", "DXY")

    regime = _risk_regime(spy, vix, btc)

    lines = ["🧠 <b>Market Take</b>\n"]

    lines.append(f"Regime: <b>{regime}</b>")

    summary_parts = []

    if spy and qqq:
        summary_parts.append(
            f"EUA em {_direction_word(spy.get('daily_change'))}, "
            f"com S&P 500 {_fmt(spy.get('daily_change'))}% e Nasdaq {_fmt(qqq.get('daily_change'))}%"
        )

    if vix:
        summary_parts.append(
            f"VIX em {_direction_word(vix.get('daily_change'))} "
            f"({_fmt(vix.get('daily_change'))}%)"
        )

    if btc:
        summary_parts.append(
            f"BTC em {_direction_word(btc.get('daily_change'))} "
            f"({_fmt(btc.get('daily_change'))}%)"
        )

    if ibov:
        summary_parts.append(
            f"IBOV em {_direction_word(ibov.get('daily_change'))} "
            f"({_fmt(ibov.get('daily_change'))}%)"
        )

    if usdb:
        summary_parts.append(
            f"USDBRL em {_direction_word(usdb.get('daily_change'))} "
            f"({_fmt(usdb.get('daily_change'))}%)"
        )

    if summary_parts:
        lines.append("")
        lines.append(" • ".join(summary_parts) + ".")

    macro_parts = []

    if dxy:
        macro_parts.append(f"DXY {_fmt(dxy.get('daily_change'))}%")
    if tnx:
        macro_parts.append(f"US10Y {_fmt(tnx.get('daily_change'))}%")

    if macro_parts:
        lines.append("")
        lines.append("Macro: " + " | ".join(macro_parts))

    tactical = []

    if spy and spy.get("ma20_status") == "↑":
        tactical.append("S&P acima da MM20")
    elif spy:
        tactical.append("S&P abaixo da MM20")

    if btc and btc.get("ma20_status") == "↑":
        tactical.append("BTC acima da MM20")
    elif btc:
        tactical.append("BTC abaixo da MM20")

    if vix and vix.get("ma20_status") == "↑":
        tactical.append("VIX acima da MM20")

    if tactical:
        lines.append("")
        lines.append("Leitura tática: " + " | ".join(tactical))

    return "\n".join(lines).strip()


if __name__ == "__main__":
    print("Starting Market Take script")
    print(market_take())
