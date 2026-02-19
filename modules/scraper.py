import requests
from bs4 import BeautifulSoup
from urllib.parse import quote, unquote, urlparse, parse_qs


def get_link(keywords, school_type=None, max_results=10):
    """
    Recherche des liens sur DuckDuckGo à partir de mots-clés
    et retourne une liste de vraies URLs (non redirections).
    """

    # 1️⃣ Construction de la requête texte
    query = keywords
    if school_type:
        query += f" {school_type}"

    # 2️⃣ Encodage de la requête pour qu'elle soit valide dans une URL
    encoded_query = quote(query)

    # 3️⃣ Construction de l'URL de recherche DuckDuckGo (version HTML simple)
    url = f"https://html.duckduckgo.com/html/?q={encoded_query}"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    # 4️⃣ Envoie de la requête HTTP
    response = requests.get(url, headers=headers)

    # 5️⃣ Parser le HTML
    soup = BeautifulSoup(response.text, "html.parser")

    # 6️⃣ Extraction des liens
    results = []

    for a in soup.find_all("a", class_="result__a"):
        link = a.get("href")

        if link:
            # Des liens de redirection
            parsed_url = urlparse(link)
            query_params = parse_qs(parsed_url.query)

            # On récupère le vrai lien dans le paramètre "uddg"
            if "uddg" in query_params:
                real_url = unquote(query_params["uddg"][0])
                results.append(real_url)

        if len(results) >= max_results:
            break

    return results


# ==============================
# TEST - Scraper.py
# ==============================
if __name__ == "__main__":

    print("Test de la fonction get_link...\n")

    links = get_link(
        keywords="école ingénieur Paris",
        school_type="informatique",
        max_results=11
    )

    if links:
        for i, link in enumerate(links, 1):
            print(f"{i}. {link}")
    else:
        print("Aucun résultat trouvé.")
