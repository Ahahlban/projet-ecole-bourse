import re
import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

def _clean_text(text: str) -> str:
    """Nettoie le texte extrait : espaces, lignes vides, etc."""
    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n+", " ", text) 
    return text.strip()

def extract_text(url: str, timeout: int = 10) -> str:
    """Télécharge une page web et renvoie le texte utile."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
        resp.raise_for_status()

        if "application/pdf" in resp.headers.get("Content-Type", "").lower():
            return "Document PDF détecté (lecture directe impossible)."

        soup = BeautifulSoup(resp.text, "html.parser")

        for tag in soup(["script", "style", "noscript", "header", "footer", "nav", "aside", "form"]):
            tag.decompose()

        main_content = soup.find("main") or soup.find("article") or soup.find("div", {"id": "content"})
        root = main_content if main_content else soup

        text = _clean_text(root.get_text(separator=" "))

        if len(text) < 100:
            return "Le contenu de cette page est trop court ou protégé."

        return text[:5000] 

    except Exception as e:
        return f"Erreur lors de la lecture : {str(e)}"