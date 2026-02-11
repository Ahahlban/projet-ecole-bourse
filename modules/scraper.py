from googlesearch import search

def get_links(query, location="", school_type=""):
    # 1. On nettoie la requête pour qu'elle soit la plus simple possible
    full_query = f"{query} {school_type} {location} bourse"
    
    # CE MESSAGE DOIT APPARAÎTRE DANS TON TERMINAL
    print(f"\n--- DEBUG START ---")
    print(f"Requête envoyée : {full_query}")
    
    links = []
    try:
        # On essaie la méthode la plus simple possible
        # On demande juste les URLs
        for url in search(full_query, num_results=3):
            print(f"Lien trouvé : {url}")
            links.append(url)
            
    except Exception as e:
        print(f"!!! ERREUR DANS LE SCRAPER : {e}")
        # Si ça échoue, on renvoie au moins un lien de secours pour tester le reste de l'app
        return ["https://www.google.com"] 

    print(f"Total liens récupérés : {len(links)}")
    print(f"--- DEBUG END ---\n")
    
    return links