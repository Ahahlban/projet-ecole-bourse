from duckduckgo_search import DDGS

def get_links(query, location="", school_type=""):
    # Construction de la requête
    full_query = f"{query} {school_type} {location} bourse"
    print(f"--- Recherche lancée : {full_query} ---")
    
    links = []
    try:
        # On utilise DDGS qui est bien présent dans ta liste
        with DDGS() as ddgs:
            results = ddgs.text(full_query, max_results=5)
            for r in results:
                links.append(r['href'])
                print(f"Lien trouvé : {r['href']}")
    except Exception as e:
        print(f"Erreur Scraper : {e}")
        return []
    
    return links