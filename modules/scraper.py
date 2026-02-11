from duckduckgo_search import DDGS

def get_links(query, location="", school_type=""):
    """
    Recherche via DuckDuckGo (plus stable que Google pour le développement).
    """
    full_query = f"{query} {school_type} {location} bourse"
    print(f"--- Recherche DuckDuckGo : {full_query} ---")
    
    links = []
    try:
        # On utilise le moteur DuckDuckGo qui est plus "gentil" avec les robots
        with DDGS() as ddgs:
            # On demande les 5 premiers résultats
            results = ddgs.text(full_query, max_results=5)
            for r in results:
                print(f"Lien trouvé : {r['href']}")
                links.append(r['href'])
                
    except Exception as e:
        print(f"!!! Erreur Scraper : {e}")
        return []
    
    return links