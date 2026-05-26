import json
import re

import google.generativeai as genai
import streamlit as st

from modules.utils import fits_access_mission

# --- LISTES COMPLETES (identiques a school_search pour coherence) ---
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

DOMAINES_ETUDES = [
    "Informatique / Technologie / IA",
    "Medecine / Sante / Pharmacie",
    "Ingenierie / Genie Civil / Mecanique",
    "Commerce / Business / Finance",
    "Droit / Sciences Politiques",
    "Architecture / Urbanisme",
    "Arts / Design / Mode",
    "Sciences exactes (Maths, Physique, Chimie)",
    "Sciences humaines / Lettres / Langues",
    "Education / Sciences de l'education",
    "Agriculture / Agroalimentaire / Environnement",
    "Communication / Journalisme / Media",
    "Psychologie / Sociologie",
    "Tourisme / Hotellerie / Restauration",
    "Energie / Developpement durable",
    "Autre (preciser dans formation souhaitee)"
]

NIVEAUX_ETUDES = [
    "Indifferent",
    "BTS (Brevet de Technicien Superieur)",
    "BUT (Bachelor Universitaire de Technologie)",
    "Classe Preparatoire (CPGE)",
    "Licence / Bachelor (Bac +3)",
    "Master (Bac +5 / MSc / MA)",
    "Doctorat (PhD)",
    "MBA",
    "Diplome d'Ingenieur",
    "Formation courte / Certifiante",
    "Autre"
]

CRITERES_PRIORITAIRES = [
    "Montant de la bourse le plus eleve possible",
    "Frais de scolarite les plus bas possible",
    "Cout de la vie faible dans le pays d'accueil",
    "Programme entierement en anglais",
    "Programme entierement en francais",
    "Facilite d'obtention du visa etudiant",
    "Diplome reconnu a l'international",
    "Ecole avec stage ou alternance integre",
    "Acces au marche du travail local apres diplome",
    "Campus avec logement etudiant inclus ou abordable",
    "Double diplome possible",
    "Formation en ligne / hybride disponible",
]


def render_comparison_profile_form() -> dict | None:
    """
    Affiche le formulaire de profil etudiant pour la comparaison personnalisee.
    Collecte le domaine, la formation souhaitee, le niveau, le budget, les pays/langues et criteres.

    Complexite : O(1) - rendu d'interface statique.
    Retourne un dict de profil si le formulaire est soumis, None sinon.
    """
    st.subheader("Comparaison personnalisee")
    st.caption("L'IA classe les etablissements trouves en tenant compte de votre profil et de votre budget.")

    with st.form("profil_form"):
        col1, col2 = st.columns(2)

        with col1:
            domaine = st.selectbox("Domaine d'etudes", DOMAINES_ETUDES)

            formation_libre = st.text_input(
                "Formation souhaitee (libre, prioritaire)",
                placeholder="Ex: Master Droit International, BTS Communication, PhD Biologie moleculaire..."
            )

            niveau = st.selectbox("Niveau d'etudes vise", NIVEAUX_ETUDES)

            budget = st.slider("Budget annuel maximum (euros)", 0, 60000, 10000, 500)
            budget_vie = st.slider("Budget vie courante mensuel estimee (euros)", 0, 5000, 800, 50)

        with col2:
            pays_pref = st.multiselect(
                "Pays preferes (selection multiple)",
                options=PAYS_DU_MONDE[1:],  # Exclure "Indifferent" de la liste multiselect
                default=[]
            )

            pays_exclus = st.multiselect(
                "Pays a exclure",
                options=PAYS_DU_MONDE[1:],
                default=[]
            )

            langue = st.multiselect(
                "Langues d'enseignement acceptees",
                options=LANGUES_DU_MONDE[1:],
                default=[]
            )

            criteres = st.multiselect(
                "Criteres prioritaires pour votre choix",
                options=CRITERES_PRIORITAIRES,
                default=[]
            )

            type_ecole = st.multiselect(
                "Types d'etablissements preferes",
                options=["Universite publique", "Universite privee", "Grande Ecole", "IUT / Institut", "Ecole de commerce", "Ecole d'ingenieurs", "Indifferent"],
                default=["Indifferent"]
            )

        submitted = st.form_submit_button("Lancer la comparaison personnalisee", use_container_width=True)

        if submitted:
            return {
                "domaine": domaine,
                "formation_libre": formation_libre.strip(),
                "niveau": niveau,
                "budget": budget,
                "budget_vie": budget_vie,
                "pays_pref": pays_pref,
                "pays_exclus": pays_exclus,
                "langues": langue,
                "criteres": criteres,
                "type_ecole": type_ecole,
            }

    return None


