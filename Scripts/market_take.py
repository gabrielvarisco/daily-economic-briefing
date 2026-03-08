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


def _risk_regime(spy: Optional[dict], vix: Optional[dict], btc: Optional[dict]) -> str:
    score = 0

    if spy:
        if (spy.get("daily_change") or 0) > 0:
            score += 1
        if spy.get("ma20_status") == "↑":
            score += 1

    if btc:
        if (btc.get("daily_change") or 0) > 0:
            score += 1
        if btc.get("ma20_status") == "↑":
            score += 1

    if vix:
        if (vix.get("daily_change") or 0) > 0:
            score -= 2
        if vix.get("ma20_status") == "↑":
            score -= 1

    if score >= 2:
        return "Risk-on"
    if score <= -1:
        return "Risk-off"
    return "Neutro"


def _session_tone(spy: Optional[dict], qqq: Optional[dict], vix: Optional[dict], btc: Optional[dict]) -> str:
    spy_chg = spy.get("daily_change") if spy else None
    qqq_chg = qqq.get("daily_change") if qqq else None
    vix_chg = vix.get("daily_change") if vix else None
    btc_chg = btc.get("daily_change") if btc else None

    if (
        spy_chg is not None and spy_chg < -0.8
        and qqq_chg is not None and qqq_chg < -1.0
        and vix_chg is not None and vix_chg > 5
    ):
        return "Sessão clara de aversão a risco, com pressão forte sobre equities americanas e aumento de volatilidade."

    if (
        spy_chg is not None and spy_chg > 0.6
        and qqq_chg is not None and qqq_chg > 0.8
        and vix_chg is not None and vix_chg < 0
    ):
        return "Sessão de apetite por risco, com ações americanas firmes e volatilidade cedendo."

    if (
        btc_chg is not None and abs(btc_chg) > 2
        and spy_chg is not None and abs(spy_chg) < 0.5
    ):
        return "Crypto lidera a direção do dia, enquanto equities americanas mostram comportamento mais contido."

    return "Mercado em sessão mista, com sinais cruzados entre ações, volatilidade e cripto."


def _brazil_take(ibov: Optional[dict], usdb: Optional[dict]) -> str:
    if not ibov and not usdb:
        return "No Brasil, sem leitura clara disponível."

    ibov_chg = ibov.get("daily_change") if ibov else None
    usdb_chg = usdb.get("daily_change") if usdb else None

    if ibov_chg is not None and usdb_chg is not None:
        if ibov_chg < 0 and usdb_chg > 0:
            return (
                f"No Brasil, o IBOV cai {_fmt(abs(ibov_chg))}% enquanto o dólar sobe {_fmt(usdb_chg)}%, "
                f"um desenho típico de maior cautela local."
            )
        if ibov_chg > 0 and usdb_chg < 0:
            return (
                f"No Brasil, o IBOV avança {_fmt(ibov_chg)}% com dólar em queda de {_fmt(abs(usdb_chg))}%, "
                f"sinal de ambiente mais construtivo para ativos domésticos."
            )

    if ibov_chg is not None:
        direction = "avança" if ibov_chg > 0 else "recua" if ibov_chg < 0 else "fica estável"
        return f"No Brasil, o IBOV {direction} {_fmt(abs(ibov_chg))}%."

    return f"No Brasil, o dólar está em {_fmt(usdb_chg)}% no dia."


def _macro_take(dxy: Optional[dict], tnx: Optional[dict], vix: Optional[dict]) -> str:
    parts = []

    if dxy and dxy.get("daily_change") is not None:
        dxy_chg = dxy["daily_change"]
        if dxy_chg > 0:
            parts.append(f"DXY em alta de {_fmt(dxy_chg)}%")
        elif dxy_chg < 0:
            parts.append(f"DXY em queda de {_fmt(abs(dxy_chg))}%")

    if tnx and tnx.get("daily_change") is not None:
        tnx_chg = tnx["daily_change"]
        if tnx_chg > 0:
            parts.append(f"US10Y sobe {_fmt(tnx_chg)}%")
        elif tnx_chg < 0:
            parts.append(f"US10Y recua {_fmt(abs(tnx_chg))}%")

    if vix and vix.get("daily_change") is not None:
        vix_chg = vix["daily_change"]
        if vix_chg > 0:
            parts.append(f"VIX sobe {_fmt(vix_chg)}%")
        elif vix_chg < 0:
            parts.append(f"VIX cede {_fmt(abs(vix_chg))}%")

    if not parts:
        return "Macro sem sinais fortes no momento."

    return "Macro: " + " | ".join(parts) + "."


def _tactical_take(spy: Optional[dict], btc: Optional[dict], vix: Optional[dict]) -> str:
    parts = []

    if spy:
        parts.append("S&P acima da MM20" if spy.get("ma20_status") == "↑" else "S&P abaixo da MM20")

    if btc:
        parts.append("BTC acima da MM20" if btc.get("ma20_status") == "↑" else "BTC abaixo da MM20")

    if vix and vix.get("ma20_status") == "↑":
        parts.append("VIX acima da MM20")

    if not parts:
        return "Leitura tática indisponível."

    return "Leitura tática: " + " | ".join(parts) + "."


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
    tone = _session_tone(spy, qqq, vix, btc)
    brazil = _brazil_take(ibov, usdb)
    macro = _macro_take(dxy, tnx, vix)
    tactical = _tactical_take(spy, btc, vix)

    report = "🧠 <b>Market Take</b>\n\n"
    report += f"Regime: <b>{regime}</b>\n\n"
    report += f"{tone}\n\n"
    report += f"{brazil}\n\n"
    report += f"{macro}\n\n"
    report += tactical

    return report.strip()


if __name__ == "__main__":
    print("Starting Market Take script")
    print(market_take())
