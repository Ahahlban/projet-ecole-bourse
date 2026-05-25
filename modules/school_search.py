import google.generativeai as genai
import streamlit as st

from modules.utils import (
    extract_json_from_text,
    extract_numeric_amount,
    fits_access_mission,
    format_list_as_text,
    normalize_school_result,
)


def initialize_search_state():
    if "results" not in st.session_state:
        st.session_state.results = []
    if "last_query" not in st.session_state:
        st.session_state.last_query = ""
    if "search_filters" not in st.session_state:
        st.session_state.search_filters = {
            "city": "",
            "country": "",
            "degree_level": "",
            "language": "",
            "budget_max": "",
            "scholarship_only": False,
        }


def store_search_context(results: list[dict]):
    context_parts = []

    for i, result in enumerate(results, 1):
        context_parts.append(
            f"Résultat {i}:\n"
            f"  - Établissement: {result.get('school_name', 'Non détecté')}\n"
            f"  - URL officielle: {result.get('url', 'N/A')}\n"
            f"  - Localisation: {result.get('location', 'Non détecté')}\n"
            f"  - Pays: {result.get('country', 'Non détecté')}\n"
            f"  - Type d'établissement: {result.get('school_type', 'Non détecté')}\n"
            f"  - Programmes: {format_list_as_text(result.get('programs', []))}\n"
            f"  - Niveaux d'études: {format_list_as_text(result.get('degree_levels', []))}\n"
            f"  - Langue d'enseignement: {result.get('language_of_instruction', 'Non détecté')}\n"
            f"  - Frais de scolarité: {result.get('tuition_fee', 'Non détecté')}\n"
            f"  - Bourse disponible: {result.get('scholarship_available', 'À vérifier')}\n"
            f"  - Éligibilité: {result.get('eligibility', 'Non détecté')}\n"
            f"  - Date limite: {result.get('deadline', 'Non détecté')}\n"
            f"  - Durée: {result.get('duration', 'Non détecté')}\n"
            f"  - Résumé: {result.get('summary', 'Non détecté')}\n"
        )

    st.session_state.search_context = "\n".join(context_parts)


def _clean_optional_value(value: str) -> str:
    if value is None:
        return ""
    value = str(value).strip()
    invalid_values = {
        "", "n/a", "non détecté", "non verifie", "non verifié", "non vérifié",
        "à vérifier", "a vérifier", "unknown", "null", "none"
    }
    return "" if value.lower() in invalid_values else value


def _infer_duration_if_possible(item: dict) -> str:
    duration = _clean_optional_value(item.get("duration", ""))
    if duration:
        return duration

    school_type = str(item.get("school_type", "")).lower()
    programs = " ".join(item.get("programs", [])) if isinstance(item.get("programs", []), list) else str(item.get("programs", ""))
    degree_levels = " ".join(item.get("degree_levels", [])) if isinstance(item.get("degree_levels", []), list) else str(item.get("degree_levels", ""))
    combined = f"{school_type} {programs} {degree_levels}".lower()

    if "bachelor" in combined or "licence" in combined or "license" in combined:
        return "3 ans"
    if "master" in combined:
        return "2 ans"
    if "doctorat" in combined or "phd" in combined:
        return "3 ans ou plus"
    if "post-bac" in combined:
        return "5 ans"
    if "prépa" in combined or "prepa" in combined:
        return "3 ans"

    return ""


