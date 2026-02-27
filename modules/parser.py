import streamlit as st
from google import genai # Nouveau nom d'import
import json

def analyze_content(html_content):
    if not html_content or "Erreur" in html_content or len(html_content) < 100:
        return {"scholarship": "À vérifier", "montant": "Non détecté", "details": "Contenu illisible."}

    try:
        # On crée le client avec la nouvelle méthode
        client = genai.Client(api_key=st.secrets["Gemini_API_Key"])
        
        prompt = f"""
        Tu es un expert en bourses. Analyse ce texte et réponds UNIQUEMENT en JSON.
        Format : 
        {{
            "scholarship": "Oui" ou "Non",
            "montant": "Le montant (ex: 500€) ou 'Non précisé'",
            "details": "Résumé des conditions."
        }}
        Texte : {html_content[:4000]}
        """

       # On passe sur la version 2.0, plus stable et disponible partout en 2026
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=prompt
        )
        
        # On récupère le texte et on nettoie le JSON
        raw_res = response.text.strip().replace('```json', '').replace('```', '')
        return json.loads(raw_res)

    except Exception as e:
        return {
            "scholarship": "Erreur IA",
            "montant": "N/A",
            "details": f"Erreur technique (v2) : {str(e)}"
        }