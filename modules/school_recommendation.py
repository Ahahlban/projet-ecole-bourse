import google.generativeai as genai
import streamlit as st
import json
import re


def _extract_json(text: str):
    cleaned = text.strip().replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    match = re.search(r"(\[.*\]|\{.*\})", cleaned, re.DOTALL)
    if match:
        return json.loads(match.group(1))

    raise ValueError("JSON invalide")


def render_profile_form():
    st.subheader("Profil étudiant")

    with st.form("profile_form"):
        col1, col2 = st.columns(2)

        with col1:
            domaine = st.selectbox(
                "Domaine",
                ["Informatique", "Ingénierie", "Business", "Santé", "Autre"]
            )
            niveau = st.selectbox(
                "Niveau",
                ["Licence", "Master", "Doctorat"]
            )
            budget = st.slider("Budget annuel max", 0, 50000, 10000)

        with col2:
            pays = st.text_input("Pays souhaité")
            langue = st.selectbox("Langue", ["Français", "Anglais", "Autre"])
            priorite = st.selectbox(
                "Priorité",
                ["Coût faible", "Bourse", "Prestige"]
            )

        submitted = st.form_submit_button("Analyser")

        if submitted:
            return {
                "domaine": domaine,
                "niveau": niveau,
                "budget": budget,
                "pays": pays,
                "langue": langue,
                "priorite": priorite,
            }

    return None


def generate_recommendations(profile: dict, results: list[dict]):
    api_key = st.secrets.get("Gemini_API_Key")

    if not api_key:
        st.error("Clé API manquante.")
        return []

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-flash-lite-latest")

    prompt = f"""
Profil étudiant :
{profile}

Options disponibles :
{results}

Classe les meilleures options.
Retourne uniquement JSON :
[
  {{
    "school_name": "...",
    "score": 0,
    "reason": "..."
  }}
]
"""

    response = model.generate_content(prompt)
    data = _extract_json(response.text)

    if not isinstance(data, list):
        return []

    return data


def render_recommendation_page(results: list[dict]):
    if not results:
        st.info("Aucune donnée disponible.")
        return

    profile = render_profile_form()

    if profile:
        with st.spinner("Analyse en cours..."):
            recs = generate_recommendations(profile, results)

        for rec in recs:
            st.write(f"### {rec.get('school_name', '')}")
            st.write(f"Score : {rec.get('score', 0)}")
            st.write(rec.get("reason", ""))