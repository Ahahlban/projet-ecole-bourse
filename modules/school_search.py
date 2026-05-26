import streamlit as st
from google import genai
import pandas as pd
from modules.utils import (
    extract_json_from_text,
    extract_numeric_amount,
    fits_access_mission,
    format_list_as_text,
    normalize_school_result,
)

# --- REPERTOIRE COMPLET DES PAYS ---
PAYS_DU_MONDE = [
    "Indifferent", "Afghanistan", "Afrique du Sud", "Albanie", "Algerie", "Allemagne", "Andorre", "Angola",
    "Antigua-et-Barbuda", "Arabie Saoudite", "Argentine", "Armenie", "Australie", "Autriche", "Azerbaidjan",
    "Bahamas", "Bahrein", "Bangladesh", "Barbade", "Belgique", "Belize", "Benin", "Bhoutan", "Bielorussie",
    "Birmanie", "Bolivie", "Bosnie-Herzegovine", "Botswana", "Bresil", "Brunei", "Bulgarie", "Burkina Faso",
    "Burundi", "Cambodge", "Cameroun", "Canada", "Cap-Vert", "Chili", "Chine", "Chypre", "Colombie",
    "Comores", "Congo (Brazzaville)", "Congo (Kinshasa)", "Coree du Nord", "Coree du Sud", "Costa Rica",
    "Cote d'Ivoire", "Croatie", "Cuba", "Danemark", "Djibouti", "Dominique", "Egypte", "Emirats Arabes Unis",
    "Equateur", "Erythree", "Espagne", "Estonie", "Eswatini", "Etats-Unis", "Ethiopie", "Fidji", "Finlande",
    "France", "Gabon", "Gambie", "Georgie", "Ghana", "Grece", "Grenade", "Guatemala", "Guinee", "Guinee-Bissau",
    "Guinee Equatoriale", "Guyana", "Haiti", "Honduras", "Hongrie", "Inde", "Indonesie", "Irak", "Iran",
    "Irlande", "Islande", "Israel", "Italie", "Jamaique", "Japon", "Jordanie", "Kazakhstan", "Kenya",
    "Kirghizistan", "Kiribati", "Koweit", "Laos", "Lesotho", "Lettonie", "Liban", "Liberia", "Libye",
    "Liechtenstein", "Lituanie", "Luxembourg", "Macedoine du Nord", "Madagascar", "Malaisie", "Malawi",
    "Maldives", "Mali", "Malte", "Maroc", "Maurice", "Mauritanie", "Mexique", "Micronesie", "Moldavie",
    "Monaco", "Mongolie", "Montenegro", "Mozambique", "Namibie", "Nauru", "Nepal", "Nicaragua", "Niger",
    "Nigeria", "Norvege", "Nouvelle-Zelande", "Oman", "Ouganda", "Ouzbekistan", "Pakistan", "Palaos",
    "Palestine", "Panama", "Papouasie-Nouvelle-Guinee", "Paraguay", "Pays-Bas", "Perou", "Philippines",
    "Pologne", "Portugal", "Qatar", "Republique Centrafricaine", "Republique Dominicaine", "Republique Tcheque",
    "Roumanie", "Royaume-Uni", "Russie", "Rwanda", "Saint-Christophe-et-Nieve", "Sainte-Lucie",
    "Saint-Marin", "Saint-Vincent-et-les-Grenadines", "Salomon", "Samoa", "Sao Tome-et-Principe", "Senegal",
    "Serbie", "Seychelles", "Sierra Leone", "Singapour", "Slovaquie", "Slovenie", "Somalie", "Soudan",
    "Soudan du Sud", "Sri Lanka", "Suede", "Suisse", "Suriname", "Syrie", "Tadjikistan", "Taiwan",
    "Tanzanie", "Tchad", "Thailande", "Timor oriental", "Togo", "Tonga", "Trinite-et-Tobago", "Tunisie",
    "Turkmenistan", "Turquie", "Tuvalu", "Ukraine", "Uruguay", "Vanuatu", "Vatican", "Venezuela",
    "Vietnam", "Yemen", "Zambie", "Zimbabwe"
]

