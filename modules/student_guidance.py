import json
import re

import google.generativeai as genai
import streamlit as st

from modules.utils import fits_access_mission


def render_comparison_profile_form() -> dict | None:
    st.subheader("Comparaison personnalisée")
    st.caption("L'IA classe les établissements trouvés en tenant compte du budget et de l'accessibilité financière.")

    with st.form("profil_form"):
        col1, col2 = st.columns(2)

        with col1:
            domaine = st.selectbox(
                "Domaine d'études",
                [
                    "Informatique / Tech", "Médecine / Santé", "Ingénierie",
                    "Commerce / Business", "Droit", "Architecture",
                    "Arts / Design", "Sciences", "Lettres / Langues", "Autre"
                ]
            )
            niveau = st.selectbox(
                "Niveau d'études visé",
                ["Licence (Bachelor)", "Master", "Doctorat (PhD)", "MBA", "Formation courte"]
            )
            budget = st.slider("Budget annuel max (€)", 0, 50000, 10000, 1000)

        with col2:
            pays_pref = st.multiselect(
                "Pays préférés",
                [
                    "France", "Canada", "Belgique", "Allemagne", "Espagne",
                    "Italie", "Pays-Bas", "Suède", "Japon", "Autre"
                ],
                default=[]
            )
            langue = st.multiselect(
                "Langues parlées",
                ["Français", "Anglais", "Espagnol", "Allemand", "Arabe", "Autre"],
                default=[]
            )
            criteres = st.multiselect(
                "Critères importants",
                [
                    "Montant de la bourse élevé",
                    "Coût de la vie faible",
                    "Frais de scolarité faibles",
                    "Programme en anglais",
                    "Facilité d'obtention du visa"
                ],
                default=[]
            )

        submitted = st.form_submit_button("Lancer la comparaison", use_container_width=True)

        if submitted:
            return {
                "domaine": domaine,
                "niveau": niveau,
                "budget": budget,
                "pays_pref": pays_pref,
                "langues": langue,
                "criteres": criteres
            }

    return None


def _extract_json_from_text(text: str):
    if not text:
        raise ValueError("Réponse vide.")

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
    api_key = st.secrets.get("Gemini_API_Key")

    if not api_key:
        st.error("Clé API manquante dans les Secrets Streamlit.")
        return []

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-flash-lite-latest")

        affordable_results = [
            result for result in results
            if fits_access_mission(result, max_budget=profile.get("budget"))
        ]

        if not affordable_results:
            return []

        results_text = ""
        for i, result in enumerate(affordable_results, 1):
            results_text += f"""
Option {i}:
Nom de l'école: {result.get('school_name', 'Non détecté')}
URL: {result.get('url', 'Non détecté')}
Localisation: {result.get('location', 'Non détecté')}
Pays: {result.get('country', 'Non détecté')}
Type d'établissement: {result.get('school_type', 'Non détecté')}
Programmes: {", ".join(result.get('programs', [])) if result.get('programs') else 'Non détecté'}
Niveaux d'études: {", ".join(result.get('degree_levels', [])) if result.get('degree_levels') else 'Non détecté'}
Langue d'enseignement: {result.get('language_of_instruction', 'Non détecté')}
Frais de scolarité: {result.get('tuition_fee', 'Non détecté')}
Frais de dossier: {result.get('application_fee', 'Non détecté')}
Bourse disponible: {result.get('scholarship_available', 'À vérifier')}
Montant de la bourse: {result.get('scholarship_amount', 'Non détecté')}
Détails bourse: {result.get('scholarship_details', 'Non détecté')}
Éligibilité: {result.get('eligibility', 'Non détecté')}
Conditions d'admission: {result.get('admission_requirements', 'Non détecté')}
Date limite: {result.get('deadline', 'Non détecté')}
Durée: {result.get('duration', 'Non détecté')}
Contact officiel: {result.get('official_contact', 'Non détecté')}
Résumé: {result.get('summary', 'Non détecté')}
"""

        prompt = f"""
Tu es un conseiller d'orientation spécialisé dans les parcours accessibles pour des étudiants avec budget limité.

Voici le profil d'un étudiant :
{profile}

Voici une liste d'écoles / options trouvées :
{results_text}

Ta mission :
- classer les meilleures options pour cet étudiant
- prendre en compte le domaine, le niveau, le budget, les pays préférés, les langues et les critères importants
- ne pas inventer d'informations absentes
- pénaliser fortement les options dont le coût semble dépasser le budget
- valoriser les options avec bourse, frais modérés, langue compatible et bon alignement académique
- éviter de recommander des écoles élitistes ou inaccessibles financièrement

Réponds UNIQUEMENT en JSON valide sous ce format :
[
  {{
    "score": 85,
    "school_name": "Nom de l'école",
    "url": "https://...",
    "reason": "Pourquoi cette option correspond au profil",
    "strengths": "Points forts principaux",
    "risks": "Points de vigilance",
    "advice": "Conseil concret pour candidater"
  }}
]

Retourne au maximum 5 options comparées, triées de la meilleure à la moins bonne.
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
                "school_name": item.get("school_name", "Option suggérée"),
                "url": item.get("url", ""),
                "reason": item.get("reason", ""),
                "strengths": item.get("strengths", ""),
                "risks": item.get("risks", ""),
                "advice": item.get("advice", "")
            })

        return normalized_recommendations

    except Exception as error:
        st.error(f"Erreur lors de la comparaison IA : {str(error)}")
        return []


def render_ranked_comparisons(recommendations: list[dict]):
    if not recommendations:
        st.warning("Aucune comparaison exploitable n'a été générée.")
        return

    for recommendation in recommendations:
        score = recommendation.get("score", 0)
        title = recommendation.get("school_name", "Option suggérée")
        url = recommendation.get("url", "")

        st.info(
            f"**Score : {score}/100** - {title}\n\n"
            f"**URL :** {url if url else 'Non détectée'}\n\n"
            f"**Pourquoi :** {recommendation.get('reason', '')}\n\n"
            f"**Points forts :** {recommendation.get('strengths', '')}\n\n"
            f"**Points de vigilance :** {recommendation.get('risks', '')}\n\n"
            f"**Conseil :** {recommendation.get('advice', '')}"
        )


def render_comparison_page(results: list[dict]):
    if not results:
        st.info("Lancez d'abord une recherche dans l'onglet 'Recherche' pour activer la comparaison personnalisée.")
        return

    profile = render_comparison_profile_form()
    if profile:
        with st.spinner("Analyse comparative des établissements en cours..."):
            recommendations = generate_accessible_comparisons(profile, results)
            render_ranked_comparisons(recommendations)
