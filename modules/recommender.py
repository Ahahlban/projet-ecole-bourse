import google.generativeai as genai
import streamlit as st
import json
import re


def render_profile_form() -> dict | None:
    """Affiche le formulaire de profil utilisateur."""
    st.subheader("🎯 Système de Recommandation Personnalisé")
    st.caption("L'IA va comparer votre profil avec les résultats trouvés.")

    with st.form("profil_form"):
        col1, col2 = st.columns(2)

        with col1:
            domaine = st.selectbox(
                "📚 Domaine d'études",
                [
                    "Informatique / Tech", "Médecine / Santé", "Ingénierie",
                    "Commerce / Business", "Droit", "Architecture",
                    "Arts / Design", "Sciences", "Lettres / Langues", "Autre"
                ]
            )
            niveau = st.selectbox(
                "🎓 Niveau d'études visé",
                ["Licence (Bachelor)", "Master", "Doctorat (PhD)", "MBA", "Formation courte"]
            )
            budget = st.slider("💶 Budget annuel max (€)", 0, 50000, 10000, 1000)

        with col2:
            pays_pref = st.multiselect(
                "🌍 Pays préférés",
                [
                    "France", "Canada", "États-Unis", "Royaume-Uni", "Allemagne",
                    "Suisse", "Belgique", "Pays-Bas", "Australie", "Japon",
                    "Espagne", "Italie", "Suède", "Corée du Sud", "Singapour", "Autre"
                ],
                default=["France", "Canada"]
            )
            langue = st.multiselect(
                "🗣️ Langues parlées",
                ["Français", "Anglais", "Espagnol", "Allemand", "Arabe", "Autre"],
                default=["Français"]
            )
            criteres = st.multiselect(
                "⭐ Critères importants",
                [
                    "Montant de la bourse élevé",
                    "Coût de la vie faible",
                    "Prestige de l'école",
                    "Programme en anglais",
                    "Facilité d'obtention du visa"
                ],
                default=["Montant de la bourse élevé"]
            )

        submitted = st.form_submit_button("🚀 Obtenir mes recommandations", use_container_width=True)

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
    """Extrait un JSON valide depuis une réponse Gemini."""
    if not text:
        raise ValueError("Réponse vide.")

    cleaned = text.strip().replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    match = re.search(r'(\[.*\]|\{.*\})', cleaned, re.DOTALL)
    if match:
        return json.loads(match.group(1))

    raise ValueError("Impossible d'extraire un JSON valide.")


def generate_recommendations(profile: dict, results: list[dict]) -> list[dict]:
    """Analyse le match entre le profil étudiant et les écoles trouvées."""
    api_key = st.secrets.get("Gemini_API_Key")

    if not api_key:
        st.error("❌ Clé API manquante dans les Secrets Streamlit.")
        return []

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-flash-lite-latest")

        results_text = ""
        for i, r in enumerate(results, 1):
            results_text += f"""
Option {i}:
Nom de l'école: {r.get('school_name', 'Non détecté')}
URL: {r.get('url', 'Non détecté')}
Localisation: {r.get('location', 'Non détecté')}
Pays: {r.get('country', 'Non détecté')}
Type d'établissement: {r.get('school_type', 'Non détecté')}
Programmes: {", ".join(r.get('programs', [])) if r.get('programs') else 'Non détecté'}
Niveaux d'études: {", ".join(r.get('degree_levels', [])) if r.get('degree_levels') else 'Non détecté'}
Langue d'enseignement: {r.get('language_of_instruction', 'Non détecté')}
Frais de scolarité: {r.get('tuition_fee', 'Non détecté')}
Frais de dossier: {r.get('application_fee', 'Non détecté')}
Bourse disponible: {r.get('scholarship_available', 'À vérifier')}
Montant de la bourse: {r.get('scholarship_amount', 'Non détecté')}
Détails bourse: {r.get('scholarship_details', 'Non détecté')}
Éligibilité: {r.get('eligibility', 'Non détecté')}
Conditions d'admission: {r.get('admission_requirements', 'Non détecté')}
Date limite: {r.get('deadline', 'Non détecté')}
Durée: {r.get('duration', 'Non détecté')}
Contact officiel: {r.get('official_contact', 'Non détecté')}
Résumé: {r.get('summary', 'Non détecté')}
"""

        prompt = f"""
Tu es un expert en orientation académique internationale.

Voici le profil d'un étudiant :
{profile}

Voici une liste d'écoles / options trouvées :
{results_text}

Ta mission :
- classer les meilleures options pour cet étudiant
- prendre en compte le domaine, le niveau, le budget, les pays préférés, les langues et les critères importants
- ne pas inventer d'informations absentes
- pénaliser les options dont le coût semble dépasser le budget
- valoriser les options avec bourse, langue compatible et bon alignement académique

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

Retourne au maximum 5 recommandations, triées de la meilleure à la moins bonne.
"""

        response = model.generate_content(prompt)
        data = _extract_json_from_text(response.text)

        if not isinstance(data, list):
            return []

        normalized = []
        for item in data:
            if not isinstance(item, dict):
                continue

            normalized.append({
                "score": item.get("score", 0),
                "school_name": item.get("school_name", "Option suggérée"),
                "url": item.get("url", ""),
                "reason": item.get("reason", ""),
                "strengths": item.get("strengths", ""),
                "risks": item.get("risks", ""),
                "advice": item.get("advice", "")
            })

        return normalized

    except Exception as e:
        st.error(f"❌ Erreur lors de la recommandation IA : {str(e)}")
        return []


def render_recommendations(recommendations: list[dict]):
    """Affiche les résultats de recommandation."""
    if not recommendations:
        st.warning("Aucune recommandation exploitable n'a été générée.")
        return

    for rec in recommendations:
        score = rec.get("score", 0)
        color = "🟢" if score >= 75 else "🟡" if score >= 50 else "🔴"

        title = rec.get("school_name", "Option suggérée")
        url = rec.get("url", "")

        st.info(
            f"{color} **Score : {score}/100** — {title}\n\n"
            f"**URL :** {url if url else 'Non détectée'}\n\n"
            f"**Pourquoi :** {rec.get('reason', '')}\n\n"
            f"**Points forts :** {rec.get('strengths', '')}\n\n"
            f"**Points de vigilance :** {rec.get('risks', '')}\n\n"
            f"**💡 Conseil :** {rec.get('advice', '')}"
        )


def render_recommendation_page(results: list[dict]):
    """Point d'entrée de l'onglet recommandations."""
    if not results:
        st.info("🎯 Lancez d'abord une recherche dans l'onglet 'Recherche' pour activer l'analyse personnalisée.")
        return

    profile = render_profile_form()
    if profile:
        with st.spinner("🧠 L'IA compare les écoles avec votre profil..."):
            recs = generate_recommendations(profile, results)
            render_recommendations(recs)