import io
import pandas as pd
import streamlit as st
from datetime import datetime
 
 
def create_excel_report(results: list[dict], query: str = "") -> bytes:
    """
    Crée un fichier Excel structuré avec les résultats.
 
    Args:
        results: Liste de dicts avec les données de bourses
        query: La recherche effectuée
 
    Returns:
        Bytes du fichier Excel
    """
    # Créer le DataFrame principal
    rows = []
    for i, r in enumerate(results, 1):
        rows.append({
            "#": i,
            "Bourse": r.get("scholarship", "N/A"),
            "Montant Bourse": r.get("montant", "N/A"),
            "Coût Scolarité": r.get("cout_annuel", "N/A"),
            "Résumé": r.get("details", "N/A"),
            "Source (URL)": r.get("url", "N/A"),
        })
 
    df = pd.DataFrame(rows)
 
    # Créer le fichier Excel avec mise en forme
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        # Feuille principale
        df.to_excel(writer, sheet_name="Résultats Bourses", index=False)
 
        # Feuille de résumé
        summary_data = {
            "Info": [
                "Recherche effectuée",
                "Date du rapport",
                "Nombre de résultats",
                "Généré par"
            ],
            "Valeur": [
                query or "N/A",
                datetime.now().strftime("%d/%m/%Y à %H:%M"),
                len(results),
                "EduSearch Global 🌍"
            ]
        }
        pd.DataFrame(summary_data).to_excel(writer, sheet_name="Résumé", index=False)
 
        # Ajuster la largeur des colonnes
        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]
            for column_cells in worksheet.columns:
                max_length = 0
                column = column_cells[0].column_letter
                for cell in column_cells:
                    try:
                        if cell.value:
                            max_length = max(max_length, len(str(cell.value)))
                    except Exception:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column].width = adjusted_width
 
    return output.getvalue()
 
 
def create_csv_report(results: list[dict]) -> str:
    """
    Crée un fichier CSV simple avec les résultats.
 
    Args:
        results: Liste de dicts avec les données de bourses
 
    Returns:
        String CSV
    """
    rows = []
    for r in results:
        rows.append({
            "Bourse": r.get("scholarship", "N/A"),
            "Montant": r.get("montant", "N/A"),
            "Coût Scolarité": r.get("cout_annuel", "N/A"),
            "Résumé": r.get("details", "N/A"),
            "URL": r.get("url", "N/A"),
        })
 
    df = pd.DataFrame(rows)
    return df.to_csv(index=False)
 
 
def create_text_report(results: list[dict], query: str = "") -> str:
    """
    Crée un rapport texte formaté.
 
    Args:
        results: Liste de dicts avec les données de bourses
        query: La recherche effectuée
 
    Returns:
        String du rapport
    """
    lines = [
        "=" * 60,
        "       RAPPORT - EduSearch Global 🌍",
        "=" * 60,
        f"Recherche : {query or 'N/A'}",
        f"Date : {datetime.now().strftime('%d/%m/%Y à %H:%M')}",
        f"Résultats trouvés : {len(results)}",
        "=" * 60,
        "",
    ]
 
    for i, r in enumerate(results, 1):
        lines.extend([
            f"--- Résultat #{i} ---",
            f"📌 Bourse     : {r.get('scholarship', 'N/A')}",
            f"💰 Montant    : {r.get('montant', 'N/A')}",
            f"🏫 Coût       : {r.get('cout_annuel', 'N/A')}",
            f"📝 Résumé     : {r.get('details', 'N/A')}",
            f"🔗 Source     : {r.get('url', 'N/A')}",
            "",
        ])
 
    lines.extend([
        "=" * 60,
        "Rapport généré automatiquement par EduSearch Global",
        "=" * 60,
    ])
 
    return "\n".join(lines)
 
 
def render_export_section(results: list[dict], query: str = ""):
    """
    Affiche les boutons d'export dans l'interface Streamlit.
 
    Args:
        results: Liste de dicts avec les données de bourses
        query: La recherche effectuée
    """
    if not results:
        return
 
    st.markdown("---")
    st.subheader("📥 Exporter les Résultats")
 
    col1, col2, col3 = st.columns(3)
 
    with col1:
        # Export Excel
        excel_data = create_excel_report(results, query)
        st.download_button(
            label="📊 Télécharger Excel (.xlsx)",
            data=excel_data,
            file_name=f"bourses_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
 
    with col2:
        # Export CSV
        csv_data = create_csv_report(results)
        st.download_button(
            label="📋 Télécharger CSV",
            data=csv_data,
            file_name=f"bourses_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True,
        )
 
    with col3:
        # Export Texte
        text_data = create_text_report(results, query)
        st.download_button(
            label="📄 Télécharger Rapport (.txt)",
            data=text_data,
            file_name=f"rapport_bourses_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
            use_container_width=True,
        )
