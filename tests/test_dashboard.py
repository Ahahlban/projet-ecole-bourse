from modules.dashboard import build_results_dataframe


def test_build_results_dataframe_empty():
    assert build_results_dataframe([]).empty


def test_build_results_dataframe_adds_numeric_and_labels():
    df = build_results_dataframe([
        {
            "school_name": "Université publique",
            "url": "https://example.edu/program",
            "scholarship_amount": "500 EUR",
            "tuition_fee": "1200 EUR",
            "scholarship_available": "oui",
        },
        {
            "school_name": "",
            "url": "https://fallback.edu/path",
            "scholarship_amount": "",
            "tuition_fee": "",
        },
    ])

    assert df.loc[0, "scholarship_amount_num"] == 500.0
    assert df.loc[0, "tuition_fee_num"] == 1200.0
    assert df.loc[0, "source_label"] == "Université publique"
    assert df.loc[1, "source_label"] == "fallback.edu"
    assert df.loc[1, "scholarship_status"] == "À vérifier"
