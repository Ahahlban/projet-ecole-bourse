import streamlit as st
import time
from modules.scraper import get_links
from modules.web_reader import get_page_content
from modules.parser import filter_school_links, analyze_content
 
# ===== NOUVEAUX IMPORTS (tes features) =====
from modules.chatbot import render_chatbot, update_search_context, init_chatbot
from modules.dashboard import render_dashboard
from modules.recommender import render_recommendation_page
from modules.export import render_export_section
 
# --- CONFIGURATION ---
st.set_page_config(page_title="EduSearch Global", page_icon="🌍", layout="wide")
 
# --- INITIALISATION SESSION ---
if "all_results" not in st.session_state:
    st.session_state.all_results = []
if "last_query" not in st.session_state:
    st.session_state.last_query = ""
 
init_chatbot()
 
# --- FONCTIONS AVEC CACHE (Économie de Quota) ---
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
 
# --- CLÉ API (nécessaire pour les features IA) ---
api_key = st.sidebar.text_input("🔑 Clé API Google Gemini", type="password")
 
# --- BARRE LATÉRALE ---
st.sidebar.header("🌐 Options Internationales")
 
target_lang = st.sidebar.selectbox(
    "Langue des résultats",
    ["Français", "English", "Español", "Deutsch", "Português"]
)
 
st.sidebar.divider()
 
location = st.sidebar.text_input("📍 Localisation (Pays/Ville)", placeholder="ex: Canada, Tokyo, Berlin...")
school_type = st.sidebar.text_input("🏫 Type d'école", placeholder="ex: University, Design School...")
 
# --- NAVIGATION PAR ONGLETS (NOUVELLE FEATURE) ---
st.title("🌍 EduSearch Global")
st.subheader("Trouvez des bourses et comparez les coûts de scolarité")
 
tab_search, tab_dashboard, tab_reco, tab_chat = st.tabs([
    "🔍 Recherche",
    "📊 Dashboard",
    "🎯 Recommandations IA",
    "🤖 Chatbot IA"
])
 
# ===== ONGLET 1 : RECHERCHE (code existant amélioré) =====
with tab_search:
    st.markdown("---")
    query = st.text_input("Quelle formation cherchez-vous ?", placeholder="ex: Architecture, Medicine...")
 
    if st.button("🚀 Lancer la recherche internationale"):
        if not query:
            st.warning("Veuillez entrer un mot-clé.")
        else:
            st.session_state.last_query = query
            collected_results = []
 
            with st.spinner(f"Analyse mondiale en cours ({target_lang})..."):
                # Étape 1 : Scraping
                raw_links = cached_get_links(query, location, school_type)
 
                if not raw_links:
                    st.error("❌ Aucun résultat. Essayez des termes en anglais pour l'international.")
                else:
                    # Étape 2 : Filtrage intelligent
                    links = cached_filter_links(raw_links)
                    st.success(f"✅ {len(links)} sources pertinentes identifiées !")
                    progress_bar = st.progress(0)
 
                    # Étape 3 : Analyse détaillée
                    for i, link in enumerate(links):
                        percent_complete = (i + 1) / len(links)
                        progress_bar.progress(percent_complete)
 
                        data, raw_text = cached_analysis(link, target_lang)
 
                        # Stocker les résultats pour le dashboard et les exports
                        result_entry = {
                            "url": link,
                            "scholarship": data.get("scholarship", "N/A"),
                            "montant": data.get("montant", "N/A"),
                            "cout_annuel": data.get("cout_annuel", "N/A"),
                            "details": data.get("details", "N/A"),
                        }
                        collected_results.append(result_entry)
 
                        with st.expander(f"📍 Source : {link[:70]}..."):
                            col1, col2 = st.columns([2, 1])
                            with col1:
                                st.write(f"**Bourse :** {data.get('scholarship', 'N/A')}")
                                st.write(f"**Montant Bourse :** :green[{data.get('montant', 'N/A')}]")
                                st.write(f"**Coût Scolarité :** :red[{data.get('cout_annuel', 'N/A')}]")
                                st.write(f"**Résumé ({target_lang}) :** {data.get('details', 'N/A')}")
                            with col2:
                                st.link_button("🌐 Visiter le site", link)
                            st.divider()
                            st.caption(f"Texte source détecté : {raw_text[:250]}...")
 
                    # Sauvegarder les résultats dans la session
                    st.session_state.all_results = collected_results
 
                    # Mettre à jour le contexte du chatbot
                    update_search_context(collected_results)
 
                    st.balloons()
 
    # Section export (s'affiche si des résultats existent)
    render_export_section(st.session_state.all_results, st.session_state.last_query)
 
# ===== ONGLET 2 : DASHBOARD =====
with tab_dashboard:
    render_dashboard(st.session_state.all_results)
 
# ===== ONGLET 3 : RECOMMANDATIONS IA =====
with tab_reco:
    if not api_key:
        st.warning("⚠️ Entrez votre clé API Google Gemini dans la barre latérale pour utiliser cette fonctionnalité.")
    else:
        render_recommendation_page(st.session_state.all_results, api_key)
 
# ===== ONGLET 4 : CHATBOT IA =====
with tab_chat:
    if not api_key:
        st.warning("⚠️ Entrez votre clé API Google Gemini dans la barre latérale pour utiliser le chatbot.")
    else:
        render_chatbot(api_key)
