"""
MAIN.PY — EduSearch Global
===========================
Application principale Streamlit.
Fonctionne 100% hors-ligne une fois la base générée.

Lancement : streamlit run main.py
"""

import streamlit as st
from modules.search import search, load_database
from modules.chatbot import repondre
from modules.export import generer_txt

# ── Configuration de la page ───────────────────────────────────────────
st.set_page_config(
    page_title="EduSearch — Trouvez votre école",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Style CSS minimaliste ──────────────────────────────────────────────
st.markdown("""
<style>
    /* Couleurs principales */
    :root {
        --vert: #2ecc71;
        --bleu: #3498db;
        --rouge: #e74c3c;
        --gris: #f8f9fa;
    }

    /* Carte école */
    .carte-ecole {
        background: white;
        border-left: 5px solid #3498db;
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 12px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.07);
    }

    .carte-ecole h4 {
        color: #2c3e50;
        margin: 0 0 6px 0;
        font-size: 17px;
    }

    .badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        margin: 2px;
    }

    .badge-bourse { background: #d5f5e3; color: #1e8449; }
    .badge-pays   { background: #d6eaf8; color: #1a5276; }
    .badge-niveau { background: #fef9e7; color: #7d6608; }

    /* Bot */
    .bulle-bot {
        background: #eaf4fb;
        border-radius: 12px 12px 12px 0;
        padding: 12px 16px;
        margin: 6px 0;
        color: #1a252f;
        font-size: 14px;
    }

    .bulle-user {
        background: #d5f5e3;
        border-radius: 12px 12px 0 12px;
        padding: 12px 16px;
        margin: 6px 0;
        text-align: right;
        color: #1a252f;
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)


# ── Initialisation de la session ───────────────────────────────────────
if "resultats" not in st.session_state:
    st.session_state.resultats = []
if "historique_bot" not in st.session_state:
    st.session_state.historique_bot = []
if "filtres" not in st.session_state:
    st.session_state.filtres = {}
if "query" not in st.session_state:
    st.session_state.query = ""


# ══════════════════════════════════════════════════════════════════════
# EN-TÊTE
# ══════════════════════════════════════════════════════════════════════
st.markdown("## 🎓 EduSearch — Trouvez votre école")
st.caption("Base de données locale • Fonctionne avec peu de connexion • Téléchargeable hors-ligne")

# Vérifier si la base existe
base = load_database()
if not base:
    st.error(
        "⚠️ La base de données est vide.\n\n"
        "Lancez d'abord le générateur dans le terminal :\n"
        "```\npython modules/generator.py\n```"
    )
    st.stop()

st.success(f"✅ Base chargée : **{len(base)} écoles** disponibles hors-ligne")
st.markdown("---")


# ══════════════════════════════════════════════════════════════════════
# BARRE LATÉRALE — FILTRES
# ══════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### 🔎 Filtres de recherche")
    st.caption("Tous les filtres fonctionnent sans connexion")

    query = st.text_input(
        "Mots-clés",
        placeholder="Ex: informatique, bourse, France...",
        value=st.session_state.query
    )

    # Extraire les valeurs uniques de la base
    tous_pays = sorted({s.get("pays", "") for s in base if s.get("pays")})
    toutes_categories = sorted({s.get("categorie", "") for s in base if s.get("categorie")})
    toutes_langues = sorted({s.get("langue", "") for s in base if s.get("langue")})
    tous_niveaux = sorted({
        n for s in base
        for n in (s.get("niveau", []) if isinstance(s.get("niveau"), list) else [s.get("niveau", "")])
        if n
    })

    categorie = st.selectbox("📚 Domaine", ["Tous"] + toutes_categories)
    pays = st.selectbox("🌍 Pays", ["Tous"] + tous_pays)
    langue = st.selectbox("🗣️ Langue", ["Tous"] + toutes_langues)
    niveau = st.selectbox("🎓 Niveau visé", ["Tous"] + tous_niveaux)
    budget_max = st.text_input("💶 Budget max (€/an)", placeholder="Ex: 5000")
    bourse_seulement = st.checkbox("🎁 Avec bourse uniquement")

    rechercher = st.button("🔍 Rechercher", use_container_width=True, type="primary")

    st.markdown("---")
    st.markdown("### ℹ️ Comment ça marche ?")
    st.markdown("""
1. **Filtrez** avec les options ci-dessus
2. **Lisez** les résultats à droite
3. **Posez des questions** au mini-bot
4. **Téléchargez** votre résumé en .txt
    """)


# ══════════════════════════════════════════════════════════════════════
# LOGIQUE DE RECHERCHE
# ══════════════════════════════════════════════════════════════════════
if rechercher:
    filtres = {
        "categorie": "" if categorie == "Tous" else categorie,
        "pays": "" if pays == "Tous" else pays,
        "langue": "" if langue == "Tous" else langue,
        "niveau": "" if niveau == "Tous" else niveau,
        "budget_max": budget_max,
        "bourse_seulement": bourse_seulement,
    }

    st.session_state.resultats = search(query, filtres)
    st.session_state.filtres = filtres
    st.session_state.query = query
    # Réinitialiser le bot à chaque nouvelle recherche
    st.session_state.historique_bot = []


# ══════════════════════════════════════════════════════════════════════
# ONGLETS PRINCIPAUX
# ══════════════════════════════════════════════════════════════════════
tab1, tab2, tab3 = st.tabs(["📋 Résultats", "💬 Mini-Bot", "📥 Télécharger"])


# ─────────────────────────────────────────────
# ONGLET 1 — RÉSULTATS
# ─────────────────────────────────────────────
with tab1:
    resultats = st.session_state.resultats

    if not resultats:
        if rechercher:
            st.warning("Aucune école ne correspond à vos critères. Essayez d'élargir les filtres.")
        else:
            st.info("👈 Utilisez les filtres à gauche et cliquez sur **Rechercher**.")
    else:
        st.markdown(f"**{len(resultats)} école(s) trouvée(s)**")
        st.markdown("")

        for school in resultats:
            # Couleur selon disponibilité de bourse
            bourse = str(school.get("bourse_disponible", "")).lower()
            couleur_bordure = "#2ecc71" if bourse == "oui" else "#f39c12" if bourse == "possible" else "#3498db"

            # Badges
            badge_bourse = ""
            if bourse == "oui":
                badge_bourse = '<span class="badge badge-bourse">🎁 Bourse disponible</span>'
            elif bourse == "possible":
                badge_bourse = '<span class="badge badge-bourse" style="background:#fef9e7;color:#7d6608;">⚠️ Bourse possible</span>'

            niveaux = school.get("niveau", [])
            badges_niveaux = " ".join(
                f'<span class="badge badge-niveau">{n}</span>'
                for n in (niveaux if isinstance(niveaux, list) else [niveaux])
            )

            # Carte HTML
            st.markdown(f"""
            <div class="carte-ecole" style="border-left-color:{couleur_bordure}">
                <h4>🏫 {school.get('nom', '?')}</h4>
                <span class="badge badge-pays">🌍 {school.get('pays', '?')} — {school.get('ville', '?')}</span>
                {badges_niveaux}
                {badge_bourse}
                <p style="margin:10px 0 4px 0; color:#555; font-size:13px;">
                    <b>Domaine :</b> {school.get('categorie', '?')} &nbsp;|&nbsp;
                    <b>Langue :</b> {school.get('langue', '?')} &nbsp;|&nbsp;
                    <b>Durée :</b> {school.get('duree', '?')}
                </p>
                <p style="margin:4px 0; color:#555; font-size:13px;">
                    <b>Frais :</b> {school.get('frais_annuels', 'Non précisé')} &nbsp;|&nbsp;
                    <b>Admission :</b> {school.get('conditions_admission', '?')}
                </p>
                <p style="margin:8px 0 0 0; color:#333; font-size:13px; font-style:italic;">
                    📝 {school.get('resume', '')}
                </p>
                {"<p style='margin:6px 0 0 0; font-size:12px;'>🔗 <a href='" + school.get('site_web','') + "' target='_blank'>" + school.get('site_web','') + "</a></p>" if school.get('site_web') else ""}
            </div>
            """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# ONGLET 2 — MINI-BOT
# ─────────────────────────────────────────────
with tab2:
    st.markdown("### 💬 Posez une question sur les résultats")
    st.caption("Le bot répond sans connexion en lisant la base locale.")

    resultats = st.session_state.resultats

    if not resultats:
        st.info("Lancez d'abord une recherche pour activer le bot.")
    else:
        # Afficher l'historique
        for message in st.session_state.historique_bot:
            if message["role"] == "user":
                st.markdown(
                    f'<div class="bulle-user">👤 {message["texte"]}</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<div class="bulle-bot">🤖 {message["texte"]}</div>',
                    unsafe_allow_html=True
                )

        # Zone de saisie
        with st.form("form_bot", clear_on_submit=True):
            question = st.text_input(
                "Votre question",
                placeholder="Ex: Quelle école a une bourse ? Quelle est la moins chère ?",
                label_visibility="collapsed"
            )
            envoyer = st.form_submit_button("Envoyer ➤", use_container_width=True)

        if envoyer and question.strip():
            # Ajouter la question à l'historique
            st.session_state.historique_bot.append({
                "role": "user",
                "texte": question
            })

            # Générer la réponse
            reponse = repondre(question, resultats)

            # Ajouter la réponse à l'historique
            st.session_state.historique_bot.append({
                "role": "bot",
                "texte": reponse
            })

            st.rerun()

        # Suggestions de questions
        st.markdown("**Exemples de questions :**")
        cols = st.columns(2)
        suggestions = [
            "Quelle école a une bourse ?",
            "Quelle est la moins chère ?",
            "Quelles écoles sont en France ?",
            "Combien de résultats ?",
        ]
        for i, sugg in enumerate(suggestions):
            with cols[i % 2]:
                if st.button(sugg, key=f"sugg_{i}", use_container_width=True):
                    st.session_state.historique_bot.append({"role": "user", "texte": sugg})
                    reponse = repondre(sugg, resultats)
                    st.session_state.historique_bot.append({"role": "bot", "texte": reponse})
                    st.rerun()


# ─────────────────────────────────────────────
# ONGLET 3 — TÉLÉCHARGEMENT
# ─────────────────────────────────────────────
with tab3:
    st.markdown("### 📥 Télécharger vos résultats")
    st.caption("Fichier .txt lisible hors-ligne sur tout appareil, même sans smartphone récent.")

    resultats = st.session_state.resultats

    if not resultats:
        st.info("Lancez d'abord une recherche pour générer le fichier.")
    else:
        # Générer le contenu du fichier
        contenu_txt = generer_txt(
            resultats,
            query=st.session_state.query,
            filters=st.session_state.filtres
        )

        # Aperçu
        with st.expander("👁️ Aperçu du fichier", expanded=False):
            st.code(contenu_txt[:1500] + "\n...", language=None)

        # Bouton de téléchargement
        st.download_button(
            label=f"📄 Télécharger le résumé ({len(resultats)} école(s)) en .txt",
            data=contenu_txt.encode("utf-8"),
            file_name="edusearch_resultats.txt",
            mime="text/plain",
            use_container_width=True,
            type="primary"
        )

        st.markdown("""
        **Ce fichier contient :**
        - Le nom et la localisation de chaque école
        - Les frais annuels et les informations sur les bourses
        - Les conditions d'admission et les dates limites
        - Un résumé pour chaque école
        - Les contacts et sites web officiels
        """)
