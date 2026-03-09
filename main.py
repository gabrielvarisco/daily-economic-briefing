import os
from typing import Callable, List, Tuple

import requests

from Scripts.market_take import market_take
from Scripts.day_over_day import day_over_day
from Scripts.brazil_market import brazil_market
from Scripts.usa_market import usa_market
from Scripts.news_market import news_market
from Scripts.history_store import save_daily_snapshot
from Scripts.quant_summary import quant_summary
from Scripts.html_report import generate_html_report

try:
    from Scripts.crypto_market import crypto_market
except ImportError:
    crypto_market = None

try:
    from Scripts.macro_global import macro_global
except ImportError:
    macro_global = None


SectionFn = Callable[[], str]


def send_telegram(message: str) -> None:
    token = os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("CHAT_ID")

    if not token or not chat_id:
        print("[main] TELEGRAM_TOKEN ou CHAT_ID não configurados.")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }

    try:
        response = requests.post(url, json=payload, timeout=20)
        response.raise_for_status()
    except requests.RequestException as exc:
        print(f"[main] erro ao enviar mensagem: {exc}")


def _safe_section(name: str, fn: SectionFn) -> str:
    try:
        result = fn()

        if not result or not str(result).strip():
            return f"⚠️ <b>{name}</b>\nSem dados disponíveis."

        return str(result).strip()

    except Exception as exc:
        print(f"[main] erro na seção {name}: {exc}")
        return f"⚠️ <b>{name}</b>\nErro ao gerar esta seção."


def _build_sections() -> List[Tuple[str, str]]:
    sections: List[Tuple[str, str]] = []

    sections.append(("market_take", _safe_section("Market Take", market_take)))
    sections.append(("day_over_day", _safe_section("Since Last Snapshot", day_over_day)))

    if macro_global:
        sections.append(("macro", _safe_section("Macro Global", macro_global)))

    sections.append(("brazil", _safe_section("Brazil Market", brazil_market)))
    sections.append(("usa", _safe_section("USA Market", usa_market)))

    if crypto_market:
        sections.append(("crypto", _safe_section("Crypto Market", crypto_market)))

    sections.append(("quant", _safe_section("Quant Summary", quant_summary)))
    sections.append(("news", _safe_section("News Market", news_market)))

    return sections


def send_report_in_batches() -> dict:
    sections = _build_sections()
    structured_sections = {key: value for key, value in sections}

    batch_1_parts = [
        structured_sections["market_take"],
        structured_sections["day_over_day"],
    ]

    if "macro" in structured_sections:
        batch_1_parts.append(structured_sections["macro"])

    batch_1_parts.append(structured_sections["brazil"])
    batch_1_parts.append(structured_sections["usa"])

    batch_2_parts = []
    if "crypto" in structured_sections:
        batch_2_parts.append(structured_sections["crypto"])
    batch_2_parts.append(structured_sections["quant"])

    batch_3_parts = [
        structured_sections["news"],
    ]

    batches = [
        "\n\n".join(batch_1_parts).strip(),
        "\n\n".join(batch_2_parts).strip(),
        "\n\n".join(batch_3_parts).strip(),
    ]

    for idx, batch in enumerate(batches, start=1):
        if not batch:
            continue

        print(f"[main] enviando bloco {idx}...")
        send_telegram(batch)

    return structured_sections


if __name__ == "__main__":
    print("Starting daily economic briefing...")

    structured_sections = send_report_in_batches()

    snapshot_path = save_daily_snapshot(structured_sections)
    print(f"[main] snapshot salvo em {snapshot_path}")

    report_path, index_path = generate_html_report(structured_sections)
    print(f"[main] html report salvo em {report_path}")
    print(f"[main] index html salvo em {index_path}")
