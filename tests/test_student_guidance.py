from types import SimpleNamespace

import modules.student_guidance as student_guidance


def test_extract_json_from_text_accepts_markdown():
    text = '```json\n[{"score": 90, "school_name": "Uni"}]\n```'

    assert student_guidance._extract_json_from_text(text) == [
        {"score": 90, "school_name": "Uni"}
    ]


def test_generate_accessible_comparisons_without_api_key(monkeypatch):
    errors = []
    monkeypatch.setattr(student_guidance.st, "secrets", {})
    monkeypatch.setattr(student_guidance.st, "error", errors.append)

    assert student_guidance.generate_accessible_comparisons({}, []) == []
    assert errors


def test_generate_accessible_comparisons_normalizes_response(monkeypatch):
    class FakeModel:
        def __init__(self, name):
            self.name = name

        def generate_content(self, prompt):
            return SimpleNamespace(text="""
            [
              {
                "score": 92,
                "school_name": "Université publique",
                "url": "https://example.edu",
                "reason": "Bon alignement",
                "strengths": "Frais faibles",
                "risks": "Places limitées",
                "advice": "Préparer le dossier"
              }
            ]
            """)

    monkeypatch.setattr(student_guidance.st, "secrets", {"Gemini_API_Key": "test-key"})
    monkeypatch.setattr(student_guidance.genai, "configure", lambda api_key: None)
    monkeypatch.setattr(student_guidance.genai, "GenerativeModel", FakeModel)

    recommendations = student_guidance.generate_accessible_comparisons(
        {"budget": 1000},
        [
            {
                "school_name": "Université publique",
                "programs": ["Info"],
                "degree_levels": ["Licence"],
                "tuition_fee": "800 EUR",
                "scholarship_available": "oui",
            }
        ],
    )

    assert recommendations == [
        {
            "score": 92,
            "school_name": "Université publique",
            "url": "https://example.edu",
            "reason": "Bon alignement",
            "strengths": "Frais faibles",
            "risks": "Places limitées",
            "advice": "Préparer le dossier",
        }
    ]
