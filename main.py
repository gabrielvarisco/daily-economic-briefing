import os
import requests

from Scripts.brazil_market import brazil_market
from Scripts.usa_market import usa_market
from Scripts.news_market import news_market

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
    }

    try:
        response = requests.post(url, json=payload, timeout=20)
        response.raise_for_status()
    except requests.RequestException as exc:
        print(f"[main] erro ao enviar mensagem para o Telegram: {exc}")


def _safe_section(section_name: str, fn):
    try:
        result = fn()
        if not result or not str(result).strip():
            return f"⚠️ <b>{section_name}</b>\nSem dados disponíveis no momento."
        return str(result).strip()
    except Exception as exc:
        print(f"[main] erro na seção {section_name}: {exc}")
        return f"⚠️ <b>{section_name}</b>\nErro ao gerar esta seção."


def build_full_report() -> str:
    sections = []

    if macro_global:
        sections.append(_safe_section("Macro Global", macro_global))

    sections.append(_safe_section("Brazil Market", brazil_market))
    sections.append(_safe_section("USA Market", usa_market))

    if crypto_market:
        sections.append(_safe_section("Crypto Market", crypto_market))

    sections.append(_safe_section("News Market", news_market))

    return "\n\n".join(section for section in sections if section.strip()).strip()


if __name__ == "__main__":
    print("Starting daily economic briefing...")

    report = build_full_report()

    print(report)

    send_telegram(report)
