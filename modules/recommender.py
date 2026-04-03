import google.generativeai as genai
import streamlit as st
import json

def render_profile_form() -> dict | None:
    """Affiche le formulaire de profil utilisateur."""
    st.subheader("🎯 Système de Recommandation Personnalisé")
    st.caption("L'IA va comparer votre profil avec les résultats trouvés.")

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

def generate_recommendations(profile: dict, results: list[dict]) -> list[dict]:
    """Analyse le 'match' entre le profil et les bourses (Modèle Lite)."""
    api_key = st.secrets.get("Gemini_API_Key")
    
    if not api_key:
        st.error("❌ Clé API manquante dans les Secrets Streamlit.")
        return []

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-flash-lite-latest")

        results_text = ""
        for i, r in enumerate(results, 1):
            results_text += f"Option {i}:\n URL: {r.get('url')}\n Bourse: {r.get('scholarship')}\n Montant: {r.get('montant')}\n Coût: {r.get('cout_annuel')}\n"

        prompt = f"""
        En tant qu'expert en orientation, analyse ces bourses pour ce profil : {profile}.
        BOURSES TROUVÉES : {results_text}
        Réponds UNIQUEMENT en JSON sous ce format :
        [ {{"score": 85, "nom_bourse": "Nom", "raison": "Pourquoi ça match", "conseil": "Une astuce pour postuler"}} ]
        """

        response = model.generate_content(prompt)
        raw = response.text.strip()
        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0].strip()
        
        return json.loads(raw)
    except Exception as e:
        st.error(f"❌ Erreur lors de la recommandation IA : {str(e)}")
        return []

def render_recommendations(recommendations: list[dict]):
    """Affiche les résultats de recommandation."""
    for rec in recommendations:
        score = rec.get("score", 0)
        color = "🟢" if score >= 75 else "🟡" if score >= 50 else "🔴"
        st.info(f"{color} **Score : {score}/100** — {rec.get('nom_bourse', 'Bourse suggérée')}\n\n**Pourquoi :** {rec.get('raison', '')}\n\n**💡 Conseil :** {rec.get('conseil', '')}")

def render_recommendation_page(results: list[dict]):
    """Point d'entrée de l'onglet sans besoin d'api_key en argument."""
    if not results:
        st.info("🎯 Lancez d'abord une recherche dans l'onglet 'Recherche' pour activer l'analyse personnalisée.")
        return

    profile = render_profile_form()
    if profile:
        with st.spinner("🧠 L'IA compare les bourses avec votre profil..."):
            recs = generate_recommendations(profile, results)
            render_recommendations(recs)