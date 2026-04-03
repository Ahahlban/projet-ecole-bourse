import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
 
 
def prepare_dataframe(results: list[dict]) -> pd.DataFrame:
    """
    Transforme les résultats de recherche en DataFrame propre.
 
    Args:
        results: Liste de dicts avec les données de bourses
 
    Returns:
        DataFrame nettoyé avec colonnes numériques
    """
    if not results:
        return pd.DataFrame()
 
    df = pd.DataFrame(results)
 
    # Extraire les valeurs numériques des montants (ex: "5 000 €" -> 5000)
    def extract_number(value):
        if not value or value == "N/A":
            return None
        import re
        numbers = re.findall(r"[\d\s]+", str(value).replace(",", "."))
        if numbers:
            try:
                return float(numbers[0].replace(" ", ""))
            except ValueError:
                return None
        return None
 
    df["montant_num"] = df.get("montant", pd.Series(dtype=str)).apply(extract_number)
    df["cout_num"] = df.get("cout_annuel", pd.Series(dtype=str)).apply(extract_number)
 
    # Créer un label court pour les sources
    df["source_label"] = df.get("url", pd.Series(dtype=str)).apply(
        lambda x: str(x).split("/")[2] if pd.notna(x) and "/" in str(x) else str(x)[:30]
    )
 
    return df
 
 
def render_comparison_chart(results: list[dict]):
    """
    Affiche un graphique en barres comparant bourses et coûts.
 
    Args:
        results: Liste de dicts avec les données de bourses
    """
    df = prepare_dataframe(results)
    if df.empty or (df["montant_num"].isna().all() and df["cout_num"].isna().all()):
        st.info("📊 Pas assez de données numériques pour créer un graphique de comparaison.")
        return
 
    st.subheader("📊 Comparaison Bourses vs Coûts de Scolarité")
 
    fig = go.Figure()
 
    # Barres pour les montants de bourses
    if not df["montant_num"].isna().all():
        fig.add_trace(go.Bar(
            name="💰 Montant Bourse",
            x=df["source_label"],
            y=df["montant_num"],
            marker_color="#2ecc71",
            text=df["montant_num"].apply(lambda x: f"{x:,.0f} €" if pd.notna(x) else ""),
            textposition="outside"
        ))
 
    # Barres pour les coûts de scolarité
    if not df["cout_num"].isna().all():
        fig.add_trace(go.Bar(
            name="🏫 Coût Scolarité",
            x=df["source_label"],
            y=df["cout_num"],
            marker_color="#e74c3c",
            text=df["cout_num"].apply(lambda x: f"{x:,.0f} €" if pd.notna(x) else ""),
            textposition="outside"
        ))
 
    fig.update_layout(
        barmode="group",
        template="plotly_dark",
        title="Comparaison des montants (€)",
        xaxis_title="Sources",
        yaxis_title="Montant (€)",
        height=500,
        font=dict(size=12),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
    )
 
    st.plotly_chart(fig, use_container_width=True)
 
 
def render_scatter_plot(results: list[dict]):
    """
    Affiche un nuage de points Bourse vs Coût.
    Permet de visualiser le rapport qualité/prix.
 
    Args:
        results: Liste de dicts avec les données de bourses
    """
    df = prepare_dataframe(results)
    valid = df.dropna(subset=["montant_num", "cout_num"])
 
    if valid.empty or len(valid) < 2:
        return
 
    st.subheader("🎯 Rapport Bourse / Coût de Scolarité")
 
    # Calculer le ratio bourse/coût
    valid = valid.copy()
    valid["ratio"] = (valid["montant_num"] / valid["cout_num"] * 100).round(1)
 
    fig = px.scatter(
        valid,
        x="cout_num",
        y="montant_num",
        size="ratio",
        color="ratio",
        color_continuous_scale="RdYlGn",
        hover_data=["source_label", "scholarship", "ratio"],
        labels={
            "cout_num": "Coût de Scolarité (€)",
            "montant_num": "Montant de la Bourse (€)",
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
 
 
def render_pie_chart(results: list[dict]):
    """
    Affiche la répartition des types de bourses trouvées.
 
    Args:
        results: Liste de dicts avec les données de bourses
    """
    df = prepare_dataframe(results)
    if df.empty:
        return
 
    scholarships = df["scholarship"].dropna()
    scholarships = scholarships[scholarships != "N/A"]
 
    if scholarships.empty:
        return
 
    st.subheader("🍰 Répartition des Bourses Trouvées")
 
    counts = scholarships.value_counts().head(8)
 
    fig = px.pie(
        values=counts.values,
        names=counts.index,
        color_discrete_sequence=px.colors.qualitative.Set3,
        title="Types de bourses identifiées",
    )
 
    fig.update_layout(
        template="plotly_dark",
        height=400,
        font=dict(size=12),
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
 
    st.plotly_chart(fig, use_container_width=True)
 
 
def render_dashboard(results: list[dict]):
    """
    Fonction principale : affiche tous les graphiques du dashboard.
 
    Args:
        results: Liste de dicts avec les données de bourses
    """
    if not results:
        st.info("📊 Lancez une recherche pour voir le dashboard apparaître ici.")
        return
 
    st.markdown("---")
    st.header("📊 Dashboard Interactif")
 
    # Métriques en haut
    df = prepare_dataframe(results)
    col1, col2, col3, col4 = st.columns(4)
 
    with col1:
        st.metric("🔍 Sources analysées", len(results))
    with col2:
        avg_bourse = df["montant_num"].mean()
        st.metric("💰 Bourse moyenne", f"{avg_bourse:,.0f} €" if pd.notna(avg_bourse) else "N/A")
    with col3:
        avg_cout = df["cout_num"].mean()
        st.metric("🏫 Coût moyen", f"{avg_cout:,.0f} €" if pd.notna(avg_cout) else "N/A")
    with col4:
        if pd.notna(avg_bourse) and pd.notna(avg_cout) and avg_cout > 0:
            coverage = (avg_bourse / avg_cout * 100)
            st.metric("📈 Couverture moyenne", f"{coverage:.0f}%")
        else:
            st.metric("📈 Couverture moyenne", "N/A")
 
    # Graphiques
    render_comparison_chart(results)
    render_scatter_plot(results)
    render_pie_chart(results)
  
