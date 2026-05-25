import pytest

from modules.utils import (
    ensure_list,
    extract_json_from_text,
    extract_numeric_amount,
    fits_access_mission,
    format_list_as_text,
    normalize_school_result,
)


def test_extract_json_from_markdown_block():
    text = '```json\n{"school_name": "Uni", "programs": ["Info"]}\n```'

    assert extract_json_from_text(text) == {
        "school_name": "Uni",
        "programs": ["Info"],
    }


def test_extract_json_from_text_with_extra_words():
    assert extract_json_from_text('Voici: [{"school_name": "Uni"}] merci') == [
        {"school_name": "Uni"}
    ]


def test_extract_json_rejects_empty_or_invalid_text():
    with pytest.raises(ValueError):
        extract_json_from_text("")

    with pytest.raises(ValueError):
        extract_json_from_text("pas de json ici")


def test_ensure_list_normalizes_missing_values():
    assert ensure_list(["Licence"]) == ["Licence"]
    assert ensure_list(None) == []
    assert ensure_list("Non détecté") == []
    assert ensure_list("Master") == ["Master"]


def test_normalize_school_result_fills_defaults_and_lists():
    result = normalize_school_result({
        "school_name": "IUT Paris",
        "programs": "Informatique",
        "degree_levels": None,
        "tuition_fee": "500 EUR",
    })

    assert result["school_name"] == "IUT Paris"
    assert result["programs"] == ["Informatique"]
    assert result["degree_levels"] == []
    assert result["tuition_fee"] == "500 EUR"
    assert result["country"] == ""


def test_format_list_as_text():
    assert format_list_as_text(["A", "B"]) == "A, B"
    assert format_list_as_text([]) == ""
    assert format_list_as_text(None) == ""
    assert format_list_as_text("France") == "France"


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("1 200 EUR", 1200.0),
        ("2,500", 2.5),
        ("Non détecté", None),
        ("aucun montant", None),
    ],
)
def test_extract_numeric_amount(value, expected):
    assert extract_numeric_amount(value) == expected


def test_fits_access_mission_blocks_expensive_selective_school():
    school = {
        "school_name": "HEC Paris",
        "tuition_fee": "45000 EUR",
        "scholarship_available": "non",
    }

    assert fits_access_mission(school, max_budget=10000) is False


def test_fits_access_mission_allows_affordable_school():
    school = {
        "school_name": "Université publique",
        "tuition_fee": "800 EUR",
        "scholarship_available": "oui",
    }

    assert fits_access_mission(school, max_budget=1000) is True
