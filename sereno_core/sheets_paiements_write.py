"""
Ajout d’une ligne dans l’onglet **Paiements** (Google Sheets) — aligné sur `sheets_schema`.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


def try_append_paiement_row(
    repo_root: Path,
    secrets: Mapping[str, Any] | Any,
    *,
    session_id: str,
    montant_centimes: int,
    mode_paiement: str,
    statut: str = "SIMULE",
    stripe_id: str = "",
    notes: str = "",
) -> tuple[bool, str]:
    sid = str(session_id or "").strip()
    if not sid:
        return False, "session_id vide"

    try:
        import gspread
    except ImportError:
        return False, "gspread non installé"

    from sereno_core.gcp_credentials import credentials_for_sheets, get_service_account_info
    from sereno_core.sheets_experts import resolve_gsheet_id

    gsid = resolve_gsheet_id(repo_root, secrets).strip()
    if not gsid:
        return False, "gsheet_id manquant"

    try:
        info = get_service_account_info(repo_root, secrets)
        creds = credentials_for_sheets(info)
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(gsid)
        ws = sh.worksheet("Paiements")
    except Exception as e:
        return False, str(e)

    pid = f"PAY-{uuid.uuid4().hex[:10].upper()}"
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    row = [
        pid,
        sid,
        str(int(montant_centimes)),
        str(mode_paiement).strip(),
        str(statut).strip(),
        str(stripe_id or "").strip(),
        now,
        str(notes or "").strip()[:500],
    ]
    try:
        ws.append_row(row, value_input_option="USER_ENTERED")
    except Exception as e:
        return False, str(e)
    return True, f"Paiements : {pid}"
