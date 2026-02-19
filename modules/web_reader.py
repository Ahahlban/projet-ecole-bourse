import requests
from bs4 import BeautifulSoup

def extract_text(url):
    """Télécharge la page, nettoie les menus/scripts et récupère le texte utile."""
    try:
        # Ajout du User-Agent pour éviter d'être bloqué
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() # Vérifie si la page a bien chargé
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # ON NETTOIE : on enlève tout ce qui n'est pas du contenu informatif
        for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
            element.decompose()
            
        # On récupère le texte en séparant bien les blocs par des espaces
        text = soup.get_text(separator=' ')
        
        # On nettoie les espaces en trop (double espaces, retours à la ligne)
        clean_text = " ".join(text.split())
        
        # On passe à 5000 caractères pour être sûr d'avoir les détails
        return clean_text[:5000] 
        
    except Exception as e:
        return f"Erreur de lecture : {e}"