"""
SCRIPT 4 — export.py
====================
Génère un fichier .txt simple et lisible
que l'étudiant peut télécharger et lire hors-ligne
sur n'importe quel appareil (même vieux téléphone).
"""

from datetime import datetime


def generer_txt(schools: list[dict], query: str = "", filters: dict = {}) -> str:
    """
    Transforme la liste d'écoles filtrées en texte simple.

    Retourne une chaîne de caractères prête à être téléchargée.
    """
    lignes = []

    # ── En-tête ───────────────────────────────────────────────────────
    lignes.append("=" * 60)
    lignes.append("       EDUSEARCH — Résultats de votre recherche")
    lignes.append("=" * 60)
    lignes.append(f"Date       : {datetime.now().strftime('%d/%m/%Y à %H:%M')}")
    lignes.append(f"Recherche  : {query or 'Aucun mot-clé'}")

    # Résumé des filtres utilisés
    filtres_actifs = []
    if filters.get("categorie"):
        filtres_actifs.append(f"Domaine: {filters['categorie']}")
    if filters.get("pays"):
        filtres_actifs.append(f"Pays: {filters['pays']}")
    if filters.get("langue"):
        filtres_actifs.append(f"Langue: {filters['langue']}")
    if filters.get("niveau"):
        filtres_actifs.append(f"Niveau: {filters['niveau']}")
    if filters.get("bourse_seulement"):
        filtres_actifs.append("Bourse uniquement: Oui")
    if filters.get("budget_max"):
        filtres_actifs.append(f"Budget max: {filters['budget_max']} €/an")

    lignes.append(f"Filtres    : {' | '.join(filtres_actifs) if filtres_actifs else 'Aucun'}")
    lignes.append(f"Résultats  : {len(schools)} école(s) trouvée(s)")
    lignes.append("=" * 60)
    lignes.append("")

    if not schools:
        lignes.append("Aucune école ne correspond à vos critères.")
        lignes.append("Essayez d'élargir vos filtres.")
        return "\n".join(lignes)

    # ── Fiche de chaque école ─────────────────────────────────────────
    for i, school in enumerate(schools, 1):
        lignes.append(f"--- École #{i} {'─' * 40}")
        lignes.append(f"Nom          : {school.get('nom', 'Non précisé')}")
        lignes.append(f"Pays / Ville : {school.get('pays', '?')} — {school.get('ville', '?')}")
        lignes.append(f"Type         : {school.get('type', '?')}")
        lignes.append(f"Domaine      : {school.get('categorie', '?')}")

        # Niveaux sous forme de liste
        niveaux = school.get("niveau", [])
        if isinstance(niveaux, list):
            lignes.append(f"Niveaux      : {', '.join(niveaux) if niveaux else '?'}")
        else:
            lignes.append(f"Niveaux      : {niveaux}")

        lignes.append(f"Langue       : {school.get('langue', '?')}")
        lignes.append(f"Durée        : {school.get('duree', '?')}")
        lignes.append("")

        # Infos financières
        lignes.append("  INFORMATIONS FINANCIÈRES :")
        frais = school.get("frais_annuels", "")
        lignes.append(f"  Frais annuels    : {frais if frais else 'Non communiqué'}")

        bourse = school.get("bourse_disponible", "")
        lignes.append(f"  Bourse dispo     : {bourse if bourse else 'Non précisé'}")

        montant = school.get("montant_bourse", "")
        if montant:
            lignes.append(f"  Montant bourse   : {montant}")
        lignes.append("")

        # Infos candidature
        lignes.append("  CANDIDATURE :")
        lignes.append(f"  Conditions       : {school.get('conditions_admission', 'Voir site officiel')}")
        date = school.get("date_limite", "")
        lignes.append(f"  Date limite      : {date if date else 'À vérifier sur le site'}")
        lignes.append("")

        # Résumé
        resume = school.get("resume", "")
        if resume:
            lignes.append("  POURQUOI CETTE ÉCOLE :")
            # Couper les longues lignes pour la lisibilité
            for segment in [resume[j:j+55] for j in range(0, len(resume), 55)]:
                lignes.append(f"  {segment}")
            lignes.append("")

        # Contact
        site = school.get("site_web", "")
        contact = school.get("contact", "")
        if site or contact:
            lignes.append("  CONTACT :")
            if site:
                lignes.append(f"  Site web : {site}")
            if contact:
                lignes.append(f"  Contact  : {contact}")
            lignes.append("")

        lignes.append("")

    # ── Pied de page ──────────────────────────────────────────────────
    lignes.append("=" * 60)
    lignes.append("  Ce fichier a été généré par EduSearch.")
    lignes.append("  Il peut être lu hors-ligne sur tout appareil.")
    lignes.append("=" * 60)

    return "\n".join(lignes)
