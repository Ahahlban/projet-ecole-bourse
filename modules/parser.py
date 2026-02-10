def analyze_content(text):
    """Cherche si le mot 'bourse' ou 'éligible' est présent."""
    has_scholarship = "bourse" in text.lower()
    is_eligible = "éligible" in text.lower() or "condition" in text.lower()
    
    return {
        "scholarship": "Oui" if has_scholarship else "À vérifier",
        "details": "Conditions trouvées !" if is_eligible else "Pas de détails d'éligibilité détectés."
    }