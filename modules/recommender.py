import google.generativeai as genai
import streamlit as st
import json
import re

def render_profile_form() -> dict | None:
    """Affiche le formulaire de profil utilisateur."""
    st.subheader("🎯 Système de Recommandation Personnalisé")
    st.caption("Remplissez votre profil pour recevoir des recommandations sur mesure.")

    with st.form("profil_form"):
        col1, col2 = st.columns(2)
        with col1:
            domaine = st.selectbox("📚 Domaine d'études", ["Informatique / Tech", "Médecine / Santé", "Ingénierie", "Commerce / Business", "Droit", "Architecture", "Arts / Design", "Sciences", "Lettres / Langues", "Autre"])
            niveau = st.selectbox("🎓 Niveau d'études visé", ["Licence (Bachelor)", "Master", "Doctorat (PhD)", "MBA", "Formation courte"])
            budget = st.slider("💶 Budget annuel max (€)", 0, 50000, 10000, 1000)
        with col2:
            pays_pref = st.multiselect("🌍 Pays préférés", ["France", "Canada", "États-Unis", "Royaume-Uni", "Allemagne", "Suisse", "Belgique", "Pays-Bas", "Australie", "Japon", "Espagne", "Italie", "Suède", "Corée du Sud", "Singapour", "Autre"], default=["France", "Canada"])
            langue = st.multiselect("🗣️ Langues parlées", ["Français", "Anglais", "Espagnol", "Allemand", "Arabe", "Autre"], default=["Français"])
            criteres = st.multiselect("⭐ Critères importants", ["Montant de la bourse élevé", "Coût de la vie faible", "Prestige de l'école", "Programme en anglais", "Facilité d'obtention du visa"], default=["Montant de la bourse élevé"])

        submitted = st.form_submit_button("🚀 Obtenir mes recommandations", use_container_width=True)
        if submitted:
            return {"domaine": domaine, "niveau": niveau, "budget": budget, "pays_pref": pays_pref, "langues": langue, "criteres": criteres}
    return None

def generate_recommendations(profile: dict, results: list[dict], api_key: str) -> list[dict]:
    """Utilise l'IA Lite pour matcher le profil (1500 requêtes/jour)."""
    # Fallback sur les Secrets si la barre latérale est vide
    final_key = api_key if api_key else st.secrets.get("Gemini_API_Key")
    
    if not final_key:
        st.error("❌ Clé API manquante. Configurez-la dans les Secrets ou la barre latérale.")
        return []

    try:
        genai.configure(api_key=final_key)
        # On force le modèle haute capacité
        model = genai.GenerativeModel("gemini-2.0-flash-lite")

        results_text = ""
        for i, r in enumerate(results, 1):
            results_text += f"Option {i}:\n URL: {r.get('url')}\n Bourse: {r.get('scholarship')}\n Montant: {r.get('montant')}\n Coût: {r.get('cout_annuel')}\n"

        prompt = f"""
        En tant qu'expert, analyse ces options pour ce profil étudiant : {profile}.
        BOURSES : {results_text}
        Donne un score (0-100) et un conseil. Réponds UNIQUEMENT en JSON :
        [ {{"score": 85, "nom_bourse": "Nom", "raison": "Pourquoi", "conseil": "Astuce"}} ]
        """

        response = model.generate_content(prompt)
        raw = response.text.strip()
        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0].strip()
        
        return json.loads(raw)
    except Exception as e:
        st.error(f"❌ Erreur IA : {str(e)}")
        return []

def render_recommendations(recommendations: list[dict]):
    """Affiche les cartes visuelles des recommandations."""
    for rec in recommendations:
        score = rec.get("score", 0)
        color = "🟢" if score >= 75 else "🟡" if score >= 50 else "🔴"
        st.info(f"{color} **Score : {score}/100** — {rec.get('nom_bourse', 'Analyse en cours')}\n\n**Pourquoi :** {rec.get('raison', '')}\n\n**💡 Conseil :** {rec.get('conseil', '')}")

def render_recommendation_page(results: list[dict], api_key: str):
    """Point d'entrée de l'onglet Recommandations."""
    if not results:
        st.info("🎯 Lancez d'abord une recherche pour recevoir des recommandations.")
        return

    profile = render_profile_form() # La fonction est maintenant définie au-dessus !
    if profile:
        with st.spinner("🧠 L'IA analyse votre profil..."):
            recs = generate_recommendations(profile, results, api_key)
            render_recommendations(recs)