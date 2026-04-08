import re
import streamlit as st


def _clean_value(value):
    if value is None:
        return ""
    value = str(value).strip()
    invalid_values = {
        "",
        "n/a",
        "non détecté",
        "non verifie",
        "non vérifié",
        "à vérifier",
        "a vérifier",
        "unknown",
        "null",
        "none",
    }
    return "" if value.lower() in invalid_values else value


def _format_list(value):
    if isinstance(value, list):
        cleaned = [str(item).strip() for item in value if str(item).strip()]
        return ", ".join(cleaned) if cleaned else ""
    return _clean_value(value)


def _extract_numeric_amount(value):
    if value is None:
        return None

    text = str(value).strip().lower()
    if text in {"", "n/a", "non détecté", "non vérifié", "à vérifier"}:
        return None

    matches = re.findall(r"[\d]+(?:[\s.,]\d+)*", text)
    if not matches:
        return None

    try:
        cleaned = matches[0].replace(" ", "").replace(",", ".")
        return float(cleaned)
    except ValueError:
        return None


def _score_school(school: dict) -> int:
    score = 0

    tuition_num = _extract_numeric_amount(school.get("tuition_fee", ""))
    scholarship_num = _extract_numeric_amount(school.get("scholarship_amount", ""))
    scholarship_status = str(school.get("scholarship_available", "")).lower()

    if scholarship_status in {"oui", "possible"}:
        score += 25

    if scholarship_num is not None:
        score += 15

    if tuition_num is not None:
        if tuition_num == 0:
            score += 25
        elif tuition_num <= 3000:
            score += 22
        elif tuition_num <= 7000:
            score += 18
        elif tuition_num <= 12000:
            score += 12
        else:
            score += 5

    if _clean_value(school.get("admission_requirements", "")):
        score += 10

    if _clean_value(school.get("deadline", "")):
        score += 5

    if _clean_value(school.get("url", "")):
        score += 5

    if _clean_value(school.get("summary", "")):
        score += 5

    return score


def _school_strengths(school: dict) -> str:
    strengths = []

    scholarship_status = str(school.get("scholarship_available", "")).lower()
    tuition_num = _extract_numeric_amount(school.get("tuition_fee", ""))

    if scholarship_status in {"oui", "possible"}:
        strengths.append("bourse disponible ou probable")
    if tuition_num is not None and tuition_num <= 7000:
        strengths.append("frais raisonnables")
    if _clean_value(school.get("admission_requirements", "")):
        strengths.append("admission renseignée")
    if _clean_value(school.get("deadline", "")):
        strengths.append("date limite indiquée")
    if _clean_value(school.get("url", "")):
        strengths.append("lien officiel disponible")
    if _clean_value(school.get("language_of_instruction", "")):
        strengths.append("langue d’enseignement précisée")

    return ", ".join(strengths) if strengths else "profil correct mais informations partielles"


def _school_weaknesses(school: dict) -> str:
    weaknesses = []

    if not _clean_value(school.get("tuition_fee", "")):
        weaknesses.append("frais non précisés")
    if not _clean_value(school.get("scholarship_available", "")):
        weaknesses.append("bourse non précisée")
    if not _clean_value(school.get("admission_requirements", "")):
        weaknesses.append("admission peu détaillée")
    if not _clean_value(school.get("deadline", "")):
        weaknesses.append("date limite absente")
    if not _clean_value(school.get("summary", "")):
        weaknesses.append("résumé peu exploitable")

    return ", ".join(weaknesses) if weaknesses else "peu de points faibles visibles"


def _remove_school_from_comparison(index: int):
    selected = st.session_state.get("comparison_selection", [])
    if 0 <= index < len(selected):
        selected.pop(index)
        st.session_state.comparison_selection = selected


def _display_line(label: str, value: str):
    cleaned = _clean_value(value)
    if cleaned:
        st.write(f"**{label}** {cleaned}")
    else:
        st.write(f"**{label}** Non renseigné")


def _display_list_line(label: str, value):
    formatted = _format_list(value)
    if formatted:
        st.write(f"**{label}** {formatted}")
    else:
        st.write(f"**{label}** Non renseigné")


