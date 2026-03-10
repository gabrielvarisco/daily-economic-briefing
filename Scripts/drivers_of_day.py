from typing import Optional

from Scripts.asset_analyzer import analyze_asset


def _fmt_pct(value: Optional[float]) -> str:
    if value is None:
        return "-"
    return f"{value:+.2f}%"


def _fmt_level(value: Optional[float], digits: int = 2) -> str:
    if value is None:
        return "-"
    return f"{value:.{digits}f}"


def _get_asset(ticker: str, label: str) -> Optional[dict]:
    return analyze_asset(ticker=ticker, period="1y", interval="1d", label=label)


def _curve_signal(us2y: Optional[dict], us10y: Optional[dict]) -> str:
    if not us2y or not us10y:
        return "Curva: sem dados suficientes"

    two = us2y.get("price")
    ten = us10y.get("price")
    if two is None or ten is None:
        return "Curva: sem dados suficientes"

    spread = ten - two
    slope = "normal" if spread > 0 else "invertida"
    return f"Curva 2s10s: {spread:+.2f}pp ({slope})"


def drivers_of_day() -> str:
    us2y = _get_asset("^IRX", "US2Y proxy")
    us10y = _get_asset("^TNX", "US10Y")
    vix = _get_asset("^VIX", "VIX")
    dxy = _get_asset("DX-Y.NYB", "DXY")
    hyg = _get_asset("HYG", "High Yield")

    lines = ["🧭 <b>Drivers do Dia</b>"]
    lines.append(_curve_signal(us2y, us10y))

    if vix:
        lines.append(f"VIX: {_fmt_level(vix.get('price'))} ({_fmt_pct(vix.get('daily_change'))})")
    else:
        lines.append("VIX: -")

    if dxy:
        lines.append(f"DXY: {_fmt_level(dxy.get('price'))} ({_fmt_pct(dxy.get('daily_change'))})")
    else:
        lines.append("DXY: -")

    if hyg:
        lines.append(f"HYG: {_fmt_level(hyg.get('price'))} ({_fmt_pct(hyg.get('daily_change'))})")
    else:
        lines.append("HYG: -")

    return "\n".join(lines).strip()


if __name__ == "__main__":
    print(drivers_of_day())
