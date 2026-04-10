import streamlit as st

from modules.school_search import render_school_search_page
from modules.dashboard import render_dashboard
from modules.export import render_export_section
from modules.student_guidance import render_comparison_page


def main():
    st.set_page_config(
        page_title="BourseScope",
        page_icon="🎓",
        layout="wide"
    )

    st.title("🎓 BourseScope")
    st.write("Trouvez des établissements plus accessibles financièrement à partir d'une requête libre et de filtres ciblés.")

    tab1, tab2, tab3, tab4 = st.tabs([
        "Recherche",
        "Dashboard",
        "Comparaison",
        "Export"
    ])

    with tab1:
        render_school_search_page()

    results = st.session_state.get("results", [])
    query = st.session_state.get("last_query", "")

    with tab2:
        if results:
            render_dashboard(results)
        else:
            st.info("Lancez d'abord une recherche pour afficher le dashboard.")

    with tab3:
        if results:
            render_comparison_page(results)
        else:
            st.info("Lancez d'abord une recherche pour afficher la comparaison.")

    with tab4:
        if results:
            render_export_section(results, query)
        else:
            st.info("Lancez d'abord une recherche pour activer les exports.")


if __name__ == "__main__":
    main()
