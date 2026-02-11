import warnings
# On bloque les avertissements pour garder un terminal propre
warnings.filterwarnings("ignore")

from duckduckgo_search import DDGS

def get_links(query, location="", school_type=""):
    """
    Recherche DuckDuckGo utilisant la syntaxe simplifiée 2026.
    """
    # On nettoie la requête : on évite les doublons (ex: Université université)
    # et on enlève les espaces en trop
    clean_query = f"{query} {location} bourse".replace("  ", " ").strip()
    
    print(f"\n--- [DEBUG] Tentative avec : {clean_query} ---")
    
    links = []
    try:
        # Nouvelle syntaxe simplifiée
        with DDGS() as ddgs:
            # On utilise le moteur de recherche texte
            results = ddgs.text(clean_query, max_results=5)
            
            if results:
                for r in results:
                    links.append(r['href'])
                    print(f"✅ Trouvé : {r['href']}")
            else:
                print("⚠️ DuckDuckGo n'a retourné aucun résultat.")
                
    except Exception as e:
        print(f"❌ Erreur technique Scraper : {e}")
        return []
    
    print(f"--- [DEBUG] Total : {len(links)} liens ---\n")
    return links