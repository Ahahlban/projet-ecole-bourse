from duckduckgo_search import DDGS

def get_links(query, location="", school_type=""):
    """
    Recherche DuckDuckGo utilisant la toute dernière version de la bibliothèque.
    """
    # Nettoyage simple de la requête
    full_query = f"{query} {school_type} {location} bourse"
    print(f"--- Tentative de recherche : {full_query} ---")
    
    links = []
    try:
        # On utilise le nouveau moteur de recherche
        with DDGS() as ddgs:
            # On récupère les résultats
            results = ddgs.text(full_query, max_results=5)
            
            # On extrait les liens (href)
            for r in results:
                print(f"Lien trouvé : {r['href']}")
                links.append(r['href'])
                
    except Exception as e:
        print(f"!!! Erreur Scraper : {e}")
        # En cas de bug, on ne bloque pas l'app, on renvoie une liste vide
        return []
    
    if not links:
        print("--- Aucun résultat renvoyé par le moteur ---")
        
    return links