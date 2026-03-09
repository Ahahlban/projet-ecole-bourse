import requests
from bs4 import BeautifulSoup
from urllib.parse import quote, unquote, urlparse, parse_qs

def get_links(keywords, location="", school_type="", max_results=30): # Passé à 30 par défaut
    """
    Recherche des liens sur DuckDuckGo à partir de mots-clés
    et retourne une liste de vraies URLs (non redirections).
    """

    query = f"{keywords} {location} {school_type} bourse"
    encoded_query = quote(query)
    url = f"https://html.duckduckgo.com/html/?q={encoded_query}"

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/119.0.0.0"}

    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        results = []

        for a in soup.find_all("a", class_="result__a"):
            link = a.get("href")
            if link and "uddg=" in link:
                try:
                    # Extraction de la vraie URL depuis le lien DuckDuckGo
                    real_url = unquote(parse_qs(urlparse(link).query)["uddg"][0])
                    
                    # Filtre rapide de base (réseaux sociaux, etc.)
                    # On laisse l'IA faire le tri fin sur le reste
                    if not any(x in real_url for x in ["facebook", "wikipedia", "forum", "twitter", "instagram"]):
                        results.append(real_url)
                except (KeyError, IndexError):
                    continue
            
            # On s'arrête quand on a atteint le nouveau maximum de 30
            if len(results) >= max_results: 
                break
                
        return results
    except Exception as e:
        print(f"Erreur Scraper : {e}")
        return []