# --- REPERTOIRE COMPLET DES LANGUES ---
LANGUES_DU_MONDE = [
    "Indifferent", "Afrikaans", "Albanais", "Allemand", "Amharique", "Anglais", "Arabe", "Armenien",
    "Azeri", "Bengali", "Bielorusse", "Birman", "Bosnien", "Bulgare", "Catalan", "Chinois (Cantonais)",
    "Chinois (Mandarin)", "Cingalais", "Coreen", "Croate", "Danois", "Espagnol", "Estonien", "Finnois",
    "Francais", "Georgien", "Grec", "Gujarati", "Haoussa", "Hebreu", "Hindi", "Hongrois", "Indonesien",
    "Islandais", "Italien", "Japonais", "Javanais", "Khmer", "Kirghize", "Laotien", "Letton", "Lituanien",
    "Macedonien", "Malais", "Malayalam", "Malgache", "Maltais", "Marathi", "Mongol",
    "Neerlandais", "Nepalais", "Norvegien", "Ourdou", "Ouzbek", "Pachto", "Pendjabi", "Persan", "Polonais",
    "Portugais", "Roumain", "Russe", "Serbe", "Slovaque", "Slovene", "Somali", "Suedois", "Swahili",
    "Tadjik", "Tagalog (Philippin)", "Tamoul", "Tcheque", "Telugu", "Thai", "Turc", "Turkmene",
    "Ukrainien", "Vietnamien", "Xhosa", "Yoruba", "Zoulou"
]

# --- NIVEAUX D'ETUDES COURANTS ---
NIVEAUX_ETUDES = [
    "Indifferent",
    "BTS (Brevet de Technicien Superieur)",
    "BUT (Bachelor Universitaire de Technologie)",
    "Classe Preparatoire aux Grandes Ecoles (CPGE)",
    "Licence / Bachelor (Bac +3)",
    "Master (Bac +5 / MSc / MA)",
    "Doctorat (PhD)",
    "MBA (Master of Business Administration)",
    "Diplome d'Ingenieur",
    "Formation Courte / Certifiante",
    "Autre (preciser dans la recherche)"
]


def initialize_search_state():
    """
    Initialise les variables d'etat de session pour EduSearch.

    Complexite : O(k) ou k = nombre de cles a initialiser (constant).
    Appele une seule fois par session Streamlit.
    """
    if "results" not in st.session_state:
        st.session_state.results = []
    if "last_query" not in st.session_state:
        st.session_state.last_query = ""
    if "search_context" not in st.session_state:
        st.session_state.search_context = ""
    if "items_per_page" not in st.session_state:
        st.session_state.items_per_page = 5
    if "search_filters" not in st.session_state:
        st.session_state.search_filters = {
            "city": "",
            "country": "Indifferent",
            "degree_level": "Indifferent",
            "language": "Indifferent",
            "budget_max": "",
            "scholarship_only": False,
            "school_type": "Indifferent",
            "duration_max": "",
            "application_fee_max": "",
        }


def store_search_context(results: list[dict]):
    """
    Genere et stocke un contexte textuel structure des resultats pour l'IA de comparaison.

    Complexite : O(n) ou n = nombre de resultats.
    """
    context_parts = []
    for i, result in enumerate(results, 1):
        context_parts.append(
            f"Resultat {i}:\n"
            f"  - Etablissement: {result.get('school_name', 'Non detecte')}\n"
            f"  - URL principale: {result.get('url', 'N/A')}\n"
            f"  - Localisation: {result.get('location', 'Non detecte')}, {result.get('country', 'Non detecte')}\n"
            f"  - Date limite d'inscription: {result.get('deadline', 'Non detectee')}\n"
            f"  - Frais Extra-communautaires: {result.get('tuition_fee_non_eu', 'N/A')}\n"
            f"  - Bourse: {result.get('scholarship_available', 'A verifier')} (Est: {result.get('scholarship_estimated_amount', 'N/A')})\n"
        )
    st.session_state.search_context = "\n".join(context_parts)


def _clean_optional_value(value: str) -> str:
    """
    Nettoie une valeur optionnelle et retourne une chaine vide si invalide.

    Complexite : O(1).
    """
    if value is None:
        return ""
    value = str(value).strip()
    invalid_values = {
        "", "n/a", "non detecte", "non verifie", "non verifie", "non verifie",
        "a verifier", "unknown", "null", "none"
    }
    return "" if value.lower() in invalid_values else value


