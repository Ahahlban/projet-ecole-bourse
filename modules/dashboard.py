import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st

from modules.utils import extract_numeric_amount


def build_results_dataframe(results: list[dict]) -> pd.DataFrame:
    """
    Transforme les resultats de recherche en DataFrame propre avec colonnes numeriques.

    Complexite : O(n) ou n = nombre de resultats.
    - Conversion numerique des montants : O(n) via apply
    - Construction des labels sources : O(n) via apply
    Retourne un DataFrame vide si la liste est vide.
    """
    if not results:
        return pd.DataFrame()

    df = pd.DataFrame(results)

    # Priorite : scholarship_estimated_amount, puis scholarship_amount
    def get_scholarship_amount(row):
        val = row.get("scholarship_estimated_amount") or row.get("scholarship_amount")
        return extract_numeric_amount(val)

    df["scholarship_amount_num"] = df.apply(get_scholarship_amount, axis=1)
    df["tuition_fee_num"] = df.get("tuition_fee_non_eu", df.get("tuition_fee", pd.Series(dtype=str))).apply(extract_numeric_amount)

    def build_source_label(row):
        school_name = row.get("school_name", "")
        url = row.get("url", "")

        if pd.notna(school_name) and str(school_name).strip() not in ["", "Non detecte"]:
            return str(school_name)[:30]

        if pd.notna(url) and "/" in str(url):
            try:
                return str(url).split("/")[2]
            except Exception:
                return str(url)[:30]

        return "Source inconnue"

    df["source_label"] = df.apply(build_source_label, axis=1)
    df["scholarship_status"] = df.get("scholarship_available", pd.Series(dtype=str)).fillna("A verifier")

    return df


def render_financial_comparison_chart(results: list[dict]):
    """
    Affiche un graphique en barres groupees comparant bourses et frais de scolarite.

    Complexite : O(n) ou n = nombre de resultats (construction du DataFrame).
    N'affiche rien si les donnees numeriques sont insuffisantes.
    """
    df = build_results_dataframe(results)

    if df.empty or (df["scholarship_amount_num"].isna().all() and df["tuition_fee_num"].isna().all()):
        st.info("Pas assez de donnees numeriques pour creer un graphique de comparaison.")
        return

    st.subheader("Comparaison bourses vs frais de scolarite")

    fig = go.Figure()

    if not df["scholarship_amount_num"].isna().all():
        fig.add_trace(go.Bar(
            name="Montant bourse",
            x=df["source_label"],
            y=df["scholarship_amount_num"],
            marker_color="#2ecc71",
            text=df["scholarship_amount_num"].apply(lambda x: f"{x:,.0f} EUR" if pd.notna(x) else ""),
            textposition="outside"
        ))

    if not df["tuition_fee_num"].isna().all():
        fig.add_trace(go.Bar(
            name="Frais de scolarite",
            x=df["source_label"],
            y=df["tuition_fee_num"],
            marker_color="#e74c3c",
            text=df["tuition_fee_num"].apply(lambda x: f"{x:,.0f} EUR" if pd.notna(x) else ""),
            textposition="outside"
        ))

    fig.update_layout(
        barmode="group",
        template="plotly_dark",
        title="Comparaison des montants detectes (EUR)",
        xaxis_title="Ecoles / Sources",
        yaxis_title="Montant (EUR)",
        height=500,
        font=dict(size=12),
        xaxis=dict(tickangle=-25),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
    )

    st.plotly_chart(fig, use_container_width=True)


