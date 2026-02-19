import re

def analyze_content(text):
    """
    Analyse le texte pour détecter la présence de bourses, 
    les conditions d'éligibilité et extraire un montant potentiel.
    """
    text_lc = text.lower()
    
    # 1. Détection de la thématique (Ton code original amélioré)
    has_scholarship = "bourse" in text_lc or "allocation" in text_lc or "aide financière" in text_lc
    is_eligible = any(word in text_lc for word in ["éligible", "condition", "critère", "dossier"])
    
    # 2. Extraction du montant avec une Regex (Le nouveau "Super Pouvoir")
    # On cherche : un nombre + optionnellement un espace + le symbole €
    montant_detecte = "Non précisé"
    # Cette regex cherche des chiffres (ex: 500, 1 200, 1500) suivis de '€'
    match = re.search(r'(\d+[\d\s]*€)', text)
    
    if match:
        montant_detecte = match.group(1).strip()
    
    return {
        "scholarship": "Oui" if has_scholarship else "À vérifier",
        "montant": montant_detecte,
        "details": "Conditions détectées" if is_eligible else "Pas de détails d'éligibilité précis trouvés."
    }