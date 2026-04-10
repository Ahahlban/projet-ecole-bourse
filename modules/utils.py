import json
import re


def extract_json_from_text(text: str):
    if not text:
        raise ValueError("Réponse vide.")

    cleaned = text.strip()
    cleaned = cleaned.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    match = re.search(r'(\[.*\]|\{.*\})', cleaned, re.DOTALL)
    if match:
        return json.loads(match.group(1))

    raise ValueError("Impossible d'extraire un JSON valide.")


def ensure_list(value):
    if isinstance(value, list):
        return value
    if value in [None, "", "Non détecté", "Non vérifié"]:
        return []
    return [str(value)]


def normalize_school_result(item: dict) -> dict:
    return {
        "school_name": item.get("school_name", "Non détecté"),
        "location": item.get("location", ""),
        "country": item.get("country", ""),
        "school_type": item.get("school_type", ""),
        "programs": ensure_list(item.get("programs", [])),
        "degree_levels": ensure_list(item.get("degree_levels", [])),
        "language_of_instruction": item.get("language_of_instruction", ""),
        "tuition_fee": item.get("tuition_fee", ""),
        "application_fee": item.get("application_fee", ""),
        "scholarship_available": item.get("scholarship_available", ""),
        "scholarship_amount": item.get("scholarship_amount", ""),
        "scholarship_details": item.get("scholarship_details", ""),
        "eligibility": item.get("eligibility", ""),
        "admission_requirements": item.get("admission_requirements", ""),
        "deadline": item.get("deadline", ""),
        "duration": item.get("duration", ""),
        "official_contact": item.get("official_contact", ""),
        "summary": item.get("summary", ""),
        "url": item.get("url", ""),
        "confidence": item.get("confidence", ""),
    }


def format_list_as_text(value):
    if isinstance(value, list):
        return ", ".join(str(v) for v in value) if value else ""
    return value if value not in [None, ""] else ""


def extract_numeric_amount(value) -> float | None:
    if value in [None, "", "N/A", "Non détecté", "Non vérifié", "À vérifier", "Non précisé"]:
        return None

    numbers = re.findall(r"[\d]+(?:[\s.,]\d+)*", str(value).strip())
    if not numbers:
        return None

    try:
        return float(numbers[0].replace(" ", "").replace(",", "."))
    except ValueError:
        return None


def is_highly_selective_school(name: str) -> bool:
    normalized_name = str(name or "").lower()
    blocked_keywords = {
        "hec", "essec", "escp", "insead", "polytechnique",
        "harvard", "stanford", "mit", "princeton", "yale",
        "columbia", "caltech", "oxford", "cambridge"
    }
    return any(keyword in normalized_name for keyword in blocked_keywords)


def fits_access_mission(item: dict, max_budget: float | None = None) -> bool:
    school_name = item.get("school_name", "")
    tuition_fee = extract_numeric_amount(item.get("tuition_fee", ""))
    scholarship_status = str(item.get("scholarship_available", "")).strip().lower()

    if is_highly_selective_school(school_name):
        has_strong_financial_support = scholarship_status in {"oui", "possible"}
        if tuition_fee is None or tuition_fee > 15000:
            return False
        if not has_strong_financial_support and tuition_fee > 8000:
            return False

    if max_budget is not None and tuition_fee is not None and tuition_fee > max_budget:
        scholarship_offset = scholarship_status in {"oui", "possible"}
        if not scholarship_offset:
            return False

    return True
