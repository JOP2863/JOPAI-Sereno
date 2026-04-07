"""
Écriture pilote dans l’onglet **Disponibilite_Mois** (Google Sheets).

Pas d’auth nominative : l’administration Streamlit repose sur le choix explicite d’un `expert_id`.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Mapping


def _month_first(annee_mois: str) -> date:
    y, m = annee_mois.strip().split("-", 1)
    return date(int(y), int(m), 1)


def mois_sous_verrouillage_artisan(annee_mois: str) -> bool:
    """
    Règle pilote (CDC § 1.7.1) : mois déjà commencé ou dont le 1er jour est dans moins de 30 jours
    → saisie « sensible » (artisan : prévenir le propriétaire avant changement).
    """
    try:
        first = _month_first(annee_mois)
    except Exception:
        return True
    today = date.today()
    cur_month = date(today.year, today.month, 1)
    if first < cur_month:
        return True
    return (first - today).days < 30


def append_disponibilite_mois_row(
    repo_root: Path,
    secrets: Mapping[str, Any] | Any,
    *,
    expert_id: str,
    annee_mois: str,
    mode: str,
    commentaire_interne: str = "",
) -> tuple[bool, str]:
    """Ajoute une ligne dans **Disponibilite_Mois**. Retourne (succès, message)."""
    try:
        import gspread
    except ImportError:
        return False, "gspread non installé"

    from sereno_core.gcp_credentials import credentials_for_sheets, get_service_account_info
    from sereno_core.sheets_experts import resolve_gsheet_id

    sid = resolve_gsheet_id(repo_root, secrets).strip()
    if not sid:
        return False, "gsheet_id manquant dans les secrets"

    try:
        info = get_service_account_info(repo_root, secrets)
        creds = credentials_for_sheets(info)
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(sid)
        ws = sh.worksheet("Disponibilite_Mois")
    except Exception as e:
        return False, str(e)

    row_id = f"DM-{uuid.uuid4().hex[:8].upper()}"
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    row = [
        row_id,
        expert_id.strip(),
        annee_mois.strip(),
        mode.strip(),
        commentaire_interne.strip(),
        now,
        "",
    ]
    try:
        ws.append_row(row, value_input_option="USER_ENTERED")
    except Exception as e:
        return False, str(e)
    return True, f"Ligne {row_id} ajoutée."