def _build_search_prompt(query: str, filters: dict) -> str:
    """
    Construit le prompt Gemini avec les filtres actifs uniquement.
    Les filtres "Indifferent" ou vides sont omis du prompt pour ne pas contraindre l'IA.

    Complexite : O(1) - construction de chaine a taille fixe.

    Points cles :
    - Demande explicitement 10 a 15 resultats minimum.
    - Utilise la recherche web pour trouver de vraies URLs de bourses.
    - Genere uniquement des URLs racines pour eviter les 404.
    """
    city = filters.get("city", "").strip()
    country = "" if filters.get("country") == "Indifferent" else filters.get("country", "")
    degree_level = filters.get("degree_level", "Indifferent")
    effective_level = "" if degree_level == "Indifferent" else degree_level
    language = "" if filters.get("language") == "Indifferent" else filters.get("language", "")
    budget_max = str(filters.get("budget_max", "")).strip()
    scholarship_only = filters.get("scholarship_only", False)
    school_type = "" if filters.get("school_type") == "Indifferent" else filters.get("school_type", "")


    # Construction des lignes de filtres actifs uniquement
    filter_lines = [f"- Mots-cles de recherche : {query}"]
    if effective_level:
        filter_lines.append(f"- Niveau d'etudes vise : {effective_level}")
    if city:
        filter_lines.append(f"- Ville souhaitee : {city}")
    if country:
        filter_lines.append(f"- Pays souhaite : {country}")
    if language:
        filter_lines.append(f"- Langue d'enseignement : {language}")
    if budget_max:
        filter_lines.append(f"- Budget annuel maximum : {budget_max} euros")
    if scholarship_only:
        filter_lines.append("- OBLIGATOIRE : etablissements avec bourse disponible uniquement")
    if school_type:
        filter_lines.append(f"- Type d'etablissement : {school_type}")

    filters_text = "\n".join(filter_lines)

    return f"""
Tu es EduSearch, un assistant IA expert en orientation universitaire mondiale.
Tu dois identifier des etablissements d'enseignement superieur correspondant aux criteres d'un etudiant etranger.

OBJECTIF PRINCIPAL : Retourner entre 10 et 15 etablissements pertinents.
Si les criteres sont larges ou "Indifferent", elargis ta recherche a plusieurs pays et types d'etablissements.

REGLES STRICTES POUR LES LIENS :
1. "url" : URL racine uniquement (ex: "https://www.univ-paris1.fr"). Jamais de lien profond pour eviter les 404.
2. "scholarship_link" : Laisse ce champ vide (""). Le lien de recherche bourses sera genere automatiquement.
3. "deadline" : Estime prudemment la date limite de candidature pour l'annee en cours pour les profils internationaux.

FILTRES ACTIFS :
{filters_text}

IMPORTANT : Si aucun filtre restrictif n'est actif (tout est "Indifferent"), propose des etablissements de qualite dans des pays varies (Europe, Amerique, Asie, Afrique) avec des frais accessibles. Vise toujours 10 a 15 resultats.

Reponds UNIQUEMENT avec un tableau JSON valide (sans texte avant ou apres) :
[
  {{
    "school_name": "Nom complet de l'universite ou ecole",
    "location": "Ville",
    "country": "Pays",
    "school_type": "Universite / IUT / Grande Ecole / Institut",
    "programs": ["Nom du cursus 1", "Nom du cursus 2"],
    "degree_levels": ["Licence", "Master"],
    "language_of_instruction": "Francais",
    "tuition_fee": "Frais UE/Locaux (ex: 243 euros/an)",
    "tuition_fee_non_eu": "Frais etudiants hors-UE (ex: 2850 euros/an)",
    "application_fee": "Frais de dossier",
    "scholarship_available": "Oui / Possible / Non",
    "scholarship_estimated_amount": "Estimation du montant (ex: 3500 euros/an)",
    "scholarship_details": "Description detaillee des aides disponibles",
    "scholarship_link": "URL reelle de la page bourses ou lien Google de recherche",
    "eligibility": "Criteres d'eligibilite aux bourses",
    "admission_requirements": "Prerequis academiques et linguistiques",
    "deadline": "Ex: 31 Mars 2026 (date limite de depot de dossier)",
    "duration": "Duree du cursus",
    "official_contact": "Email ou page de contact officiel",
    "summary": "Resume clair de l'opportunite pour un etudiant international",
    "url": "https://www.site-racine-uniquement.edu",
    "confidence": "Elevee / Moyenne / Faible"
  }}
]
"""


