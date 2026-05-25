import io

import pandas as pd

from modules.export import (
    _format_export_list,
    build_csv_report,
    build_excel_report,
    build_text_report,
)


SAMPLE_RESULTS = [
    {
        "school_name": "Université publique",
        "location": "Lyon",
        "country": "France",
        "school_type": "Université",
        "programs": ["Informatique", "Data"],
        "degree_levels": ["Licence"],
        "language_of_instruction": "Français",
        "tuition_fee": "800 EUR",
        "scholarship_available": "oui",
        "summary": "Accessible",
        "url": "https://example.edu",
    }
]


def test_format_export_list():
    assert _format_export_list(["Info", "Data"]) == "Info, Data"
    assert _format_export_list([]) == "N/A"
    assert _format_export_list(None) == "N/A"
    assert _format_export_list("France") == "France"


def test_build_csv_report_contains_school_data():
    csv_data = build_csv_report(SAMPLE_RESULTS)

    assert "Université publique" in csv_data
    assert "Informatique, Data" in csv_data


def test_build_text_report_contains_summary():
    report = build_text_report(SAMPLE_RESULTS, query="informatique")

    assert "RAPPORT - BourseScope" in report
    assert "informatique" in report
    assert "Université publique" in report


def test_build_excel_report_can_be_read():
    excel_bytes = build_excel_report(SAMPLE_RESULTS, query="informatique")

    workbook = pd.read_excel(io.BytesIO(excel_bytes), sheet_name=None)

    assert set(workbook) == {"Résultats Écoles", "Résumé"}
    assert workbook["Résultats Écoles"].iloc[0]["Établissement"] == "Université publique"
