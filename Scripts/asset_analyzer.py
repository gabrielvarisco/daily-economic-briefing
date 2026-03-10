import logging
import os
import time
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
import yfinance as yf


logger = logging.getLogger("asset_analyzer")


def _normalize_close(data: pd.DataFrame | pd.Series) -> pd.Series:
    """
    Normaliza o retorno do yfinance para uma série de fechamento.
    """
    if isinstance(data, pd.Series):
        close = data.dropna()
        close.name = "Close"
        return close

    if data.empty:
        return pd.Series(dtype=float, name="Close")

    if "Close" not in data.columns:
        return pd.Series(dtype=float, name="Close")

    close = data["Close"]

    if isinstance(close, pd.DataFrame):
        # caso raro em que o yfinance devolve um DataFrame com uma coluna
        if close.shape[1] == 0:
            return pd.Series(dtype=float, name="Close")
        close = close.iloc[:, 0]

    return close.dropna().astype(float)


def _safe_download(
    ticker: str,
    period: str = "1y",
    interval: str = "1d",
    auto_adjust: bool = True,
    retries: Optional[int] = None,
    pause: Optional[float] = None,
) -> pd.Series:
    """
    Faz download com retry simples e retorna a série de fechamento.
    """
    retries = retries if retries is not None else int(os.getenv("YF_RETRIES", "3"))
    pause = pause if pause is not None else float(os.getenv("YF_RETRY_PAUSE", "1.0"))
    timeout = float(os.getenv("YF_TIMEOUT", "15"))
    retries = max(1, retries)

    last_error = None

    for attempt in range(retries):
        try:
            data = yf.download(
                ticker,
                period=period,
                interval=interval,
                auto_adjust=auto_adjust,
                progress=False,
                threads=False,
                timeout=timeout,
            )

            close = _normalize_close(data)

            if not close.empty:
                return close

        except Exception as exc:
            last_error = exc
            err = str(exc).lower()

            if "connect tunnel failed" in err or "response 403" in err or "proxyerror" in err:
                logger.warning("network/proxy blocked ticker download", extra={"section": ticker, "status": "blocked"})
                break

        if attempt < retries - 1:
            time.sleep(pause)

    if last_error:
        logger.warning(f"erro ao baixar {ticker}: {last_error}")
    else:
        logger.info(f"sem dados para {ticker}")

    return pd.Series(dtype=float, name="Close")


def _pct_change(current: float, previous: float) -> Optional[float]:
    if previous is None or previous == 0 or pd.isna(previous):
        return None
    return ((current / previous) - 1.0) * 100.0


def _annualized_vol(close: pd.Series, window: int = 21) -> Optional[float]:
    if len(close) < window + 1:
        return None

    returns = close.pct_change().dropna()
    if returns.empty:
        return None

    rolling_vol = returns.rolling(window).std().dropna()
    if rolling_vol.empty:
        return None

    vol = rolling_vol.iloc[-1] * np.sqrt(252) * 100
    return float(vol)


def _ma_value(close: pd.Series, window: int) -> Optional[float]:
    if len(close) < window:
        return None

    ma = close.rolling(window).mean().dropna()
    if ma.empty:
        return None

    return float(ma.iloc[-1])


def _ma_status(price: float, ma_value: Optional[float]) -> str:
    if ma_value is None or pd.isna(ma_value):
        return "-"
    return "↑" if price > ma_value else "↓"


def _period_return(close: pd.Series, bars_back: int) -> Optional[float]:
    if len(close) <= bars_back:
        return None

    current = float(close.iloc[-1])
    previous = float(close.iloc[-(bars_back + 1)])
    return _pct_change(current, previous)


def _rolling_high_low(close: pd.Series, window: int) -> tuple[Optional[float], Optional[float]]:
    if len(close) < 2:
        return None, None

    recent = close.tail(window) if len(close) >= window else close
    if recent.empty:
        return None, None

    return float(recent.max()), float(recent.min())




def _quality_flags(result: Dict[str, Any]) -> List[str]:
    flags: List[str] = []
    max_daily_abs = float(os.getenv("MAX_DAILY_CHANGE_ABS", "20"))
    max_weekly_abs = float(os.getenv("MAX_WEEKLY_CHANGE_ABS", "40"))

    daily_change = result.get("daily_change")
    weekly_change = result.get("weekly_change")

    if daily_change is not None and abs(float(daily_change)) > max_daily_abs:
        flags.append("daily_change_outlier")

    if weekly_change is not None and abs(float(weekly_change)) > max_weekly_abs:
        flags.append("weekly_change_outlier")

    if result.get("high_52w") is not None and result.get("low_52w") is not None:
        if float(result["high_52w"]) < float(result["low_52w"]):
            flags.append("invalid_52w_range")

    return flags
def analyze_asset(
    ticker: str,
    period: str = "1y",
    interval: str = "1d",
    auto_adjust: bool = True,
    ma_windows: Optional[List[int]] = None,
    label: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Analisador genérico de ativo.
    Serve para ação BR, ação EUA, ETF, índice, dólar, commodity, etc.
    """
    if ma_windows is None:
        ma_windows = [20, 50, 200]

    close = _safe_download(
        ticker=ticker,
        period=period,
        interval=interval,
        auto_adjust=auto_adjust,
    )

    if close.empty or len(close) < 2:
        return None

    price = float(close.iloc[-1])
    prev = float(close.iloc[-2])

    ma_map: Dict[int, Optional[float]] = {}
    ma_status_map: Dict[int, str] = {}

    for window in ma_windows:
        value = _ma_value(close, window)
        ma_map[window] = value
        ma_status_map[window] = _ma_status(price, value)

    high_52w, low_52w = _rolling_high_low(close, 252)

    result: Dict[str, Any] = {
        "ticker": ticker,
        "label": label or ticker,
        "price": round(price, 2),
        "daily_change": _round_or_none(_pct_change(price, prev)),
        "weekly_change": _round_or_none(_period_return(close, 5)),
        "monthly_change": _round_or_none(_period_return(close, 21)),
        "vol_21d": _round_or_none(_annualized_vol(close, 21)),
        "high_52w": _round_or_none(high_52w),
        "low_52w": _round_or_none(low_52w),
        "close_len": int(len(close)),
    }

    for window in ma_windows:
        result[f"ma{window}"] = _round_or_none(ma_map[window])
        result[f"ma{window}_status"] = ma_status_map[window]

    quality_flags = _quality_flags(result)
    result["quality_flags"] = quality_flags
    result["is_suspect"] = len(quality_flags) > 0

    return result


def analyze_many_assets(
    tickers: List[str],
    period: str = "1y",
    interval: str = "1d",
    auto_adjust: bool = True,
    ma_windows: Optional[List[int]] = None,
) -> List[Dict[str, Any]]:
    """
    Analisa vários ativos em sequência.
    """
    results: List[Dict[str, Any]] = []

    for ticker in tickers:
        asset = analyze_asset(
            ticker=ticker,
            period=period,
            interval=interval,
            auto_adjust=auto_adjust,
            ma_windows=ma_windows,
        )
        if asset:
            results.append(asset)

    return results


def _round_or_none(value: Optional[float], digits: int = 2) -> Optional[float]:
    if value is None or pd.isna(value):
        return None
    return round(float(value), digits)