def find_accessible_school_results(query: str, filters: dict) -> tuple[str, list[dict]]:
    """
    Interroge l'API Gemini avec la recherche web activee pour trouver des etablissements.
    Filtre les resultats selon les criteres d'accessibilite financiere.

    Complexite : O(n) ou n = nombre de resultats retournes par Gemini.
    - Appel API : O(1) du point de vue du code
    - Normalisation : O(n)
    - Filtrage budget/pays/ville : O(n)

    Retourne un tuple (message, liste_de_resultats).
    La liste peut etre vide si aucun resultat ne passe les filtres.
    """
    api_key = st.secrets.get("Gemini_API_Key")
    if not api_key:
        return "Erreur : cle API Gemini manquante dans les secrets.", []

    try:
        client = genai.Client(api_key=api_key)
        prompt = _build_search_prompt(query, filters)

        # Activation de la recherche web pour de vraies URLs de bourses
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt + f"\n\nRequete de l'etudiant : {query}",
            config={
                "tools": [{"google_search": {}}],
                "temperature": 0.3,
            }
        )

        data = extract_json_from_text(response.text)
        if not isinstance(data, list):
            return "Aucun resultat exploitable trouve.", []

        max_budget = extract_numeric_amount(filters.get("budget_max"))
        country_filter = filters.get("country", "Indifferent")
        city_filter = filters.get("city", "").strip().lower()
        scholarship_only = filters.get("scholarship_only", False)
        results = []

        for item in data:
            if not isinstance(item, dict):
                continue

            normalized = normalize_school_result(item)

            # Filtre pays uniquement si different de Indifferent
            if country_filter and country_filter != "Indifferent":
                if normalized["country"].lower() != country_filter.lower():
                    continue

            # Filtre ville uniquement si renseignee
            if city_filter:
                if city_filter not in normalized["location"].lower():
                    continue

            # Filtre bourse obligatoire
            if scholarship_only:
                scholarship_status = str(normalized.get("scholarship_available", "")).lower()
                if not any(x in scholarship_status for x in ["oui", "possible", "disponible"]):
                    continue

            # Filtre accessibilite financiere (seulement si budget precise)
            if max_budget and max_budget > 0:
                if not fits_access_mission(normalized, max_budget=max_budget):
                    continue

            results.append(normalized)

        if not results:
            return "Aucun etablissement ne correspond exactement a vos criteres. Essayez d'elargir les filtres.", []

        return f"{len(results)} etablissement(s) trouve(s) par EduSearch.", results

    except Exception as error:
        return f"Erreur technique : {str(error)}", []


def render_school_results(results: list[dict]):
    """
    Affiche les resultats par paquets de 5 avec pagination incrementale.
    Chaque etablissement est affiche dans un conteneur avec toutes ses infos.

    Complexite : O(p) ou p = items_per_page (borne par session_state).
    La pagination evite de rendre tous les N resultats en une fois.
    """
    if not results:
        st.info("Aucun etablissement trouve. Lancez une recherche ci-dessus.")
        return

    total_results = len(results)
    current_limit = min(st.session_state.items_per_page, total_results)

    st.markdown(f"#### Affichage de **{current_limit}** etablissements sur **{total_results}** trouves")
    st.markdown("---")

    for index in range(current_limit):
        school = results[index]
        with st.container(border=True):
            st.markdown(f"### {index + 1}. {school.get('school_name')}")

            deadline_val = _clean_optional_value(school.get("deadline"))
            if deadline_val:
                st.warning(f"Date limite de candidature : {deadline_val}")

            st.caption(
                f"Emplacement : {school.get('location')} ({school.get('country')}) "
                f"| Type : {school.get('school_type')} "
                f"| Confiance IA : {school.get('confidence', 'N/A')}"
            )

            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"**Formations :** {format_list_as_text(school.get('programs'))}")
                st.markdown(f"**Niveaux admis :** {format_list_as_text(school.get('degree_levels'))}")
                st.markdown(f"**Langue :** {school.get('language_of_instruction')}")
                st.markdown(f"**Duree du cursus :** {school.get('duration')}")
            with c2:
                st.markdown(f"**Frais locaux / UE :** {school.get('tuition_fee') or 'Non specifie'}")
                st.markdown(f"**Frais etudiants etrangers (Hors-UE) :** {school.get('tuition_fee_non_eu') or 'A verifier'}")
                st.markdown(f"**Bourse disponible :** {school.get('scholarship_available')}")
                st.markdown(f"**Montant estime bourse :** {school.get('scholarship_estimated_amount') or 'Non quantifie'}")

            if _clean_optional_value(school.get("scholarship_details")):
                st.info(f"**Details bourses :** {school['scholarship_details']}")
            if _clean_optional_value(school.get("eligibility")):
                st.markdown(f"**Eligibilite bourses :** {school['eligibility']}")
            if _clean_optional_value(school.get("admission_requirements")):
                st.markdown(f"**Prerequis d'admission :** {school['admission_requirements']}")
            if _clean_optional_value(school.get("summary")):
                st.markdown(f"**Presentation globale :** {school['summary']}")

            st.markdown("---")
            col_links = st.columns(2)
            with col_links[0]:
                st.markdown("**Site officiel :**")
                st.markdown(f"[Ouvrir le site officiel]({school['url']})")
                st.code(school['url'], language="text")
            with col_links[1]:
                st.markdown("**Rechercher les bourses (Google) :**")
                st.markdown(f"[Rechercher les bourses de cet etablissement]({school['scholarship_link']})")
                st.caption("Lien de recherche Google garantissant un acces valide aux informations de bourses.")

    if current_limit < total_results:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(f"Charger 5 ecoles supplementaires ({current_limit}/{total_results})", use_container_width=True):
            st.session_state.items_per_page += 5
            st.rerun()
    else:
        st.caption("Fin des resultats. Toutes les formations correspondantes ont ete affichees.")


