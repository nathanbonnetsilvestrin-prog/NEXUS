
import json
import re
import html
import urllib.request
import xml.etree.ElementTree as ET

from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

import argostranslate.translate


# =====================================================
# CONFIGURATION
# =====================================================

CACHE_FILE = "translations_cache.json"

MAX_ARTICLES_PER_FEED = 6
MAX_DESCRIPTION_LENGTH = 450
MAX_CACHE_SIZE = 5000

CACHE_TRADUCTIONS = {}


# =====================================================
# CHARGEMENT DU CACHE PERSISTANT
# =====================================================

try:
    with open(CACHE_FILE, "r", encoding="utf-8") as file:
        CACHE_TRADUCTIONS = json.load(file)

    print(f"Cache chargé : {len(CACHE_TRADUCTIONS)} traductions.")

except (FileNotFoundError, json.JSONDecodeError):
    CACHE_TRADUCTIONS = {}
    print("Aucun cache existant. Création d'un nouveau cache.")


# =====================================================
# SOURCES ANGLAISES
# =====================================================

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


# =====================================================
# CHARGEMENT DU TRADUCTEUR
# =====================================================

traducteur = None

try:
    langues = argostranslate.translate.get_installed_languages()

    anglais = next(
        (lang for lang in langues if lang.code == "en"),
        None
    )

    francais = next(
        (lang for lang in langues if lang.code == "fr"),
        None
    )

    if anglais and francais:
        traducteur = anglais.get_translation(francais)
        print("Moteur anglais-français chargé.")
    else:
        print("Modèle anglais-français introuvable.")

except Exception as error:
    print(f"Erreur de chargement du traducteur : {error}")


# =====================================================
# NETTOYAGE DU TEXTE
# =====================================================

def nettoyer_texte(texte):

    if not texte:
        return ""

    texte = html.unescape(texte)
    texte = re.sub(r"<[^>]+>", " ", texte)
    texte = re.sub(r"\s+", " ", texte)

    return texte.strip()


# =====================================================
# TRADUCTION AVEC CACHE
# =====================================================

def traduire_texte(texte, source):

    texte = nettoyer_texte(texte)

    if not texte:
        return texte

    if source not in SOURCES_ANGLAISES:
        return texte

    if traducteur is None:
        return texte

    # Limitation des descriptions trop longues
    if len(texte) > MAX_DESCRIPTION_LENGTH:
        texte = texte[:MAX_DESCRIPTION_LENGTH].rsplit(" ", 1)[0]

    # Vérification du cache
    if texte in CACHE_TRADUCTIONS:
        return CACHE_TRADUCTIONS[texte]

    try:
        resultat = traducteur.translate(texte)

        if resultat:
            CACHE_TRADUCTIONS[texte] = resultat
            return resultat

    except Exception as error:
        print(f"Erreur de traduction ({source}) : {error}")

    return texte


# =====================================================
# FLUX RSS
# =====================================================

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
    ("Exploration", "New Scientist", "https://www.newscientist.com/section/space/feed/")
]


# =====================================================
# RÉCUPÉRATION DES FLUX RSS
# =====================================================

def recuperer_flux(feed):

    category, source, url = feed

    try:
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "NEXUS-News/3.0"}
        )

        with urllib.request.urlopen(request, timeout=12) as response:
            xml = response.read()

        root = ET.fromstring(xml)

        items = root.findall(".//item")

        if not items:
            items = root.findall(".//{*}entry")

        resultats = []

        for item in items[:MAX_ARTICLES_PER_FEED]:

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

            if not title or not link:
                continue

            resultats.append({
                "title": nettoyer_texte(title),
                "link": link,
                "date": date,
                "description": nettoyer_texte(description),
                "source": source,
                "category": category
            })

        return feed, resultats, None

    except Exception as error:
        return feed, [], str(error)


# =====================================================
# RÉCUPÉRATION PARALLÈLE
# =====================================================

articles = []
seen = set()

print("Démarrage de la récupération NEXUS...")

with ThreadPoolExecutor(max_workers=12) as executor:

    futures = [
        executor.submit(recuperer_flux, feed)
        for feed in FEEDS
    ]

    for future in as_completed(futures):

        feed, resultats, erreur = future.result()

        category, source, url = feed

        if erreur:
            print(f"Flux indisponible : {source} - {erreur}")
            continue

        nouveaux = 0

        for article in resultats:

            link = article["link"]

            if link in seen:
                continue

            seen.add(link)

            article["title"] = traduire_texte(
                article["title"],
                source
            )

            article["description"] = traduire_texte(
                article["description"],
                source
            )

            articles.append(article)
            nouveaux += 1

        print(
            f"OK : {source} - {category} "
            f"({nouveaux} nouveaux articles)"
        )


# =====================================================
# ENREGISTREMENT DU CACHE
# =====================================================

# Conservation des traductions les plus récentes
if len(CACHE_TRADUCTIONS) > MAX_CACHE_SIZE:

    CACHE_TRADUCTIONS = dict(
        list(CACHE_TRADUCTIONS.items())[-MAX_CACHE_SIZE:]
    )

with open(CACHE_FILE, "w", encoding="utf-8") as file:
    json.dump(
        CACHE_TRADUCTIONS,
        file,
        ensure_ascii=False
    )

print(f"Cache enregistré : {len(CACHE_TRADUCTIONS)} traductions.")


# =====================================================
# TRI ET ENREGISTREMENT DES ACTUALITÉS
# =====================================================

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
    json.dump(
        data,
        file,
        ensure_ascii=False,
        indent=2
    )

print("--------------------------------")
print(f"NEXUS : {len(articles)} articles récupérés.")
print(f"Cache : {len(CACHE_TRADUCTIONS)} traductions.")
print("Actualisation terminée.")
