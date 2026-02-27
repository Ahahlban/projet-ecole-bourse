import streamlit as st
import time
from modules.scraper import get_links
from modules.web_reader import get_page_content # Nom corrigé ici
from modules.parser import filter_school_links, analyze_content # Import du filtre

# --- CONFIGURATION ---
st.set_page_config(page_title="EduSearch Low-Data", page_icon="🎓", layout="wide")

# --- BARRE LATÉRALE (Filtres) ---
st.sidebar.header("🔍 Filtres de recherche")
location = st.sidebar.selectbox("Région", ["Toute la France", "Paris", "Lyon", "Bordeaux", "Marseille"])
school_type = st.sidebar.multiselect("Type d'établissement", ["Université", "École de Commerce", "École d'Ingénieur", "École d'Art"])

# --- CORPS DE PAGE ---
st.title("🎓 Trouvez votre École & Bourse")
st.markdown("---")

query = st.text_input("Quelle formation cherchez-vous ?", placeholder="ex: Littérature Japonaise")

if st.button("🚀 Lancer la recherche"):
    if not query:
        st.warning("Oups ! Entre un mot-clé pour commencer.")
    else:
        with st.spinner("Recherche et filtrage intelligent en cours..."):
            
            # Étape 1 : Nettoyage des filtres
            type_str = " ".join(school_type)
            loc_str = "" if location == "Toute la France" else location
            
            # Étape 2 : Appel au Scraper (30 liens pour avoir du choix)
            raw_links = get_links(query, loc_str, type_str, max_results=30)
            
            if not raw_links:
                st.error("❌ Aucun lien trouvé. DuckDuckGo ne répond pas ou la recherche est trop précise.")
            else:
                # NOUVELLE ÉTAPE : Filtrage IA pour le Low Data
                st.info(f"🔍 {len(raw_links)} sources trouvées. L'IA sélectionne les meilleures écoles...")
                links = filter_school_links(raw_links)
                
                st.success(f"✅ {len(links)} écoles pertinentes retenues ! Analyse du contenu...")
                
                # Étape 3 : Barre de progression pour l'analyse
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i, link in enumerate(links):
                    # Mise à jour de la progression
                    percent_complete = (i + 1) / len(links)
                    progress_bar.progress(percent_complete)
                    status_text.text(f"Lecture et analyse de l'école {i+1}/{len(links)}...")

                    # Affichage du résultat dans un accordéon
                    with st.expander(f"📍 École : {link[:70]}..."):
                        # Lecture & Analyse avec les nouveaux noms
                        raw_text = get_page_content(link)
                        data = analyze_content(raw_text)
                        
                        # Mise en page des résultats
                        col1, col2 = st.columns([2, 1])
                        with col1:
                            st.write(f"**Bourse détectée :** {data.get('scholarship', 'Inconnu')}")
                            st.write(f"**Montant estimé :** :green[{data.get('montant', 'N/A')}]") 
                            st.write(f"**Analyse :** {data.get('details', 'Aucun détail')}")
                        with col2:
                            st.link_button("🌐 Visiter le site", link)
                        
                        st.divider()
                        st.caption(f"Aperçu du texte analysé : {raw_text[:200]}...")

                # Nettoyage final
                status_text.text("Analyse terminée avec succès !")
                st.balloons()