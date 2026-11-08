import json
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

FEEDS = [
    "https://www.france24.com/fr/rss",
    "https://www.france24.com/fr/france/rss",
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://feeds.bbci.co.uk/news/technology/rss.xml",
    "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml"
]

articles = []
seen = set()

for url in FEEDS:
    try:
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "NEXUS-News/1.0"}
        )

        with urllib.request.urlopen(request, timeout=20) as response:
            xml = response.read()

        root = ET.fromstring(xml)

        for item in root.findall(".//item"):
            title = item.findtext("title", "").strip()
            link = item.findtext("link", "").strip()
            date = item.findtext("pubDate", "").strip()
            description = item.findtext("description", "").strip()

            if not title or not link or link in seen:
                continue

            seen.add(link)

            articles.append({
                "title": title,
                "link": link,
                "date": date,
                "description": description,
                "source": url
            })

    except Exception as error:
        print(f"Flux indisponible : {url} — {error}")

articles.sort(key=lambda article: article["date"], reverse=True)

data = {
    "updated_at": datetime.now(timezone.utc).isoformat(),
    "count": len(articles),
    "articles": articles
}

with open("news.json", "w", encoding="utf-8") as file:
    json.dump(data, file, ensure_ascii=False, indent=2)

print(f"NEXUS : {len(articles)} articles récupérés.")