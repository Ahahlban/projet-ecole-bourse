import warnings
# On bloque tous les warnings de renommage pour ne plus polluer le terminal
warnings.filterwarnings("ignore")

from duckduckgo_search import DDGS

def get_links(query, location="", school_type=""):
    """
    Recherche DuckDuckGo avec nettoyage de requête et liens de secours.
    """
    # 1. Nettoyage : on évite les répétitions de mots
    mots = f"{query} {location} {school_type} bourse".lower().split()
    clean_query = " ".join(dict.fromkeys(mots)) # Supprime les doublons proprement
    
    print(f"\n--- [SCRAPER] Tentative : {clean_query} ---")
    
    links = []
    try:
        with DDGS() as ddgs:
            # On demande 5 résultats
            results = ddgs.text(clean_query, max_results=5)
            if results:
                for r in results:
                    links.append(r['href'])
                    print(f"✅ Trouvé : {r['href']}")
            
    except Exception as e:
        print(f"❌ Erreur technique : {e}")

    # 2. PLAN B : Si le moteur renvoie 0, on donne des liens officiels
    # Cela permet de tester le reste de ton application (lecture, affichage)
    if not links:
        print("⚠️ Moteur bloqué ou 0 résultat. Utilisation des liens de secours.")
        return [
            "https://www.etudiant.gouv.fr/fr/les-bourses-sur-criteres-sociaux-148",
            "https://www.campusfrance.org/fr/bourses-etudiants-etrangers",
            "https://www.service-public.fr/particuliers/vosdroits/F12214"
        ]

    return links