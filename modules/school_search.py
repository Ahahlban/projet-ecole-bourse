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

# --- REPERTOIRE DES PAYS ET LANGUES ---
PAYS_DU_MONDE = [
    "Indifférent", "Afghanistan", "Afrique du Sud", "Albanie", "Algérie", "Allemagne", "Andorre", "Angola", 
    "Antigua-et-Barbuda", "Arabie Saoudite", "Argentine", "Arménie", "Australie", "Autriche", "Azerbaïdjan", 
    "Bahamas", "Bahreïn", "Bangladesh", "Barbade", "Belgique", "Belize", "Bénin", "Bhoutan", "Biélorussie", 
    "Birmanie", "Bolivie", "Bosnie-Herzégovine", "Botswana", "Brésil", "Brunei", "Bulgarie", "Burkina Faso", 
    "Burundi", "Cambodge", "Cameroun", "Canada", "Cap-Vert", "Chili", "Chine", "Chypre", "Colombie", 
    "Comores", "Congo (Brazzaville)", "Congo (Kinshasa)", "Corée du Nord", "Corée du Sud", "Costa Rica", 
    "Côte d'Ivoire", "Croatie", "Cuba", "Danemark", "Djibouti", "Dominique", "Égypte", "Émirats Arabes Unis", 
    "Équateur", "Érythrée", "Espagne", "Estonie", "Eswatini", "États-Unis", "Éthiopie", "Fidji", "Finlande", 
    "France", "Gabon", "Gambie", "Géorgie", "Ghana", "Grèce", "Grenade", "Guatemala", "Guinée", "Guinée-Bissau", 
    "Guinée Équatoriale", "Guyana", "Haïti", "Honduras", "Hongrie", "Inde", "Indonésie", "Irak", "Iran", 
    "Irlande", "Islande", "Israël", "Italie", "Jamaïque", "Japon", "Jordanie", "Kazakhstan", "Kenya", 
    "Kirghizistan", "Kiribati", "Koweït", "Laos", "Lesotho", "Lettonie", "Liban", "Libéria", "Libye", 
    "Liechtenstein", "Lituanie", "Luxembourg", "Macédoine du Nord", "Madagascar", "Malaisie", "Malawi", 
    "Maldives", "Mali", "Malte", "Maroc", "Maurice", "Mauritanie", "Mexique", "Micronésie", "Moldavie", 
    "Monaco", "Mongolie", "Monténégro", "Mozambique", "Namibie", "Nauru", "Népal", "Nicaragua", "Niger", 
    "Nigeria", "Norvège", "Nouvelle-Zélande", "Oman", "Ouganda", "Ouzbékistan", "Pakistan", "Palaos", 
    "Palestine", "Panama", "Papouasie-Nouvelle-Guinée", "Paraguay", "Pays-Bas", "Pérou", "Philippines", 
    "Pologne", "Portugal", "Qatar", "République Centrafricaine", "République Dominicaine", "République Tchèque", 
    "Roumanie", "Royaume-Uni", "Russie", "Rwanda", "Saint-Christophe-et-Niévès", "Sainte-Lucie", 
    "Saint-Marin", "Saint-Vincent-et-les-Grenadines", "Salomon", "Samoa", "Sao Tomé-et-Principe", "Sénégal", 
    "Serbie", "Seychelles", "Sierra Leone", "Singapour", "Slovaquie", "Slovénie", "Somalie", "Soudan", 
    "Soudan du Sud", "Sri Lanka", "Suède", "Suisse", "Suriname", "Syrie", "Tadjikistan", "Taïwan", 
    "Tanzanie", "Tchad", "Thaïlande", "Timor oriental", "Togo", "Tonga", "Trinité-et-Tobago", "Tunisie", 
    "Turkménistan", "Turquie", "Tuvalu", "Ukraine", "Uruguay", "Vanuatu", "Vatican", "Venezuela", 
    "Vietnam", "Yémen", "Zambie", "Zimbabwe"
]

