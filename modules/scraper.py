import warnings
warnings.filterwarnings("ignore")

# On utilise la nouvelle porte d'entrée recommandée
try:
    from ddgs import DDGS
except ImportError:
    from duckduckgo_search import DDGS

def get_links(query, location="", school_type=""):
    # Nettoyage pour éviter le "bourse bourse"
    mots = f"{query} {location} {school_type} bourse".lower().split()
    clean_query = " ".join(dict.fromkeys(mots))
    
    print(f"\n--- [SCRAPER] Test final : {clean_query} ---")
    
    links = []
    try:
        with DDGS() as ddgs:
            # On utilise le moteur de recherche
            results = ddgs.text(clean_query, max_results=5)
            if results:
                for r in results:
                    links.append(r['href'])
                    print(f"✅ Trouvé : {r['href']}")
    except Exception as e:
        print(f"❌ Erreur : {e}")

    # Si ça ne marche toujours pas (blocage réseau), on garde nos liens de secours
    if not links:
        print("⚠️ Mode secours activé (0 liens trouvés).")
        return [
            "https://www.etudiant.gouv.fr/fr/les-bourses-sur-criteres-sociaux-148",
            "https://www.campusfrance.org/fr/bourses-etudiants-etrangers"
        ]

    return links