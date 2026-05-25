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
                    "Facilité d'obtention du visa",
                    "Diplôme reconnu à l'international",
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
            st.warning("Aucun établissement trouvé ne correspond aux critères d'accessibilité financière avec votre budget actuel. Essayez d'augmenter légèrement le curseur de budget annuel maximum.")
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
Tu es un conseiller d'orientation spécialisé dans les parcours accessibles pour des étudiants avec un budget limité.

Voici le profil de l'étudiant :
{profile}

Voici la liste des options d'écoles trouvées :
{results_text}

Ta mission :
- Classer les meilleures options pour cet étudiant.
- Prendre en compte scrupuleusement le domaine, le niveau, le budget, les pays préférés, les langues et les critères importants sélectionnés.
- Ne pas inventer d'informations absentes de la liste.
- Pénaliser fortement les options dont le coût semble dépasser le budget.
- Valoriser les options avec bourse disponible, frais modérés, langue compatible et bon alignement académique.
- Éviter de recommander des écoles élitistes ou inaccessibles financièrement.

Réponds UNIQUEMENT en JSON valide sous ce format exact :
[
  {{
    "score": 85,
    "school_name": "Nom de l'école",
    "url": "https://...",
    "reason": "Pourquoi cette option correspond au profil",
    "strengths": "Points forts principaux",
    "risks": "Points de vigilance ou d'alerte",
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
        return

    st.markdown("### Classement des meilleures options généré par l'IA")

    for idx, recommendation in enumerate(recommendations, 1):
        score = recommendation.get("score", 0)
        title = recommendation.get("school_name", "Option suggérée")
        url = recommendation.get("url", "")
        
        # Attribution d'une couleur au badge en fonction du score
        if score >= 80:
            badge_color = "🟢"
        elif score >= 50:
            badge_color = "🟡"
        else:
            badge_color = "🔴"

        with st.expander(f"{badge_color} #{idx} - {title} (Score : {score}/100)", expanded=(idx == 1)):
            if url and url != "Non détecté":
                st.markdown(f"🔗 **Lien officiel :** [{url}]({url})")
            else:
                st.markdown("🔗 **Lien officiel :** *Non renseigné*")
                
            st.markdown(f"💡 **Analyse de correspondance :** {recommendation.get('reason', 'N/A')}")
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f" **Points forts :**\n{recommendation.get('strengths', 'N/A')}")
            with col_b:
                st.markdown(f" **Points de vigilance :**\n{recommendation.get('risks', 'N/A')}")
                
            st.markdown("---")
            st.markdown(f" **Conseil pour votre démarche :** {recommendation.get('advice', 'N/A')}")


def render_comparison_page(results: list[dict]):
    # Vérification simple et lisible si la liste est vide
    if not results:
        st.info("Lancez d'abord une recherche dans l'onglet 'Recherche' pour activer la comparaison personnalisée.")
        return

    profile = render_comparison_profile_form()
    if profile:
        with st.spinner("Analyse comparative des établissements en cours..."):
            recommendations = generate_accessible_comparisons(profile, results)
            render_ranked_comparisons(recommendations)