
import json
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
import argostranslate.translate
# TRADUCTION AUTOMATIQUE ANGLAIS -> FRANÇAIS
SOURCES_ANGLAISES = {
    "BBC News",
    "The Guardian",
    "Al Jazeera",
    "Deutsche Welle",
    "The New York Times",
    "NPR",
    "Sky News",
    "TechCrunch",
    "The Verge",
    "WIRED",
    "Ars Technica",
    "Engadget",
    "MIT Technology Review",
    "Nature",
    "ScienceDaily",
    "New Scientist",
    "Science",
    "Scientific American",
    "CNBC",
    "Financial Times",
    "Wall Street Journal",
    "The Economist",
    "Mongabay",
    "Carbon Brief",
    "Grist",
    "NASA",
    "Defense News",
    "Breaking Defense",
    "The War Zone",
    "Naval News",
    "Air & Space Forces Magazine",
    "RUSI",
    "ESA",
    "Space.com",
    "SpaceNews",
    "Universe Today",
    "Astronomy Now"
}

def traduire_texte(texte, source):
    if not texte or source not in SOURCES_ANGLAISES:
        return texte

    try:
        return argostranslate.translate.translate(
            texte,
            "en",
            "fr"
        )
    except Exception as error:
        print(f"Erreur de traduction ({source}) : {error}")
        return texte
FEEDS = [
    # FRANCE
    ("France", "France 24", "https://www.france24.com/fr/france/rss"),
    ("France", "RFI", "https://www.rfi.fr/fr/rss"),
    ("France", "franceinfo", "https://www.francetvinfo.fr/titres.rss"),
    ("France", "Le Monde", "https://www.lemonde.fr/rss/une.xml"),
    ("France", "Libération", "https://www.liberation.fr/arc/outboundfeeds/rss-all/?outputType=xml"),
    ("France", "Le Figaro", "https://www.lefigaro.fr/rss/figaro_actualites.xml"),

    # MONDE
    ("Monde", "BBC News", "https://feeds.bbci.co.uk/news/world/rss.xml"),
    ("Monde", "The Guardian", "https://www.theguardian.com/world/rss"),
    ("Monde", "Al Jazeera", "https://www.aljazeera.com/xml/rss/all.xml"),
    ("Monde", "Deutsche Welle", "https://rss.dw.com/xml/rss-en-all"),
    ("Monde", "The New York Times", "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"),
    ("Monde", "NPR", "https://feeds.npr.org/1001/rss.xml"),
    ("Monde", "Sky News", "https://feeds.skynews.com/feeds/rss/world.xml"),

    # TECHNOLOGIE
    ("Technologie", "BBC News", "https://feeds.bbci.co.uk/news/technology/rss.xml"),
    ("Technologie", "The Guardian", "https://www.theguardian.com/technology/rss"),
    ("Technologie", "TechCrunch", "https://techcrunch.com/feed/"),
    ("Technologie", "The Verge", "https://www.theverge.com/rss/index.xml"),
    ("Technologie", "WIRED", "https://www.wired.com/feed/rss"),
    ("Technologie", "Ars Technica", "https://feeds.arstechnica.com/arstechnica/index"),
    ("Technologie", "Engadget", "https://www.engadget.com/rss.xml"),
    ("Technologie", "MIT Technology Review", "https://www.technologyreview.com/feed/"),

    # SCIENCES
    ("Sciences", "BBC News", "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml"),
    ("Sciences", "The Guardian", "https://www.theguardian.com/science/rss"),
    ("Sciences", "Nature", "https://www.nature.com/nature.rss"),
    ("Sciences", "ScienceDaily", "https://www.sciencedaily.com/rss/all.xml"),
    ("Sciences", "New Scientist", "https://www.newscientist.com/section/news/feed/"),
    ("Sciences", "Science", "https://www.science.org/rss/news_current.xml"),
    ("Sciences", "Scientific American", "https://www.scientificamerican.com/platform/syndication/rss/"),

    # ECONOMIE
    ("Économie", "BBC News", "https://feeds.bbci.co.uk/news/business/rss.xml"),
    ("Économie", "The Guardian", "https://www.theguardian.com/business/rss"),
    ("Économie", "CNBC", "https://www.cnbc.com/id/100003114/device/rss/rss.html"),
    ("Économie", "Financial Times", "https://www.ft.com/rss/home"),
    ("Économie", "Wall Street Journal", "https://feeds.a.dj.com/rss/RSSMarketsMain.xml"),
    ("Économie", "NPR", "https://feeds.npr.org/1006/rss.xml"),
    ("Économie", "The Economist", "https://www.economist.com/finance-and-economics/rss.xml"),

    # ENVIRONNEMENT
    ("Environnement", "The Guardian", "https://www.theguardian.com/environment/rss"),
    ("Environnement", "BBC News", "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml"),
    ("Environnement", "Mongabay", "https://news.mongabay.com/feed/"),
    ("Environnement", "Carbon Brief", "https://www.carbonbrief.org/feed/"),
    ("Environnement", "Grist", "https://grist.org/feed/"),
    ("Environnement", "ScienceDaily", "https://www.sciencedaily.com/rss/top/environment.xml"),
    ("Environnement", "NASA", "https://www.nasa.gov/feed/"),

    # DEFENSE
    ("Défense", "Defense News", "https://www.defensenews.com/arc/outboundfeeds/rss/?outputType=xml"),
    ("Défense", "Breaking Defense", "https://breakingdefense.com/feed/"),
    ("Défense", "The War Zone", "https://www.twz.com/feed"),
    ("Défense", "Naval News", "https://www.navalnews.com/feed/"),
    ("Défense", "Air & Space Forces Magazine", "https://www.airandspaceforces.com/feed/"),
    ("Défense", "RUSI", "https://www.rusi.org/rss.xml"),

    # EXPLORATION ET ESPACE
    ("Exploration", "NASA", "https://www.nasa.gov/feed/"),
    ("Exploration", "ESA", "https://www.esa.int/rssfeed/TopNews"),
    ("Exploration", "Space.com", "https://www.space.com/feeds/all"),
    ("Exploration", "SpaceNews", "https://spacenews.com/feed/"),
    ("Exploration", "Universe Today", "https://www.universetoday.com/feed/"),
    ("Exploration", "Astronomy Now", "https://astronomynow.com/feed/"),
    ("Exploration", "New Scientist", "https://www.newscientist.com/section/space/feed/"),
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
    "title": traduire_texte(title, source),
    "link": link,
    "date": date,
    "description": traduire_texte(description, source),
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
