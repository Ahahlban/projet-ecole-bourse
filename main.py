import streamlit as st
import time
from modules.scraper import get_links
from modules.web_reader import get_page_content
from modules.parser import filter_school_links, analyze_content

# --- CONFIGURATION ---
st.set_page_config(page_title="EduSearch Global", page_icon="🌍", layout="wide")

# --- FONCTIONS AVEC CACHE ---

@st.cache_data(ttl=3600)
def cached_get_links(q, l, t):
    return get_links(q, l, t, max_results=30)

@st.cache_data(ttl=3600)
def cached_filter_links(links_list):
    return filter_school_links(links_list)

@st.cache_data(ttl=3600)
def cached_analysis(url, lang):
    # On transmet la langue cible à l'analyseur
    raw_text = get_page_content(url)
    return analyze_content(raw_text, lang), raw_text

# --- BARRE LATÉRALE (Filtres Internationaux) ---
st.sidebar.header("🌐 Configuration Globale")

# 1. Sélecteur de langue pour les résultats
target_lang = st.sidebar.selectbox(
    "Langue des résultats", 
    ["Français", "English", "Español", "Deutsch", "Português"]
)

st.sidebar.divider()

# 2. Saisie libre pour la localisation (plus de liste limitée !)
location = st.sidebar.text_input("📍 Pays ou Ville", placeholder="ex: Canada, Berlin, Tokyo...")

# 3. Saisie libre pour le type d'école
school_type = st.sidebar.text_input("🏫 Type d'école", placeholder="ex: University, College, Art School...")

# --- CORPS DE PAGE ---
st.title("🌍 EduSearch International")
st.subheader("Trouvez des bourses partout dans le monde")
st.markdown("---")

query = st.text_input("Quelle formation cherchez-vous ?", placeholder="ex: Computer Science, Design...")

if st.button("🚀 Lancer la recherche internationale"):
    if not query:
        st.warning("Veuillez entrer un mot-clé.")
    else:
        with st.spinner(f"Recherche en cours... (Cible : {target_lang})"):
            
            # Utilisation des saisies libres
            raw_links = cached_get_links(query, location, school_type)
            
            if not raw_links:
                st.error("❌ Aucun résultat trouvé. Essayez des mots-clés en anglais si la zone est internationale.")
            else:
                status_text = st.empty()
                status_text.info("🤖 Sélection des meilleures sources internationales...")
                
                links = cached_filter_links(raw_links)
                
                st.success(f"✅ {len(links)} sources retenues !")
                
                progress_bar = st.progress(0)
                
                for i, link in enumerate(links):
                    percent_complete = (i + 1) / len(links)
                    progress_bar.progress(percent_complete)
                    
                    # On passe la langue choisie à l'analyse
                    data, raw_text = cached_analysis(link, target_lang)

                    with st.expander(f"📍 Source : {link[:70]}..."):
                        col1, col2 = st.columns([2, 1])
                        with col1:
                            st.write(f"**Bourse :** {data.get('scholarship', 'N/A')}")
                            st.write(f"**Montant :** :green[{data.get('montant', 'N/A')}]") 
                            st.write(f"**Analyse ({target_lang}) :** {data.get('details', 'N/A')}")
                        with col2:
                            st.link_button("🌐 Visiter le site", link)
                        
                        st.divider()
                        st.caption(f"Aperçu du contenu original : {raw_text[:200]}...")

                st.balloons()