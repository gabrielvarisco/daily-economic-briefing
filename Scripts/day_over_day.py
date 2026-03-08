import re
from typing import Optional

from Scripts.history_store import load_previous_day_snapshot
from Scripts.market_take import market_take
from Scripts.quant_summary import quant_summary


def _extract_regime(text: str) -> Optional[str]:
    match = re.search(r"Regime:\s*<b>(.*?)</b>", text or "")
    if match:
        return match.group(1).strip()
    return None


def _extract_metric_value(text: str, label: str) -> Optional[str]:
    """
    Extrai métricas em formato de linha única, por exemplo:
    Up/Down: 3/27
    Acima MM20: 7/30
    Acima MM50: 9/30
    Regime: Risk-off
    """
    pattern = rf"{re.escape(label)}:\s*(.+)"
    match = re.search(pattern, text or "")
    if not match:
        return None

    value = match.group(1).strip()
    value = value.split("\n")[0].strip()
    return value if value else None


def _compare_text(current: Optional[str], previous: Optional[str], label: str) -> str:
    if not current and not previous:
        return f"{label}: sem histórico comparável."
    if current and not previous:
        return f"{label}: sem base anterior."
    if not current and previous:
        return f"{label}: leitura atual indisponível."
    if current == previous:
        return f"{label}: sem mudança relevante ({current})."
    return f"{label}: {previous} → {current}"


def day_over_day() -> str:
    previous_snapshot = load_previous_day_snapshot()

    report = "📌 <b>Since Last Snapshot</b>\n\n"

    if not previous_snapshot:
        report += "Sem snapshot anterior para comparação."
        return report

    previous_data = previous_snapshot.get("data", {})

    current_market_take = market_take()
    current_quant = quant_summary()

    prev_market_take = previous_data.get("market_take", "")
    prev_quant = previous_data.get("quant", "")

    current_regime = _extract_regime(current_market_take)
    prev_regime = _extract_regime(prev_market_take)

    current_up_down = _extract_metric_value(current_quant, "Up/Down")
    prev_up_down = _extract_metric_value(prev_quant, "Up/Down")

    current_mm20 = _extract_metric_value(current_quant, "Acima MM20")
    prev_mm20 = _extract_metric_value(prev_quant, "Acima MM20")

    current_mm50 = _extract_metric_value(current_quant, "Acima MM50")
    prev_mm50 = _extract_metric_value(prev_quant, "Acima MM50")

    report += _compare_text(current_regime, prev_regime, "Regime") + "\n"
    report += _compare_text(current_up_down, prev_up_down, "Up/Down") + "\n"
    report += _compare_text(current_mm20, prev_mm20, "Acima MM20") + "\n"
    report += _compare_text(current_mm50, prev_mm50, "Acima MM50") + "\n"

    return report.strip()


if __name__ == "__main__":
    print("Starting Day-over-Day script")
    print(day_over_day())
