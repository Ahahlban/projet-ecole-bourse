from googlesearch import search
import time

def get_links(query, location="", school_type=""):
    """
    Recherche réelle sur Google. 
    On limite à 5 résultats pour la rapidité et éviter d'être bloqué par Google.
    """
    # 1. On construit une super-requête
    # On ajoute "bourse" et "inscription" pour cibler les besoins des étudiants
    full_query = f"{query} {school_type} {location} bourse d'étude inscription"
    
    print(f"--- Recherche Google lancée : {full_query} ---")
    
    links = []
    try:
        # 2. On lance la recherche
        # stop=5 : on s'arrête après 5 liens pour ne pas consommer trop de data
        # pause=2.0 : on attend 2 sec entre les requêtes pour ne pas être banni
        for url in search(full_query, stop=5, pause=2.0):
            links.append(url)
            
    except Exception as e:
        print(f"Erreur lors de la recherche Google : {e}")
        # En cas d'erreur (ex: trop de requêtes), on renvoie une liste vide
        return []
        
    return links