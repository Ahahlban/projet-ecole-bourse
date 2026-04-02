import google.generativeai as genai
import streamlit as st
import json
import re

# ... (conserver render_profile_form tel quel)

def generate_recommendations(profile: dict, results: list[dict], api_key: str) -> list[dict]:
    # Sécurité clé API
    final_key = api_key if api_key else st.secrets.get("Gemini_API_Key")
    
    if not final_key:
        st.error("Clé API manquante.")
        return []

    try:
        genai.configure(api_key=final_key)
        # Harmonisation sur le modèle haute capacité
        model = genai.GenerativeModel("gemini-flash-lite-latest")
 
        results_text = ""
        for i, r in enumerate(results, 1):
            results_text += f"Option {i}: {r.get('url')}\nBourse: {r.get('scholarship')}\n\n"
 
        prompt = f"Analyse ces bourses pour ce profil : {profile}\nBourses : {results_text}\nRéponds en JSON uniquement."
 
        response = model.generate_content(prompt)
        raw = response.text.strip()
        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0].strip()
 
        return json.loads(raw)
    except Exception as e:
        st.error(f"Erreur Recommandation : {e}")
        return []

def render_recommendation_page(results: list[dict], api_key: str):
    st.markdown("---")
    if not results:
        st.info("🎯 Faites une recherche d'abord.")
        return

    profile = render_profile_form() #
    if profile:
        with st.spinner("Analyse IA en cours..."):
            recs = generate_recommendations(profile, results, api_key)
            # ... (appel à render_recommendations existant)