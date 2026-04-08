import re

import google.generativeai as genai
import streamlit as st

from modules.data_utils import extract_json_from_text, normalize_school, list_to_text


def init_search_state():
    if "results" not in st.session_state:
        st.session_state.results = []
    if "last_query" not in st.session_state:
        st.session_state.last_query = ""
    if "search_context" not in st.session_state:
        st.session_state.search_context = ""
    if "comparison_selection" not in st.session_state:
        st.session_state.comparison_selection = []
    if "display_limit" not in st.session_state:
        st.session_state.display_limit = 5
    if "search_filters" not in st.session_state:
        st.session_state.search_filters = {
            "city": "",
            "country": "",
            "degree_level": "",
            "language": "",
            "budget_max": "",
            "scholarship_only": False,
        }


def update_results_context(results: list[dict]):
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
            f"  - Frais de dossier: {r.get('application_fee', 'Non détecté')}\n"
            f"  - Bourse disponible: {r.get('scholarship_available', 'À vérifier')}\n"
            f"  - Montant bourse: {r.get('scholarship_amount', 'Non détecté')}\n"
            f"  - Conditions d'admission: {r.get('admission_requirements', 'Non détecté')}\n"
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
        "", "n/a", "non détecté", "non verifie", "non vérifié",
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


def _extract_numeric_amount(value):
    if value is None:
        return None

    text = str(value).strip().lower()
    if text in {"", "n/a", "non détecté", "non vérifié", "à vérifier"}:
        return None

    matches = re.findall(r"[\d]+(?:[\s.,]\d+)*", text)
    if not matches:
        return None

    try:
        cleaned = matches[0].replace(" ", "").replace(",", ".")
        return float(cleaned)
    except ValueError:
        return None