def _render_compare_box(label: str, value: str):
    display_value = _clean_value(value) or "Non renseigné"
    st.markdown(
        f"""
        <div class="compare-mini-box">
            <div class="compare-mini-label">{label}</div>
            <div class="compare-mini-value">{display_value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_school_compare_card(school: dict, index: int):
    title = school.get("school_name", f"École {index + 1}")
    subtitle = " • ".join(
        [
            part for part in [
                _clean_value(school.get("location", "")),
                _clean_value(school.get("country", "")),
                _clean_value(school.get("school_type", "")),
            ] if part
        ]
    )

    url = _clean_value(school.get("url", ""))

    with st.container(border=True):
        st.markdown(f"### {title}")
        if subtitle:
            st.caption(subtitle)

        st.markdown(
            f"""
            <div class="compare-score-box">
                <div class="compare-score-label">Score global</div>
                <div class="compare-score-value">{school.get('global_score', 0)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        _render_compare_box("Budget", str(school.get("tuition_fee", "")) or "Non renseigné")
        _render_compare_box("Bourse", str(school.get("scholarship_available", "")) or "Non renseigné")
        _render_compare_box("Montant bourse", str(school.get("scholarship_amount", "")) or "Non renseigné")
        _render_compare_box("Durée", str(school.get("duration", "")) or "Non renseigné")
        _render_compare_box("Date limite", str(school.get("deadline", "")) or "Non renseigné")
        _render_compare_box("Langue", str(school.get("language_of_instruction", "")) or "Non renseigné")

        st.markdown("#### Points forts")
        st.write(school.get("strengths", "") or "Non renseigné")

        st.markdown("#### Points faibles")
        st.write(school.get("weaknesses", "") or "Non renseigné")

        st.markdown("#### Académique")
        _display_list_line("Programmes :", school.get("programs", []))
        _display_list_line("Niveaux :", school.get("degree_levels", []))

        st.markdown("#### Admission")
        _display_line("Conditions d'admission :", school.get("admission_requirements", ""))
        _display_line("Éligibilité :", school.get("eligibility", ""))

        st.markdown("#### Résumé")
        st.write(_clean_value(school.get("summary", "")) or "Non renseigné")

        if url:
            st.markdown(f'<div class="school-link"><a href="{url}" target="_blank">Lien officiel</a></div>', unsafe_allow_html=True)


def render_school_comparison_page():
    st.subheader("Comparateur d'écoles")

    selected = st.session_state.get("comparison_selection", [])

    if not selected:
        st.info("Aucune école sélectionnée. Ajoute des écoles depuis l'onglet Recherche.")
        return

    st.caption("Tu peux comparer jusqu'à 3 écoles.")

    top_left, top_right = st.columns([3, 1])
    with top_left:
        st.write(f"**{len(selected)} école(s) sélectionnée(s)**")
    with top_right:
        if st.button("Vider la sélection", use_container_width=True):
            st.session_state.comparison_selection = []
            st.rerun()

    remove_cols = st.columns(len(selected))
    for index, school in enumerate(selected):
        with remove_cols[index]:
            if st.button(
                f"Retirer {school.get('school_name', f'École {index + 1}')}",
                key=f"remove_compare_{index}",
                use_container_width=True,
            ):
                _remove_school_from_comparison(index)
                st.rerun()

    st.markdown("---")

    scored_schools = []
    for school in selected:
        school_copy = dict(school)
        school_copy["global_score"] = _score_school(school_copy)
        school_copy["strengths"] = _school_strengths(school_copy)
        school_copy["weaknesses"] = _school_weaknesses(school_copy)
        scored_schools.append(school_copy)

    best_school = max(scored_schools, key=lambda x: x.get("global_score", 0))

    st.success(
        f"Meilleure option actuelle : **{best_school.get('school_name', 'École non détectée')}** "
        f"avec un score de **{best_school.get('global_score', 0)}**."
    )

    st.markdown("### Comparaison visuelle")

    cols = st.columns(len(scored_schools))
    for index, school in enumerate(scored_schools):
        with cols[index]:
            _render_school_compare_card(school, index)