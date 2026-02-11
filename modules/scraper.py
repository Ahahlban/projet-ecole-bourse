import warnings
# On ignore les messages de renommage pour ne pas polluer le terminal
warnings.filterwarnings("ignore", category=RuntimeWarning)

from duckduckgo_search import DDGS

def get_links(query, location="", school_type=""):
    """
    Recherche DuckDuckGo optimisée et silencieuse.
    """
    full_query = f"{query} {school_type} {location} bourse"
    print(f"\n--- [DEBUG] Recherche lancée : {full_query} ---")
    
    links = []
    try:
        with DDGS() as ddgs:
            # On récupère les résultats
            results = ddgs.text(full_query, max_results=5)
            
            for r in results:
                url = r['href']
                links.append(url)
                print(f"✅ Lien trouvé : {url}") # Pour voir dans le terminal
                
    except Exception as e:
        print(f"❌ Erreur Scraper : {e}")
        return []
    
    if not links:
        print("⚠️ Aucun lien trouvé pour cette recherche.")
        
    print(f"--- [DEBUG] Fin de recherche ({len(links)} liens) ---\n")
    return links