import html
import logging
import re
import requests
import xml.etree.ElementTree as ET
from typing import Dict, List


logger = logging.getLogger("news_market")

RSS_FEEDS = {
    "brazil": [
        "https://www.infomoney.com.br/feed/",
        "https://www.moneytimes.com.br/feed/",
    ],
    "usa": [
        "https://feeds.a.dj.com/rss/RSSMarketsMain.xml",
        "https://www.cnbc.com/id/100003114/device/rss/rss.html",
        "https://www.marketwatch.com/rss/topstories",
    ],
    "crypto": [
        "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "https://cointelegraph.com/rss",
    ],
}


KEYWORDS = {
    "brazil": [
        "ibovespa", "bolsa", "selic", "copom", "dólar", "fiscal", "juros",
        "inflação", "ipca", "banco central", "petrobras", "vale", "b3",
        "mercado", "ações", "real", "brasil", "economia", "arcabouço",
    ],
    "usa": [
        "fed", "fomc", "s&p", "nasdaq", "dow", "treasury", "yield",
        "inflation", "cpi", "ppi", "jobs", "payroll", "economy",
        "stocks", "market", "wall street", "rates", "recession",
    ],
    "crypto": [
        "bitcoin", "btc", "ethereum", "eth", "solana", "crypto",
        "blockchain", "etf", "token", "stablecoin", "defi",
        "exchange", "altcoin", "on-chain",
    ],
}


NEGATIVE_KEYWORDS = {
    "brazil": [
        "messi", "inter miami", "celebrity", "famoso", "novela",
        "bbb", "cpi do inss", "esporte", "futebol", "entretenimento",
    ],
    "usa": [
        "celebrity", "movie", "tv", "sports", "football", "basketball",
        "entertainment",
    ],
    "crypto": [
        "giveaway", "airdrop scam", "casino",
    ],
}


SOURCE_LABELS = {
    "infomoney.com.br": "InfoMoney",
    "moneytimes.com.br": "Money Times",
    "wsj.com": "WSJ",
    "cnbc.com": "CNBC",
    "marketwatch.com": "MarketWatch",
    "coindesk.com": "CoinDesk",
    "cointelegraph.com": "Cointelegraph",
}


def _download_feed(url: str) -> str:
    response = requests.get(
        url,
        timeout=20,
        headers={"User-Agent": "Mozilla/5.0"},
    )
    response.raise_for_status()
    return response.text


def _clean_text(text: str) -> str:
    text = html.unescape(text or "")
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _extract_domain(link: str) -> str:
    match = re.search(r"https?://([^/]+)", link or "")
    if not match:
        return ""
    return match.group(1).lower().replace("www.", "")


def _extract_items_from_rss(xml_text: str) -> List[Dict]:
    items = []

    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return items

    for item in root.findall(".//item"):
        title = _clean_text(item.findtext("title") or "")
        link = (item.findtext("link") or "").strip()
        description = _clean_text(item.findtext("description") or "")
        pub_date = (item.findtext("pubDate") or "").strip()

        if not title or not link:
            continue

        items.append({
            "title": title,
            "link": link,
            "description": description,
            "pub_date": pub_date,
            "domain": _extract_domain(link),
        })

    return items


def _deduplicate(items: List[Dict]) -> List[Dict]:
    seen = set()
    unique_items = []

    for item in items:
        key = (item["title"].strip().lower(), item["domain"])
        if key in seen:
            continue
        seen.add(key)
        unique_items.append(item)

    return unique_items


def _score_item(item: Dict, market: str) -> int:
    text = f"{item['title']} {item['description']}".lower()

    score = 0

    for keyword in KEYWORDS.get(market, []):
        if keyword in text:
            score += 3

    for keyword in NEGATIVE_KEYWORDS.get(market, []):
        if keyword in text:
            score -= 5

    title_lower = item["title"].lower()
    for keyword in KEYWORDS.get(market, []):
        if keyword in title_lower:
            score += 2

    if item["domain"] in SOURCE_LABELS:
        score += 1

    return score


def get_market_news(market: str, limit: int = 3) -> List[Dict]:
    feeds = RSS_FEEDS.get(market, [])
    all_items: List[Dict] = []

    for feed_url in feeds:
        try:
            xml_text = _download_feed(feed_url)
            feed_items = _extract_items_from_rss(xml_text)
            all_items.extend(feed_items)
        except Exception as exc:
            logger.warning(f"erro ao ler feed {feed_url}: {exc}")

    all_items = _deduplicate(all_items)

    scored_items = []
    for item in all_items:
        score = _score_item(item, market)
        item["score"] = score
        scored_items.append(item)

    scored_items.sort(key=lambda x: x["score"], reverse=True)

    strong = [item for item in scored_items if item["score"] >= 3]
    if len(strong) >= limit:
        return strong[:limit]

    medium = [item for item in scored_items if item["score"] >= 1]
    if len(medium) >= limit:
        return medium[:limit]

    return scored_items[:limit]


def format_news_section(market: str, title: str, limit: int = 3) -> str:
    news = get_market_news(market, limit=limit)

    section = f"📰 <b>{title}</b>\n\n"

    if not news:
        section += "Sem notícias disponíveis no momento."
        return section

    for item in news:
        source = SOURCE_LABELS.get(item["domain"], item["domain"] or "Fonte")
        headline = item["title"].strip()
        section += f"• {headline} <i>({source})</i>\n"

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
