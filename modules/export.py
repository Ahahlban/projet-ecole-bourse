import io
import pandas as pd
import streamlit as st
from datetime import datetime


def _format_export_value(value) -> str:
    """
    Convertit une valeur (liste, None, chaine) en texte lisible pour l'export.
    Les listes sont jointes par ' | ' pour eviter les conflits avec les virgules CSV.
    Les valeurs invalides ou nulles sont remplacees par 'N/A'.

    Complexite : O(n) ou n = nombre d'elements si liste, O(1) sinon.
    """
    invalid_values = {
        "", "n/a", "non detecte", "non verifie", "non verifie",
        "a verifier", "unknown", "null", "none"
    }

    if isinstance(value, list):
        cleaned = [
            str(v).strip()
            for v in value
            if str(v).strip() and str(v).lower().strip() not in invalid_values
        ]
        return " | ".join(cleaned) if cleaned else "N/A"

    if value is None:
        return "N/A"

    str_value = str(value).strip()
    if str_value.lower() in invalid_values:
        return "N/A"

    return str_value


def _build_export_rows(results: list[dict]) -> list[dict]:
    """
    Transforme la liste de resultats en liste de lignes pretes pour l'export.
    Applique _format_export_value sur toutes les colonnes.

    Complexite : O(n * k) ou n = nombre de resultats, k = nombre de colonnes (constant).
    """
    rows = []
    for i, r in enumerate(results, 1):
        rows.append({
            "N°": i,
            "Etablissement": _format_export_value(r.get("school_name")),
            "Ville": _format_export_value(r.get("location")),
            "Pays": _format_export_value(r.get("country")),
            "Type": _format_export_value(r.get("school_type")),
            "Programmes": _format_export_value(r.get("programs")),
            "Niveaux": _format_export_value(r.get("degree_levels")),
            "Langue": _format_export_value(r.get("language_of_instruction")),
            "Frais UE": _format_export_value(r.get("tuition_fee")),
            "Frais Hors-UE": _format_export_value(r.get("tuition_fee_non_eu")),
            "Frais Dossier": _format_export_value(r.get("application_fee")),
            "Bourse Disponible": _format_export_value(r.get("scholarship_available")),
            "Montant Bourse": _format_export_value(
                r.get("scholarship_estimated_amount") or r.get("scholarship_amount")
            ),
            "Details Bourse": _format_export_value(r.get("scholarship_details")),
            "Lien Bourse": _format_export_value(r.get("scholarship_link")),
            "Eligibilite": _format_export_value(r.get("eligibility")),
            "Admission": _format_export_value(r.get("admission_requirements")),
            "Date Limite": _format_export_value(r.get("deadline")),
            "Duree": _format_export_value(r.get("duration")),
            "Contact": _format_export_value(r.get("official_contact")),
            "Resume": _format_export_value(r.get("summary")),
            "Site Officiel": _format_export_value(r.get("url")),
        })
    return rows


def build_excel_report(results: list[dict], query: str = "") -> bytes:
    """
    Cree un fichier Excel structure avec les resultats dans un onglet et un resume dans un autre.
    Ajuste automatiquement la largeur des colonnes.

    Complexite : O(n * k) ou n = nombre de resultats, k = colonnes.
    Retourne des bytes prets au telechargement.
    """
    rows = _build_export_rows(results)
    df = pd.DataFrame(rows)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Resultats Ecoles", index=False)

        summary_data = {
            "Information": [
                "Recherche effectuee",
                "Date du rapport",
                "Nombre de resultats",
                "Source"
            ],
            "Valeur": [
                query or "N/A",
                datetime.now().strftime("%d/%m/%Y a %H:%M"),
                len(results),
                "EduSearch"
            ]
        }
        pd.DataFrame(summary_data).to_excel(writer, sheet_name="Resume", index=False)

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


def build_csv_report(results: list[dict]) -> bytes:
    """
    Cree un fichier CSV correctement formate avec encodage UTF-8 BOM (compatible Excel).
    Les listes sont converties en texte lisible (separateur ' | ') pour eviter les problemes.

    Complexite : O(n * k) ou n = resultats, k = colonnes.
    Retourne des bytes UTF-8 avec BOM.
    """
    rows = _build_export_rows(results)
    df = pd.DataFrame(rows)
    # UTF-8 avec BOM pour compatibilite Excel (evite les problemes d'accents)
    return df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")