def render_school_search_page():
    """
    Interface utilisateur principale de la page de recherche EduSearch.
    Gere les filtres, le declenchement de la recherche et l'affichage des resultats.

    Complexite : O(1) pour le rendu de l'interface.
    O(n) pour le traitement des resultats (appel a find_accessible_school_results).
    """
    initialize_search_state()

    st.caption("Trouvez des universites mondiales adaptees a votre budget et vos ambitions.")

    query = st.text_input(
        "Quelle formation recherchez-vous ? (Saisie libre)",
        value=st.session_state.get("last_query", ""),
        placeholder="Exemple : Master intelligence artificielle, Licence economie, BUT informatique..."
    )

    with st.expander("Filtres de recherche avances", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            degree_level = st.selectbox(
                "Niveau d'etudes vise",
                options=NIVEAUX_ETUDES,
                index=NIVEAUX_ETUDES.index(st.session_state.search_filters.get("degree_level", "Indifferent"))
            )
            country = st.selectbox(
                "Pays souhaite",
                options=PAYS_DU_MONDE,
                index=PAYS_DU_MONDE.index(st.session_state.search_filters.get("country", "Indifferent"))
            )
            city = st.text_input(
                "Ville specifique (optionnel)",
                value=st.session_state.search_filters.get("city", ""),
                placeholder="Ex: Paris, Montreal, Berlin... (laisser vide = indifferent)"
            )

        with col2:
            language = st.selectbox(
                "Langue d'enseignement",
                options=LANGUES_DU_MONDE,
                index=LANGUES_DU_MONDE.index(st.session_state.search_filters.get("language", "Indifferent"))
            )
            school_type = st.selectbox(
                "Type d'etablissement",
                options=["Indifferent", "Universite publique", "Universite privee", "Grande Ecole", "IUT / BUT", "Institut specialise", "Ecole de commerce", "Ecole d'ingenieurs"],
                index=0
            )
            budget_max = st.text_input(
                "Budget annuel maximum (en euros, optionnel)",
                value=st.session_state.search_filters.get("budget_max", ""),
                placeholder="Ex: 5000 (laisser vide = pas de limite)"
            )
            scholarship_only = st.checkbox(
                "Afficher uniquement les etablissements avec bourse disponible",
                value=st.session_state.search_filters.get("scholarship_only", False)
            )

    if st.button("Lancer la recherche EduSearch", use_container_width=True, type="primary"):
        if not query.strip():
            st.warning("Veuillez saisir une formation ou des mots-cles avant de lancer la recherche.")
            return

        st.session_state.items_per_page = 5

        filters = {
            "city": city.strip(),
            "country": country,
            "degree_level": degree_level,
            "language": language,
            "budget_max": budget_max.strip(),
            "scholarship_only": scholarship_only,
            "school_type": school_type,
        }
        st.session_state.search_filters = filters
        st.session_state.last_query = query

        with st.spinner("Recherche en cours sur le reseau academique international..."):
            message, results = find_accessible_school_results(query, filters)
            st.session_state.results = results
            store_search_context(results)

        if results:
            st.success(message)
        else:
            st.warning(message)

    render_school_results(st.session_state.get("results", []))