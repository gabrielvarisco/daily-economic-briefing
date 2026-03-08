import os
import requests

from Scripts.brazil_market import brazil_market
from Scripts.usa_market import usa_market
from Scripts.news_market import news_market
from Scripts.history_store import save_daily_snapshot
from Scripts.quant_summary import quant_summary

try:
    from Scripts.crypto_market import crypto_market
except ImportError:
    crypto_market = None

try:
    from Scripts.macro_global import macro_global
except ImportError:
    macro_global = None


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


def _safe_section(name: str, fn):
    try:
        result = fn()

        if not result or not str(result).strip():
            return f"⚠️ <b>{name}</b>\nSem dados disponíveis."

        return str(result).strip()

    except Exception as exc:
        print(f"[main] erro na seção {name}: {exc}")
        return f"⚠️ <b>{name}</b>\nErro ao gerar esta seção."


def build_full_report():
    sections = {}
    ordered_sections = []

    if macro_global:
        macro = _safe_section("Macro Global", macro_global)
        sections["macro"] = macro
        ordered_sections.append(macro)

    brazil = _safe_section("Brazil Market", brazil_market)
    sections["brazil"] = brazil
    ordered_sections.append(brazil)

    usa = _safe_section("USA Market", usa_market)
    sections["usa"] = usa
    ordered_sections.append(usa)

    if crypto_market:
        crypto = _safe_section("Crypto Market", crypto_market)
        sections["crypto"] = crypto
        ordered_sections.append(crypto)

    quant = _safe_section("Quant Summary", quant_summary)
    sections["quant"] = quant
    ordered_sections.append(quant)

    news = _safe_section("News Market", news_market)
    sections["news"] = news
    ordered_sections.append(news)

    report_text = "\n\n".join(ordered_sections).strip()

    return report_text, sections


if __name__ == "__main__":
    print("Starting daily economic briefing...")

    report, structured_sections = build_full_report()

    print(report)

    filepath = save_daily_snapshot(structured_sections)
    print(f"[main] snapshot salvo em {filepath}")

    send_telegram(report)
