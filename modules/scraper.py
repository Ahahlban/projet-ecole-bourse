from googlesearch import search

def get_links(query, location="", school_type=""):
    """Génère une requête précise et récupère 3 liens pour économiser la data."""
    # On construit une requête "intelligente"
    full_query = f"{query} {school_type} {location} bourse d'étude"
    
    print(f"DEBUG: Recherche Google pour -> {full_query}")
    
    # On limite à 3 résultats pour le test et pour la rapidité
    links = []
    for url in search(full_query, num_results=3):
        links.append(url)
    return links