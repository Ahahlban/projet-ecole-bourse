import google.generativeai as genai
import streamlit as st
import json
import re
 
 
def render_profile_form() -> dict | None:
    """
    Affiche le formulaire de profil utilisateur et retourne les données.
 
    Returns:
        Dict avec le profil utilisateur ou None si non soumis
    """
    st.subheader("🎯 Système de Recommandation Personnalisé")
    st.caption("Remplissez votre profil pour recevoir des recommandations sur mesure.")
 
    with st.form("profil_form"):
        col1, col2 = st.columns(2)
 
        with col1:
            domaine = st.selectbox(
                "📚 Domaine d'études",
                [
                    "Informatique / Tech",
                    "Médecine / Santé",
                    "Ingénierie",
                    "Commerce / Business",
                    "Droit",
                    "Architecture",
                    "Arts / Design",
                    "Sciences",
                    "Lettres / Langues",
                    "Autre"
                ]
            )
            niveau = st.selectbox(
                "🎓 Niveau d'études visé",
                ["Licence (Bachelor)", "Master", "Doctorat (PhD)", "MBA", "Formation courte"]
            )
            budget = st.slider(
                "💶 Budget annuel max (€)",
                min_value=0, max_value=50000, value=10000, step=1000
            )
 
        with col2:
            pays_pref = st.multiselect(
                "🌍 Pays préférés",
                [
                    "France", "Canada", "États-Unis", "Royaume-Uni",
                    "Allemagne", "Suisse", "Belgique", "Pays-Bas",
                    "Australie", "Japon", "Espagne", "Italie",
                    "Suède", "Corée du Sud", "Singapour", "Autre"
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
                    "Possibilité de travailler en parallèle",
                    "Programme en anglais",
                    "Facilité d'obtention du visa",
                    "Proximité géographique"
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
 
 
def generate_recommendations(profile: dict, results: list[dict], api_key: str) -> list[dict]:
    """
    Utilise l'IA pour matcher le profil avec les résultats et générer des scores.
 
    Args:
        profile: Dict avec le profil utilisateur
        results: Liste des résultats de recherche
        api_key: Clé API Google Gemini
 
    Returns:
        Liste de recommandations avec scores
    """
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")
 
        # Préparer les résultats pour le prompt
        results_text = ""
        for i, r in enumerate(results, 1):
            results_text += (
                f"Option {i}:\n"
                f"  URL: {r.get('url', 'N/A')}\n"
                f"  Bourse: {r.get('scholarship', 'N/A')}\n"
                f"  Montant: {r.get('montant', 'N/A')}\n"
                f"  Coût: {r.get('cout_annuel', 'N/A')}\n"
                f"  Détails: {r.get('details', 'N/A')}\n\n"
            )
 
        prompt = f"""Tu es un conseiller en orientation scolaire expert.
 
PROFIL DE L'ÉTUDIANT :
- Domaine : {profile['domaine']}
- Niveau : {profile['niveau']}
- Budget max : {profile['budget']}€/an
- Pays préférés : {', '.join(profile['pays_pref'])}
- Langues : {', '.join(profile['langues'])}
- Critères importants : {', '.join(profile['criteres'])}
 
BOURSES DISPONIBLES :
{results_text}
 
CONSIGNE : Analyse chaque option et donne un score de compatibilité (0-100).
Réponds UNIQUEMENT en JSON valide, sous cette forme exacte :
[
  {{
    "index": 1,
    "score": 85,
    "nom_bourse": "Nom de la bourse",
    "raison": "Explication courte de pourquoi c'est compatible",
    "conseil": "Un conseil personnalisé pour l'étudiant"
  }}
]
 
Classe les résultats du meilleur score au pire.
Si une option n'a pas assez d'infos, donne un score de 30 avec une explication.
"""
 
        response = model.generate_content(prompt)
        raw = response.text
 
        # Nettoyer la réponse JSON
        raw = raw.strip()
        if raw.startswith("```"):
            raw = re.sub(r"```json?\s*", "", raw)
            raw = re.sub(r"```\s*$", "", raw)
 
        recommendations = json.loads(raw)
        return recommendations
 
    except json.JSONDecodeError:
        st.error("⚠️ L'IA n'a pas pu formater correctement les recommandations.")
        return []
    except Exception as e:
        st.error(f"❌ Erreur : {str(e)}")
        return []
 
 
def render_recommendations(recommendations: list[dict]):
    """
    Affiche les recommandations avec des cartes visuelles.
 
    Args:
        recommendations: Liste de dicts avec scores et conseils
    """
    if not recommendations:
        return
 
    st.subheader("🏆 Vos Recommandations Personnalisées")
 
    for rec in recommendations:
        score = rec.get("score", 0)
 
        # Couleur selon le score
        if score >= 75:
            color = "🟢"
            border_color = "#2ecc71"
        elif score >= 50:
            color = "🟡"
            border_color = "#f1c40f"
        else:
            color = "🔴"
            border_color = "#e74c3c"
 
        with st.container():
            st.markdown(
                f"""
                <div style="
                    border-left: 4px solid {border_color};
                    padding: 15px;
                    margin: 10px 0;
                    border-radius: 5px;
                    background-color: rgba(0,0,0,0.05);
                ">
                    <h4>{color} Score : {score}/100 — {rec.get('nom_bourse', 'Bourse')}</h4>
                    <p><strong>Pourquoi :</strong> {rec.get('raison', '')}</p>
                    <p><strong>💡 Conseil :</strong> {rec.get('conseil', '')}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
 
 
def render_recommendation_page(results: list[dict], api_key: str):
    """
    Fonction principale : affiche le formulaire + les recommandations.
 
    Args:
        results: Liste des résultats de recherche
        api_key: Clé API Google Gemini
    """
    st.markdown("---")
 
    if not results:
        st.info("🎯 Lancez d'abord une recherche pour recevoir des recommandations personnalisées.")
        return
 
    profile = render_profile_form()
 
    if profile:
        with st.spinner("🧠 L'IA analyse votre profil et les bourses disponibles..."):
            recs = generate_recommendations(profile, results, api_key)
        render_recommendations(recs)