def render_scholarship_coverage_chart(results: list[dict]):
    """
    Affiche un nuage de points Bourse vs Frais de Scolarite.
    La taille et la couleur de chaque point indiquent le taux de couverture de la bourse.

    Complexite : O(n) ou n = nombre de resultats valides (avec les deux montants).
    Necessite au moins 1 point valide pour s'afficher.
    """
    df = build_results_dataframe(results)
    if df.empty:
        return

    valid = df.dropna(subset=["scholarship_amount_num", "tuition_fee_num"])

    if valid.empty:
        return

    st.subheader("Rapport bourse / frais de scolarite")

    valid = valid.copy()
    valid = valid[valid["tuition_fee_num"] > 0]

    if valid.empty:
        return

    valid["ratio"] = (valid["scholarship_amount_num"] / valid["tuition_fee_num"] * 100).round(1)

    fig = px.scatter(
        valid,
        x="tuition_fee_num",
        y="scholarship_amount_num",
        size="ratio",
        color="ratio",
        color_continuous_scale="RdYlGn",
        hover_data=["source_label", "scholarship_status", "ratio"],
        labels={
            "tuition_fee_num": "Frais de Scolarite (EUR)",
            "scholarship_amount_num": "Montant de la Bourse (EUR)",
            "ratio": "Couverture (%)"
        },
        title="Plus le point est gros et vert, meilleur est le rapport bourse/frais",
    )

    fig.update_layout(
        template="plotly_dark",
        height=450,
        font=dict(size=12),
    )

    st.plotly_chart(fig, use_container_width=True)


def render_scholarship_distribution_chart(results: list[dict]):
    """
    Affiche un camembert de la repartition des statuts de bourses.

    Complexite : O(n) pour le comptage des valeurs.
    N'affiche rien si la colonne est absente ou vide.
    """
    df = build_results_dataframe(results)
    if df.empty or "scholarship_status" not in df.columns:
        return

    scholarships = df["scholarship_status"].dropna()
    scholarships = scholarships[~scholarships.isin(["N/A", "A verifier"])]

    if scholarships.empty:
        return

    st.subheader("Repartition des statuts de bourses")

    counts = scholarships.value_counts().head(8)

    fig = px.pie(
        values=counts.values,
        names=counts.index,
        color_discrete_sequence=px.colors.qualitative.Set3,
        title="Disponibilite des bourses par etablissement",
    )

    fig.update_layout(
        template="plotly_dark",
        height=400,
        font=dict(size=12),
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")

    st.plotly_chart(fig, use_container_width=True)


def render_country_distribution_chart(results: list[dict]):
    """
    Affiche un graphique en barres de la repartition des etablissements par pays.

    Complexite : O(n) pour le comptage, O(k log k) pour le tri (k = pays distincts).
    Affiche les 10 premiers pays.
    """
    df = build_results_dataframe(results)
    if df.empty or "country" not in df.columns:
        return

    countries = df["country"].dropna()
    countries = countries[countries != "Non detecte"]

    if countries.empty:
        return

    st.subheader("Repartition par pays")

    counts = countries.value_counts().head(10)

    fig = px.bar(
        x=counts.index,
        y=counts.values,
        labels={"x": "Pays", "y": "Nombre d'etablissements"},
        title="Top 10 pays detectes",
        color=counts.index,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )

    fig.update_layout(
        template="plotly_dark",
        height=400,
        font=dict(size=12),
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)


def render_dashboard(results: list[dict]):
    """
    Fonction principale du dashboard : affiche les KPIs et tous les graphiques.

    Complexite totale : O(n * g) ou n = nombre de resultats, g = nombre de graphiques (constant = 4).
    Chaque graphique reconstruit le DataFrame independamment : O(n) chacun.
    Affiche un message si aucun resultat n'est disponible.
    """
    if not results:
        st.info("Lancez une recherche pour voir le dashboard apparaitre ici.")
        return

    st.markdown("---")
    st.header("Dashboard analytique")

    df = build_results_dataframe(results)
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Sources analysees", len(results))

    with col2:
        avg_bourse = df["scholarship_amount_num"].mean()
        st.metric("Bourse moyenne", f"{avg_bourse:,.0f} EUR" if pd.notna(avg_bourse) else "N/A")

    with col3:
        avg_cout = df["tuition_fee_num"].mean()
        st.metric("Frais moyens", f"{avg_cout:,.0f} EUR" if pd.notna(avg_cout) else "N/A")

    with col4:
        if pd.notna(avg_bourse) and pd.notna(avg_cout) and avg_cout > 0:
            coverage = (avg_bourse / avg_cout * 100)
            st.metric("Couverture moyenne", f"{coverage:.0f}%")
        else:
            st.metric("Couverture moyenne", "N/A")

    render_financial_comparison_chart(results)

    col_left, col_right = st.columns(2)
    with col_left:
        render_scholarship_distribution_chart(results)
    with col_right:
        render_country_distribution_chart(results)

    render_scholarship_coverage_chart(results)