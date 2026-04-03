import streamlit as st
from modules.scraper import get_links
from modules.web_reader import get_page_content
from modules.parser import filter_school_links, analyze_content
from modules.chatbot import render_chatbot, update_search_context, init_chatbot
from modules.dashboard import render_dashboard
from modules.recommender import render_recommendation_page
from modules.export import render_export_section

st.set_page_config(page_title="EduSearch Global", page_icon="🌍", layout="wide")

# Initialisation des états
if "all_results" not in st.session_state:
    st.session_state.all_results = []
if "last_query" not in st.session_state:
    st.session_state.last_query = ""
init_chatbot()

# --- CACHE ---
@st.cache_data(ttl=3600)
def cached_get_links(q, l, t):
    return get_links(q, l, t, max_results=30)

@st.cache_data(ttl=3600)
def cached_filter_links(links_list):
    return filter_school_links(links_list)

@st.cache_data(ttl=3600)
def cached_analysis(url, lang):
    raw_text = get_page_content(url)
    data = analyze_content(raw_text, lang)
    return data, raw_text

# --- BARRE LATÉRALE ---
st.sidebar.header("🌐 Options Internationales")
target_lang = st.sidebar.selectbox("Langue des résultats", ["Français", "English", "Español", "Deutsch", "Português"])
st.sidebar.divider()
location = st.sidebar.text_input("📍 Localisation (Pays/Ville)", placeholder="ex: Canada, France...")
school_type = st.sidebar.text_input("🏫 Type d'école", placeholder="ex: University, Ecole de commerce...")

st.title("🌍 EduSearch Global")
tab_search, tab_dashboard, tab_reco, tab_chat = st.tabs(["🔍 Recherche", "📊 Dashboard", "🎯 Recommandations IA", "🤖 Chatbot IA"])

with tab_search:
    query = st.text_input("Quelle formation cherchez-vous ?", placeholder="ex: Management, Informatique...")
    if st.button("🚀 Lancer la recherche"):
        if not query:
            st.warning("Entrez un mot-clé.")
        else:
            st.session_state.last_query = query
            collected_results = []
            with st.spinner("Analyse mondiale en cours..."):
                raw_links = cached_get_links(query, location, school_type)
                if not raw_links:
                    st.error("❌ Aucun résultat trouvé.")
                else:
                    links = cached_filter_links(raw_links)
                    progress_bar = st.progress(0)
                    for i, link in enumerate(links):
                        progress_bar.progress((i + 1) / len(links))
                        data, raw_text = cached_analysis(link, target_lang)
                        res = {"url": link, "scholarship": data.get("scholarship"), "montant": data.get("montant"), "cout_annuel": data.get("cout_annuel"), "details": data.get("details")}
                        collected_results.append(res)
                        with st.expander(f"📍 {link[:60]}..."):
                            st.write(f"**Bourse :** {res['scholarship']} | **Montant :** :green[{res['montant']}] | **Coût :** :red[{res['cout_annuel']}]")
                            st.write(f"**Détails :** {res['details']}")
                    
                    st.session_state.all_results = collected_results
                    update_search_context(collected_results) # Pour le chatbot
                    st.balloons()
    
    render_export_section(st.session_state.all_results, st.session_state.last_query)

with tab_dashboard: render_dashboard(st.session_state.all_results)
with tab_reco: render_recommendation_page(st.session_state.all_results)
with tab_chat: render_chatbot()