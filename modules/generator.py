import json
import re
import os
import time
from collections import defaultdict
from google import genai

# ── Clé API ──────────────────────────────────────────────────────────
try:
    import tomllib
    with open(".streamlit/secrets.toml", "rb") as f:
        secrets = tomllib.load(f)
    API_KEY = secrets.get("Gemini_API_Key", "")
except Exception:
    API_KEY = ""

OUTPUT_FILE = "data/schools.json"
DELAY_BETWEEN_REQUESTS = 65

# ── Ton nouveau PLAN augmenté ────────────────────────────────────────
PLAN = [
    # --- TECH & INNOVATION ---
    ("Cybersécurité et Cloud Computing", "Europe", "France, Allemagne, Estonie"),
    ("Intelligence Artificielle et Data Science", "Amérique du Nord", "USA, Canada"),
    ("Robotique et Systèmes Embarqués", "Asie", "Japon, Corée du Sud, Singapour"),
    
    # --- SANTÉ & SCIENCES ---
    ("Médecine et Santé Publique", "Afrique", "Sénégal, Maroc, Côte d'Ivoire, Afrique du Sud"),
    ("Biotechnologies et Pharmaceutique", "Europe", "Suisse, France, Belgique"),
    ("Agronomie et Sécurité Alimentaire", "Amérique Latine", "Brésil, Argentine, Colombie"),
    
    # --- BUSINESS & DROIT ---
    ("Finance Durable et Fintech", "Monde", "Royaume-Uni, Luxembourg, Hong Kong"),
    ("Droit International et Relations Publiques", "Europe", "Belgique, France, Pays-Bas"),
    
    # --- ARTS, DESIGN & ENVIRONNEMENT ---
    ("Design Graphique et Animation 3D", "Europe & Asie", "France, Japon"),
    ("Énergies Renouvelables et Écologie", "Scandinavie", "Suède, Norvège, Danemark"),
    
    # --- NOUVEAU : LITTÉRATURE & LETTRES ---
    ("Littérature Comparée et Langues Modernes", "Europe", "France, Italie, Espagne"),
    ("Écriture Créative et Journalisme", "Amérique du Nord", "USA, Canada"),
    ("Lettres et Sciences Humaines", "Afrique", "Sénégal, Côte d'Ivoire, Bénin"),
    ("Littérature Japonaise et Études Orientales", "Asie", "Japon (Tokyo/Kyoto), Corée du Sud")
]

def ask_gemini(domaine: str, zone: str, pays_precis: str, noms_existants: set) -> list[dict]:
    client = genai.Client(api_key=API_KEY)

    # Prompt amélioré pour éviter l'erreur "pays_precis not defined"
    prompt = f"""
    Génère une liste de 15 écoles ou programmes de bourses RÉELS pour : {domaine} en {zone} ({pays_precis}).
    Pour chaque école, fournis impérativement :
    - "nom": Le nom complet de l'établissement
    - "pays": La ville et le pays
    - "bourse": Le montant de la bourse (ou 'Exonération totale')
    - "frais": Les frais de scolarité annuels
    - "conditions": Les conditions d'admission (ex: niveau d'anglais)
    - "date_limite": La date limite (mois)
    - "site_web": Le lien officiel (URL réelle uniquement)
    - "resume": Un court résumé de 2 lignes
    - "categorie": Met exactement "{domaine}"

    Réponds UNIQUEMENT au format JSON (une liste d'objets).
    """

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash", 
                contents=prompt,
            )
            text = response.text.strip()
            text = re.sub(r"```json\s*", "", text).replace("```", "").strip()
            return json.loads(text)
        except Exception as e:
            print(f"         ⚠️ Tentative {attempt+1} échouée. Attente...")
            time.sleep(10)
    return []

def supprimer_doublons(schools: list[dict]) -> list[dict]:
    vus = set()
    uniques = []
    for s in schools:
        # On crée une clé unique combinant le nom ET la catégorie
        nom = str(s.get("nom", "")).strip().lower()
        categorie = str(s.get("categorie", "")).strip().lower()
        cle_unique = (nom, categorie) 
        
        if nom and cle_unique not in vus:
            vus.add(cle_unique)
            uniques.append(s)
    return uniques

def generate_full_database():
    print("=" * 60)
    print("  EduSearch — Génération de la base (Littérature incluse)")
    print("=" * 60)
    
    os.makedirs("data", exist_ok=True)
    all_schools = []
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            all_schools = json.load(f)

    noms_existants = {str(s.get("nom", "")).strip().lower() for s in all_schools}

    for i, (domaine, zone, pays_precis) in enumerate(PLAN, 1):
        print(f"[{i:02d}/{len(PLAN)}] {domaine[:30]:<30} | {zone}")
        
        # On vérifie si on a déjà des écoles pour ce domaine
        deja_la = [s for s in all_schools if s.get("categorie") == domaine]
        if len(deja_la) >= 10:
            print(f"         ✅ Zone déjà couverte ({len(deja_la)} écoles).")
            continue

        nouvelles = ask_gemini(domaine, zone, pays_precis, noms_existants)
        if nouvelles:
            nouvelles_uniques = [s for s in nouvelles if str(s.get("nom","")).lower() not in noms_existants]
            all_schools.extend(nouvelles_uniques)
            
            # Sauvegarde après chaque succès
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(all_schools, f, ensure_ascii=False, indent=2)
            
            print(f"         ✨ {len(nouvelles_uniques)} écoles ajoutées.")
            time.sleep(DELAY_BETWEEN_REQUESTS)

    print("\n✅ Terminé ! Relancez : streamlit run main.py")

if __name__ == "__main__":
    if not API_KEY:
        print("❌ Clé API manquante dans .streamlit/secrets.toml")
    else:
        generate_full_database()