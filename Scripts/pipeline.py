import logging
import time
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple

from Scripts.day_over_day import day_over_day
from Scripts.market_take import market_take
from Scripts.brazil_market import brazil_market
from Scripts.usa_market import usa_market
from Scripts.news_market import news_market
from Scripts.quant_summary import quant_summary
from Scripts.drivers_of_day import drivers_of_day

try:
    from Scripts.crypto_market import crypto_market
except ImportError:
    crypto_market = None

try:
    from Scripts.macro_global import macro_global
except ImportError:
    macro_global = None


SectionFn = Callable[[], str]
logger = logging.getLogger("pipeline")


@dataclass
class SectionSpec:
    key: str
    title: str
    fn: SectionFn
    source: str


def get_section_specs() -> List[SectionSpec]:
    specs = [
        SectionSpec("market_take", "Market Take", market_take, "internal"),
        SectionSpec("day_over_day", "Since Last Snapshot", day_over_day, "snapshot"),
    ]

    if macro_global:
        specs.append(SectionSpec("macro", "Macro Global", macro_global, "yfinance"))

    specs.extend(
        [
            SectionSpec("brazil", "Brazil Market", brazil_market, "yfinance"),
            SectionSpec("usa", "USA Market", usa_market, "yfinance"),
        ]
    )

    if crypto_market:
        specs.append(SectionSpec("crypto", "Crypto Market", crypto_market, "yfinance"))

    specs.extend(
        [
            SectionSpec("drivers", "Drivers do Dia", drivers_of_day, "yfinance"),
            SectionSpec("quant", "Quant Summary", quant_summary, "yfinance"),
            SectionSpec("news", "News Market", news_market, "rss"),
        ]
    )

    return specs


def _safe_section(title: str, fn: SectionFn, source: str, run_id: Optional[str] = None) -> Tuple[str, Dict[str, object]]:
    start = time.perf_counter()
    try:
        result = fn()
        elapsed_ms = int((time.perf_counter() - start) * 1000)

        if not result or not str(result).strip():
            logger.warning(
                "section empty",
                extra={"run_id": run_id, "section": title, "status": "empty", "elapsed_ms": elapsed_ms},
            )
            return (
                f"⚠️ <b>{title}</b>\nSem dados disponíveis.",
                {"status": "empty", "elapsed_ms": elapsed_ms, "source": source},
            )

        logger.info(
            "section generated",
            extra={"run_id": run_id, "section": title, "status": "ok", "elapsed_ms": elapsed_ms},
        )
        return str(result).strip(), {"status": "ok", "elapsed_ms": elapsed_ms, "source": source}

    except Exception as exc:
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        logger.exception(
            "section failed",
            extra={"run_id": run_id, "section": title, "status": "error", "elapsed_ms": elapsed_ms},
        )
        return (
            f"⚠️ <b>{title}</b>\nErro ao gerar esta seção.",
            {"status": "error", "elapsed_ms": elapsed_ms, "error": str(exc), "source": source},
        )


def build_sections(run_id: Optional[str] = None) -> Tuple[Dict[str, str], Dict[str, Dict[str, object]]]:
    structured_sections: Dict[str, str] = {}
    metrics: Dict[str, Dict[str, object]] = {}

    for spec in get_section_specs():
        content, metric = _safe_section(spec.title, spec.fn, source=spec.source, run_id=run_id)
        structured_sections[spec.key] = content
        metrics[spec.key] = metric

    return structured_sections, metrics


def build_health_report(metrics: Dict[str, Dict[str, object]]) -> Dict[str, object]:
    status_count = {"ok": 0, "empty": 0, "error": 0}
    elapsed_total = 0
    degraded_sections: List[str] = []

    for section, data in metrics.items():
        status = str(data.get("status", "error"))
        elapsed = int(data.get("elapsed_ms", 0) or 0)
        elapsed_total += elapsed

        if status in status_count:
            status_count[status] += 1
        else:
            status_count["error"] += 1

        if status in {"empty", "error"}:
            degraded_sections.append(section)

    return {
        "ok_sections": status_count["ok"],
        "empty_sections": status_count["empty"],
        "error_sections": status_count["error"],
        "elapsed_total_ms": elapsed_total,
        "degraded_sections": degraded_sections,
    }


def build_batches(structured_sections: Dict[str, str]) -> List[str]:
    batch_1_parts = [
        structured_sections["market_take"],
        structured_sections["day_over_day"],
    ]

    if "macro" in structured_sections:
        batch_1_parts.append(structured_sections["macro"])

    batch_1_parts.extend([structured_sections["brazil"], structured_sections["usa"]])

    if "drivers" in structured_sections:
        batch_1_parts.append(structured_sections["drivers"])

    batch_2_parts = []
    if "crypto" in structured_sections:
        batch_2_parts.append(structured_sections["crypto"])
    batch_2_parts.append(structured_sections["quant"])

    batch_3_parts = [structured_sections["news"]]

    return [
        "\n\n".join(batch_1_parts).strip(),
        "\n\n".join(batch_2_parts).strip(),
        "\n\n".join(batch_3_parts).strip(),
    ]
