def compute_school_score(school: dict) -> float:
    """
    Score d’accessibilité basé sur :
    - présence de bourse
    - coût
    - cohérence globale
    """

    score = 0

    scholarship = str(school.get("scholarship_available", "")).lower()
    tuition = str(school.get("tuition_fee", "")).lower()
    summary = str(school.get("summary", "")).lower()

    # Bourse
    if scholarship in {"oui", "possible"}:
        score += 4

    # Indices de faible coût
    low_cost_keywords = [
        "gratuit", "faible", "réduit", "abordable", "public",
        "low", "affordable"
    ]

    if any(word in tuition for word in low_cost_keywords):
        score += 3

    if any(word in summary for word in low_cost_keywords):
        score += 1

    # Bonus Europe (souvent moins cher)
    country = str(school.get("country", "")).lower()
    if country in {"france", "allemagne", "belgique", "italie", "espagne"}:
        score += 1

    return score


def rank_schools(results: list[dict]) -> list[dict]:
    """
    Trie les écoles par accessibilité.
    """
    for school in results:
        school["ranking_score"] = compute_school_score(school)

    return sorted(results, key=lambda x: x.get("ranking_score", 0), reverse=True)