def _build_accessible_search_prompt(query: str, filters: dict) -> str:
    city = filters.get("city", "").strip()
    country = filters.get("country", "").strip()
    degree_level = filters.get("degree_level", "").strip()
    language = filters.get("language", "").strip()
    budget_max = str(filters.get("budget_max", "")).strip()
    scholarship_only = filters.get("scholarship_only", False)

    return f"""
Tu es un moteur de recherche académique spécialisé dans les écoles et universités accessibles financièrement.

Ta mission :
- trouver au maximum 10 établissements pertinents
- aider en priorité des étudiants avec budget limité
- répondre selon la requête utilisateur et les filtres
- retourner uniquement un JSON valide
- éviter tout ton conversationnel
- ne pas écrire de champs inconnus avec "Non vérifié"
- si une information n'est pas fiable, laisser simplement la chaîne vide ""
- ne pas inventer de montant précis de frais ou de bourse
- ne pas inventer d'URL
- exclure les établissements élitistes ou notoirement très coûteux quand ils ne sont pas adaptés à un budget modeste
- éviter des écoles comme HEC, ESSEC, ESCP, Ivy League et équivalents
- pour la durée uniquement, tu peux faire une inférence prudente si elle découle logiquement du type de cursus :
  - bachelor/licence = 3 ans
  - master = 2 ans
  - doctorat/phd = 3 ans ou plus
  - école d’ingénieur post-bac = 5 ans
  - cursus après prépa / cycle ingénieur = 3 ans

Filtres utilisateur :
- mots-clés : {query}
- ville : {city}
- pays : {country}
- niveau visé : {degree_level}
- langue : {language}
- budget maximum : {budget_max}
- bourse requise : {"oui" if scholarship_only else "non"}

Contraintes :
- si "bourse requise = oui", privilégie les établissements avec bourse connue ou plausiblement disponible
- si un budget maximum est donné, évite les options manifestement hors budget quand c'est connu
- privilégie les universités publiques, écoles accessibles, formations professionnalisantes et options avec aides financières
- pénalise fortement les établissements prestigieux à frais élevés qui correspondent mal à un profil sans grands moyens
- privilégie les établissements cohérents avec la ville/pays demandés
- ne retourne pas de texte hors JSON

Format JSON attendu :
[
  {{
    "school_name": "Nom de l'école",
    "location": "Ville ou région",
    "country": "Pays",
    "school_type": "Université / École / Institut",
    "programs": ["programme 1", "programme 2"],
    "degree_levels": ["Licence", "Master"],
    "language_of_instruction": "Langue principale",
    "tuition_fee": "",
    "application_fee": "",
    "scholarship_available": "",
    "scholarship_amount": "",
    "scholarship_details": "",
    "eligibility": "",
    "admission_requirements": "",
    "deadline": "",
    "duration": "",
    "official_contact": "",
    "summary": "Résumé utile en 2 ou 3 lignes",
    "url": "",
    "confidence": "Faible / Moyenne / Élevée"
  }}
]
"""


def find_accessible_school_results(query: str, filters: dict) -> tuple[str, list[dict]]:
    api_key = st.secrets.get("Gemini_API_Key")

    if not api_key:
        return "Erreur : clé API Gemini manquante.", []

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-flash-lite-latest")

        prompt = _build_accessible_search_prompt(query, filters)
        full_prompt = prompt + f"\n\nRequête utilisateur finale : {query}"

        response = model.generate_content(full_prompt)
        data = extract_json_from_text(response.text)

        if not isinstance(data, list):
            return "Aucun résultat exploitable.", []

        budget_max = filters.get("budget_max")
        max_budget = extract_numeric_amount(budget_max)

        results = []
        for item in data[:10]:
            if not isinstance(item, dict):
                continue

            normalized = normalize_school_result(item)

            for key in [
                "location", "country", "school_type", "language_of_instruction",
                "tuition_fee", "application_fee", "scholarship_available",
                "scholarship_amount", "scholarship_details", "eligibility",
                "admission_requirements", "deadline", "duration",
                "official_contact", "summary", "url", "confidence"
            ]:
                normalized[key] = _clean_optional_value(normalized.get(key, ""))

            normalized["duration"] = _infer_duration_if_possible(normalized)

            if filters.get("scholarship_only"):
                scholarship_value = normalized.get("scholarship_available", "").lower()
                if scholarship_value not in {"oui", "possible", "à vérifier", "a vérifier"}:
                    continue

            if not fits_access_mission(normalized, max_budget=max_budget):
                continue

            results.append(normalized)

        if not results:
            return "0 résultat trouvé.", []

        return f"{len(results)} résultats trouvés", results

    except Exception as error:
        return f"Erreur technique : {str(error)}", []


def _display_if_present(label: str, value: str):
    cleaned = _clean_optional_value(value)
    if cleaned:
        st.write(f"**{label}** {cleaned}")


