"""
Lecture / écriture du paramétrage **parcours client** dans l’onglet Google Sheets **Config**
(colonnes **cle** / **valeur**). Partagé entre **toutes** les sessions Streamlit si le classeur est accessible.
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from typing import Any, Mapping

import streamlit as st

_PRESET_STANDARD = "standard"
_PRESET_SIMPLIFIED = "simplified"
_PRESET_CUSTOM = "custom"


def _norm_header_key(key: str) -> str:
    n = unicodedata.normalize("NFKD", str(key).strip().lower())
    n = "".join(c for c in n if not unicodedata.combining(c))
    n = re.sub(r"[^a-z0-9]+", "_", n)
    return n.strip("_")


def _as_bool(v: Any) -> bool:
    s = str(v or "").strip().lower()
    return s in ("1", "true", "vrai", "oui", "yes", "on", "o")


def _open_config_ws(repo_root: Path, secrets: Mapping[str, Any] | Any):
    try:
        import gspread
    except ImportError:
        return None, "gspread non installé"
    from sereno_core.gcp_credentials import credentials_for_sheets, get_service_account_info
    from sereno_core.sheets_experts import resolve_gsheet_id

    gsid = resolve_gsheet_id(repo_root, secrets).strip()
    if not gsid:
        return None, "gsheet_id manquant"
    try:
        info = get_service_account_info(repo_root, secrets)
        creds = credentials_for_sheets(info)
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(gsid)
        ws = sh.worksheet("Config")
        return ws, ""
    except Exception as e:
        return None, str(e)


def _header_map(ws: Any) -> dict[str, int]:
    try:
        raw = [str(h or "").strip() for h in ws.row_values(1)]
    except Exception:
        return {}
    out: dict[str, int] = {}
    for i, h in enumerate(raw):
        k = _norm_header_key(h)
        if k and k not in out:
            out[k] = i + 1
    return out


KEY_PRESET = "SERENO_JOURNEY_PRESET"
KEY_SST = "SERENO_JOURNEY_CUSTOM_SST"
KEY_PAY = "SERENO_JOURNEY_CUSTOM_PAYMENT"
KEY_NPS = "SERENO_JOURNEY_CUSTOM_NPS"


@st.cache_data(ttl=45)
def read_journey_config_cached(gsheet_id: str) -> dict[str, Any] | None:
    """
    Retourne un dict normalisé ``preset, custom_sst, custom_payment, custom_nps`` si la feuille **Config**
    contient au moins ``SERENO_JOURNEY_PRESET`` ; sinon ``None`` (repli session / défauts).
    Retourne ``None`` aussi en cas d’erreur réseau ou d’onglet absent.
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
    hm = _header_map(ws)
    col_cle = hm.get("cle") or hm.get("cle_config") or hm.get("key")
    col_val = hm.get("valeur") or hm.get("value")
    if not col_cle or not col_val:
        return None
    try:
        rows = ws.get_all_values()
    except Exception:
        return None
    if len(rows) < 2:
        return None
    kv: dict[str, str] = {}
    for ri in range(1, len(rows)):
        line = rows[ri]
        c_idx = col_cle - 1
        v_idx = col_val - 1
        if c_idx >= len(line):
            continue
        ck = str(line[c_idx] or "").strip()
        if not ck:
            continue
        val = str(line[v_idx]).strip() if v_idx < len(line) else ""
        kv[ck.upper()] = val
    if KEY_PRESET not in kv:
        return None
    preset_raw = kv.get(KEY_PRESET, "").strip().lower()
    if preset_raw not in (_PRESET_STANDARD, _PRESET_SIMPLIFIED, _PRESET_CUSTOM):
        preset_raw = _PRESET_STANDARD
    return {
        "preset": preset_raw,
        "custom_sst": _as_bool(kv.get(KEY_SST, "true")),
        "custom_payment": _as_bool(kv.get(KEY_PAY, "true")),
        "custom_nps": _as_bool(kv.get(KEY_NPS, "true")),
    }


def invalidate_journey_sheet_cache() -> None:
    read_journey_config_cached.clear()


def load_global_journey_dict(repo_root: Path, secrets: Mapping[str, Any] | Any) -> dict[str, Any] | None:
    from sereno_core.sheets_experts import resolve_gsheet_id

    gsid = resolve_gsheet_id(repo_root, secrets).strip()
    if not gsid:
        return None
    return read_journey_config_cached(gsid)


def persist_journey_config(
    repo_root: Path,
    secrets: Mapping[str, Any] | Any,
    *,
    preset: str,
    custom_sst: bool,
    custom_payment: bool,
    custom_nps: bool,
) -> tuple[bool, str]:
    """Écrit les quatre clés dans **Config** (mise à jour de ligne existante ou ajout)."""
    ws, err = _open_config_ws(repo_root, secrets)
    if ws is None:
        return False, err or "Config inaccessible"
    pr = str(preset or "").strip().lower()
    if pr not in (_PRESET_STANDARD, _PRESET_SIMPLIFIED, _PRESET_CUSTOM):
        pr = _PRESET_STANDARD
    hm = _header_map(ws)
    col_cle = hm.get("cle") or hm.get("cle_config") or hm.get("key")
    col_val = hm.get("valeur") or hm.get("value")
    if not col_cle or not col_val:
        return False, "Colonnes cle/valeur introuvables dans Config"

    pairs = [
        (KEY_PRESET, pr),
        (KEY_SST, "true" if custom_sst else "false"),
        (KEY_PAY, "true" if custom_payment else "false"),
        (KEY_NPS, "true" if custom_nps else "false"),
    ]

    try:
        rows = ws.get_all_values()
    except Exception as e:
        return False, str(e)

    def _row_idx_for_key(key: str) -> int | None:
        cix = col_cle - 1
        for ri in range(1, len(rows)):
            line = rows[ri]
            if cix < len(line) and str(line[cix] or "").strip().upper() == key.upper():
                return ri + 1
        return None

    try:
        ncols = max(len(rows[0]) if rows else 0, col_cle, col_val)
        try:
            ncols = max(ncols, ws.col_count)
        except Exception:
            pass
        for key, val in pairs:
            rnum = _row_idx_for_key(key)
            if rnum:
                ws.update_cell(rnum, col_val, val)
            else:
                line = [""] * ncols
                line[col_cle - 1] = key
                line[col_val - 1] = val
                ws.append_row(line, value_input_option="USER_ENTERED")
                rows.append(line)
    except Exception as e:
        return False, str(e)
    invalidate_journey_sheet_cache()
    return True, ""
