import io
import pandas as pd
import streamlit as st
from datetime import datetime


def _format_export_list(value) -> str:
    """
    Convertit une liste ou une valeur en texte lisible pour l'export,
    en nettoyant les résidus de chaînes vides ou invalides.
    """
    invalid_values = {
        "", "n/a", "non détecté", "non verifie", "non verifié", "non vérifié",
        "à vérifier", "a vérifier", "unknown", "null", "none"
    }
    
    if isinstance(value, list):
        cleaned_list = [str(v).strip() for v in value if str(v).strip() and str(v).lower().strip() not in invalid_values]
        return ", ".join(cleaned_list) if cleaned_list else "N/A"
        
    if value is None or str(value).strip().lower() in invalid_values:
        return "N/A"
        
    return str(value).strip()


def build_excel_report(results: list[dict], query: str = "") -> bytes:
    """
    Crée un fichier Excel structuré avec les résultats et un onglet résumé.

    Args:
        results: Liste de dicts avec les données des écoles
        query: La recherche effectuée

    Returns:
        Bytes du fichier Excel prêt pour le téléchargement
    """
    rows = []
    for i, r in enumerate(results, 1):
        rows.append({
            "#": i,
            "Établissement": _format_export_list(r.get("school_name")),
            "Localisation": _format_export_list(r.get("location")),
            "Pays": _format_export_list(r.get("country")),
            "Type d'établissement": _format_export_list(r.get("school_type")),
            "Programmes": _format_export_list(r.get("programs")),
            "Niveaux d'études": _format_export_list(r.get("degree_levels")),
            "Langue d'enseignement": _format_export_list(r.get("language_of_instruction")),
            "Frais de scolarité": _format_export_list(r.get("tuition_fee")),
            "Frais de dossier": _format_export_list(r.get("application_fee")),
            "Bourse disponible": _format_export_list(r.get("scholarship_available")),
            "Montant bourse": _format_export_list(r.get("scholarship_amount")),
            "Détails bourse": _format_export_list(r.get("scholarship_details")),
            "Éligibilité": _format_export_list(r.get("eligibility")),
            "Conditions d'admission": _format_export_list(r.get("admission_requirements")),
            "Date limite": _format_export_list(r.get("deadline")),
            "Durée": _format_export_list(r.get("duration")),
            "Contact officiel": _format_export_list(r.get("official_contact")),
            "Résumé": _format_export_list(r.get("summary")),
            "Source (URL)": _format_export_list(r.get("url")),
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
                "SchoolFinder"
            ]
        }
        pd.DataFrame(summary_data).to_excel(writer, sheet_name="Résumé", index=False)

        # Ajustement automatique de la largeur des colonnes Excel
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
    Crée un fichier CSV avec les résultats formatés.

    Args:
        results: Liste de dicts avec les données des écoles

    Returns:
        String au format CSV
    """
    rows = []
    for r in results:
        rows.append({
            "Établissement": _format_export_list(r.get("school_name")),
            "Localisation": _format_export_list(r.get("location")),
            "Pays": _format_export_list(r.get("country")),
            "Type": _format_export_list(r.get("school_type")),
            "Programmes": _format_export_list(r.get("programs")),
            "Niveaux": _format_export_list(r.get("degree_levels")),
            "Langue": _format_export_list(r.get("language_of_instruction")),
            "Frais de scolarité": _format_export_list(r.get("tuition_fee")),
            "Frais de dossier": _format_export_list(r.get("application_fee")),
            "Bourse disponible": _format_export_list(r.get("scholarship_available")),
            "Montant bourse": _format_export_list(r.get("scholarship_amount")),
            "Détails bourse": _format_export_list(r.get("scholarship_details")),
            "Éligibilité": _format_export_list(r.get("eligibility")),
            "Admission": _format_export_list(r.get("admission_requirements")),
            "Date limite": _format_export_list(r.get("deadline")),
            "Durée": _format_export_list(r.get("duration")),
            "Contact": _format_export_list(r.get("official_contact")),
            "Résumé": _format_export_list(r.get("summary")),
            "URL": _format_export_list(r.get("url")),
        })

    df = pd.DataFrame(rows)
    return df.to_csv(index=False)


def build_text_report(results: list[dict], query: str = "") -> str:
    """
    Crée un rapport texte joliment formaté pour lecture brute.

    Args:
        results: Liste de dicts avec les données des écoles
        query: La recherche effectuée

    Returns:
        String du rapport textuel complet
    """
    lines = [
        "=" * 70,
        "                      RAPPORT - SchoolFinder",
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
            f"Établissement         : {_format_export_list(r.get('school_name'))}",
            f"Localisation          : {_format_export_list(r.get('location'))}",
            f"Pays                  : {_format_export_list(r.get('country'))}",
            f"Type                  : {_format_export_list(r.get('school_type'))}",
            f"Programmes            : {_format_export_list(r.get('programs'))}",
            f"Niveaux               : {_format_export_list(r.get('degree_levels'))}",
            f"Langue                : {_format_export_list(r.get('language_of_instruction'))}",
            f"Frais scolarité       : {_format_export_list(r.get('tuition_fee'))}",
            f"Frais dossier         : {_format_export_list(r.get('application_fee'))}",
            f"Bourse disponible     : {_format_export_list(r.get('scholarship_available'))}",
            f"Montant bourse        : {_format_export_list(r.get('scholarship_amount'))}",
            f"Détails bourse        : {_format_export_list(r.get('scholarship_details'))}",
            f"Éligibilité           : {_format_export_list(r.get('eligibility'))}",
            f"Admission             : {_format_export_list(r.get('admission_requirements'))}",
            f"Date limite           : {_format_export_list(r.get('deadline'))}",
            f"Durée                 : {_format_export_list(r.get('duration'))}",
            f"Contact officiel      : {_format_export_list(r.get('official_contact'))}",
            f"Résumé                : {_format_export_list(r.get('summary'))}",
            f"Source                : {_format_export_list(r.get('url'))}",
            "",
        ])

    lines.extend([
        "=" * 70,
        "Rapport généré automatiquement par SchoolFinder",
        "=" * 70,
    ])

    return "\n".join(lines)


def render_export_section(results: list[dict], query: str = ""):
    """
    Affiche les sections et les boutons de téléchargement d'export dans Streamlit.

    Args:
        results: Liste de dicts avec les données des écoles
        query: La recherche effectuée
    """
    if not results:
        return

    st.markdown("---")
    st.subheader("Exporter les résultats")
    st.caption("Téléchargez la liste des établissements correspondants sous différents formats.")

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
            label="Télécharger CSV (.csv)",
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