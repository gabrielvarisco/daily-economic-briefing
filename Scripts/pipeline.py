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


def get_section_specs() -> List[SectionSpec]:
    specs = [
        SectionSpec("market_take", "Market Take", market_take),
        SectionSpec("day_over_day", "Since Last Snapshot", day_over_day),
    ]

    if macro_global:
        specs.append(SectionSpec("macro", "Macro Global", macro_global))

    specs.extend(
        [
            SectionSpec("brazil", "Brazil Market", brazil_market),
            SectionSpec("usa", "USA Market", usa_market),
        ]
    )

    if crypto_market:
        specs.append(SectionSpec("crypto", "Crypto Market", crypto_market))

    specs.extend(
        [
            SectionSpec("quant", "Quant Summary", quant_summary),
            SectionSpec("news", "News Market", news_market),
        ]
    )

    return specs


def _safe_section(title: str, fn: SectionFn, run_id: Optional[str] = None) -> Tuple[str, Dict[str, object]]:
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
                {"status": "empty", "elapsed_ms": elapsed_ms},
            )

        logger.info(
            "section generated",
            extra={"run_id": run_id, "section": title, "status": "ok", "elapsed_ms": elapsed_ms},
        )
        return str(result).strip(), {"status": "ok", "elapsed_ms": elapsed_ms}

    except Exception as exc:
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        logger.exception(
            "section failed",
            extra={"run_id": run_id, "section": title, "status": "error", "elapsed_ms": elapsed_ms},
        )
        return (
            f"⚠️ <b>{title}</b>\nErro ao gerar esta seção.",
            {"status": "error", "elapsed_ms": elapsed_ms, "error": str(exc)},
        )


def build_sections(run_id: Optional[str] = None) -> Tuple[Dict[str, str], Dict[str, Dict[str, object]]]:
    structured_sections: Dict[str, str] = {}
    metrics: Dict[str, Dict[str, object]] = {}

    for spec in get_section_specs():
        content, metric = _safe_section(spec.title, spec.fn, run_id=run_id)
        structured_sections[spec.key] = content
        metrics[spec.key] = metric

    return structured_sections, metrics


def build_batches(structured_sections: Dict[str, str]) -> List[str]:
    batch_1_parts = [
        structured_sections["market_take"],
        structured_sections["day_over_day"],
    ]

    if "macro" in structured_sections:
        batch_1_parts.append(structured_sections["macro"])

    batch_1_parts.extend([structured_sections["brazil"], structured_sections["usa"]])

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
