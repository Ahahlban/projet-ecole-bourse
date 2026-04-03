import requests
from bs4 import BeautifulSoup
from urllib.parse import quote, unquote, urlparse, parse_qs

def get_links(keywords, location="", school_type="", max_results=30):
    """Recherche DuckDuckGo optimisée."""
    french_indicators = ["france", "paris", "lyon", "marseille", "bordeaux", "lille"]
    search_term = "bourse" if any(city in location.lower() for city in french_indicators) else "scholarship"

    # Construction propre : on filtre les éléments vides
    parts = [keywords, location, school_type, search_term]
    query = " ".join(filter(None, parts))
    
    encoded_query = quote(query)
    url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        results = []
        for a in soup.find_all("a", class_="result__a"):
            link = a.get("href")
            if link and "uddg=" in link:
                real_url = unquote(parse_qs(urlparse(link).query)["uddg"][0])
                if not any(x in real_url.lower() for x in ["facebook", "twitter", "instagram", "youtube", "linkedin"]):
                    results.append(real_url)
            if len(results) >= max_results: break
        return results
    except: return []