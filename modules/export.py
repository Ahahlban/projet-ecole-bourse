import io
import pandas as pd
import streamlit as st
from datetime import datetime


def _format_export_list(value):
    """Convertit une liste en texte lisible pour export."""
    if isinstance(value, list):
        return ", ".join(str(v) for v in value) if value else "N/A"
    return value if value not in [None, ""] else "N/A"


def build_excel_report(results: list[dict], query: str = "") -> bytes:
    """
    Crée un fichier Excel structuré avec les résultats.

    Args:
        results: Liste de dicts avec les données des écoles
        query: La recherche effectuée

    Returns:
        Bytes du fichier Excel
    """
    rows = []
    for i, r in enumerate(results, 1):
        rows.append({
            "#": i,
            "Établissement": r.get("school_name", "N/A"),
            "Localisation": r.get("location", "N/A"),
            "Pays": r.get("country", "N/A"),
            "Type d'établissement": r.get("school_type", "N/A"),
            "Programmes": _format_export_list(r.get("programs", [])),
            "Niveaux d'études": _format_export_list(r.get("degree_levels", [])),
            "Langue d'enseignement": r.get("language_of_instruction", "N/A"),
            "Frais de scolarité": r.get("tuition_fee", "N/A"),
            "Frais de dossier": r.get("application_fee", "N/A"),
            "Bourse disponible": r.get("scholarship_available", "N/A"),
            "Montant bourse": r.get("scholarship_amount", "N/A"),
            "Détails bourse": r.get("scholarship_details", "N/A"),
            "Éligibilité": r.get("eligibility", "N/A"),
            "Conditions d'admission": r.get("admission_requirements", "N/A"),
            "Date limite": r.get("deadline", "N/A"),
            "Durée": r.get("duration", "N/A"),
            "Contact officiel": r.get("official_contact", "N/A"),
            "Résumé": r.get("summary", "N/A"),
            "Source (URL)": r.get("url", "N/A"),
        })

    df = pd.DataFrame(rows)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Résultats Écoles", index=False)

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
                "BourseScope"
            ]
        }
        pd.DataFrame(summary_data).to_excel(writer, sheet_name="Résumé", index=False)

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
                adjusted_width = min(max_length + 2, 60)
                worksheet.column_dimensions[column].width = adjusted_width

    return output.getvalue()


def build_csv_report(results: list[dict]) -> str:
    """
    Crée un fichier CSV avec les résultats.

    Args:
        results: Liste de dicts avec les données des écoles

    Returns:
        String CSV
    """
    rows = []
    for r in results:
        rows.append({
            "Établissement": r.get("school_name", "N/A"),
            "Localisation": r.get("location", "N/A"),
            "Pays": r.get("country", "N/A"),
            "Type": r.get("school_type", "N/A"),
            "Programmes": _format_export_list(r.get("programs", [])),
            "Niveaux": _format_export_list(r.get("degree_levels", [])),
            "Langue": r.get("language_of_instruction", "N/A"),
            "Frais de scolarité": r.get("tuition_fee", "N/A"),
            "Frais de dossier": r.get("application_fee", "N/A"),
            "Bourse disponible": r.get("scholarship_available", "N/A"),
            "Montant bourse": r.get("scholarship_amount", "N/A"),
            "Détails bourse": r.get("scholarship_details", "N/A"),
            "Éligibilité": r.get("eligibility", "N/A"),
            "Admission": r.get("admission_requirements", "N/A"),
            "Date limite": r.get("deadline", "N/A"),
            "Durée": r.get("duration", "N/A"),
            "Contact": r.get("official_contact", "N/A"),
            "Résumé": r.get("summary", "N/A"),
            "URL": r.get("url", "N/A"),
        })

    df = pd.DataFrame(rows)
    return df.to_csv(index=False)


def build_text_report(results: list[dict], query: str = "") -> str:
    """
    Crée un rapport texte formaté.

    Args:
        results: Liste de dicts avec les données des écoles
        query: La recherche effectuée

    Returns:
        String du rapport
    """
    lines = [
        "=" * 70,
        "              RAPPORT - BourseScope",
        "=" * 70,
        f"Recherche : {query or 'N/A'}",
        f"Date : {datetime.now().strftime('%d/%m/%Y à %H:%M')}",
        f"Résultats trouvés : {len(results)}",
        "=" * 70,
        "",
    ]

    for i, r in enumerate(results, 1):
        lines.extend([
            f"--- Résultat #{i} ---",
            f"Établissement         : {r.get('school_name', 'N/A')}",
            f"Localisation          : {r.get('location', 'N/A')}",
            f"Pays                  : {r.get('country', 'N/A')}",
            f"Type                  : {r.get('school_type', 'N/A')}",
            f"Programmes            : {_format_export_list(r.get('programs', []))}",
            f"Niveaux               : {_format_export_list(r.get('degree_levels', []))}",
            f"Langue                : {r.get('language_of_instruction', 'N/A')}",
            f"Frais scolarité       : {r.get('tuition_fee', 'N/A')}",
            f"Frais dossier         : {r.get('application_fee', 'N/A')}",
            f"Bourse disponible     : {r.get('scholarship_available', 'N/A')}",
            f"Montant bourse        : {r.get('scholarship_amount', 'N/A')}",
            f"Détails bourse        : {r.get('scholarship_details', 'N/A')}",
            f"Éligibilité           : {r.get('eligibility', 'N/A')}",
            f"Admission             : {r.get('admission_requirements', 'N/A')}",
            f"Date limite           : {r.get('deadline', 'N/A')}",
            f"Durée                 : {r.get('duration', 'N/A')}",
            f"Contact officiel      : {r.get('official_contact', 'N/A')}",
            f"Résumé                : {r.get('summary', 'N/A')}",
            f"Source                : {r.get('url', 'N/A')}",
            "",
        ])

    lines.extend([
        "=" * 70,
        "Rapport généré automatiquement par BourseScope",
        "=" * 70,
    ])

    return "\n".join(lines)


def render_export_section(results: list[dict], query: str = ""):
    """
    Affiche les boutons d'export dans l'interface Streamlit.

    Args:
        results: Liste de dicts avec les données des écoles
        query: La recherche effectuée
    """
    if not results:
        return

    st.markdown("---")
    st.subheader("Exporter les résultats")

    col1, col2, col3 = st.columns(3)

    with col1:
        excel_data = build_excel_report(results, query)
        st.download_button(
            label="Télécharger Excel (.xlsx)",
            data=excel_data,
            file_name=f"ecoles_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    with col2:
        csv_data = build_csv_report(results)
        st.download_button(
            label="Télécharger CSV",
            data=csv_data,
            file_name=f"ecoles_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with col3:
        text_data = build_text_report(results, query)
        st.download_button(
            label="Télécharger Rapport (.txt)",
            data=text_data,
            file_name=f"rapport_ecoles_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
            use_container_width=True,
        )
