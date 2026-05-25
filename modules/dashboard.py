import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st

from modules.utils import extract_numeric_amount


def build_results_dataframe(results: list[dict]) -> pd.DataFrame:
    """
    Transforme les résultats de recherche en DataFrame propre.

    Args:
        results: Liste de dicts avec les données des écoles

    Returns:
        DataFrame nettoyé avec colonnes numériques
    """
    if not results:
        return pd.DataFrame()

    df = pd.DataFrame(results)

    df["scholarship_amount_num"] = df.get("scholarship_amount", pd.Series(dtype=str)).apply(extract_numeric_amount)
    df["tuition_fee_num"] = df.get("tuition_fee", pd.Series(dtype=str)).apply(extract_numeric_amount)

    # Label plus lisible
    def build_source_label(row):
        school_name = row.get("school_name", "")
        url = row.get("url", "")

        if pd.notna(school_name) and str(school_name).strip() not in ["", "Non détecté"]:
            return str(school_name)[:40]

        if pd.notna(url) and "/" in str(url):
            try:
                return str(url).split("/")[2]
            except Exception:
                return str(url)[:40]

        return "Source inconnue"

    df["source_label"] = df.apply(build_source_label, axis=1)

    # Normalisation du statut bourse
    df["scholarship_status"] = df.get("scholarship_available", pd.Series(dtype=str)).fillna("À vérifier")

    return df


def render_financial_comparison_chart(results: list[dict]):
    """
    Affiche un graphique en barres comparant montant de bourse et frais de scolarité.
    """
    df = build_results_dataframe(results)

    if df.empty or (df["scholarship_amount_num"].isna().all() and df["tuition_fee_num"].isna().all()):
        st.info("Pas assez de données numériques pour créer un graphique de comparaison.")
        return

    st.subheader("Comparaison bourses vs frais de scolarité")

    fig = go.Figure()

    if not df["scholarship_amount_num"].isna().all():
        fig.add_trace(go.Bar(
            name="Montant bourse",
            x=df["source_label"],
            y=df["scholarship_amount_num"],
            marker_color="#2ecc71",
            text=df["scholarship_amount_num"].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else ""),
            textposition="outside"
        ))

    if not df["tuition_fee_num"].isna().all():
        fig.add_trace(go.Bar(
            name="Frais de scolarité",
            x=df["source_label"],
            y=df["tuition_fee_num"],
            marker_color="#e74c3c",
            text=df["tuition_fee_num"].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else ""),
            textposition="outside"
        ))

    fig.update_layout(
        barmode="group",
        template="plotly_dark",
        title="Comparaison des montants détectés",
        xaxis_title="Écoles / Sources",
        yaxis_title="Montant",
        height=500,
        font=dict(size=12),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
    )

    st.plotly_chart(fig, use_container_width=True)


def render_scholarship_coverage_chart(results: list[dict]):
    """
    Affiche un nuage de points Bourse vs Frais de Scolarité.
    """
    df = build_results_dataframe(results)
    valid = df.dropna(subset=["scholarship_amount_num", "tuition_fee_num"])

    if valid.empty or len(valid) < 2:
        return

    st.subheader("Rapport bourse / frais de scolarité")

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
            "tuition_fee_num": "Frais de Scolarité",
            "scholarship_amount_num": "Montant de la Bourse",
            "ratio": "Couverture (%)"
        },
        title="Plus le point est gros et vert, meilleur est le rapport",
    )

    fig.update_layout(
        template="plotly_dark",
        height=450,
        font=dict(size=12),
    )

    st.plotly_chart(fig, use_container_width=True)


def render_scholarship_distribution_chart(results: list[dict]):
    """
    Affiche la répartition des statuts de bourses trouvés.
    """
    df = build_results_dataframe(results)
    if df.empty or "scholarship_status" not in df.columns:
        return

    scholarships = df["scholarship_status"].dropna()
    scholarships = scholarships[scholarships != "N/A"]

    if scholarships.empty:
        return

    st.subheader("Répartition des bourses trouvées")

    counts = scholarships.value_counts().head(8)

    fig = px.pie(
        values=counts.values,
        names=counts.index,
        color_discrete_sequence=px.colors.qualitative.Set3,
        title="Disponibilité des bourses",
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
    Affiche la répartition des résultats par pays.
    """
    df = build_results_dataframe(results)
    if df.empty or "country" not in df.columns:
        return

    countries = df["country"].dropna()
    countries = countries[countries != "Non détecté"]

    if countries.empty:
        return

    st.subheader("Répartition par pays")

    counts = countries.value_counts().head(10)

    fig = px.bar(
        x=counts.index,
        y=counts.values,
        labels={"x": "Pays", "y": "Nombre d'écoles"},
        title="Top pays détectés"
    )

    fig.update_layout(
        template="plotly_dark",
        height=400,
        font=dict(size=12),
    )

    st.plotly_chart(fig, use_container_width=True)


def render_dashboard(results: list[dict]):
    """
    Fonction principale : affiche tous les graphiques du dashboard.
    """
    if not results:
        st.info("Lancez une recherche pour voir le dashboard apparaître ici.")
        return

    st.markdown("---")
    st.header("Dashboard interactif")

    df = build_results_dataframe(results)
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Sources analysées", len(results))

    with col2:
        avg_bourse = df["scholarship_amount_num"].mean()
        st.metric("Bourse moyenne", f"{avg_bourse:,.0f}" if pd.notna(avg_bourse) else "N/A")

    with col3:
        avg_cout = df["tuition_fee_num"].mean()
        st.metric("Coût moyen", f"{avg_cout:,.0f}" if pd.notna(avg_cout) else "N/A")

    with col4:
        if pd.notna(avg_bourse) and pd.notna(avg_cout) and avg_cout > 0:
            coverage = (avg_bourse / avg_cout * 100)
            st.metric("Couverture moyenne", f"{coverage:.0f}%")
        else:
            st.metric("Couverture moyenne", "N/A")

    render_financial_comparison_chart(results)
    render_scholarship_coverage_chart(results)
    render_scholarship_distribution_chart(results)
    render_country_distribution_chart(results)