LANGUES_DU_MONDE = [
    "Indifférent", "Afrikaans", "Albanais", "Allemand", "Amharique", "Anglais", "Arabe", "Arménien", 
    "Azéri", "Bengali", "Biélorusse", "Birman", "Bosnien", "Bulgare", "Catalan", "Chinois (Cantonais)", 
    "Chinois (Mandarin)", "Cingalais", "Coréen", "Croate", "Danois", "Espagnol", "Estonien", "Finnois", 
    "Français", "Géorgien", "Grec", "Gujarati", "Haoussa", "Hébreu", "Hindi", "Hongrois", "Indonésien", 
    "Islandais", "Italien", "Japonais", "Javanais", "Khmer", "Kirghize", "Laotien", "Letton", "Lituanien", 
    "Macédonien", "Malais", "Malayalam", "Malgache", "Maltais", "Marandais", "Marathi", "Mongol", 
    "Néerlandais", "Népalais", "Norvégien", "Ourdou", "Ouzbek", "Pachto", "Pendjabi", "Persan", "Polonais", 
    "Portugais", "Roumain", "Russe", "Serbe", "Slovaque", "Slovène", "Somali", "Suédois", "Swahili", 
    "Tadjik", "Tagalog (Philippin)", "Tamoul", "Tchèque", "Telugu", "Thaï", "Turc", "Turkmène", 
    "Ukrainien", "Vietnamien", "Xhosa", "Yoruba", "Zoulou"
]

FORMATIONS_PARCOURSUP = [
    "Indifférent",
    "BTS (Brevet de Technicien Supérieur)",
    "BUT (Bachelor Universitaire de Technologie)",
    "Classe Préparatoire aux Grandes Écoles (CPGE)",
    "Licence / Bachelor (Bac +3)",
    "Master (Bac +5 / MSc / MA)",
    "Doctorat (PhD)",
    "MBA (Master of Business Administration)",
    "Diplôme d'Ingénieur",
    "Formation Courte / Certifiante"
]


def initialize_search_state():
    """Initialise les variables d'état pour la recherche dans EduSearch."""
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
            "city": "Indifférent",
            "country": "Indifférent",
            "degree_level": "Indifférent",
            "language": "Indifférent",
            "budget_max": "",
            "scholarship_only": False,
        }


