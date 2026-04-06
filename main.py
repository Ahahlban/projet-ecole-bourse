import streamlit as st

from modules.chatbot import render_search_interface
from modules.dashboard import render_dashboard
from modules.export import render_export_section
from modules.recommender import render_recommendation_page


def main():
    st.set_page_config(
        page_title="EduSearch Global",
        page_icon="🎓",
        layout="wide"
    )

    st.title("EduSearch Global")
    st.write("Trouvez des établissements à partir d'une requête libre et de filtres de recherche.")

    tab1, tab2, tab3, tab4 = st.tabs([
        "Recherche",
        "Dashboard",
        "Recommandations",
        "Export"
    ])

    with tab1:
        render_search_interface()

    results = st.session_state.get("results", [])
    query = st.session_state.get("last_query", "")

    with tab2:
        if results:
            render_dashboard(results)
        else:
            st.info("Lancez d'abord une recherche pour afficher le dashboard.")

    with tab3:
        if results:
            render_recommendation_page(results)
        else:
            st.info("Lancez d'abord une recherche pour afficher les recommandations.")

    with tab4:
        if results:
            render_export_section(results, query)
        else:
            st.info("Lancez d'abord une recherche pour activer les exports.")


if __name__ == "__main__":
    main()