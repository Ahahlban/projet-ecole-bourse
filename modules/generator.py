"""
SCRIPT 1 — generator.py (version 200+ écoles)
==============================================
Appelle Gemini pour générer plus de 200 écoles réelles
réparties en 8 domaines × 3 zones géographiques.

Chaque appel = 10 écoles → 24 appels au total = ~240 écoles.

À lancer UNE SEULE FOIS dans le terminal :
  python modules/generator.py
"""

import json
import re
import os
import time
from collections import defaultdict

from google import genai

# ── Clé API (lue depuis secrets.toml si possible) ─────────────────────
try:
    import tomllib
    with open(".streamlit/secrets.toml", "rb") as f:
        secrets = tomllib.load(f)
    API_KEY = secrets.get("Gemini_API_Key", "")
except Exception:
    API_KEY = "METTEZ_VOTRE_CLE_ICI"

OUTPUT_FILE = "data/schools.json"

# Délai entre chaque requête — respecte le free tier Gemini (15 req/min)
# On prend 65s pour être safe (légèrement au-dessus de 60s)
DELAY_BETWEEN_REQUESTS = 65

PLAN = [
    ("informatique et intelligence artificielle", "Europe francophone",        "France, Belgique, Suisse"),
    ("informatique et intelligence artificielle", "Afrique francophone",       "Maroc, Tunisie, Sénégal, Côte d'Ivoire, Cameroun"),
    ("informatique et intelligence artificielle", "Amérique du Nord francophone", "Canada (Québec), États-Unis"),

    ("médecine et santé",          "Europe francophone",   "France, Belgique, Suisse"),
    ("médecine et santé",          "Afrique francophone",  "Maroc, Tunisie, Algérie, Sénégal, Madagascar"),
    ("médecine et santé",          "Amérique et Asie",     "Canada, Liban, Vietnam"),

    ("ingénierie et sciences",     "Europe francophone",   "France, Belgique, Suisse"),
    ("ingénierie et sciences",     "Afrique francophone",  "Maroc, Tunisie, Algérie, Cameroun"),
    ("ingénierie et sciences",     "International",        "Canada, Liban, Maurice"),

    ("commerce et management",     "Europe francophone",   "France, Belgique, Luxembourg"),
    ("commerce et management",     "Afrique francophone",  "Maroc, Tunisie, Côte d'Ivoire, Sénégal"),
    ("commerce et management",     "International",        "Canada, Suisse, Liban"),

    ("droit et sciences politiques","Europe francophone",  "France, Belgique, Suisse"),
    ("droit et sciences politiques","Afrique francophone", "Maroc, Tunisie, Algérie, Sénégal"),
    ("droit et sciences politiques","International",       "Canada, Liban"),

    ("arts et design",             "Europe francophone",          "France, Belgique, Suisse"),
    ("arts et design",             "Afrique et international",    "Maroc, Tunisie, Canada"),

    ("architecture et urbanisme",  "Europe francophone",          "France, Belgique, Suisse"),
    ("architecture et urbanisme",  "Afrique et international",    "Maroc, Algérie, Tunisie, Canada"),

    ("lettres, langues et sciences humaines", "Europe francophone",  "France, Belgique, Suisse"),
    ("lettres, langues et sciences humaines", "Afrique francophone", "Maroc, Sénégal, Côte d'Ivoire"),
    ("lettres, langues et sciences humaines", "International",       "Canada, Liban"),

    ("sciences de l'éducation et formation",  "Europe et Afrique",          "France, Belgique, Maroc, Sénégal"),
    ("environnement et développement durable","International francophone",   "France, Canada, Maroc, Tunisie"),
]


def ask_gemini(domaine: str, zone: str, pays: str, noms_existants: set) -> list[dict]:
    """
    Demande à Gemini 10 écoles réelles.
    Retente automatiquement en cas de rate limit 429.
    """
    client = genai.Client(api_key=API_KEY)

    exclusions = ""
    if noms_existants:
        sample = list(noms_existants)[:20]
        exclusions = f"\n- NE PAS inclure : {', '.join(sample)}"

    prompt = f"""
Tu es une base de données académique mondiale spécialisée en orientations post-bac.

Génère exactement 10 établissements réels dans :
- Domaine : "{domaine}"
- Zone géographique : {zone}
- Pays ciblés : {pays}

RÈGLES :
- Établissements qui existent vraiment
- Privilégie l'accessibilité financière
- Varie les types (universités publiques, grandes écoles, instituts)
- Montants réalistes ou vide si inconnu{exclusions}

Retourne UNIQUEMENT un tableau JSON valide, sans texte autour, sans balises markdown :
[
  {{
    "nom": "Nom officiel complet",
    "pays": "Pays",
    "ville": "Ville principale",
    "categorie": "{domaine}",
    "type": "Université publique / Grande École / Institut privé / IUT",
    "langue": "Français / Anglais / Arabe / Bilingue",
    "niveau": ["Licence", "Master"],
    "frais_annuels": "Montant réel ou vide",
    "bourse_disponible": "Oui / Non / Possible",
    "montant_bourse": "Montant et source ou vide",
    "conditions_admission": "Bac / Concours / Dossier etc.",
    "date_limite": "Mois approximatif ou vide",
    "duree": "3 ans / 5 ans etc.",
    "resume": "2 phrases : points forts, accessibilité, débouchés",
    "site_web": "URL officielle ou vide",
    "contact": "Email ou téléphone ou vide"
  }}
]
"""

    max_retries = 5
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",  # Plus de quota que flash-lite
                contents=prompt,
            )
            text = response.text.strip()
            text = re.sub(r"```json\s*", "", text)
            text = re.sub(r"```\s*", "", text).strip()

            try:
                data = json.loads(text)
                if isinstance(data, list):
                    return data
            except json.JSONDecodeError:
                match = re.search(r'\[.*\]', text, re.DOTALL)
                if match:
                    try:
                        return json.loads(match.group(0))
                    except Exception:
                        pass
            print(f"         ⚠️  Réponse non parseable — tentative {attempt+1}/{max_retries}")
            time.sleep(15)

        except Exception as e:
            err = str(e)
            if "429" in err or "RESOURCE_EXHAUSTED" in err:
                m = re.search(r'retryDelay.*?(\d+)s', err)
                wait = int(m.group(1)) + 10 if m else 75
                print(f"         ⏳ Rate limit — attente {wait}s (tentative {attempt+1}/{max_retries})...")
                time.sleep(wait)
            else:
                raise

    return []


