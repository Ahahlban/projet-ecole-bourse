import json
import re
import urllib.parse


def extract_json_from_text(text: str):
    """
    Extrait et decode un objet JSON depuis une chaine brute, gerant les blocs Markdown.

    Complexite : O(n) ou n = longueur du texte.
    Essaie d'abord un parsing direct, puis recherche regex en fallback.
    """
    if not text:
        raise ValueError("Reponse vide.")
    cleaned = text.strip().replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    match = re.search(r'(\[.*\]|\{.*\})', cleaned, re.DOTALL)
    if match:
        return json.loads(match.group(1))
    raise ValueError("Impossible d'extraire un JSON valide.")


def ensure_list(value) -> list:
    """
    Garantit que la valeur retournee est une liste propre de chaines.

    Complexite : O(n) ou n = nombre d'elements dans la liste.
    """
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    if value in [None, "", "Non detecte", "Non verifie", "N/A"]:
        return []
    return [str(value).strip()]


def generate_search_fallback_url(school_name: str, country: str, context: str = "") -> str:
    """
    Genere un lien de recherche Google cible vers la racine de l'ecole pour eviter les 404.

    Complexite : O(n) ou n = longueur des chaines concatenees.
    """
    query = f"{school_name} {country} {context}".strip()
    query_encoded = urllib.parse.quote_plus(query)
    return f"https://www.google.com/search?q={query_encoded}"


def normalize_school_result(item: dict) -> dict:
    """
    Normalise un resultat d'etablissement pour securiser les liens, les bourses, les frais et les dates.

    Complexite : O(1) - acces dictionnaire a cle fixe, nombre de champs constant.
    """
    school_name = item.get("school_name", "Non detecte")
    country = item.get("country", "")

    raw_url = item.get("url", "").strip()
    if not raw_url or raw_url in ["Non detecte", "N/A"] or not raw_url.startswith("http"):
        valid_url = generate_search_fallback_url(school_name, country, "official website home")
    else:
        valid_url = raw_url

    # On force toujours un lien Google Search pour les bourses.
    # Les URLs profondes generees par l'IA menent systematiquement vers des 404 ou pages login.
    # Un lien Google Search cible est toujours valide et amene vers les vraies pages de bourses.
    valid_scholarship_url = generate_search_fallback_url(
        school_name, country, "bourses aide financiere etudiants internationaux scholarships"
    )

    return {
        "school_name": school_name,
        "location": item.get("location", ""),
        "country": country,
        "school_type": item.get("school_type", ""),
        "programs": ensure_list(item.get("programs", [])),
        "degree_levels": ensure_list(item.get("degree_levels", [])),
        "language_of_instruction": item.get("language_of_instruction", ""),
        "tuition_fee": item.get("tuition_fee", ""),
        "tuition_fee_non_eu": item.get("tuition_fee_non_eu", ""),
        "application_fee": item.get("application_fee", ""),
        "scholarship_available": item.get("scholarship_available", "A verifier"),
        "scholarship_estimated_amount": item.get("scholarship_estimated_amount", ""),
        "scholarship_amount": item.get("scholarship_amount", item.get("scholarship_estimated_amount", "")),
        "scholarship_details": item.get("scholarship_details", ""),
        "scholarship_link": valid_scholarship_url,
        "eligibility": item.get("eligibility", ""),
        "admission_requirements": item.get("admission_requirements", ""),
        "deadline": item.get("deadline", ""),
        "duration": item.get("duration", ""),
        "official_contact": item.get("official_contact", ""),
        "summary": item.get("summary", ""),
        "url": valid_url,
        "confidence": item.get("confidence", ""),
    }


def format_list_as_text(value) -> str:
    """
    Convertit une liste ou une valeur en texte lisible CSV-safe.

    Complexite : O(n) ou n = nombre d'elements.
    """
    if isinstance(value, list):
        return ", ".join(str(v) for v in value) if value else ""
    return str(value) if value not in [None, ""] else ""


def extract_numeric_amount(value) -> float | None:
    """
    Extrait le premier nombre numerique d'une chaine (frais, bourse, budget).
    Gere les formats europeens (espaces, virgules, euros).

    Complexite : O(n) ou n = longueur de la chaine.
    Retourne None si aucun nombre trouve.
    """
    if value in [None, "", "N/A", "Non detecte", "Non verifie", "A verifier", "Non precise"]:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    cleaned_value = str(value).replace("\xa0", "").replace(" ", "").replace("\u202f", "")
    if any(x in cleaned_value.lower() for x in ["gratuit", "free"]):
        return 0.0
    numbers = re.findall(r"\d+(?:[.,]\d+)?", cleaned_value)
    if not numbers:
        return None
    try:
        return float(numbers[0].replace(",", "."))
    except ValueError:
        return None


def is_highly_selective_school(name: str) -> bool:
    """
    Detecte les ecoles tres selectves/elitistes par mots-cles.

    Complexite : O(k) ou k = nombre de mots-cles bloquants (constant).
    """
    normalized_name = str(name or "").lower()
    blocked_keywords = {
        "hec", "essec", "escp", "insead", "polytechnique",
        "harvard", "stanford", "mit", "princeton", "yale",
        "columbia", "caltech", "oxford", "cambridge"
    }
    return any(keyword in normalized_name for keyword in blocked_keywords)


def fits_access_mission(item: dict, max_budget: float | None = None) -> bool:
    """
    Verifie si un etablissement correspond aux criteres d'accessibilite financiere.
    Prend en compte les bourses pour compenser les frais.

    Complexite : O(1) - nombre d'operations constant par item.
    Retourne True si l'etablissement est accessible, False sinon.
    """
    school_name = item.get("school_name", "")
    fee_to_check = item.get("tuition_fee_non_eu", "") or item.get("tuition_fee", "")
    tuition_fee = extract_numeric_amount(fee_to_check)
    scholarship_status = str(item.get("scholarship_available", "")).strip().lower()
    scholarship_amount = extract_numeric_amount(
        item.get("scholarship_estimated_amount", "") or item.get("scholarship_amount", "")
    )

    if is_highly_selective_school(school_name):
        has_strong_financial_support = any(x in scholarship_status for x in ["oui", "possible", "disponible"])
        if tuition_fee is None or tuition_fee > 15000:
            return False
        if not has_strong_financial_support and tuition_fee > 8000:
            return False

    if max_budget is not None and max_budget > 0 and tuition_fee is not None:
        if tuition_fee > max_budget:
            if scholarship_amount is not None:
                return (tuition_fee - scholarship_amount) <= max_budget
            has_scholarship = any(x in scholarship_status for x in ["oui", "possible", "disponible"])
            if not has_scholarship:
                return False

    return True