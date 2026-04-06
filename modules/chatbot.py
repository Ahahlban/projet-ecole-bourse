"""
SCRIPT 3 — chatbot.py (version améliorée)
==========================================
Mini-bot intégré à l'application.
Répond avec les détails complets : montant bourse, conditions,
date limite, frais, contact, etc.
Fonctionne 100% hors-ligne.
"""


# ── Réponses fixes pour salutations ───────────────────────────────────
REPONSES_FIXES = {
    "bonjour": "Bonjour ! Je suis le bot EduSearch 🎓\nJe peux répondre à des questions sur les écoles affichées.\nEssayez : *Quelle école a une bourse ?* ou *Donne-moi les détails de l'école 1*",
    "aide":    "Je peux répondre à des questions comme :\n• Quelle école a une bourse ?\n• Quel est le montant de la bourse ?\n• Quelle est la moins chère ?\n• Quelles écoles sont en France ?\n• Donne-moi les détails de l'école 1\n• Quelles sont les conditions d'admission ?",
    "merci":   "Avec plaisir ! Bonne continuation 🌟",
    "au revoir": "Bonne chance pour vos études ! 👋",
}


# ══════════════════════════════════════════════════════════════════════
# Fonctions utilitaires
# ══════════════════════════════════════════════════════════════════════

def _val(school: dict, cle: str, defaut: str = "Non précisé") -> str:
    """Retourne la valeur d'un champ ou un texte par défaut."""
    v = school.get(cle, "")
    if not v or str(v).strip().lower() in {"", "none", "null", "non précisé"}:
        return defaut
    return str(v).strip()


def _niveaux(school: dict) -> str:
    """Formate les niveaux d'études."""
    niveaux = school.get("niveau", [])
    if isinstance(niveaux, list):
        return ", ".join(niveaux) if niveaux else "Non précisé"
    return str(niveaux) if niveaux else "Non précisé"


def _fiche_complete(school: dict, numero: int = 0) -> str:
    """
    Génère une fiche complète et détaillée d'une école.
    C'est ce que le bot envoie quand l'étudiant veut tout savoir.
    """
    titre = f"{'─'*40}\n🏫 {_val(school, 'nom')}"
    if numero:
        titre = f"{'─'*40}\n🏫 École #{numero} — {_val(school, 'nom')}"

    bourse = _val(school, "bourse_disponible", "").lower()
    icone_bourse = "✅" if bourse == "oui" else "⚠️" if bourse == "possible" else "❌"

    lignes = [
        titre,
        f"📍 Localisation    : {_val(school, 'ville')}, {_val(school, 'pays')}",
        f"🏷️  Type            : {_val(school, 'type')}",
        f"📚 Domaine         : {_val(school, 'categorie')}",
        f"🗣️  Langue          : {_val(school, 'langue')}",
        f"🎓 Niveaux         : {_niveaux(school)}",
        f"⌛ Durée           : {_val(school, 'duree')}",
        "",
        "💰 INFORMATIONS FINANCIÈRES",
        f"   Frais annuels   : {_val(school, 'frais_annuels')}",
        f"   {icone_bourse} Bourse dispo  : {_val(school, 'bourse_disponible')}",
        f"   💶 Montant bourse : {_val(school, 'montant_bourse')}",
        "",
        "📄 CANDIDATURE",
        f"   Conditions      : {_val(school, 'conditions_admission')}",
        f"   Date limite     : {_val(school, 'date_limite')}",
        "",
        f"📝 {_val(school, 'resume')}",
    ]

    site = _val(school, "site_web", "")
    contact = _val(school, "contact", "")
    if site != "Non précisé" or contact != "Non précisé":
        lignes.append("")
        lignes.append("📞 CONTACT")
        if site != "Non précisé":
            lignes.append(f"   Site web : {site}")
        if contact != "Non précisé":
            lignes.append(f"   Contact  : {contact}")

    return "\n".join(lignes)


def _fiche_bourse(school: dict) -> str:
    """Fiche focalisée uniquement sur les infos de bourse."""
    bourse = _val(school, "bourse_disponible", "").lower()
    icone = "✅" if bourse == "oui" else "⚠️" if bourse == "possible" else "❌"

    return (
        f"{icone} **{_val(school, 'nom')}** ({_val(school, 'pays')})\n"
        f"   • Bourse dispo   : {_val(school, 'bourse_disponible')}\n"
        f"   • Montant        : {_val(school, 'montant_bourse')}\n"
        f"   • Conditions     : {_val(school, 'conditions_admission')}\n"
        f"   • Date limite    : {_val(school, 'date_limite')}\n"
        f"   • Frais annuels  : {_val(school, 'frais_annuels')}"
    )


