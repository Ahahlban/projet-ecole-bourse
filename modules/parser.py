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

        # Utilisation du modèle haute capacité pour le filtrage
        response = client.models.generate_content(
            model="gemini-flash-latest", 
            contents=prompt
        )
        
        # Nettoyage et chargement du JSON
        raw_res = response.text.strip().replace('```json', '').replace('```', '')
        filtered_links = json.loads(raw_res)
        
        # On limite pour rester dans l'esprit Low Data
        return filtered_links[:8]

    except Exception as e:
        print(f"Erreur lors du filtrage IA : {e}")
        return url_list[:5]


def analyze_content(html_content, lang="Français"):
    """
    Analyse le texte d'une page pour détecter les bourses et traduit le résultat.
    """
    if not html_content or "Erreur" in html_content or len(html_content) < 100:
        return {"scholarship": "À vérifier", "montant": "Non détecté", "details": "Contenu illisible."}

    try:
        client = genai.Client(api_key=st.secrets["Gemini_API_Key"])
        
        # Prompt mis à jour pour la traduction internationale
        prompt = f"""
        Tu es un expert en bourses internationales. 
        Analyse ce texte et réponds UNIQUEMENT en JSON.
        TRADUIS impérativement ton résumé et les détails en {lang}.

        Format de réponse JSON : 
        {{
            "scholarship": "Oui" ou "Non",
            "montant": "Le montant (converti ou original)",
            "details": "Résumé des conditions rédigé obligatoirement en {lang}."
        }}
        Texte à analyser : {html_content[:4000]}
        """

        # Utilisation du modèle haute capacité pour l'analyse
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
            "details": f"Erreur technique : {str(e)}"
        }