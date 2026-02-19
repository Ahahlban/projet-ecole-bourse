import re
import requests
from bs4 import BeautifulSoup


HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}


def _clean_text(text: str) -> str:
    """Nettoie le texte extrait: espaces, lignes vides, caractères parasites."""
    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_text(url: str, timeout: int = 10) -> str:
    """
    Télécharge une page web et renvoie uniquement le texte nettoyé.
    Compatible avec scraper.get_link() qui renvoie list[str] d'URLs.
    En cas d'erreur -> renvoie "" (string vide).
    """
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)

        resp.raise_for_status()

        content_type = (resp.headers.get("Content-Type") or "").lower()
        if "application/pdf" in content_type:
            return ""

        soup = BeautifulSoup(resp.text, "html.parser")

        for tag in soup(["script", "style", "noscript", "header", "footer", "nav", "aside", "form"]):
            tag.decompose()

        main = soup.find("main") or soup.find("article")
        root = main if main else soup

        text = root.get_text(separator="\n", strip=True)
        text = _clean_text(text)

        if len(text) < 200:
            return ""

        return text

    except requests.exceptions.RequestException:
        return ""
    except Exception:
        return ""


def extract_text_info(url: str, timeout: int = 10) -> dict:
    """
    Variante qui renvoie aussi des infos utiles (status/title/error).
    """
    info = {"url": url, "final_url": None, "status_code": None, "title": None, "text": "", "error": None}

    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
        info["final_url"] = resp.url
        info["status_code"] = resp.status_code

        content_type = (resp.headers.get("Content-Type") or "").lower()
        if "application/pdf" in content_type:
            info["error"] = "pdf_not_supported"
            return info

        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        if soup.title and soup.title.string:
            info["title"] = soup.title.string.strip()

        for tag in soup(["script", "style", "noscript", "header", "footer", "nav", "aside", "form"]):
            tag.decompose()

        main = soup.find("main") or soup.find("article")
        root = main if main else soup

        text = _clean_text(root.get_text(separator="\n", strip=True))
        if len(text) < 200:
            info["error"] = "too_little_text"
            info["text"] = text
            return info

        info["text"] = text
        return info

    except requests.exceptions.Timeout:
        info["error"] = "timeout"
        return info
    except requests.exceptions.HTTPError:
        info["error"] = "http_error"
        return info
    except requests.exceptions.RequestException:
        info["error"] = "request_exception"
        return info
    except Exception:
        info["error"] = "unexpected_error"
        return info