def _build_school_search_prompt(query: str, filters: dict) -> str:
    city = filters.get("city", "").strip()
    country = filters.get("country", "").strip()
    degree_level = filters.get("degree_level", "").strip()
    language = filters.get("language", "").strip()
    budget_max = str(filters.get("budget_max", "")).strip()
    scholarship_only = filters.get("scholarship_only", False)

    return f"""
Tu es un moteur de recherche académique spécialisé dans les écoles et universités pour étudiants internationaux à budget limité.

Ta mission :
- trouver au maximum 10 établissements pertinents
- privilégier les options adaptées aux étudiants à faible budget
- valoriser les établissements avec frais réduits, bourses, exonérations, ou coûts raisonnables
- répondre selon la requête utilisateur et les filtres
- retourner uniquement un JSON valide
- éviter tout ton conversationnel
- si une information n'est pas fiable, laisser simplement la chaîne vide ""
- ne pas inventer de montant précis de frais ou de bourse
- ne pas inventer d'URL
- privilégier des liens officiels ou pages d'admission quand disponibles
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

Contraintes importantes :
- priorité aux établissements compatibles avec un budget étudiant faible
- si un budget maximum est donné, favoriser clairement les options dans cette limite
- si "bourse requise = oui", privilégier les établissements avec bourse connue ou plausiblement disponible
- afficher les conditions d’admission quand elles sont connues
- fournir un lien officiel vers l’école ou la page programme/admission quand possible
- privilégier les établissements cohérents avec la ville/pays demandés
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


def _compute_budget_priority_score(item: dict) -> int:
    score = 0

    tuition = str(item.get("tuition_fee", "")).lower()
    scholarship = str(item.get("scholarship_available", "")).lower()
    scholarship_amount = str(item.get("scholarship_amount", "")).lower()
    country = str(item.get("country", "")).lower()
    summary = str(item.get("summary", "")).lower()

    if scholarship in {"oui", "possible"}:
        score += 3

    if scholarship_amount and scholarship_amount not in {"", "non détecté"}:
        score += 2

    low_cost_keywords = [
        "gratuit", "faible", "réduit", "abordable", "public",
        "low", "affordable", "scholarship", "funding"
    ]
    if any(word in tuition for word in low_cost_keywords):
        score += 2

    if any(word in summary for word in low_cost_keywords):
        score += 1

    if country in {"france", "allemagne", "belgique", "italie", "espagne"}:
        score += 1

    return score


def _compute_comparison_score(item: dict, filters: dict) -> int:
    score = 0

    tuition_num = _extract_numeric_amount(item.get("tuition_fee", ""))
    scholarship_num = _extract_numeric_amount(item.get("scholarship_amount", ""))
    budget_max_num = _extract_numeric_amount(filters.get("budget_max", ""))

    scholarship_status = str(item.get("scholarship_available", "")).lower()
    language = str(item.get("language_of_instruction", "")).lower()
    filter_language = str(filters.get("language", "")).lower()
    country = str(item.get("country", "")).lower()
    filter_country = str(filters.get("country", "")).lower()

    degree_values = item.get("degree_levels", [])
    if not isinstance(degree_values, list):
        degree_values = [str(degree_values)]
    degree_levels = " ".join(degree_values).lower()
    filter_degree = str(filters.get("degree_level", "")).lower()

    if scholarship_status in {"oui", "possible"}:
        score += 25

    if scholarship_num is not None:
        score += 15

    if tuition_num is not None:
        if tuition_num == 0:
            score += 25
        elif tuition_num <= 3000:
            score += 22
        elif tuition_num <= 7000:
            score += 18
        elif tuition_num <= 12000:
            score += 12
        else:
            score += 5

    if budget_max_num is not None and tuition_num is not None:
        if tuition_num <= budget_max_num:
            score += 20
        else:
            score -= 15

    if filter_language and filter_language in language:
        score += 10

    if filter_country and filter_country in country:
        score += 10

    if filter_degree and filter_degree in degree_levels:
        score += 10

    if _clean_optional_value(item.get("admission_requirements", "")):
        score += 5

    if _clean_optional_value(item.get("url", "")):
        score += 5

    return max(score, 0)


def search_schools(query: str, filters: dict) -> tuple[str, list[dict]]:
    api_key = st.secrets.get("Gemini_API_Key")

    if not api_key:
        return "Erreur : clé API Gemini manquante.", []

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-flash-lite-latest")

        prompt = _build_school_search_prompt(query, filters)
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

            normalized["budget_score"] = _compute_budget_priority_score(normalized)
            normalized["comparison_score"] = _compute_comparison_score(normalized, filters)

            results.append(normalized)

        if not results:
            return "0 résultat trouvé.", []

        results.sort(
            key=lambda x: (x.get("comparison_score", 0), x.get("budget_score", 0)),
            reverse=True
        )

        return f"{len(results)} résultats trouvés", results

    except Exception as e:
        return f"Erreur technique : {str(e)}", []


def add_school_to_comparison(school: dict):
    current = st.session_state.get("comparison_selection", [])
    school_name = school.get("school_name", "")

    already_exists = any(s.get("school_name") == school_name for s in current)
    if not already_exists:
        if len(current) < 3:
            current.append(school)
            st.session_state.comparison_selection = current
            st.success(f"{school_name} ajouté au comparateur.")
        else:
            st.warning("Vous pouvez comparer jusqu'à 3 écoles maximum.")


def _line(label: str, value):
    if isinstance(value, list):
        value = [str(v).strip() for v in value if str(v).strip()]
        if not value:
            return
        value = ", ".join(value)

    cleaned = _clean_optional_value(value)
    if cleaned:
        st.markdown(
            f'<div class="compact-line"><strong>{label}</strong> {cleaned}</div>',
            unsafe_allow_html=True,
        )


def _render_school_card(school: dict, index: int):
    school_name = school.get("school_name", "Établissement non détecté")
    location = _clean_optional_value(school.get("location", ""))
    country = _clean_optional_value(school.get("country", ""))
    school_type = _clean_optional_value(school.get("school_type", ""))
    url = _clean_optional_value(school.get("url", ""))
    summary = _clean_optional_value(school.get("summary", ""))

    subtitle_parts = [part for part in [location, country, school_type] if part]
    subtitle = " • ".join(subtitle_parts)

    with st.container(border=True):
        st.markdown(f"### {index}. {school_name}")
        if subtitle:
            st.caption(subtitle)

        st.markdown('<div class="compact-section">', unsafe_allow_html=True)
        st.markdown('<div class="compact-section-title">Informations</div>', unsafe_allow_html=True)

        _line("Programmes :", school.get("programs", []))
        _line("Niveaux :", school.get("degree_levels", []))
        _line("Langue :", school.get("language_of_instruction", ""))
        _line("Frais de scolarité :", school.get("tuition_fee", ""))
        _line("Frais de dossier :", school.get("application_fee", ""))
        _line("Bourse :", school.get("scholarship_available", ""))
        _line("Montant bourse :", school.get("scholarship_amount", ""))
        _line("Durée :", school.get("duration", ""))
        _line("Date limite :", school.get("deadline", ""))
        _line("Conditions d’admission :", school.get("admission_requirements", ""))
        _line("Éligibilité :", school.get("eligibility", ""))
        _line("Contact :", school.get("official_contact", ""))

        st.markdown("</div>", unsafe_allow_html=True)

        if summary:
            st.markdown('<div class="compact-section">', unsafe_allow_html=True)
            st.markdown('<div class="compact-section-title">Résumé</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="school-summary">{summary}</div>',
                unsafe_allow_html=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)

        action_col1, action_col2 = st.columns([1, 1])

        with action_col1:
            if st.button("Ajouter au comparateur", key=f"compare_{index}", use_container_width=True):
                add_school_to_comparison(school)

        with action_col2:
            if url:
                st.markdown(
                    f'<div class="school-link"><a href="{url}" target="_blank">Lien officiel</a></div>',
                    unsafe_allow_html=True,
                )


def render_school_results(results: list[dict]):
    if not results:
        st.info("Aucun résultat à afficher.")
        return

    st.markdown("### Résultats")
    st.caption("Les résultats sont triés pour mettre en avant les options les plus pertinentes pour un budget étudiant limité.")

    total_results = len(results)
    current_limit = st.session_state.get("display_limit", 5)

    available_limits = [3, 5, 10]
    available_limits = [x for x in available_limits if x <= total_results]

    if not available_limits:
        available_limits = [total_results]

    if current_limit not in available_limits:
        current_limit = available_limits[0]
        st.session_state.display_limit = current_limit

    top_left, top_right = st.columns([2, 1])
    with top_left:
        st.write(f"**{total_results} école(s) trouvée(s)**")
    with top_right:
        selected_limit = st.selectbox(
            "Nombre d’écoles à afficher",
            options=available_limits,
            index=available_limits.index(current_limit),
            key="display_limit_selector"
        )
        st.session_state.display_limit = selected_limit

    for i, school in enumerate(results[:st.session_state.display_limit], 1):
        _render_school_card(school, i)


def render_school_search_page():
    init_search_state()

    st.subheader("Recherche d'établissements")

    with st.form("search_form", clear_on_submit=False):
        query = st.text_input(
            "Requête",
            value=st.session_state.get("last_query", ""),
            placeholder="Exemple : master informatique bourse france, école ingénieur pas chère..."
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
        st.session_state.comparison_selection = []

        with st.spinner("Recherche en cours..."):
            message, results = search_schools(query, filters)

        st.session_state.results = results
        update_results_context(results)

        if message:
            st.info(message)

    render_school_results(st.session_state.get("results", []))