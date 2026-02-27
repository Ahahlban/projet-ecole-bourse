import streamlit as st
import time
from modules.scraper import get_links
from modules.web_reader import get_page_content
from modules.parser import filter_school_links, analyze_content

# --- CONFIGURATION ---
st.set_page_config(page_title="EduSearch Low-Data", page_icon="🎓", layout="wide")

# --- FONCTIONS AVEC CACHE (Économie de Quota) ---

@st.cache_data(ttl=3600) # Garde en mémoire pendant 1 heure
def cached_get_links(q, l, t):
    return get_links(q, l, t, max_results=30)

@st.cache_data(ttl=3600)
def cached_filter_links(links_list):
    return filter_school_links(links_list)

@st.cache_data(ttl=3600)
def cached_analysis(url):
    # Combine la lecture et l'analyse pour ne faire qu'une seule entrée en cache
    raw_text = get_page_content(url)
    return analyze_content(raw_text), raw_text

# --- INTERFACE ---
st.sidebar.header("🔍 Filtres de recherche")
location = st.sidebar.selectbox("Région", ["Toute la France", "Paris", "Lyon", "Bordeaux", "Marseille"])
school_type = st.sidebar.multiselect("Type d'établissement", ["Université", "École de Commerce", "École d'Ingénieur", "École d'Art"])

st.title("🎓 Trouvez votre École & Bourse")
st.markdown("---")

query = st.text_input("Quelle formation cherchez-vous ?", placeholder="ex: Informatique")

if st.button("🚀 Lancer la recherche"):
    if not query:
        st.warning("Oups ! Entre un mot-clé.")
    else:
        with st.spinner("Recherche intelligente... (Optimisation Data en cours)"):
            
            type_str = " ".join(school_type)
            loc_str = "" if location == "Toute la France" else location
            
            # Utilisation des versions CACHÉES
            raw_links = cached_get_links(query, loc_str, type_str)
            
            if not raw_links:
                st.error("❌ Aucun lien trouvé.")
            else:
                status_text = st.empty()
                status_text.info("🤖 Filtrage IA des écoles (Utilise le cache si déjà fait)...")
                
                # Filtrage optimisé
                links = cached_filter_links(raw_links)
                
                st.success(f"✅ {len(links)} écoles retenues.")
                
                progress_bar = st.progress(0)
                
                for i, link in enumerate(links):
                    percent_complete = (i + 1) / len(links)
                    progress_bar.progress(percent_complete)
                    
                    # Analyse optimisée : si l'URL a déjà été vue, l'IA n'est pas appelée
                    data, raw_text = cached_analysis(link)

                    with st.expander(f"📍 École : {link[:70]}..."):
                        col1, col2 = st.columns([2, 1])
                        with col1:
                            st.write(f"**Bourse :** {data.get('scholarship', 'N/A')}")
                            st.write(f"**Montant :** :green[{data.get('montant', 'N/A')}]") 
                            st.write(f"**Détails :** {data.get('details', 'N/A')}")
                        with col2:
                            st.link_button("🌐 Visiter", link)
                        
                        st.divider()
                        st.caption(f"Aperçu : {raw_text[:200]}...")

                st.balloons()