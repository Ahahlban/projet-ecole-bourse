import requests
from bs4 import BeautifulSoup
from urllib.parse import quote, unquote, urlparse, parse_qs
import random

def get_links(keywords, location="", school_type="", max_results=30):
    """Recherche des liens sur DuckDuckGo (Version robuste)."""
    
    # Choix du terme selon la localisation
    french_indicators = ["france", "paris", "lyon", "marseille", "bordeaux", "lille", "nantes", "toulouse"]
    loc_lower = location.lower()
    search_term = "bourse" if any(city in loc_lower for city in french_indicators) else "scholarship"

    # Construction propre de la requête sans doubles espaces
    query_parts = [keywords, location, school_type, search_term]
    query = " ".join(filter(None, query_parts)) # Enlève les éléments vides
    
    encoded_query = quote(query)
    url = f"https://html.duckduckgo.com/html/?q={encoded_query}"

    # Liste de User-Agents pour éviter d'être bloqué comme robot
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    ]
    headers = {"User-Agent": random.choice(user_agents)}

    try:
        response = requests.get(url, headers=headers, timeout=12)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        results = []

        # Extraction des liens
        for a in soup.find_all("a", class_="result__a"):
            link = a.get("href")
            if link and "uddg=" in link:
                try:
                    real_url = unquote(parse_qs(urlparse(link).query)["uddg"][0])
                    blacklist = ["facebook", "wikipedia", "forum", "twitter", "instagram", "youtube", "linkedin", "studyrama", "letudiant"]
                    if not any(x in real_url.lower() for x in blacklist):
                        results.append(real_url)
                except (KeyError, IndexError):
                    continue
            
            if len(results) >= max_results: 
                break
                
        return results
    except Exception as e:
        print(f"Erreur Scraper : {e}")
        return []