def supprimer_doublons(schools: list[dict]) -> list[dict]:
    vus = set()
    uniques = []
    for s in schools:
        nom = str(s.get("nom", "")).strip().lower()
        if nom and nom not in vus:
            vus.add(nom)
            uniques.append(s)
    return uniques


def generate_full_database():
    print("=" * 60)
    print("  EduSearch — Génération de la base (200+ écoles)")
    print("=" * 60)
    print(f"  Plan : {len(PLAN)} requêtes × ~10 écoles = ~{len(PLAN)*10} écoles")
    print(f"  ⚠️  Durée estimée : ~{len(PLAN) * DELAY_BETWEEN_REQUESTS // 60} minutes")
    print("=" * 60)

    os.makedirs("data", exist_ok=True)

    # ── Charger la base existante SANS effacer ────────────────────────────
    all_schools = []
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                existing = json.load(f)
            if isinstance(existing, list):
                all_schools = existing
                print(f"\n  ℹ️  Base existante : {len(all_schools)} écoles chargées.")
                print("  → Reprise automatique (zones déjà couvertes seront sautées).\n")
        except Exception:
            print("  ⚠️  Impossible de lire la base, on repart de zéro.\n")

    noms_existants = {str(s.get("nom", "")).strip().lower() for s in all_schools}

    # ── Boucle principale ─────────────────────────────────────────────────
    for i, (domaine, zone, pays) in enumerate(PLAN, 1):
        print(f"\n[{i:02d}/{len(PLAN)}] {domaine[:35]:<35} | {zone}")

        # Détecter si cette zone est déjà couverte
        pays_liste = [p.strip().replace("(Québec)", "").strip()
                      for p in pays.split(",") if len(p.strip()) > 2]
        ecoles_zone = [
            s for s in all_schools
            if s.get("categorie", "") == domaine
            and any(p.lower() in s.get("pays", "").lower() for p in pays_liste)
        ]

        if len(ecoles_zone) >= 5:
            print(f"         ✅ Déjà {len(ecoles_zone)} écoles pour cette zone — sauté.")
            continue

        try:
            nouvelles = ask_gemini(domaine, zone, pays, noms_existants)

            nouvelles_uniques = [
                s for s in nouvelles
                if str(s.get("nom", "")).strip().lower() not in noms_existants
            ]
            all_schools.extend(nouvelles_uniques)
            for s in nouvelles_uniques:
                noms_existants.add(str(s.get("nom", "")).strip().lower())

            print(f"         ✅ {len(nouvelles_uniques)} écoles ajoutées "
                  f"(sur {len(nouvelles)}) — Total : {len(all_schools)}")

            # Sauvegarde intermédiaire
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(all_schools, f, ensure_ascii=False, indent=2)

            if i < len(PLAN):
                print(f"         ⏳ Pause {DELAY_BETWEEN_REQUESTS}s (rate limit)...")
                time.sleep(DELAY_BETWEEN_REQUESTS)

        except Exception as e:
            print(f"         ❌ Erreur : {e}")
            print("         → Passage à la suivante...")
            time.sleep(10)
            continue

    # ── Nettoyage final ───────────────────────────────────────────────────
    avant = len(all_schools)
    all_schools = supprimer_doublons(all_schools)
    apres = len(all_schools)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_schools, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*60}")
    print(f"  ✅ GÉNÉRATION TERMINÉE")
    print(f"  📊 {apres} écoles uniques ({avant - apres} doublons supprimés)")
    print(f"  📁 Fichier : {OUTPUT_FILE}")
    print(f"{'='*60}")
    print("\n  Lancez maintenant l'application :")
    print("  streamlit run main.py\n")


if __name__ == "__main__":
    if API_KEY in {"", "METTEZ_VOTRE_CLE_ICI"}:
        print("❌ Clé API manquante !")
        print("   Ouvrez .streamlit/secrets.toml et ajoutez votre clé Gemini.")
    else:
        generate_full_database()