def _extract_json_from_text(text: str):
    """
    Extrait un JSON valide depuis une reponse brute de l'IA.

    Complexite : O(n) ou n = longueur du texte.
    Essaie un parsing direct, puis regex en fallback.
    """
    if not text:
        raise ValueError("Reponse vide.")

    cleaned = text.strip().replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    match = re.search(r"(\[.*\]|\{.*\})", cleaned, re.DOTALL)
    if match:
        return json.loads(match.group(1))

    raise ValueError("Impossible d'extraire un JSON valide.")


def generate_accessible_comparisons(profile: dict, results: list[dict]) -> list[dict]:
    """
    Envoie le profil etudiant et la liste des etablissements a Gemini pour un classement personnalise.
    Filtre d'abord les etablissements incompatibles avec le budget.

    Complexite :
    - Filtrage pre-IA : O(n) ou n = nombre de resultats
    - Construction du prompt : O(n)
    - Appel API : O(1) du point de vue du code
    - Parsing reponse : O(m) ou m = longueur de la reponse

    Retourne une liste de recommandations triees par score (0 a 100).
    """
    api_key = st.secrets.get("Gemini_API_Key")

    if not api_key:
        st.error("Cle API manquante dans les Secrets Streamlit.")
        return []

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")

        # Pre-filtrage : exclure les etablissements hors budget
        affordable_results = [
            result for result in results
            if fits_access_mission(result, max_budget=profile.get("budget"))
        ]

        # Exclure les pays indesirables
        pays_exclus = [p.lower() for p in profile.get("pays_exclus", [])]
        if pays_exclus:
            affordable_results = [
                r for r in affordable_results
                if r.get("country", "").lower() not in pays_exclus
            ]

        if not affordable_results:
            st.warning(
                "Aucun etablissement ne correspond aux criteres d'accessibilite financiere "
                "avec votre budget actuel. Essayez d'augmenter le budget ou d'elargir les filtres."
            )
            return []

        # Construction du texte de contexte pour l'IA
        results_text = ""
        for i, result in enumerate(affordable_results, 1):
            results_text += f"""
Option {i}:
  Ecole : {result.get('school_name', 'Non detecte')}
  URL : {result.get('url', 'N/A')}
  Localisation : {result.get('location', 'N/A')}, {result.get('country', 'N/A')}
  Type : {result.get('school_type', 'N/A')}
  Programmes : {', '.join(result.get('programs', [])) if result.get('programs') else 'N/A'}
  Niveaux : {', '.join(result.get('degree_levels', [])) if result.get('degree_levels') else 'N/A'}
  Langue : {result.get('language_of_instruction', 'N/A')}
  Frais locaux : {result.get('tuition_fee', 'N/A')}
  Frais hors-UE : {result.get('tuition_fee_non_eu', 'N/A')}
  Bourse : {result.get('scholarship_available', 'N/A')} (estimation : {result.get('scholarship_estimated_amount', 'N/A')})
  Details bourse : {result.get('scholarship_details', 'N/A')}
  Admission : {result.get('admission_requirements', 'N/A')}
  Date limite : {result.get('deadline', 'N/A')}
  Duree : {result.get('duration', 'N/A')}
  Resume : {result.get('summary', 'N/A')}
"""

        # Construction du profil lisible
        pays_pref_str = ", ".join(profile.get("pays_pref", [])) or "Indifferent"
        langues_str = ", ".join(profile.get("langues", [])) or "Indifferent"
        criteres_str = "\n  - ".join(profile.get("criteres", [])) or "Aucun critere specifique"
        types_str = ", ".join(profile.get("type_ecole", [])) or "Indifferent"

        prompt = f"""
Tu es un conseiller d'orientation universitaire international specialise dans l'accessibilite financiere.

Profil de l'etudiant :
  - Domaine d'etudes : {profile.get('domaine')}
  - Formation souhaitee (prioritaire) : {profile.get('formation_libre') or 'Non precise'}
  - Niveau vise : {profile.get('niveau')}
  - Budget scolarite annuel max : {profile.get('budget')} euros
  - Budget vie courante mensuel : {profile.get('budget_vie')} euros
  - Pays preferes : {pays_pref_str}
  - Langues d'enseignement acceptees : {langues_str}
  - Types d'etablissements : {types_str}
  - Criteres prioritaires :
    - {criteres_str}

Liste des etablissements disponibles :
{results_text}

Ta mission :
  1. Classer les meilleures options selon le profil ci-dessus.
  2. Prioriser la formation souhaitee et le domaine.
  3. Valoriser les bourses disponibles et les frais moderes.
  4. Penaliser les etablissements dont le cout net (frais - bourse) depasse le budget.
  5. Ne pas inventer d'informations absentes de la liste.
  6. Favoriser les pays preferes si renseignes.
  7. Retourner au maximum 5 options, triees de la meilleure a la moins bonne.

Reponds UNIQUEMENT en JSON valide sous ce format (sans texte avant ou apres) :
[
  {{
    "score": 85,
    "school_name": "Nom de l'ecole",
    "url": "https://...",
    "reason": "Pourquoi cette option correspond au profil de l'etudiant",
    "strengths": "Points forts principaux par rapport au profil",
    "risks": "Points de vigilance ou d'alerte importants",
    "cost_analysis": "Analyse detaillee du cout net apres bourse eventuelle",
    "advice": "Conseil concret et actionnable pour candidater"
  }}
]
"""

        response = model.generate_content(prompt)
        data = _extract_json_from_text(response.text)

        if not isinstance(data, list):
            return []

        normalized_recommendations = []
        for item in data:
            if not isinstance(item, dict):
                continue
            normalized_recommendations.append({
                "score": item.get("score", 0),
                "school_name": item.get("school_name", "Option suggeree"),
                "url": item.get("url", ""),
                "reason": item.get("reason", ""),
                "strengths": item.get("strengths", ""),
                "risks": item.get("risks", ""),
                "cost_analysis": item.get("cost_analysis", ""),
                "advice": item.get("advice", "")
            })

        return normalized_recommendations

    except Exception as error:
        st.error(f"Erreur lors de la comparaison IA : {str(error)}")
        return []


