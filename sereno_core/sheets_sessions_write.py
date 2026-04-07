"""
Synchronisation de l’onglet **Sessions** (Google Sheets) avec le parcours prototype.

Les événements `log_event` restent dans `session_state` ; ce module alimente la **vérité tableur**
attendue au pilote (CDC § 3.6) lorsque `gsheet_id` + compte de service sont configurés.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

# Référence doc / init (`sheets_schema` — onglet Sessions)
SESSION_HEADERS: list[str] = [
    "session_id",
    "created_at",
    "type_code",
    "statut",
    "user_pseudo",
    "user_contact",
    "expert_id",
    "room_url",
    "notes_cloture",
    "prix_centimes_factures",
    "debut_visio",
    "fin_visio",
]


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


def try_upsert_session_row(
    repo_root: Path,
    secrets: Mapping[str, Any] | Any,
    *,
    session_id: str,
    updates: dict[str, Any | None],
) -> tuple[bool, str]:
    """
    Crée ou met à jour **une ligne par session_id** (colonne `session_id` du classeur).
    Clés de `updates` = noms de colonnes **tels qu’à la ligne 1** de l’onglet ; **None** = laisser inchangé.
    """
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
        ws = sh.worksheet("Sessions")
    except Exception as e:
        return False, str(e)

    try:
        all_rows = ws.get_all_values()
    except Exception as e:
        return False, str(e)

    if not all_rows:
        return False, "onglet Sessions vide (ligne 1 = en-têtes attendue)"

    headers = [str(h).strip() for h in all_rows[0]]
    if not headers:
        return False, "en-têtes Sessions illisibles"

    if "session_id" not in headers:
        return False, "colonne session_id absente (ligne 1)"

    ix_sid = headers.index("session_id")

    row_num: int | None = None
    row_dict: dict[str, str] = {h: "" for h in headers}

    for r_i, row in enumerate(all_rows[1:], start=2):
        cells = list(row) + [""] * (len(headers) - len(row))
        if ix_sid >= len(cells):
            continue
        if str(cells[ix_sid]).strip() == sid:
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

    row_dict["session_id"] = sid
    if row_num is None and not row_dict.get("created_at"):
        row_dict["created_at"] = _now_iso()

    line_out = [row_dict.get(h, "") for h in headers]

    try:
        if row_num is None:
            ws.append_row(line_out, value_input_option="USER_ENTERED")
            return True, "Sessions : ligne créée"
        end_l = _col_letter(len(headers))
        rng = f"A{row_num}:{end_l}{row_num}"
        ws.update(range_name=rng, values=[line_out], value_input_option="USER_ENTERED")
        return True, "Sessions : ligne mise à jour"
    except Exception as e:
        return False, str(e)
