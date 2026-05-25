import streamlit as st

from modules.school_search import render_school_search_page
from modules.dashboard import render_dashboard
from modules.export import render_export_section
from modules.student_guidance import render_comparison_page


def main():
    # Configuration de la page Streamlit
    st.set_page_config(
        page_title="EduSearch",
        page_icon="Graduation_Cap",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Barre latérale d'information
    with st.sidebar:
        st.markdown("### A propos de EduSearch")
        st.write(
            "Cette plateforme est concue pour aider les étudiants à identifier, analyser "
            "et comparer les établissements d'enseignement supérieur internationaux "
            "en mettant l'accent sur l'accessibilité financière et les opportunités de bourses."
        )
        st.markdown("---")
        
        # Indicateur de configuration de la cle API Gemini
        st.markdown("### Statut des Services")
        api_key_status = "Gemini_API_Key" in st.secrets
        if api_key_status:
            st.success("Service d'Analyse IA (Gemini) actif")
        else:
            st.error("Cle API Gemini manquante dans les Secrets")
            
        st.markdown("---")
        st.caption("Version 1.2.0 - Mission Accessibilite")

    # Zone Principale de l'Application
    st.title("EduSearch")
    st.markdown(
        "##### *Découvrez des établissements d'enseignement supérieur adaptés à vos ambitions et à votre budget.*"
    )
    st.write(
        "Explorez les données récoltées en temps réel à l'aide d'une recherche par mots-cles libres, "
        "puis laissez notre outil analyser la compatibilité avec vos critères financiers."
    )
    st.markdown(" ")

    # Recuperation des donnees partagees dans la session Streamlit
    results = st.session_state.get("results", [])
    query = st.session_state.get("last_query", "")

    # Creation des onglets de navigation principale
    tab1, tab2, tab3, tab4 = st.tabs([
        "Recherche d'Etablissements",
        "Dashboard Analytique",
        "Orientation assistée",
        "Export des Données"
    ])

    # Onglet 1 : Recherche et filtres de base
    with tab1:
        render_school_search_page()

    # Onglet 2 : Visualisation graphique des donnees financieres
    with tab2:
        if results:
            render_dashboard(results)
        else:
            st.info("Lancez d'abord une recherche dans le premier onglet pour afficher les statistiques du dashboard.")

    # Onglet 3 : Analyse personnalisee par profil d'etudiant (IA)
    with tab3:
        if results:
            render_comparison_page(results)
        else:
            st.info("Lancez d'abord une recherche dans le premier onglet pour debloquer le conseiller d'orientation virtuel.")

    # Onglet 4 : Telechargement des rapports (Excel, CSV, TXT)
    with tab4:
        if results:
            render_export_section(results, query)
        else:
            st.info("Lancez d'abord une recherche dans le premier onglet pour pouvoir exporter vos resultats.")


if __name__ == "__main__":
    main()