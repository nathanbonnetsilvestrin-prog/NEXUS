
import json
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

FEEDS = [
    # FRANCE ET MONDE
    ("France", "France 24", "https://www.france24.com/fr/france/rss"),
    ("Monde", "France 24", "https://www.france24.com/fr/rss"),
    ("Monde", "BBC News", "https://feeds.bbci.co.uk/news/world/rss.xml"),

    # TECHNOLOGIE
    ("Technologie", "BBC News", "https://feeds.bbci.co.uk/news/technology/rss.xml"),
    ("Technologie", "The Guardian", "https://www.theguardian.com/technology/rss"),

    # SCIENCES
    ("Sciences", "BBC News", "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml"),
    ("Sciences", "The Guardian", "https://www.theguardian.com/science/rss"),

    # ECONOMIE
    ("Économie", "BBC News", "https://feeds.bbci.co.uk/news/business/rss.xml"),
    ("Économie", "The Guardian", "https://www.theguardian.com/business/rss"),

    # ENVIRONNEMENT
    ("Environnement", "The Guardian", "https://www.theguardian.com/environment/rss"),

    # DEFENSE
    ("Défense", "Defense News", "https://www.defensenews.com/arc/outboundfeeds/rss/?outputType=xml"),

    # EXPLORATION ET ESPACE
    ("Exploration", "NASA", "https://www.nasa.gov/feed/"),
    ("Exploration", "ESA", "https://www.esa.int/rssfeed/TopNews"),
]

articles = []
seen = set()

for category, source, url in FEEDS:
    try:
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "NEXUS-News/2.0"}
        )

        with urllib.request.urlopen(request, timeout=25) as response:
            xml = response.read()

        root = ET.fromstring(xml)

        # Compatibilité RSS et Atom
        items = root.findall(".//item")
        if not items:
            items = root.findall(".//{*}entry")

        for item in items:
            title = (
                item.findtext("title")
                or item.findtext("{*}title")
                or ""
            ).strip()

            link = item.findtext("link", "").strip()

            if not link:
                link_element = item.find("{*}link")
                if link_element is not None:
                    link = (
                        link_element.attrib.get("href")
                        or link_element.text
                        or ""
                    ).strip()

            date = (
                item.findtext("pubDate")
                or item.findtext("{*}published")
                or item.findtext("{*}updated")
                or ""
            ).strip()

            description = (
                item.findtext("description")
                or item.findtext("{*}summary")
                or item.findtext("{*}description")
                or ""
            ).strip()

            if not title or not link or link in seen:
                continue

            seen.add(link)

            articles.append({
                "title": title,
                "link": link,
                "date": date,
                "description": description,
                "source": source,
                "category": category
            })

        print(f"OK : {source} - {category}")

    except Exception as error:
        print(f"Flux indisponible : {source} - {error}")

articles.sort(
    key=lambda article: article["date"],
    reverse=True
)

data = {
    "updated_at": datetime.now(timezone.utc).isoformat(),
    "count": len(articles),
    "articles": articles
}

with open("news.json", "w", encoding="utf-8") as file:
    json.dump(data, file, ensure_ascii=False, indent=2)

print(f"NEXUS : {len(articles)} articles récupérés.")
