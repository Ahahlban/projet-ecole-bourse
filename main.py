import streamlit as st
from modules.scraper import get_links
from modules.web_reader import extract_text
from modules.parser import analyze_content

st.set_page_config(page_title="EduSearch Low-Data", page_icon="🎓")

st.title("🎓 Trouvez votre École & Bourse")

# --- BARRE LATÉRALE (Filtres) ---
st.sidebar.header("Filtres de recherche")
location = st.sidebar.selectbox("Région", ["Toute la France", "Paris", "Lyon", "Bordeaux"])
school_type = st.sidebar.multiselect("Type d'établissement", ["Université", "École de Commerce", "École d'Art"])

# --- CORPS DE PAGE ---
query = st.text_input("Quelle formation cherchez-tu ?", placeholder="ex: Littérature Japonaise")

if st.button("Lancer la recherche"):
    with st.spinner("Analyse du web en cours (optimisé basse consommation)..."):
        # 1. On récupère les liens
                # Dans main.py, juste avant "links = get_links(...)"
        type_str = " ".join(school_type) # Transforme la liste en une seule phrase
        links = get_links(query, location, type_str)
                
        for link in links:
            with st.expander(f"📍 Source : {link[:50]}..."):
                # 2. On lit le texte
                raw_text = extract_text(link)
                
                # 3. On analyse
                data = analyze_content(raw_text)
                
                # 4. On affiche proprement
                st.write(f"**Bourse détectée :** {data['scholarship']}")
                st.write(f"**Note :** {data['details']}")
                st.info(f"Résumé du texte extrait : {raw_text[:200]}...")
                st.link_button("Voir le site original", link)