"""
Lecture de l’onglet **Types_Urgence** (Google Sheets) — codes actifs, ordre d’affichage, libellés.

Repli si classeur inaccessible : mêmes codes que ``proto_checklists.URGENCE_LABELS``.
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from typing import Any, Mapping

import streamlit as st

from sereno_core.gcp_credentials import credentials_for_sheets, get_service_account_info
from sereno_core.proto_checklists import URGENCE_LABELS
from sereno_core.sheets_experts import resolve_gsheet_id


def _strip_accents(s: str) -> str:
    n = unicodedata.normalize("NFKD", str(s))
    return "".join(c for c in n if not unicodedata.combining(c))


def _norm_header_key(key: str) -> str:
    s = _strip_accents(str(key).strip().lower())
    s = re.sub(r"[^a-z0-9]+", "_", s)
    return s.strip("_")


def _normalize_row(row: Mapping[str, Any]) -> dict[str, Any]:
    return {_norm_header_key(k): v for k, v in row.items() if str(k).strip()}


def _flex_get(norm_row: Mapping[str, Any], *candidates: str) -> Any:
    for c in candidates:
        nc = _norm_header_key(c)
        if nc in norm_row and norm_row[nc] not in (None, ""):
            return norm_row[nc]
    return None


def _row_actif_ok(actif_raw: Any) -> bool:
    """Même logique que ``sheets_experts._row_actif_ok`` (copie locale pour éviter cycles)."""
    if actif_raw is None or (isinstance(actif_raw, str) and not actif_raw.strip()):
        return True
    if isinstance(actif_raw, bool):
        return actif_raw
    if isinstance(actif_raw, (int, float)):
        return float(actif_raw) != 0.0
    s = str(actif_raw).strip().upper()
    if s in ("NON", "N", "0", "FALSE", "INACTIF", "NO", "FAUX"):
        return False
    return True


def _open_types_urgence_ws(sh: Any, secrets: Mapping[str, Any] | Any) -> Any | None:
    custom = None
    try:
        if hasattr(secrets, "get"):
            custom = secrets.get("types_urgence_worksheet_name") or secrets.get("types_urgence_tab_name")
    except Exception:
        custom = None
    if custom and str(custom).strip():
        try:
            return sh.worksheet(str(custom).strip())
        except Exception:
            pass
    for name in (
        "Types_Urgence",
        "Types_Urgences",
        "Type_Urgence",
        "Types urgence",
        "TYPE_URGENCE",
        "Types-urgence",
    ):
        try:
            return sh.worksheet(name)
        except Exception:
            continue
    try:
        for ws in sh.worksheets():
            t = ws.title.strip().lower()
            if "urgence" in t and "type" in t.replace(" ", ""):
                return ws
    except Exception:
        pass
    return None


def _fallback_bundle() -> tuple[list[tuple[str, str]], frozenset[str], dict[str, str]]:
    ordered = [(k, str(v)) for k, v in URGENCE_LABELS.items()]
    codes = frozenset(URGENCE_LABELS.keys())
    labels = dict(URGENCE_LABELS)
    return ordered, codes, labels


@st.cache_data(ttl=45)
def _cached_types_urgence_rows(gsheet_id: str) -> list[dict[str, Any]] | None:
    """Lecture brute (lignes normalisées) pour éviter d’ouvrir Sheets à chaque interaction."""
    gsid = (gsheet_id or "").strip()
    if not gsid:
        return None
    try:
        import gspread
    except ImportError:
        return None
    try:
        repo = Path(__file__).resolve().parent.parent
        info = get_service_account_info(repo, dict(st.secrets))
        creds = credentials_for_sheets(info)
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(gsid)
        ws = _open_types_urgence_ws(sh, dict(st.secrets))
        if ws is None:
            return None
        rows = ws.get_all_values()
    except Exception:
        return None
    if not rows:
        return None
    headers = [str(h or "").strip() for h in rows[0]]
    if not headers:
        return None
    out: list[dict[str, Any]] = []
    for line in rows[1:]:
        cells = list(line) + [""] * (len(headers) - len(line))
        row_raw = {headers[i]: cells[i] for i in range(len(headers))}
        nr = _normalize_row(row_raw)
        if any(str(v or "").strip() for v in nr.values()):
            out.append(nr)
    return out or None


def bundle_urgence_catalog(
    repo_root: Path,
    secrets: Mapping[str, Any] | Any,
) -> tuple[list[tuple[str, str]], frozenset[str], dict[str, str]]:
    """
    Retourne :
    - ``ordered`` : ``(type_code, libelle_affichage)`` triés par **ordre** (Sheet), **actifs** uniquement
    - ``active_codes`` : ensemble des codes actifs
    - ``labels`` : libellés pour affichage (actifs depuis la feuille ; sinon repli ``URGENCE_LABELS``)
    """
    base_labels = dict(URGENCE_LABELS)
    gsid = resolve_gsheet_id(repo_root, secrets).strip()
    rows = _cached_types_urgence_rows(gsid) if gsid else None
    if not rows:
        return _fallback_bundle()

    parsed: list[tuple[int, str, str, bool]] = []
    for nr in rows:
        code = str(_flex_get(nr, "type_code", "code", "code_urgence", "urgence_code") or "").strip().upper()
        if not code or code not in base_labels:
            continue
        lib = str(_flex_get(nr, "libelle_affichage", "libelle", "libellé", "label") or "").strip()
        if not lib:
            lib = base_labels.get(code, code)
        ord_raw = _flex_get(nr, "ordre", "order", "priorite", "priorité", "rang")
        try:
            ordre = int(str(ord_raw or "999").strip() or "999")
        except Exception:
            ordre = 999
        actif_raw = _flex_get(nr, "actif", "active", "enabled", "on")
        active = _row_actif_ok(actif_raw if actif_raw is not None else "OUI")
        parsed.append((ordre, code, lib, active))

    if not parsed:
        return _fallback_bundle()

    parsed.sort(key=lambda t: (t[0], t[1]))
    active_rows = [t for t in parsed if t[3]]
    if not active_rows:
        # Évite un écran d’accueil vide si la feuille est mal remplie (tout en NON, etc.).
        return _fallback_bundle()

    ordered = [(c, lab) for _, c, lab, _ in active_rows]
    active_codes = frozenset(c for _, c, _, _ in active_rows)

    labels = dict(base_labels)
    for _, c, lab, is_act in parsed:
        if is_act and lab:
            labels[c] = lab
    return ordered, active_codes, labels


def invalidate_types_urgence_cache() -> None:
    try:
        _cached_types_urgence_rows.clear()  # type: ignore[attr-defined]
    except Exception:
        pass
