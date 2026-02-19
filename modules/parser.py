import re
from bs4 import BeautifulSoup

def analyze_content(html_content):
    """"Fonction pour résumer le texte du site web"""

    if not html_content or "Erreur" in html_content:
        return {"scholarship": "À vérifier", "montant": "Non détecté", "details": "Contenu trop court."}

    text_lc = html_content.lower()
    
    has_scholarship = any(w in text_lc for w in ["bourse", "allocation", "aide financière"])
    is_eligible = any(w in text_lc for w in ["éligible", "condition", "critère", "plafond", "quotient familial"])

    montant = "Non précisé"
    match = re.search(r'(\d+[\d\s]*€)', html_content)
    if match:
        montant = match.group(1).strip()
    
    return {
        "scholarship": "Oui" if has_scholarship else "À vérifier",
        "montant": montant,
        "details": "Conditions détectées" if is_eligible else "Pas de détails d'éligibilité précis."
    }
   