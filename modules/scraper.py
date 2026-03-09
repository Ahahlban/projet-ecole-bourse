import requests
from bs4 import BeautifulSoup
from urllib.parse import quote, unquote, urlparse, parse_qs

def get_links(keywords, location="", school_type="", max_results=30):
    """
    Recherche des liens sur DuckDuckGo de manière intelligente (International).
    Bascule entre 'bourse' et 'scholarship' selon la localisation.
    """

    # Liste des marqueurs pour la France
    french_indicators = ["france", "paris", "lyon", "marseille", "bordeaux", "lille", "nantes", "toulouse"]
    
    # Choix du terme de recherche
    # Si la localisation contient un indicateur français, on garde "bourse"
    # Sinon (ou si c'est vide), on utilise "scholarship" pour l'international
    loc_lower = location.lower()
    if any(city in loc_lower for city in french_indicators):
        search_term = "bourse"
    else:
        search_term = "scholarship"

    # Construction de la requête
    query = f"{keywords} {location} {school_type} {search_term}"
    encoded_query = quote(query)
    url = f"https://html.duckduckgo.com/html/?q={encoded_query}"

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/119.0.0.0"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        results = []

        for a in soup.find_all("a", class_="result__a"):
            link = a.get("href")
            if link and "uddg=" in link:
                try:
                    # Extraction de la vraie URL
                    real_url = unquote(parse_qs(urlparse(link).query)["uddg"][0])
                    
                    # Filtre de base pour éviter les sites inutiles
                    blacklist = ["facebook", "wikipedia", "forum", "twitter", "instagram", "youtube", "linkedin"]
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