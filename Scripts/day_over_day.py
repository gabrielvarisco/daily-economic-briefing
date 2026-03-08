from typing import Optional

from Scripts.history_store import load_previous_day_snapshot
from Scripts.market_take import market_take
from Scripts.quant_summary import quant_summary


def _extract_regime(text: str) -> Optional[str]:
    marker = "Regime: <b>"
    if marker not in text:
        return None

    start = text.find(marker) + len(marker)
    end = text.find("</b>", start)

    if end == -1:
        return None

    return text[start:end].strip()


def _extract_line_after(header: str, text: str) -> Optional[str]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    for idx, line in enumerate(lines):
        if line == header and idx + 1 < len(lines):
            return lines[idx + 1]

    return None


def _compare_text(current: Optional[str], previous: Optional[str], label: str) -> str:
    if not current and not previous:
        return f"{label}: sem histórico comparável."
    if current and not previous:
        return f"{label}: sem base anterior."
    if current == previous:
        return f"{label}: sem mudança relevante."
    return f"{label}: {previous or '-'} → {current or '-'}"


def day_over_day() -> str:
    previous_snapshot = load_previous_day_snapshot()

    report = "📌 <b>Since Last Snapshot</b>\n\n"

    if not previous_snapshot:
        report += "Sem snapshot anterior para comparação."
        return report

    previous_data = previous_snapshot.get("data", {})

    current_market_take = market_take()
    current_quant = quant_summary()

    prev_market_take = previous_data.get("market_take")
    prev_quant = previous_data.get("quant")

    current_regime = _extract_regime(current_market_take)
    prev_regime = _extract_regime(prev_market_take or "")

    current_up_down = _extract_line_after("Up/Down:", current_quant)
    prev_up_down = _extract_line_after("Up/Down:", prev_quant or "")

    current_mm20 = _extract_line_after("Acima MM20:", current_quant)
    prev_mm20 = _extract_line_after("Acima MM20:", prev_quant or "")

    current_mm50 = _extract_line_after("Acima MM50:", current_quant)
    prev_mm50 = _extract_line_after("Acima MM50:", prev_quant or "")

    report += _compare_text(current_regime, prev_regime, "Regime") + "\n"
    report += _compare_text(current_up_down, prev_up_down, "Up/Down") + "\n"
    report += _compare_text(current_mm20, prev_mm20, "Acima MM20") + "\n"
    report += _compare_text(current_mm50, prev_mm50, "Acima MM50") + "\n"

    return report.strip()


if __name__ == "__main__":
    print("Starting Day-over-Day script")
    print(day_over_day())
