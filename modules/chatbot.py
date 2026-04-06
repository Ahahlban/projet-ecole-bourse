import google.generativeai as genai
import streamlit as st

from modules.utils import extract_json_from_text, normalize_school, list_to_text


def init_chatbot():
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


def update_search_context(results: list[dict]):
    context_parts = []

    for i, r in enumerate(results, 1):
        context_parts.append(
            f"Résultat {i}:\n"
            f"  - Établissement: {r.get('school_name', 'Non détecté')}\n"
            f"  - URL officielle: {r.get('url', 'N/A')}\n"
            f"  - Localisation: {r.get('location', 'Non détecté')}\n"
            f"  - Pays: {r.get('country', 'Non détecté')}\n"
            f"  - Type d'établissement: {r.get('school_type', 'Non détecté')}\n"
            f"  - Programmes: {list_to_text(r.get('programs', []))}\n"
            f"  - Niveaux d'études: {list_to_text(r.get('degree_levels', []))}\n"
            f"  - Langue d'enseignement: {r.get('language_of_instruction', 'Non détecté')}\n"
            f"  - Frais de scolarité: {r.get('tuition_fee', 'Non détecté')}\n"
            f"  - Bourse disponible: {r.get('scholarship_available', 'À vérifier')}\n"
            f"  - Éligibilité: {r.get('eligibility', 'Non détecté')}\n"
            f"  - Date limite: {r.get('deadline', 'Non détecté')}\n"
            f"  - Durée: {r.get('duration', 'Non détecté')}\n"
            f"  - Résumé: {r.get('summary', 'Non détecté')}\n"
        )

    st.session_state.search_context = "\n".join(context_parts)


def _clean_optional_value(value: str) -> str:
    if value is None:
        return ""
    value = str(value).strip()
    invalid_values = {
        "", "n/a", "non détecté", "non verifié", "non vérifié",
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

    if "bachelor" in combined or "licence" in combined or "licence" in combined:
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


def _build_search_prompt(query: str, filters: dict) -> str:
    city = filters.get("city", "").strip()
    country = filters.get("country", "").strip()
    degree_level = filters.get("degree_level", "").strip()
    language = filters.get("language", "").strip()
    budget_max = str(filters.get("budget_max", "")).strip()
    scholarship_only = filters.get("scholarship_only", False)

    return f"""
Tu es un moteur de recherche académique spécialisé dans les écoles et universités.

Ta mission :
- trouver au maximum 10 établissements pertinents
- répondre selon la requête utilisateur et les filtres
- retourner uniquement un JSON valide
- éviter tout ton conversationnel
- ne pas écrire de champs inconnus avec "Non vérifié"
- si une information n'est pas fiable, laisser simplement la chaîne vide ""
- ne pas inventer de montant précis de frais ou de bourse
- ne pas inventer d'URL
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


def generate_school_results(query: str, filters: dict) -> tuple[str, list[dict]]:
    api_key = st.secrets.get("Gemini_API_Key")

    if not api_key:
        return "Erreur : clé API Gemini manquante.", []

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-flash-lite-latest")

        prompt = _build_search_prompt(query, filters)
        full_prompt = prompt + f"\n\nRequête utilisateur finale : {query}"

        response = model.generate_content(full_prompt)
        data = extract_json_from_text(response.text)

        if not isinstance(data, list):
            return "Aucun résultat exploitable.", []

        results = []
        for item in data[:10]:
            if not isinstance(item, dict):
                continue

            normalized = normalize_school(item)

            # Nettoyage des champs optionnels
            for key in [
                "location", "country", "school_type", "language_of_instruction",
                "tuition_fee", "application_fee", "scholarship_available",
                "scholarship_amount", "scholarship_details", "eligibility",
                "admission_requirements", "deadline", "duration",
                "official_contact", "summary", "url", "confidence"
            ]:
                normalized[key] = _clean_optional_value(normalized.get(key, ""))

            normalized["duration"] = _infer_duration_if_possible(normalized)

            # Filtre bourse côté app si demandé
            if filters.get("scholarship_only"):
                scholarship_value = normalized.get("scholarship_available", "").lower()
                if scholarship_value not in {"oui", "possible", "à vérifier", "a vérifier"}:
                    continue

            results.append(normalized)

        if not results:
            return "0 résultat trouvé.", []

        return f"{len(results)} résultats trouvés", results

    except Exception as e:
        return f"Erreur technique : {str(e)}", []


def _display_if_present(label: str, value: str):
    cleaned = _clean_optional_value(value)
    if cleaned:
        st.write(f"**{label}** {cleaned}")


def _display_list_if_present(label: str, value):
    if isinstance(value, list):
        value = [str(v).strip() for v in value if str(v).strip()]
        if value:
            st.write(f"**{label}** {', '.join(value)}")


def render_school_cards(results: list[dict]):
    if not results:
        st.info("Aucun résultat à afficher.")
        return

    st.markdown("### Résultats")

    for i, school in enumerate(results, 1):
        with st.container(border=True):
            st.markdown(f"#### {i}. {school.get('school_name', 'Établissement non détecté')}")

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


def render_search_interface():
    init_chatbot()

    st.subheader("Recherche d'établissements")

    with st.form("search_form", clear_on_submit=False):
        query = st.text_input(
            "Requête",
            value=st.session_state.get("last_query", ""),
            placeholder="Exemple : informatique, école ingénieur, master data science..."
        )

        with st.expander("Filtres", expanded=True):
            col1, col2, col3 = st.columns(3)

            with col1:
                city = st.text_input(
                    "Ville",
                    value=st.session_state.search_filters.get("city", "")
                )
                degree_level = st.selectbox(
                    "Niveau visé",
                    ["", "Licence", "Bachelor", "Master", "Doctorat", "Ingénieur"],
                    index=["", "Licence", "Bachelor", "Master", "Doctorat", "Ingénieur"].index(
                        st.session_state.search_filters.get("degree_level", "")
                        if st.session_state.search_filters.get("degree_level", "") in ["", "Licence", "Bachelor", "Master", "Doctorat", "Ingénieur"]
                        else ""
                    )
                )

            with col2:
                country = st.text_input(
                    "Pays",
                    value=st.session_state.search_filters.get("country", "")
                )
                language = st.selectbox(
                    "Langue",
                    ["", "Français", "Anglais", "Espagnol", "Allemand", "Arabe"],
                    index=["", "Français", "Anglais", "Espagnol", "Allemand", "Arabe"].index(
                        st.session_state.search_filters.get("language", "")
                        if st.session_state.search_filters.get("language", "") in ["", "Français", "Anglais", "Espagnol", "Allemand", "Arabe"]
                        else ""
                    )
                )

            with col3:
                budget_max = st.text_input(
                    "Budget max annuel",
                    value=st.session_state.search_filters.get("budget_max", ""),
                    placeholder="Exemple : 10000 €"
                )
                scholarship_only = st.checkbox(
                    "Bourse uniquement",
                    value=st.session_state.search_filters.get("scholarship_only", False)
                )

        submitted = st.form_submit_button("Rechercher", use_container_width=True)

    if submitted:
        filters = {
            "city": city,
            "country": country,
            "degree_level": degree_level,
            "language": language,
            "budget_max": budget_max,
            "scholarship_only": scholarship_only,
        }

        st.session_state.last_query = query
        st.session_state.search_filters = filters

        with st.spinner("Recherche en cours..."):
            message, results = generate_school_results(query, filters)

        st.session_state.results = results
        update_search_context(results)

        if message:
            st.caption(message)

    render_school_cards(st.session_state.get("results", []))