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


def _safe_section(name: str, fn):
    try:
        result = fn()

        if not result or not str(result).strip():
            return f"⚠️ <b>{name}</b>\nSem dados disponíveis."

        return str(result).strip()

    except Exception as exc:
        print(f"[build_site] erro na seção {name}: {exc}")
        return f"⚠️ <b>{name}</b>\nErro ao gerar esta seção."


def build_sections() -> dict:
    sections = {}

    sections["market_take"] = _safe_section("Market Take", market_take)
    sections["day_over_day"] = _safe_section("Since Last Snapshot", day_over_day)

    if macro_global:
        sections["macro"] = _safe_section("Macro Global", macro_global)

    sections["brazil"] = _safe_section("Brazil Market", brazil_market)
    sections["usa"] = _safe_section("USA Market", usa_market)

    if crypto_market:
        sections["crypto"] = _safe_section("Crypto Market", crypto_market)

    sections["quant"] = _safe_section("Quant Summary", quant_summary)
    sections["news"] = _safe_section("News Market", news_market)

    return sections


if __name__ == "__main__":
    print("Starting silent site build...")

    structured_sections = build_sections()

    snapshot_path = save_daily_snapshot(structured_sections)
    print(f"[build_site] snapshot salvo em {snapshot_path}")

    report_path, index_path = generate_html_report(structured_sections)
    print(f"[build_site] html report salvo em {report_path}")
    print(f"[build_site] index html salvo em {index_path}")
