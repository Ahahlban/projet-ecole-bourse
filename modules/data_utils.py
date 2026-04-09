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

    match = re.search(r"(\[.*\]|\{.*\})", cleaned, re.DOTALL)
    if match:
        return json.loads(match.group(1))

    raise ValueError("Impossible d'extraire un JSON valide.")


def ensure_list(value):
    if isinstance(value, list):
        return value
    if value in [None, "", "Non détecté", "Non vérifié"]:
        return []
    return [str(value)]


def normalize_school(item: dict) -> dict:
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


def list_to_text(value):
    if isinstance(value, list):
        return ", ".join(str(v) for v in value) if value else ""
    return value if value not in [None, ""] else ""