import requests
from bs4 import BeautifulSoup
from urllib.parse import quote, unquote, urlparse, parse_qs


def get_links(keywords, location="", school_type="", max_results=10):
    """
    Recherche des liens sur DuckDuckGo à partir de mots-clés
    et retourne une liste de vraies URLs (non redirections).
    """

    query = f"{keywords} {location} {school_type} bourse"
    encoded_query = quote(query)
    url = f"https://html.duckduckgo.com/html/?q={encoded_query}"

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/119.0.0.0"}

    try:
    
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        results = []

        for a in soup.find_all("a", class_="result__a"):
            link = a.get("href")
            if link and "uddg=" in link:
                real_url = unquote(parse_qs(urlparse(link).query)["uddg"][0])
                if not any(x in real_url for x in ["facebook", "wikipedia", "forum"]):
                    results.append(real_url)
            
            if len(results) >= max_results: break
        return results
    except:
        return []


# ==============================
# TEST - Scraper.py
# ==============================
# if __name__ == "__main__":

#     print("Test de la fonction get_link...\n")

#     links = get_link(
#         keywords="école ingénieur Paris",
#         school_type="informatique",
#         max_results=11
#     )

#     if links:
#         for i, link in enumerate(links, 1):
#             print(f"{i}. {link}")
#     else:
#         print("Aucun résultat trouvé.")
