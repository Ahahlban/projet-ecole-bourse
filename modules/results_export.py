import io
from datetime import datetime

import pandas as pd
import streamlit as st


def list_to_export_text(value):
    if isinstance(value, list):
        return ", ".join(str(v) for v in value) if value else "N/A"
    return value if value not in [None, ""] else "N/A"


def build_excel_report(results: list[dict], query: str = "") -> bytes:
    rows = []

    for index, school in enumerate(results, 1):
        rows.append(
            {
                "#": index,
                "Établissement": school.get("school_name", "N/A"),
                "Localisation": school.get("location", "N/A"),
                "Pays": school.get("country", "N/A"),
                "Type d'établissement": school.get("school_type", "N/A"),
                "Programmes": list_to_export_text(school.get("programs", [])),
                "Niveaux d'études": list_to_export_text(school.get("degree_levels", [])),
                "Langue d'enseignement": school.get("language_of_instruction", "N/A"),
                "Frais de scolarité": school.get("tuition_fee", "N/A"),
                "Frais de dossier": school.get("application_fee", "N/A"),
                "Bourse disponible": school.get("scholarship_available", "N/A"),
                "Montant bourse": school.get("scholarship_amount", "N/A"),
                "Détails bourse": school.get("scholarship_details", "N/A"),
                "Éligibilité": school.get("eligibility", "N/A"),
                "Conditions d'admission": school.get("admission_requirements", "N/A"),
                "Date limite": school.get("deadline", "N/A"),
                "Durée": school.get("duration", "N/A"),
                "Contact officiel": school.get("official_contact", "N/A"),
                "Résumé": school.get("summary", "N/A"),
                "Source (URL)": school.get("url", "N/A"),
            }
        )

    df = pd.DataFrame(rows)
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Résultats Écoles", index=False)

        summary_df = pd.DataFrame(
            {
                "Info": [
                    "Recherche effectuée",
                    "Date du rapport",
                    "Nombre de résultats",
                    "Généré par",
                ],
                "Valeur": [
                    query or "N/A",
                    datetime.now().strftime("%d/%m/%Y à %H:%M"),
                    len(results),
                    "EduSearch Global",
                ],
            }
        )
        summary_df.to_excel(writer, sheet_name="Résumé", index=False)

        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]
            for column_cells in worksheet.columns:
                max_length = 0
                column_letter = column_cells[0].column_letter

                for cell in column_cells:
                    try:
                        if cell.value is not None:
                            max_length = max(max_length, len(str(cell.value)))
                    except Exception:
                        pass

                worksheet.column_dimensions[column_letter].width = min(max_length + 2, 60)

    return output.getvalue()


def build_csv_report(results: list[dict]) -> str:
    rows = []

    for school in results:
        rows.append(
            {
                "Établissement": school.get("school_name", "N/A"),
                "Localisation": school.get("location", "N/A"),
                "Pays": school.get("country", "N/A"),
                "Type": school.get("school_type", "N/A"),
                "Programmes": list_to_export_text(school.get("programs", [])),
                "Niveaux": list_to_export_text(school.get("degree_levels", [])),
                "Langue": school.get("language_of_instruction", "N/A"),
                "Frais de scolarité": school.get("tuition_fee", "N/A"),
                "Frais de dossier": school.get("application_fee", "N/A"),
                "Bourse disponible": school.get("scholarship_available", "N/A"),
                "Montant bourse": school.get("scholarship_amount", "N/A"),
                "Détails bourse": school.get("scholarship_details", "N/A"),
                "Éligibilité": school.get("eligibility", "N/A"),
                "Admission": school.get("admission_requirements", "N/A"),
                "Date limite": school.get("deadline", "N/A"),
                "Durée": school.get("duration", "N/A"),
                "Contact": school.get("official_contact", "N/A"),
                "Résumé": school.get("summary", "N/A"),
                "URL": school.get("url", "N/A"),
            }
        )

    df = pd.DataFrame(rows)
    return df.to_csv(index=False)


def build_text_report(results: list[dict], query: str = "") -> str:
    lines = [
        "=" * 70,
        "RAPPORT - EduSearch Global",
        "=" * 70,
        f"Recherche : {query or 'N/A'}",
        f"Date : {datetime.now().strftime('%d/%m/%Y à %H:%M')}",
        f"Résultats trouvés : {len(results)}",
        "=" * 70,
        "",
    ]

    for index, school in enumerate(results, 1):
        lines.extend(
            [
                f"Résultat #{index}",
                f"Établissement         : {school.get('school_name', 'N/A')}",
                f"Localisation          : {school.get('location', 'N/A')}",
                f"Pays                  : {school.get('country', 'N/A')}",
                f"Type                  : {school.get('school_type', 'N/A')}",
                f"Programmes            : {list_to_export_text(school.get('programs', []))}",
                f"Niveaux               : {list_to_export_text(school.get('degree_levels', []))}",
                f"Langue                : {school.get('language_of_instruction', 'N/A')}",
                f"Frais scolarité       : {school.get('tuition_fee', 'N/A')}",
                f"Frais dossier         : {school.get('application_fee', 'N/A')}",
                f"Bourse disponible     : {school.get('scholarship_available', 'N/A')}",
                f"Montant bourse        : {school.get('scholarship_amount', 'N/A')}",
                f"Détails bourse        : {school.get('scholarship_details', 'N/A')}",
                f"Éligibilité           : {school.get('eligibility', 'N/A')}",
                f"Admission             : {school.get('admission_requirements', 'N/A')}",
                f"Date limite           : {school.get('deadline', 'N/A')}",
                f"Durée                 : {school.get('duration', 'N/A')}",
                f"Contact officiel      : {school.get('official_contact', 'N/A')}",
                f"Résumé                : {school.get('summary', 'N/A')}",
                f"Source                : {school.get('url', 'N/A')}",
                "",
            ]
        )

    lines.extend(
        [
            "=" * 70,
            "Rapport généré automatiquement par EduSearch Global",
            "=" * 70,
        ]
    )

    return "\n".join(lines)


def render_results_export_section(results: list[dict], query: str = ""):
    if not results:
        st.info("Aucun résultat à exporter.")
        return

    st.subheader("Exporter les résultats")

    col1, col2, col3 = st.columns(3)

    with col1:
        excel_data = build_excel_report(results, query)
        st.download_button(
            label="Télécharger Excel",
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
            label="Télécharger TXT",
            data=text_data,
            file_name=f"rapport_ecoles_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
            use_container_width=True,
        )