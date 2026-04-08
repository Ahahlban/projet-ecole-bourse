import streamlit as st

from modules.school_search import render_school_search_page
from modules.school_comparison import render_school_comparison_page
from modules.school_recommendation import render_recommendation_page
from modules.results_export import render_results_export_section


def _inject_global_styles():
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 1.1rem !important;
            padding-bottom: 1.6rem !important;
            max-width: 980px !important;
        }

        h1 {
            margin-bottom: 0.1rem !important;
        }

        h2, h3 {
            margin-top: 0.25rem !important;
            margin-bottom: 0.35rem !important;
            font-weight: 700 !important;
        }

        p, li, div {
            line-height: 1.45;
        }

        div[data-testid="stTabs"] button {
            font-size: 0.93rem !important;
        }

        .stAlert {
            border-radius: 12px !important;
        }

        div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 14px !important;
        }

        .compact-section {
            margin-top: 0.55rem;
        }

        .compact-section-title {
            font-size: 0.98rem;
            font-weight: 700;
            margin-bottom: 0.35rem;
            color: #111827;
        }

        .compact-line {
            margin-bottom: 0.28rem;
            font-size: 0.95rem;
            color: #1f2937;
        }

        .compact-line strong {
            color: #111827;
        }

        .school-summary {
            margin-top: 0.2rem;
            font-size: 0.95rem;
            color: #1f2937;
        }

        .school-link {
            margin-top: 0.55rem;
            font-size: 0.92rem;
        }

        .results-header {
            margin-bottom: 0.5rem;
        }

        .element-container:has(div.stButton) + div .school-link {
            margin-top: 0.3rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def main():
    st.set_page_config(
        page_title="EduSearch Global",
        page_icon="🎓",
        layout="wide",
    )

    _inject_global_styles()

    st.title("EduSearch Global")
    st.caption("Recherche, comparaison et recommandations d'écoles pour étudiants à budget limité.")

    if "results" not in st.session_state:
        st.session_state.results = []
    if "last_query" not in st.session_state:
        st.session_state.last_query = ""

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Recherche", "Comparaison", "Recommandations", "Export"]
    )

    with tab1:
        render_school_search_page()

    with tab2:
        render_school_comparison_page()

    with tab3:
        render_recommendation_page(st.session_state.get("results", []))

    with tab4:
        render_results_export_section(
            st.session_state.get("results", []),
            st.session_state.get("last_query", ""),
        )


if __name__ == "__main__":
    main()