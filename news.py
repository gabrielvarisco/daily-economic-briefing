import requests
import os
import xml.etree.ElementTree as ET

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

RSS_URL = "https://feeds.bbci.co.uk/news/business/rss.xml"

def get_news():
    response = requests.get(RSS_URL, timeout=10)
    root = ET.fromstring(response.content)

    items = root.findall(".//item")
    headlines = []

    for item in items[:5]:
        title = item.find("title").text
        headlines.append(f"- {title}")

    return "\n".join(headlines)

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }
    requests.post(url, data=payload)

if __name__ == "__main__":
    news = get_news()
    message = f"📊 Resumo Econômico do Dia\n\n{news}"
    send_telegram(message)
