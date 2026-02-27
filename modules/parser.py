import streamlit as st
from google import genai
import json


def filter_school_links(url_list):
    """
    Utilise l'IA pour trier les URLs et ne garder que les sites officiels d'écoles.
    Évite de télécharger du contenu inutile pour rester 'Low Data'.
    """
    if not url_list:
        return []

    try:
        client = genai.Client(api_key=st.secrets["Gemini_API_Key"])
        
        # On prépare la liste pour l'IA
        urls_string = "\n".join(url_list)
        
        prompt = f"""
        Tu es un assistant spécialisé dans l'orientation scolaire. 
        Parmi cette liste d'URLs, identifie UNIQUEMENT celles qui sont des sites officiels d'écoles, 
        d'universités ou de centres de formation.
        
        EXCLUS formellement : 
        - Les annuaires (Studyrama, Diplomeo, L'Etudiant, etc.)
        - Les forums ou blogs
        - Les sites de presse
        
        Réponds UNIQUEMENT sous forme d'une liste JSON de strings.
        Liste : {urls_string}
        """

        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=prompt
        )
        
        # Nettoyage et chargement du JSON
        raw_res = response.text.strip().replace('```json', '').replace('```', '')
        filtered_links = json.loads(raw_res)
        
        # On s'assure de ne pas en garder trop pour limiter la data finale (ex: top 8)
        return filtered_links[:8]

    except Exception as e:
        print(f"Erreur lors du filtrage IA : {e}")
        # En cas d'erreur, on renvoie les 5 premiers par défaut pour ne pas bloquer l'app
        return url_list[:5]


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

     # On utilise l'alias 'latest' ou la version 'lite' qui ont de bien meilleurs quotas
        # par rapport aux 20 requêtes du 2.5
        response = client.models.generate_content(
            model="gemini-flash-latest", 
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