def _display_list_if_present(label: str, value):
    if isinstance(value, list):
        value = [str(v).strip() for v in value if str(v).strip()]
        if value:
            st.write(f"**{label}** {', '.join(value)}")


def render_school_results(results: list[dict]):
    if not results:
        st.info("Aucun résultat à afficher.")
        return

    st.markdown("### Établissements proposés")

    for index, school in enumerate(results, 1):
        with st.container(border=True):
            st.markdown(f"#### {index}. {school.get('school_name', 'Établissement non détecté')}")

            subtitle_parts = []
            if _clean_optional_value(school.get("location", "")):
                subtitle_parts.append(school["location"])
            if _clean_optional_value(school.get("country", "")):
                subtitle_parts.append(school["country"])
            if _clean_optional_value(school.get("school_type", "")):
                subtitle_parts.append(school["school_type"])

            if subtitle_parts:
                st.caption(" • ".join(subtitle_parts))

            col1, col2 = st.columns(2)

            with col1:
                _display_list_if_present("Programmes :", school.get("programs", []))
                _display_list_if_present("Niveaux :", school.get("degree_levels", []))
                _display_if_present("Langue :", school.get("language_of_instruction", ""))
                _display_if_present("Durée :", school.get("duration", ""))

            with col2:
                _display_if_present("Frais de scolarité :", school.get("tuition_fee", ""))
                _display_if_present("Frais de dossier :", school.get("application_fee", ""))
                _display_if_present("Bourse :", school.get("scholarship_available", ""))
                _display_if_present("Montant bourse :", school.get("scholarship_amount", ""))

            _display_if_present("Éligibilité :", school.get("eligibility", ""))
            _display_if_present("Admission :", school.get("admission_requirements", ""))
            _display_if_present("Date limite :", school.get("deadline", ""))
            _display_if_present("Détails bourse :", school.get("scholarship_details", ""))
            _display_if_present("Résumé :", school.get("summary", ""))
            _display_if_present("Contact :", school.get("official_contact", ""))
            _display_if_present("URL :", school.get("url", ""))


def render_school_search_page():
    initialize_search_state()

    st.subheader("Recherche d'écoles accessibles")
    st.caption("Cette recherche privilégie les établissements cohérents avec un budget limité et les aides disponibles.")

    query = st.text_input(
        "Que recherchez-vous ?",
        value=st.session_state.get("last_query", ""),
        placeholder="Exemple : licence informatique publique, master data science avec bourse..."
    )

    with st.expander("Filtres avancés"):
        col1, col2, col3 = st.columns(3)

        with col1:
            city = st.text_input("Ville", value=st.session_state.search_filters.get("city", ""))
            country = st.text_input("Pays", value=st.session_state.search_filters.get("country", ""))

        with col2:
            degree_level = st.selectbox(
                "Niveau visé",
                ["", "Licence", "Master", "Doctorat", "Formation courte"],
                index=["", "Licence", "Master", "Doctorat", "Formation courte"].index(
                    st.session_state.search_filters.get("degree_level", "")
                    if st.session_state.search_filters.get("degree_level", "") in ["", "Licence", "Master", "Doctorat", "Formation courte"]
                    else ""
                )
            )
            language = st.text_input("Langue", value=st.session_state.search_filters.get("language", ""))

        with col3:
            budget_max = st.text_input("Budget annuel max (€)", value=st.session_state.search_filters.get("budget_max", ""))
            scholarship_only = st.checkbox(
                "Afficher seulement les options avec bourse",
                value=st.session_state.search_filters.get("scholarship_only", False),
            )

    if st.button("Lancer la recherche", use_container_width=True):
        filters = {
            "city": city,
            "country": country,
            "degree_level": degree_level,
            "language": language,
            "budget_max": budget_max,
            "scholarship_only": scholarship_only,
        }
        st.session_state.search_filters = filters
        st.session_state.last_query = query

        with st.spinner("Analyse des établissements en cours..."):
            message, results = find_accessible_school_results(query, filters)
            st.session_state.results = results
            store_search_context(results)

        st.success(message)

    render_school_results(st.session_state.get("results", []))
