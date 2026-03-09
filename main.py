import streamlit as st
import time
from modules.scraper import get_links
from modules.web_reader import get_page_content
from modules.parser import filter_school_links, analyze_content

# --- CONFIGURATION ---
st.set_page_config(page_title="EduSearch Global", page_icon="🌍", layout="wide")

# --- FONCTIONS AVEC CACHE (Économie de Quota) ---

@st.cache_data(ttl=3600)
def cached_get_links(q, l, t):
    return get_links(q, l, t, max_results=30)

@st.cache_data(ttl=3600)
def cached_filter_links(links_list):
    return filter_school_links(links_list)

@st.cache_data(ttl=3600)
def cached_analysis(url, lang):
    # Combine la lecture et l'analyse avec support de langue
    raw_text = get_page_content(url)
    data = analyze_content(raw_text, lang)
    return data, raw_text

# --- BARRE LATÉRALE ---
st.sidebar.header("🌐 Options Internationales")

# Choix de la langue d'affichage
target_lang = st.sidebar.selectbox(
    "Langue des résultats", 
    ["Français", "English", "Español", "Deutsch", "Português"]
)

st.sidebar.divider()

# Saisie libre pour l'international
location = st.sidebar.text_input("📍 Localisation (Pays/Ville)", placeholder="ex: Canada, Tokyo, Berlin...")
school_type = st.sidebar.text_input("🏫 Type d'école", placeholder="ex: University, Design School...")

# --- CORPS DE PAGE ---
st.title("🌍 EduSearch Global")
st.subheader("Trouvez des bourses et comparez les coûts de scolarité")
st.markdown("---")

query = st.text_input("Quelle formation cherchez-vous ?", placeholder="ex: Architecture, Medicine...")

if st.button("🚀 Lancer la recherche internationale"):
    if not query:
        st.warning("Veuillez entrer un mot-clé.")
    else:
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

                    with st.expander(f"📍 Source : {link[:70]}..."):
                        col1, col2 = st.columns([2, 1])
                        with col1:
                            st.write(f"**Bourse :** {data.get('scholarship', 'N/A')}")
                            st.write(f"**Montant Bourse :** :green[{data.get('montant', 'N/A')}]") 
                            # Affichage du nouveau coût de l'école
                            st.write(f"**Coût Scolarité :** :red[{data.get('cout_annuel', 'N/A')}]") 
                            st.write(f"**Résumé ({target_lang}) :** {data.get('details', 'N/A')}")
                        with col2:
                            st.link_button("🌐 Visiter le site", link)
                        
                        st.divider()
                        st.caption(f"Texte source détecté : {raw_text[:250]}...")

                st.balloons()