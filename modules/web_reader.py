import requests
from bs4 import BeautifulSoup

def extract_text(url):
    """Télécharge la page et ne garde que le texte (très léger)."""
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # On supprime les scripts et les styles (le gras inutile)
        for script in soup(["script", "style"]):
            script.decompose()
            
        return soup.get_text()[:1000] # On ne prend que le début pour l'exemple
    except:
        return "Impossible de lire le contenu de cette page."