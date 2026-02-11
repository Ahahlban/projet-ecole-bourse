from googlesearch import search

def get_links(query, location="", school_type=""):
    """
    Recherche réelle sur Google sans les arguments qui font planter le code.
    """
    # 1. On construit la requête
    full_query = f"{query} {school_type} {location} bourse d'étude"
    
    print(f"--- Requête envoyée à Google : {full_query} ---")
    
    links = []
    try:
        # 2. Utilisation de num_results (plus moderne que 'stop')
        # On demande 5 résultats
        results = search(full_query, num_results=5)
        
        # On transforme le résultat en liste
        for url in results:
            links.append(url)
            
    except Exception as e:
        # Si Google bloque ou s'il y a un souci réseau, on l'affiche dans le terminal
        print(f"Erreur lors de la recherche Google : {e}")
        return []
        
    return links