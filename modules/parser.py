import streamlit as st
from google import genai
import json

def analyze_content(html_content):
    if not html_content or "Erreur" in html_content or len(html_content) < 100:
        return {"scholarship": "À vérifier", "montant": "Non détecté", "details": "Contenu illisible."}

    try:
        # Utilisation de ton nom de clé exact
        client = genai.Client(api_key=st.secrets["Gemini_API_Key"])
        
        # --- BLOC DE DIAGNOSTIC ---
        # Cette fois, on enlève les '#' pour que ça s'affiche vraiment dans le terminal !
        print("\n=== LISTE DES MODÈLES DISPONIBLES POUR TA CLÉ ===")
        try:
            for m in client.models.list():
                print(f"-> {m.name}")
        except Exception as diag_err:
            print(f"Erreur lors du listing des modèles : {diag_err}")
        print("================================================\n")

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

      # On utilise le modèle 2.5 Flash qui est en haut de ta liste diagnostic
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=prompt
        )
        
        raw_res = response.text.strip().replace('```json', '').replace('```', '')
        return json.loads(raw_res)

    except Exception as e:
        return {
            "scholarship": "Erreur IA",
            "montant": "N/A",
            "details": f"Erreur technique (v2) : {str(e)}"
        }