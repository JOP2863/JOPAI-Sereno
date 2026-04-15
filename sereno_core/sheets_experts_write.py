"""
Écriture / mise à jour de l’onglet **Experts** (Google Sheets) — pilote.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _col_letter(n: int) -> str:
    if n < 1:
        return "A"
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def try_upsert_expert_row(
    repo_root: Path,
    secrets: Mapping[str, Any] | Any,
    *,
    expert_id: str,
    updates: dict[str, Any | None],
) -> tuple[bool, str]:
    """
    Crée ou met à jour **une ligne par expert_id** (colonne ``expert_id`` ou ``id`` en ligne 1).
    Les clés de ``updates`` doivent correspondre aux **en-têtes** de la ligne 1 (ex. ``prenom``, ``nom``).
    ``None`` = ne pas modifier.
    """
    eid = str(expert_id or "").strip()
    if not eid:
        return False, "expert_id vide"

    try:
        import gspread
    except ImportError:
        return False, "gspread non installé"

    from sereno_core.gcp_credentials import credentials_for_sheets, get_service_account_info
    from sereno_core.sheets_experts import _open_experts_worksheet, resolve_gsheet_id

    gsid = resolve_gsheet_id(repo_root, secrets).strip()
    if not gsid:
        return False, "gsheet_id manquant"

    try:
        info = get_service_account_info(repo_root, secrets)
        creds = credentials_for_sheets(info)
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(gsid)
        ws = _open_experts_worksheet(sh, secrets)
        if ws is None:
            return False, "onglet Experts introuvable"
    except Exception as e:
        return False, str(e)

    try:
        all_rows = ws.get_all_values()
    except Exception as e:
        return False, str(e)

    if not all_rows:
        return False, "onglet Experts vide"

    headers = [str(h).strip() for h in all_rows[0]]
    if not headers:
        return False, "en-têtes Experts illisibles"

    id_candidates = ("expert_id", "id", "code_expert", "identifiant")
    ix_id = None
    for cand in id_candidates:
        if cand in headers:
            ix_id = headers.index(cand)
            break
    if ix_id is None:
        return False, "colonne expert_id/id absente (ligne 1)"

    id_key_name = headers[ix_id]

    row_num: int | None = None
    row_dict: dict[str, str] = {h: "" for h in headers}

    for r_i, row in enumerate(all_rows[1:], start=2):
        cells = list(row) + [""] * (len(headers) - len(row))
        if ix_id >= len(cells):
            continue
        if str(cells[ix_id]).strip() == eid:
            row_num = r_i
            for hi, hn in enumerate(headers):
                row_dict[hn] = str(cells[hi] if hi < len(cells) else "").strip()
            break

    for key, val in updates.items():
        if val is None:
            continue
        k = str(key).strip()
        if k not in row_dict:
            continue
        row_dict[k] = str(val).strip()

    row_dict[id_key_name] = eid
    now = _now_iso()
    if "maj_le" in row_dict:
        row_dict["maj_le"] = now
    if row_num is None:
        if "enregistre_le" in row_dict and not str(row_dict.get("enregistre_le") or "").strip():
            row_dict["enregistre_le"] = now

    line_out = [row_dict.get(h, "") for h in headers]

    try:
        if row_num is None:
            ws.append_row(line_out, value_input_option="USER_ENTERED")
            return True, "Experts : ligne créée"
        end_l = _col_letter(len(headers))
        rng = f"A{row_num}:{end_l}{row_num}"
        ws.update(range_name=rng, values=[line_out], value_input_option="USER_ENTERED")
        return True, "Experts : ligne mise à jour"
    except Exception as e:
        return False, str(e)
