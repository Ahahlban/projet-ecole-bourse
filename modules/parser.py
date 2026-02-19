import re
from bs4 import BeautifulSoup

def analyse_content(html_content):
    """"Fonction pour résumer le texte du site web"""

    if not html_content or "Erreur" in html_content:
        return "Contenu indisponible ou erreur de lecture."

    # on transforme le code brut en objet BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Retirer les éléments inutiles pour alléger
    for script_or_style in soup(["script", "style"]):
        script_or_style.decompose()

    #on récupère le texte des paragraphes <p>
    paragraphs = soup.find_all('p')

    # on rassemble le texte des 3 premiers paragraphes
    text_list = [p.get_text().strip() for p in paragraphs if len(p.get_text()) > 20]
    full_text = " ".join(text_list[:3])

    # Si on ne trouve rien, on essaie de prendre le texte global
    if not full_text:
        full_text = soup.get_text(separator=' ', strip=True)[:300]

    return full_text if full_text else "Aucun texte descriptif trouvé sur la page."