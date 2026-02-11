import streamlit as st
import time
from modules.scraper import get_links
from modules.web_reader import extract_text
from modules.parser import analyze_content

# --- CONFIGURATION ---
st.set_page_config(page_title="EduSearch Low-Data", page_icon="🎓", layout="wide")

# --- BARRE LATÉRALE (Filtres) ---
st.sidebar.header("🔍 Filtres de recherche")
location = st.sidebar.selectbox("Région", ["Toute la France", "Paris", "Lyon", "Bordeaux", "Marseille"])
school_type = st.sidebar.multiselect("Type d'établissement", ["Université", "École de Commerce", "École d'Ingénieur", "École d'Art"])

# --- CORPS DE PAGE ---
st.title("🎓 Trouvez votre École & Bourse")
st.markdown("---")

query = st.text_input("Quelle formation cherchez-tu ?", placeholder="ex: Littérature Japonaise")

if st.button("🚀 Lancer la recherche"):
    if not query:
        st.warning("Oups ! Entre un mot-clé pour commencer.")
    else:
        # On prépare le message de chargement
        with st.spinner("Recherche des meilleures opportunités..."):
            
            # Étape 1 : Nettoyage des filtres
            type_str = " ".join(school_type)
            loc_str = "" if location == "Toute la France" else location
            
            # Étape 2 : Appel au Scraper
            links = get_links(query, loc_str, type_str)
            
            # --- DIAGNOSTIC ---
            if not links:
                st.error("❌ Aucun lien trouvé. Google ne répond pas ou la recherche est trop précise.")
                st.info("💡 Conseil : Essaie de décocher certains types d'établissements ou change de région.")
            else:
                st.success(f"✅ {len(links)} sources trouvées ! Analyse en cours...")
                
                # Étape 3 : Barre de progression pour l'analyse
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i, link in enumerate(links):
                    # Mise à jour de la progression
                    percent_complete = (i + 1) / len(links)
                    progress_bar.progress(percent_complete)
                    status_text.text(f"Lecture du site {i+1}/{len(links)}...")

                    # Affichage du résultat dans un accordéon
                    with st.expander(f"📍 Source : {link[:60]}..."):
                        # Lecture & Analyse
                        raw_text = extract_text(link)
                        data = analyze_content(raw_text)
                        
                        # Mise en page des résultats
                        col1, col2 = st.columns([2, 1])
                        with col1:
                            st.write(f"**Bourse détectée :** {data['scholarship']}")
                            st.write(f"**Analyse :** {data['details']}")
                        with col2:
                            st.link_button("🌐 Visiter le site", link)
                        
                        st.divider()
                        st.caption(f"Aperçu du contenu : {raw_text[:250]}...")

                # Nettoyage final
                status_text.text("Analyse terminée avec succès !")
                st.balloons() # La petite touche festive !