def store_search_context(results: list[dict]):
    """Génère et stocke un contexte textuel structuré des résultats pour l'IA."""
    context_parts = []
    for i, result in enumerate(results, 1):
        context_parts.append(
            f"Résultat {i}:\n"
            f"  - Établissement: {result.get('school_name', 'Non détecté')}\n"
            f"  - URL principale: {result.get('url', 'N/A')}\n"
            f"  - Localisation: {result.get('location', 'Non détecté')}, {result.get('country', 'Non détecté')}\n"
            f"  - Date limite d'inscription: {result.get('deadline', 'Non détectée')}\n"
            f"  - Frais Extra-communautaires: {result.get('tuition_fee_non_eu', 'N/A')}\n"
            f"  - Bourse: {result.get('scholarship_available', 'À vérifier')} (Est: {result.get('scholarship_estimated_amount', 'N/A')})\n"
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


def _build_accessible_search_prompt(query: str, filters: dict) -> str:
    city = "" if filters.get("city") == "Indifférent" else filters.get("city", "")
    country = "" if filters.get("country") == "Indifférent" else filters.get("country", "")
    degree_level = "" if filters.get("degree_level") == "Indifférent" else filters.get("degree_level", "")
    language = "" if filters.get("language") == "Indifférent" else filters.get("language", "")
    budget_max = str(filters.get("budget_max", "")).strip()
    scholarship_only = filters.get("scholarship_only", False)

    return f"""
Tu es EduSearch, un assistant IA expert en orientation universitaire mondiale, calqué sur la structure de Parcoursup.
Tu dois identifier des établissements d'enseignement supérieur correspondant aux critères de l'étudiant étranger.

CONTRAINTES DE LIENS ET DE DATES (TRÈS STRICTES) :
1. "url" : Écris UNIQUEMENT l'URL brute de la page d'accueil principale de l'école (ex: "https://www.univ-paris1.fr"). Aucun lien profond de formation pour éviter les erreurs 404.
2. "scholarship_link" : L'adresse URL brute d'accueil ou de la rubrique bourses.
3. "deadline" : Trouve ou estime prudemment la DATE LIMITE DE CANDIDATURE pour l'année universitaire en cours/prochaine pour les profils internationaux.

Filtres :
- Mots-clés : {query}
- Ville : {city if city else "Indifférent"}
- Pays : {country if country else "Indifférent"}
- Diplôme : {degree_level}
- Langue : {language}
- Budget max : {budget_max} €

Format JSON à retourner (sans aucun texte explicatif avant ou après) :
[
  {{
    "school_name": "Nom de l'université ou école",
    "location": "Ville",
    "country": "Pays",
    "school_type": "Université / Lycée / IUT / École",
    "programs": ["Nom du cursus"],
    "degree_levels": ["Licence", "Master"],
    "language_of_instruction": "Français",
    "tuition_fee": "Frais UE/Locaux",
    "tuition_fee_non_eu": "Frais Étudiants Extracommunautaires (ex: 2850€/an)",
    "application_fee": "Frais de dossier",
    "scholarship_available": "Oui / Possible / Non",
    "scholarship_estimated_amount": "Estimation (ex: 3500€/an)",
    "scholarship_details": "Détails de l'aide",
    "scholarship_link": "https://www.site-bourse-ecole.edu",
    "eligibility": "Critères",
    "admission_requirements": "Prérequis",
    "deadline": "Ex: 31 Mars 2026 (Date limite de dépôt)",
    "duration": "Durée",
    "official_contact": "Contact",
    "summary": "Résumé de l'opportunité.",
    "url": "https://www.site-accueil-uniquement.edu",
    "confidence": "Élevée"
  }}
]
"""


def find_accessible_school_results(query: str, filters: dict) -> tuple[str, list[dict]]:
    api_key = st.secrets.get("Gemini_API_Key")
    if not api_key:
        return "Erreur : clé API Gemini manquante dans les secrets.", []

    try:
        client = genai.Client(api_key=api_key)
        prompt = _build_accessible_search_prompt(query, filters)
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt + f"\n\nRequête : {query}",
        )
        
        data = extract_json_from_text(response.text)
        if not isinstance(data, list):
            return "Aucun résultat exploitable trouvé.", []

        max_budget = extract_numeric_amount(filters.get("budget_max"))
        results = []
        
        for item in data:
            if not isinstance(item, dict):
                continue

            normalized = normalize_school_result(item)

            if filters.get("country") != "Indifférent" and normalized["country"].lower() != filters["country"].lower():
                continue
            if filters.get("city") != "Indifférent" and normalized["location"].lower() != filters["city"].lower():
                continue

            if not fits_access_mission(normalized, max_budget=max_budget):
                continue

            results.append(normalized)

        if not results:
            return "0 résultat correspondant à vos critères géographiques et budgétaires.", []

        return f" {len(results)} établissement(s) trouvé(s) par EduSearch !", results

    except Exception as error:
        return f"Erreur technique : {str(error)}", []


