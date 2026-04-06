"""
SCRIPT 2 — search.py
====================
Filtre la base de données locale (JSON) sans aucun appel internet.
C'est le cœur "low-tech" du projet.
"""

import json
import os

DATABASE_FILE = "data/schools.json"


def load_database() -> list[dict]:
    """
    Charge le fichier schools.json en mémoire.
    Si le fichier n'existe pas, retourne une liste vide.
    """
    if not os.path.exists(DATABASE_FILE):
        return []

    with open(DATABASE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data if isinstance(data, list) else []


def filter_schools(
    schools: list[dict],
    categorie: str = "",
    pays: str = "",
    langue: str = "",
    niveau: str = "",
    bourse_seulement: bool = False,
    budget_max: str = "",
) -> list[dict]:
    """
    Filtre la liste d'écoles selon les critères de l'étudiant.
    Tout se passe en local, zéro connexion nécessaire.

    Paramètres :
    - categorie     : ex. "informatique"
    - pays          : ex. "France"
    - langue        : ex. "Français"
    - niveau        : ex. "Master"
    - bourse_seulement : True = ne garder que les écoles avec bourse
    - budget_max    : ex. "5000" (en euros/an)
    """
    results = []

    for school in schools:

        # ── Filtre catégorie ──────────────────────────────────────────
        if categorie:
            cat_school = str(school.get("categorie", "")).lower()
            if categorie.lower() not in cat_school:
                continue

        # ── Filtre pays ───────────────────────────────────────────────
        if pays:
            pays_school = str(school.get("pays", "")).lower()
            if pays.lower() not in pays_school:
                continue

        # ── Filtre langue ─────────────────────────────────────────────
        if langue:
            langue_school = str(school.get("langue", "")).lower()
            if langue.lower() not in langue_school:
                continue

        # ── Filtre niveau ─────────────────────────────────────────────
        if niveau:
            niveaux_school = school.get("niveau", [])
            if isinstance(niveaux_school, list):
                niveaux_str = " ".join(niveaux_school).lower()
            else:
                niveaux_str = str(niveaux_school).lower()
            if niveau.lower() not in niveaux_str:
                continue

        # ── Filtre bourse uniquement ──────────────────────────────────
        if bourse_seulement:
            bourse = str(school.get("bourse_disponible", "")).lower()
            if bourse not in {"oui", "possible"}:
                continue

        # ── Filtre budget ─────────────────────────────────────────────
        if budget_max:
            try:
                budget_limite = float(budget_max)
                frais_str = str(school.get("frais_annuels", ""))
                # Extraire le nombre dans la chaîne
                import re
                nombres = re.findall(r"\d+", frais_str.replace(" ", "").replace(",", ""))
                if nombres:
                    frais = float(nombres[0])
                    if frais > budget_limite:
                        continue
            except (ValueError, TypeError):
                pass  # Si on ne peut pas comparer, on garde l'école

        results.append(school)

    return results


def search(query: str, filters: dict) -> list[dict]:
    """
    Fonction principale : charge la base et filtre.

    query   : texte libre tapé par l'étudiant
    filters : dict avec les clés categorie, pays, langue, niveau,
              bourse_seulement, budget_max
    """
    schools = load_database()

    if not schools:
        return []

    # Filtre par texte libre dans nom, résumé, catégorie
    if query.strip():
        q = query.lower()
        schools = [
            s for s in schools
            if q in str(s.get("nom", "")).lower()
            or q in str(s.get("resume", "")).lower()
            or q in str(s.get("categorie", "")).lower()
            or q in str(s.get("pays", "")).lower()
        ]

    # Filtres avancés
    schools = filter_schools(
        schools,
        categorie=filters.get("categorie", ""),
        pays=filters.get("pays", ""),
        langue=filters.get("langue", ""),
        niveau=filters.get("niveau", ""),
        bourse_seulement=filters.get("bourse_seulement", False),
        budget_max=filters.get("budget_max", ""),
    )

    return schools
