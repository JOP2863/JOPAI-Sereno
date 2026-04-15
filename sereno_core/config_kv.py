"""
Helpers partagés pour lire/écrire des paires clé/valeur dans l’onglet Google Sheets **Config**.

But : éviter de dupliquer la logique (modes parcours, libellés, satisfaction, etc.).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

import streamlit as st


@st.cache_data(ttl=45)
def read_config_kv_cached(gsheet_id: str) -> dict[str, str] | None:
    """
    Lit toutes les paires clé/valeur de l’onglet **Config** (tableur pilote).
    Retourne None si le classeur n’est pas accessible.
    """
    gsid = (gsheet_id or "").strip()
    if not gsid:
        return None
    repo = Path(__file__).resolve().parent.parent
    try:
        secrets = dict(st.secrets)
    except Exception:
        secrets = {}
    try:
        import gspread
        from sereno_core.gcp_credentials import credentials_for_sheets, get_service_account_info

        info = get_service_account_info(repo, secrets)
        creds = credentials_for_sheets(info)
        gc = gspread.authorize(creds)
        ws = gc.open_by_key(gsid).worksheet("Config")
    except Exception:
        return None
    try:
        rows = ws.get_all_values()
    except Exception:
        return None
    if len(rows) < 2:
        return {}

    header = [str(h or "").strip().lower() for h in rows[0]]

    def _find_col(names: tuple[str, ...]) -> int | None:
        for i, h in enumerate(header):
            if h in names:
                return i
        return None

    ix_k = _find_col(("cle", "clé", "key"))
    ix_v = _find_col(("valeur", "value"))
    if ix_k is None or ix_v is None:
        return {}

    kv: dict[str, str] = {}
    for line in rows[1:]:
        k = str(line[ix_k] if ix_k < len(line) else "").strip()
        if not k:
            continue
        v = str(line[ix_v] if ix_v < len(line) else "").strip()
        kv[k.upper()] = v
    return kv


def invalidate_config_kv_cache() -> None:
    read_config_kv_cached.clear()


def resolve_gsheet_id_from_secrets(repo_root: Path, secrets: Mapping[str, Any] | Any) -> str:
    from sereno_core.sheets_experts import resolve_gsheet_id

    return resolve_gsheet_id(repo_root, secrets).strip()


def config_upsert_pairs(
    repo_root: Path,
    secrets: Mapping[str, Any] | Any,
    *,
    pairs: list[tuple[str, str]],
) -> tuple[bool, str]:
    """
    Upsert une liste de paires (clé/valeur) dans l’onglet **Config**.
    """
    try:
        import gspread
    except ImportError:
        return False, "gspread non installé"
    from sereno_core.gcp_credentials import credentials_for_sheets, get_service_account_info

    gsid = resolve_gsheet_id_from_secrets(repo_root, secrets).strip()
    if not gsid:
        return False, "gsheet_id manquant"
    try:
        info = get_service_account_info(repo_root, secrets)
        creds = credentials_for_sheets(info)
        gc = gspread.authorize(creds)
        ws = gc.open_by_key(gsid).worksheet("Config")
    except Exception as e:
        return False, str(e)

    try:
        rows = ws.get_all_values()
    except Exception as e:
        return False, str(e)
    if not rows:
        return False, "onglet Config vide"
    header = [str(h or "").strip().lower() for h in rows[0]]
    try:
        ix_k = header.index("cle")
    except ValueError:
        try:
            ix_k = header.index("key")
        except ValueError:
            return False, "colonne cle/key introuvable"
    try:
        ix_v = header.index("valeur")
    except ValueError:
        try:
            ix_v = header.index("value")
        except ValueError:
            return False, "colonne valeur/value introuvable"

    def _find_row_num(key_upper: str) -> int | None:
        for r_i, line in enumerate(rows[1:], start=2):
            k = str(line[ix_k] if ix_k < len(line) else "").strip().upper()
            if k == key_upper:
                return r_i
        return None

    try:
        ncols = max(len(rows[0]), ix_k + 1, ix_v + 1)
        try:
            ncols = max(ncols, ws.col_count)
        except Exception:
            pass
        for k, v in pairs:
            ku = str(k).strip().upper()
            vv = str(v).strip()
            rnum = _find_row_num(ku)
            if rnum:
                ws.update_cell(rnum, ix_v + 1, vv)
            else:
                newline = [""] * ncols
                newline[ix_k] = ku
                newline[ix_v] = vv
                ws.append_row(newline, value_input_option="USER_ENTERED")
                rows.append(newline)
    except Exception as e:
        return False, str(e)

    invalidate_config_kv_cache()
    return True, ""

