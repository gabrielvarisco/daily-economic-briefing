import html
import requests
import xml.etree.ElementTree as ET


RSS_FEEDS = {
    "brazil": [
        "https://www.infomoney.com.br/feed/",
        "https://valor.globo.com/financas/rss/",
    ],
    "usa": [
        "https://feeds.a.dj.com/rss/RSSMarketsMain.xml",
        "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    ],
    "crypto": [
        "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "https://cointelegraph.com/rss",
    ],
}


KEYWORDS = {
    "brazil": [
        "ibovespa", "selic", "copom", "dólar", "fiscal", "petrobras",
        "vale", "b3", "bolsa", "economia", "juros", "inflação", "banco central"
    ],
    "usa": [
        "fed", "s&p", "nasdaq", "dow", "treasury", "inflation", "jobs",
        "rates", "stocks", "market", "economy", "yield", "wall street"
    ],
    "crypto": [
        "bitcoin", "btc", "ethereum", "eth", "solana", "crypto",
        "blockchain", "etf", "exchange", "token", "stablecoin"
    ],
}


def _download_feed(url: str) -> str:
    response = requests.get(
        url,
        timeout=20,
        headers={"User-Agent": "Mozilla/5.0"}
    )
    response.raise_for_status()
    return response.text


def _extract_items_from_rss(xml_text: str) -> list[dict]:
    items = []

    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return items

    for item in root.findall(".//item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        pub_date = (item.findtext("pubDate") or "").strip()
        description = (item.findtext("description") or "").strip()

        if not title or not link:
            continue

        items.append({
            "title": html.unescape(title),
            "link": link,
            "pub_date": pub_date,
            "description": html.unescape(description),
        })

    return items


def _is_relevant(text: str, market: str) -> bool:
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in KEYWORDS.get(market, []))


def _deduplicate(items: list[dict]) -> list[dict]:
    seen = set()
    unique_items = []

    for item in items:
        key = item["title"].strip().lower()

        if key in seen:
            continue

        seen.add(key)
        unique_items.append(item)

    return unique_items


def get_market_news(market: str, limit: int = 3) -> list[dict]:
    feeds = RSS_FEEDS.get(market, [])
    all_items = []

    for feed_url in feeds:
        try:
            xml_text = _download_feed(feed_url)
            feed_items = _extract_items_from_rss(xml_text)
            all_items.extend(feed_items)
        except Exception as exc:
            print(f"[news_market] erro ao ler feed {feed_url}: {exc}")

    all_items = _deduplicate(all_items)

    relevant = []
    fallback = []

    for item in all_items:
        combined_text = f"{item['title']} {item['description']}"

        if _is_relevant(combined_text, market):
            relevant.append(item)
        else:
            fallback.append(item)

    if len(relevant) >= limit:
        return relevant[:limit]

    combined = relevant + fallback
    return combined[:limit]


def format_news_section(market: str, title: str, limit: int = 3) -> str:
    news = get_market_news(market, limit=limit)

    section = f"📰 <b>{title}</b>\n\n"

    if not news:
        section += "Sem notícias disponíveis no momento."
        return section

    for item in news:
        headline = item["title"].strip()
        section += f"• {headline}\n"

    return section.strip()


def news_market() -> str:
    sections = [
        format_news_section("brazil", "News Brasil", limit=3),
        format_news_section("usa", "News EUA", limit=3),
        format_news_section("crypto", "News Crypto", limit=3),
    ]

    return "\n\n".join(sections)


if __name__ == "__main__":
    print("Starting News Market script")
    print(news_market())