# ══════════════════════════════════════════════════════════════════════
# Fonctions de recherche dans la base
# ══════════════════════════════════════════════════════════════════════

def _ecoles_avec_bourse(schools: list[dict]) -> list[dict]:
    return [
        s for s in schools
        if str(s.get("bourse_disponible", "")).lower() in {"oui", "possible"}
    ]


def _ecole_moins_chere(schools: list[dict]) -> dict | None:
    import re
    moins_chere = None
    frais_min = float("inf")
    for school in schools:
        frais_str = str(school.get("frais_annuels", ""))
        nombres = re.findall(r"\d+", frais_str.replace(" ", "").replace(",", ""))
        if nombres:
            frais = float(nombres[0])
            if frais < frais_min:
                frais_min = frais
                moins_chere = school
    return moins_chere


def _ecoles_par_pays(schools: list[dict], pays: str) -> list[dict]:
    return [s for s in schools if pays.lower() in str(s.get("pays", "")).lower()]


def _ecole_par_numero(schools: list[dict], numero: int) -> dict | None:
    if 1 <= numero <= len(schools):
        return schools[numero - 1]
    return None


# ══════════════════════════════════════════════════════════════════════
# Fonction principale du bot
# ══════════════════════════════════════════════════════════════════════

def repondre(question: str, schools: list[dict]) -> str:
    """
    Analyse la question de l'étudiant et retourne une réponse détaillée.

    question : texte posé par l'étudiant
    schools  : résultats actuellement affichés dans l'appli
    """
    import re

    q = question.lower().strip()

    if not schools:
        return "Aucun résultat chargé. Lancez d'abord une recherche avec les filtres."

    # ── Réponses fixes ────────────────────────────────────────────────
    for mot, reponse in REPONSES_FIXES.items():
        if mot in q:
            return reponse

    # ── Fiche complète par numéro (ex: "détails école 2") ────────────
    match_numero = re.search(r"(\d+)", q)
    if match_numero and any(mot in q for mot in [
        "école", "détail", "detail", "fiche", "info", "montre", "numéro", "numero", "#"
    ]):
        numero = int(match_numero.group(1))
        school = _ecole_par_numero(schools, numero)
        if school:
            return _fiche_complete(school, numero)
        return f"Il n'y a pas d'école #{numero} dans les résultats (il y en a {len(schools)})."

    # ── Montant ou détail de la bourse ────────────────────────────────
    if any(mot in q for mot in [
        "montant", "combien la bourse", "bourse de combien",
        "détail bourse", "detail bourse", "valeur bourse", "montant bourse"
    ]):
        ecoles = _ecoles_avec_bourse(schools)
        if not ecoles:
            return "Aucune école avec bourse dans les résultats actuels."
        lignes = [f"💶 Détail des bourses ({len(ecoles)} école(s)) :\n"]
        for school in ecoles:
            lignes.append(_fiche_bourse(school))
            lignes.append("")
        return "\n".join(lignes)

    # ── Bourses disponibles (question générale) ───────────────────────
    if any(mot in q for mot in ["bourse", "financement", "aide financière", "subvention"]):
        ecoles = _ecoles_avec_bourse(schools)
        if not ecoles:
            return "Aucune école avec bourse dans les résultats actuels."
        lignes = [f"🎁 {len(ecoles)} école(s) avec bourse :\n"]
        for school in ecoles:
            lignes.append(_fiche_bourse(school))
            lignes.append("")
        return "\n".join(lignes)

    # ── Conditions d'admission ────────────────────────────────────────
    if any(mot in q for mot in ["admission", "condition", "candidater", "dossier", "s'inscrire", "prérequis"]):
        lignes = ["📄 Conditions d'admission :\n"]
        for i, school in enumerate(schools[:6], 1):
            lignes.append(
                f"#{i} {_val(school, 'nom')}\n"
                f"   → Conditions  : {_val(school, 'conditions_admission')}\n"
                f"   → Date limite : {_val(school, 'date_limite')}"
            )
            lignes.append("")
        return "\n".join(lignes)

    # ── Dates limites ─────────────────────────────────────────────────
    if any(mot in q for mot in ["date", "deadline", "délai", "limite", "quand candidater"]):
        lignes = ["⏳ Dates limites de candidature :\n"]
        for i, school in enumerate(schools[:8], 1):
            lignes.append(f"#{i} {_val(school, 'nom')} → {_val(school, 'date_limite')}")
        return "\n".join(lignes)

    # ── Frais / coût ──────────────────────────────────────────────────
    if any(mot in q for mot in ["frais", "coût", "prix", "tarif", "cher"]):
        lignes = ["💰 Frais annuels par école :\n"]
        for i, school in enumerate(schools[:8], 1):
            frais = _val(school, "frais_annuels")
            bourse = _val(school, "bourse_disponible", "").lower()
            icone = "✅" if bourse == "oui" else "⚠️" if bourse == "possible" else "  "
            lignes.append(f"{icone} #{i} {_val(school, 'nom')} → {frais}")
        return "\n".join(lignes)

    # ── Moins chère ───────────────────────────────────────────────────
    if any(mot in q for mot in ["moins cher", "pas cher", "économique", "abordable", "accessible"]):
        school = _ecole_moins_chere(schools)
        if school:
            return "💰 L'école la plus abordable :\n\n" + _fiche_complete(school)
        return "Je n'ai pas de données de frais précises pour comparer."

    # ── Contact / site web ────────────────────────────────────────────
    if any(mot in q for mot in ["contact", "site", "email", "mail", "téléphone"]):
        lignes = ["📞 Contacts officiels :\n"]
        for i, school in enumerate(schools[:6], 1):
            site = _val(school, "site_web", "")
            contact = _val(school, "contact", "")
            infos = []
            if site not in {"Non précisé", ""}:
                infos.append(f"🌐 {site}")
            if contact not in {"Non précisé", ""}:
                infos.append(f"✉️ {contact}")
            if infos:
                lignes.append(f"#{i} {_val(school, 'nom')}")
                for info in infos:
                    lignes.append(f"   {info}")
                lignes.append("")
        return "\n".join(lignes) if len(lignes) > 1 else "Aucun contact disponible."

    # ── Pays ──────────────────────────────────────────────────────────
    pays_detectes = [
        "france", "canada", "maroc", "belgique", "tunisie",
        "sénégal", "senegal", "allemagne", "espagne", "suisse",
        "algérie", "algerie", "mali", "cameroun", "côte d'ivoire",
        "états-unis", "etats-unis", "royaume-uni", "pays-bas"
    ]
    for pays in pays_detectes:
        if pays in q:
            ecoles = _ecoles_par_pays(schools, pays)
            if ecoles:
                lignes = [f"🌍 {len(ecoles)} école(s) en {pays.capitalize()} :\n"]
                for i, school in enumerate(ecoles, 1):
                    lignes.append(
                        f"#{i} {_val(school, 'nom')}\n"
                        f"   Frais : {_val(school, 'frais_annuels')} | "
                        f"Bourse : {_val(school, 'bourse_disponible')}"
                    )
                    lignes.append("")
                return "\n".join(lignes)
            return f"Aucune école trouvée en {pays.capitalize()} dans les résultats."

    # ── Résumé général ────────────────────────────────────────────────
    if any(mot in q for mot in ["combien", "résumé", "résume", "total", "liste", "toutes", "tout"]):
        nb = len(schools)
        avec_bourse = len(_ecoles_avec_bourse(schools))
        pays_uniques = list({s.get("pays", "?") for s in schools})[:5]
        return (
            f"📊 Résumé des résultats :\n\n"
            f"• {nb} école(s) au total\n"
            f"• {avec_bourse} avec bourse disponible\n"
            f"• Pays représentés : {', '.join(pays_uniques)}\n\n"
            f"Tapez *détails école 1* pour la fiche complète d'une école."
        )

    # ── Recherche par fragment de nom ─────────────────────────────────
    for school in schools:
        nom = str(school.get("nom", "")).lower()
        mots_nom = [m for m in nom.split() if len(m) > 4]
        for mot in mots_nom:
            if mot in q:
                return _fiche_complete(school)

    # ── Réponse par défaut ────────────────────────────────────────────
    return (
        "Je n'ai pas compris votre question 🤔\n\n"
        "Voici ce que je sais faire :\n"
        "• *Quelle école a une bourse ?*\n"
        "• *Quel est le montant de la bourse ?*\n"
        "• *Quelle est la moins chère ?*\n"
        "• *Conditions d'admission ?*\n"
        "• *Dates limites ?*\n"
        "• *Écoles en France ?*\n"
        "• *Détails école 2* → fiche complète de l'école #2"
    )
