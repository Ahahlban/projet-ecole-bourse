import streamlit as st
from modules.scraper import get_links
from modules.web_reader import get_page_content
from modules.parser import filter_school_links, analyze_content
import pandas as pd

st.set_page_config(page_title="EcoBourse - Recherche Low Data", page_icon="🎓")

st.title("🎓 EcoBourse")
st.subheader("Trouvez des bourses d'études sans gaspiller votre data")

# Formulaire de recherche
with st.sidebar:
    st.header("Critères de recherche")
    keywords = st.text_input("Mots-clés (ex: Ingénieur, Design)", "Informatique")
    location = st.text_input("Ville ou Région", "Lyon")
    school_type = st.selectbox("Type d'école", ["Université", "École Privée", "IUT", "Grande École"])
    
    btn_search = st.button("Lancer la recherche")

if btn_search:
    # Étape 1 : Scraping des liens bruts
    with st.status("🔍 Recherche des liens sur DuckDuckGo...", expanded=True) as status:
        raw_links = get_links(keywords, location, school_type, max_results=30)
        st.write(f"{len(raw_links)} liens trouvés au total.")
        
        # Étape 2 : Filtrage IA (L'étape magique Low Data)
        status.update(label="🤖 L'IA sélectionne les meilleures écoles...", state="running")
        valid_links = filter_school_links(raw_links)
        st.write(f"Filtrage terminé : {len(valid_links)} sites d'écoles retenus.")
        
        results_data = []
        
        # Étape 3 : Analyse approfondie des liens retenus
        status.update(label="📄 Analyse du contenu des pages...", state="running")
        for url in valid_links:
            st.write(f"Analyse de : {url}")
            
            # Lecture du texte de la page
            content = get_page_content(url)
            
            # Analyse IA du texte
            analysis = analyze_content(content)
            
            results_data.append({
                "École/Lien": url,
                "Bourse détectée": analysis.get("scholarship", "N/A"),
                "Montant": analysis.get("montant", "N/A"),
                "Détails": analysis.get("details", "N/A")
            })
        
        status.update(label="✅ Analyse terminée !", state="complete")

    # Affichage des résultats
    if results_data:
        df = pd.DataFrame(results_data)
        st.table(df)
    else:
        st.warning("Aucun résultat pertinent n'a été trouvé.")

else:
    st.info("Entrez vos critères à gauche et cliquez sur 'Lancer la recherche' pour commencer.")