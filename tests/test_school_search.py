from types import SimpleNamespace

import modules.school_search as school_search


def test_clean_optional_value_removes_unusable_values():
    assert school_search._clean_optional_value(" Non vérifié ") == ""
    assert school_search._clean_optional_value("unknown") == ""
    assert school_search._clean_optional_value("Paris") == "Paris"
    assert school_search._clean_optional_value(None) == ""


def test_infer_duration_from_degree_level():
    assert school_search._infer_duration_if_possible({
        "degree_levels": ["Bachelor"],
        "programs": [],
    }) == "3 ans"

    assert school_search._infer_duration_if_possible({
        "school_type": "Master universitaire",
        "programs": [],
    }) == "2 ans"

    assert school_search._infer_duration_if_possible({"duration": "18 mois"}) == "18 mois"


def test_build_accessible_search_prompt_contains_filters():
    prompt = school_search._build_accessible_search_prompt(
        "informatique",
        {
            "city": "Lyon",
            "country": "France",
            "degree_level": "Licence",
            "language": "Français",
            "budget_max": "1000",
            "scholarship_only": True,
        },
    )

    assert "informatique" in prompt
    assert "Lyon" in prompt
    assert "bourse requise : oui" in prompt


def test_find_accessible_school_results_without_api_key(monkeypatch):
    monkeypatch.setattr(school_search.st, "secrets", {})

    message, results = school_search.find_accessible_school_results("info", {})

    assert message == "Erreur : clé API Gemini manquante."
    assert results == []


def test_find_accessible_school_results_normalizes_and_filters(monkeypatch):
    class FakeModel:
        def __init__(self, name):
            self.name = name

        def generate_content(self, prompt):
            return SimpleNamespace(text="""
            [
              {
                "school_name": "Université publique",
                "programs": "Informatique",
                "degree_levels": ["Bachelor"],
                "tuition_fee": "800 EUR",
                "scholarship_available": "oui",
                "duration": ""
              },
              {
                "school_name": "HEC Paris",
                "tuition_fee": "45000 EUR",
                "scholarship_available": "non"
              }
            ]
            """)

    monkeypatch.setattr(school_search.st, "secrets", {"Gemini_API_Key": "test-key"})
    monkeypatch.setattr(school_search.genai, "configure", lambda api_key: None)
    monkeypatch.setattr(school_search.genai, "GenerativeModel", FakeModel)

    message, results = school_search.find_accessible_school_results(
        "informatique",
        {"budget_max": "1000", "scholarship_only": True},
    )

    assert message == "1 résultats trouvés"
    assert results[0]["school_name"] == "Université publique"
    assert results[0]["programs"] == ["Informatique"]
    assert results[0]["duration"] == "3 ans"


def test_store_search_context(monkeypatch):
    fake_state = SimpleNamespace()
    monkeypatch.setattr(school_search.st, "session_state", fake_state)

    school_search.store_search_context([
        {
            "school_name": "Université publique",
            "programs": ["Info"],
            "degree_levels": ["Licence"],
        }
    ])

    assert "Université publique" in fake_state.search_context
    assert "Info" in fake_state.search_context