def render_ranked_comparisons(recommendations: list[dict]):
    """
    Affiche le classement des etablissements recommandes par l'IA.
    Chaque carte inclut score, analyse de cout, points forts/risques et conseils.

    Complexite : O(r) ou r = nombre de recommandations (borne a 5).
    """
    if not recommendations:
        return

    st.markdown("### Classement personnalise genere par l'IA")

    for idx, recommendation in enumerate(recommendations, 1):
        score = recommendation.get("score", 0)
        title = recommendation.get("school_name", "Option suggeree")
        url = recommendation.get("url", "")

        if score >= 80:
            badge = "Tres bonne correspondance"
        elif score >= 60:
            badge = "Bonne correspondance"
        elif score >= 40:
            badge = "Correspondance moyenne"
        else:
            badge = "Correspondance faible"

        with st.expander(f"#{idx} - {title} | Score : {score}/100 | {badge}", expanded=(idx == 1)):
            if url and url not in ["Non detecte", "N/A"]:
                st.markdown(f"**Lien officiel :** [{url}]({url})")
            else:
                st.markdown("**Lien officiel :** Non renseigne")

            st.markdown(f"**Analyse de correspondance :** {recommendation.get('reason', 'N/A')}")
            st.markdown(f"**Analyse financiere :** {recommendation.get('cost_analysis', 'N/A')}")

            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"**Points forts :**\n{recommendation.get('strengths', 'N/A')}")
            with col_b:
                st.markdown(f"**Points de vigilance :**\n{recommendation.get('risks', 'N/A')}")

            st.markdown("---")
            st.markdown(f"**Conseil pour votre demarche :** {recommendation.get('advice', 'N/A')}")


def render_comparison_page(results: list[dict]):
    """
    Page principale de l'onglet Orientation assistee.
    Verifie que des resultats existent, affiche le formulaire, lance la comparaison et affiche les resultats.

    Complexite globale : O(n) ou n = nombre de resultats de recherche disponibles.
    """
    if not results:
        st.info("Lancez d'abord une recherche dans l'onglet 'Recherche' pour activer la comparaison personnalisee.")
        return

    profile = render_comparison_profile_form()
    if profile:
        with st.spinner("Analyse comparative des etablissements en cours..."):
            recommendations = generate_accessible_comparisons(profile, results)
            render_ranked_comparisons(recommendations)