def build_text_report(results: list[dict], query: str = "") -> str:
    """
    Cree un rapport texte structure et lisible pour impression ou archivage.

    Complexite : O(n * k) ou n = resultats, k = champs par resultat.
    Retourne une chaine multi-lignes.
    """
    lines = [
        "=" * 70,
        "                   RAPPORT - EduSearch",
        "=" * 70,
        f"Recherche  : {query or 'N/A'}",
        f"Date       : {datetime.now().strftime('%d/%m/%Y a %H:%M')}",
        f"Resultats  : {len(results)}",
        "=" * 70,
        "",
    ]

    for i, r in enumerate(results, 1):
        lines.extend([
            f"--- Resultat #{i} ---",
            f"Etablissement       : {_format_export_value(r.get('school_name'))}",
            f"Ville               : {_format_export_value(r.get('location'))}",
            f"Pays                : {_format_export_value(r.get('country'))}",
            f"Type                : {_format_export_value(r.get('school_type'))}",
            f"Programmes          : {_format_export_value(r.get('programs'))}",
            f"Niveaux             : {_format_export_value(r.get('degree_levels'))}",
            f"Langue              : {_format_export_value(r.get('language_of_instruction'))}",
            f"Frais UE            : {_format_export_value(r.get('tuition_fee'))}",
            f"Frais Hors-UE       : {_format_export_value(r.get('tuition_fee_non_eu'))}",
            f"Frais Dossier       : {_format_export_value(r.get('application_fee'))}",
            f"Bourse Disponible   : {_format_export_value(r.get('scholarship_available'))}",
            f"Montant Bourse      : {_format_export_value(r.get('scholarship_estimated_amount') or r.get('scholarship_amount'))}",
            f"Details Bourse      : {_format_export_value(r.get('scholarship_details'))}",
            f"Lien Bourse         : {_format_export_value(r.get('scholarship_link'))}",
            f"Eligibilite         : {_format_export_value(r.get('eligibility'))}",
            f"Admission           : {_format_export_value(r.get('admission_requirements'))}",
            f"Date Limite         : {_format_export_value(r.get('deadline'))}",
            f"Duree               : {_format_export_value(r.get('duration'))}",
            f"Contact             : {_format_export_value(r.get('official_contact'))}",
            f"Resume              : {_format_export_value(r.get('summary'))}",
            f"Site Officiel       : {_format_export_value(r.get('url'))}",
            "",
        ])

    lines.extend([
        "=" * 70,
        "Rapport genere automatiquement par EduSearch",
        "=" * 70,
    ])

    return "\n".join(lines)


def render_export_section(results: list[dict], query: str = ""):
    """
    Affiche les boutons de telechargement des exports (Excel, CSV, TXT).
    Les fichiers sont generes a la volee et proposes en telechargement direct.

    Complexite : O(n) pour la generation de chaque format,
    ou n = nombre de resultats. Trois appels de generation distincts.
    """
    if not results:
        return

    st.markdown("---")
    st.subheader("Exporter les resultats")
    st.caption(f"{len(results)} etablissement(s) prets a l'export dans le format de votre choix.")

    col1, col2, col3 = st.columns(3)

    with col1:
        excel_data = build_excel_report(results, query)
        st.download_button(
            label="Telecharger Excel (.xlsx)",
            data=excel_data,
            file_name=f"edusearch_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    with col2:
        csv_data = build_csv_report(results)
        st.download_button(
            label="Telecharger CSV (.csv)",
            data=csv_data,
            file_name=f"edusearch_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv; charset=utf-8",
            use_container_width=True,
        )

    with col3:
        text_data = build_text_report(results, query)
        st.download_button(
            label="Telecharger Rapport (.txt)",
            data=text_data.encode("utf-8"),
            file_name=f"rapport_edusearch_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain; charset=utf-8",
            use_container_width=True,
        )