def render_school_results(results: list[dict]):
    """Affiche les résultats 5 par 5 avec dates limites et URLs textuelles lisibles."""
    if not results:
        st.info("Aucun établissement trouvé. Lancez une recherche ci-dessus.")
        return

    total_results = len(results)
    current_limit = min(st.session_state.items_per_page, total_results)

    st.markdown(f"#### Affichage de **{current_limit}** établissements sur **{total_results}** trouvés")
    st.markdown("---")

    for index in range(current_limit):
        school = results[index]
        with st.container(border=True):
            st.markdown(f"### {index + 1}. {school.get('school_name')}")
            
            # --- SECTION DÉDIÉE REQUANTED : DATE LIMITE DE CANDIDATURE ---
            deadline_val = _clean_optional_value(school.get("deadline"))
            if deadline_val:
                st.warning(f" **Date limite de candidature :** **{deadline_val}**")

            st.caption(f"📍 Emplacement : {school.get('location')} ({school.get('country')}) • Type : {school.get('school_type')}")

            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f" **Formations :** {format_list_as_text(school.get('programs'))}")
                st.markdown(f" **Niveaux admis :** {format_list_as_text(school.get('degree_levels'))}")
                st.markdown(f" **Langue :** {school.get('language_of_instruction')}")
                st.markdown(f" **Durée du cursus :** {school.get('duration')}")
            with c2:
                st.markdown(f" **Frais locaux / UE :** {school.get('tuition_fee') or 'Non spécifié'}")
                st.markdown(f" **Frais Étudiants Étrangers (Hors-UE) :** :red[{school.get('tuition_fee_non_eu') or 'À vérifier'}]")
                st.markdown(f" **Bourse disponible :** {school.get('scholarship_available')}")
                st.markdown(f" **Montant estimé bourse :** :green[{school.get('scholarship_estimated_amount') or 'Non quantifié'}]")

            if _clean_optional_value(school.get("scholarship_details")):
                st.info(f" **Détails bourses :** {school['scholarship_details']}")
            if _clean_optional_value(school.get("admission_requirements")):
                st.markdown(f" **Prérequis d'admission :** {school['admission_requirements']}")
            if _clean_optional_value(school.get("summary")):
                st.markdown(f" **Présentation globale :** {school['summary']}")
            
            # --- SECTION LIENS VISUELS + LIENS TEXTUELS ÉCRITS EN CLAIR (POUR TÉLÉCHARGEMENT) ---
            st.markdown("---")
            st.markdown("** Liens officiels (Accessibles en téléchargement / impression) :**")
            col_links = st.columns(2)
            with col_links[0]:
                st.markdown(f"[ Ouvrir le Site Officiel]({school['url']})")
                st.code(school['url'], language="text")  # Lien écrit en clair visuel
            with col_links[1]:
                st.markdown(f"[ Ouvrir l'Espace Bourses]({school['scholarship_link']})")
                st.code(school['scholarship_link'], language="text")  # Lien écrit en clair visuel
            st.markdown(" ")

    # --- PROGRESSION PAR PAQUETS DE 5 ---
    if current_limit < total_results:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(f" Charger 5 écoles supplémentaires ({current_limit}/{total_results})", use_container_width=True):
            st.session_state.items_per_page += 5
            st.rerun()
    else:
        st.caption(" Fin des résultats. Toutes les formations correspondantes d'EduSearch ont été affichées.")


def render_school_search_page():
    """Interface utilisateur principale d'EduSearch."""
    initialize_search_state()

    st.caption("Trouvez des universités mondiales adaptées à votre budget d'étudiant international et surveillez les dates de dépôt.")

    query = st.text_input(
        "Quelle formation recherchez-vous ? (Saisie libre)",
        value=st.session_state.get("last_query", ""),
        placeholder="Exemple : BUT informatique, Licence économie, Master intelligence artificielle..."
    )

    with st.expander(" Filtres d'autocomplétion & Paramètres mondiaux", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            degree_level = st.selectbox("Cursus visé", options=FORMATIONS_PARCOURSUP, index=FORMATIONS_PARCOURSUP.index(st.session_state.search_filters["degree_level"]))
            
            # Liste complète mondiale triée par ordre alphabétique
            country = st.selectbox("Sélectionner un Pays du monde", options=PAYS_DU_MONDE, index=PAYS_DU_MONDE.index(st.session_state.search_filters["country"]))
            
            # Gestion de la ville ("Indifférent" par défaut ou texte libre si choix précis)
            city_default = "Indifférent" if country == "Indifférent" else st.session_state.search_filters.get("city", "Indifférent")
            city = st.text_input(f"Ville spécifique ({country}) — Laisser 'Indifférent' pour tout inclure", value=city_default)

        with col2:
            # Liste complète des langues triée par ordre alphabétique
            language = st.selectbox("Langue d'apprentissage", options=LANGUES_DU_MONDE, index=LANGUES_DU_MONDE.index(st.session_state.search_filters["language"]))
            
            budget_max = st.text_input("Budget maximal annuel alloué (€)", value=st.session_state.search_filters.get("budget_max", ""))
            scholarship_only = st.checkbox("Exclure les établissements sans bourses d'études", value=st.session_state.search_filters.get("scholarship_only", False))

    if st.button(" Lancer l'analyse EduSearch", use_container_width=True):
        st.session_state.items_per_page = 5  
        
        filters = {
            "city": city.strip(),
            "country": country,
            "degree_level": degree_level,
            "language": language,
            "budget_max": budget_max.strip(),
            "scholarship_only": scholarship_only,
        }
        st.session_state.search_filters = filters
        st.session_state.last_query = query

        with st.spinner("Interrogation du réseau académique international et calcul des dates limites..."):
            message, results = find_accessible_school_results(query, filters)
            st.session_state.results = results
            store_search_context(results)

        st.success(message)

    render_school_results(st.session_state.get("results", []))