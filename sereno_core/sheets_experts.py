"""
Charge la liste des experts depuis l’onglet Google Sheets « Experts » (pilote).

Colonnes souples : expert_id (ou id, Expert ID…), nom, email, telephone, actif,
types_autorises / types_autorisees / Types autorisées / type_intervention…
Valeurs : codes EAU;GAZ ou libellés français « Eau », « Gaz », « Chauffage »…
Plusieurs lignes pour le même expert_id sont fusionnées (union des types).
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from typing import Any, Mapping

import streamlit as st

from sereno_core.gcp_credentials import credentials_for_sheets, get_service_account_info

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore[no-redef, unused-ignore]

from sereno_core.proto_checklists import URGENCE_LABELS

_VALID_CODES = frozenset(URGENCE_LABELS.keys())


def _strip_accents(s: str) -> str:
    n = unicodedata.normalize("NFKD", s)
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


def _normalize_type_token(raw: str) -> str | None:
    s = str(raw).strip()
    if not s:
        return None
    su = _strip_accents(s).upper().strip()
    su_compact = re.sub(r"\s+", "", su)
    if su_compact in ("TOUS", "ALL", "TOUTES", "*"):
        return "__ALL__"
    if su_compact in _VALID_CODES:
        return su_compact
    if su_compact == "CHUFF":
        return "CHAUFF"
    if "ELECT" in su_compact or su_compact in ("ELEC",):
        return "ELEC"
    if "SERRUR" in su_compact or "ACCES" in su_compact or "ACCÈS" in s.upper():
        return "SERR"
    if "CHAUFF" in su_compact or "CHAUD" in su_compact or "HEATING" in su_compact:
        return "CHAUFF"
    if su_compact in ("GAS", "GAZ"):
        return "GAZ"
    if su_compact in ("WATER", "EAU", "PLUMB"):
        return "EAU"
    for code, label in URGENCE_LABELS.items():
        lab = _strip_accents(label).upper()
        if su == lab or su_compact == re.sub(r"\s+", "", lab):
            return code
    return None


def _split_types_cell(cell: str) -> list[str]:
    if not cell:
        return []
    parts = re.split(r"[;,|/]", str(cell))
    out: list[str] = []
    for p in parts:
        code = _normalize_type_token(p)
        if code == "__ALL__":
            for c in sorted(_VALID_CODES):
                if c not in out:
                    out.append(c)
        elif code and code not in out:
            out.append(code)
    return out


def _looks_like_types_column(norm_key: str) -> bool:
    """Colonne probable pour les codes d’urgence (libellés Sheets variables)."""
    nk = str(norm_key).lower()
    if "type" in nk and "expert" not in nk:
        return True
    if "special" in nk:
        return True
    if "urgence" in nk:
        return True
    if nk in ("metiers", "metier", "domaines", "competences", "compétences"):
        return True
    return False


def _row_types(norm_row: Mapping[str, Any]) -> list[str]:
    cell = _flex_get(
        norm_row,
        "types_autorises",
        "types_autorisees",
        "types_autorisées",
        "types_autorise",
        "type_intervention",
        "types_intervention",
        "types",
        "specialites",
        "spécialités",
    )
    if cell is not None and str(cell).strip():
        return _split_types_cell(str(cell))
    # Fallback : première colonne « parlante » remplie (ex. « Types » seul, typo d’en-tête)
    for k in sorted(norm_row.keys()):
        if not _looks_like_types_column(k):
            continue
        v = norm_row.get(k)
        if v is None or not str(v).strip():
            continue
        got = _split_types_cell(str(v))
        if got:
            return got
    return []


def _row_actif_ok(actif_raw: Any) -> bool:
    """Considère actif par défaut ; exclut 0 numérique, NON, FALSE, etc."""
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


def _row_expert_id(norm_row: Mapping[str, Any]) -> str:
    v = _flex_get(
        norm_row,
        "expert_id",
        "id_expert",
        "code_expert",
        "identifiant",
        "identifier",
        "expert",
    )
    if v is None:
        v = norm_row.get("id")
    return str(v).strip() if v is not None else ""


def canonicalize_type_list(raw: list[Any] | None) -> list[str]:
    """Normalise une liste de types (codes ou libellés) vers EAU, ELEC, …"""
    if not raw:
        return []
    out: list[str] = []
    for x in raw:
        code = _normalize_type_token(str(x))
        if code == "__ALL__":
            for c in sorted(_VALID_CODES):
                if c not in out:
                    out.append(c)
        elif code and code not in out:
            out.append(code)
    return out


def resolve_gsheet_id(repo_root: Path, secrets: Mapping[str, Any] | Any) -> str:
    """gsheet_id à la racine des secrets, ou dans `.streamlit/secrets.toml`, ou section `[google]`."""
    for k in ("gsheet_id", "GSheet_ID", "spreadsheet_id", "google_sheet_id"):
        try:
            v = secrets.get(k) if hasattr(secrets, "get") else None
        except Exception:
            v = None
        if v is None and hasattr(secrets, "__getitem__"):
            try:
                v = secrets[k]
            except Exception:
                v = None
        if v and str(v).strip():
            return str(v).strip()
    for section in ("google", "sheets", "gsheet"):
        try:
            sub = secrets.get(section) if hasattr(secrets, "get") else None
        except Exception:
            sub = None
        if isinstance(sub, dict):
            for k in ("gsheet_id", "GSheet_ID", "spreadsheet_id", "google_sheet_id"):
                v = sub.get(k)
                if v and str(v).strip():
                    return str(v).strip()
    path = repo_root / ".streamlit" / "secrets.toml"
    if path.is_file():
        try:
            data = tomllib.loads(path.read_text(encoding="utf-8"))
        except Exception:
            data = {}
        for k in ("gsheet_id", "GSheet_ID", "spreadsheet_id", "google_sheet_id"):
            v = data.get(k)
            if v and str(v).strip():
                return str(v).strip()
        for section in ("google", "sheets", "gsheet"):
            sub = data.get(section)
            if isinstance(sub, dict):
                for k in ("gsheet_id", "spreadsheet_id", "id"):
                    v = sub.get(k)
                    if v and str(v).strip():
                        return str(v).strip()
    return ""


def _expert_rows_from_sheet(ws: Any) -> list[dict[str, Any]]:
    """
    Lit l’onglet via `get_all_values` (une cellule = une chaîne).
    Plus fiable que `get_all_records` si une cellule contient des retours ligne (ex. e-mail mal formaté).
    """
    vals = ws.get_all_values()
    if len(vals) < 2:
        return []
    headers_raw = vals[0]
    out: list[dict[str, Any]] = []
    for ri in range(1, len(vals)):
        cells = vals[ri]
        row: dict[str, Any] = {}
        for ci, h_raw in enumerate(headers_raw):
            hs = str(h_raw).strip()
            if not hs:
                continue
            hk = _norm_header_key(hs)
            if not hk:
                continue
            row[hk] = cells[ci] if ci < len(cells) else ""
        if any(str(v).strip() for v in row.values()):
            out.append(row)
    return out


def _open_experts_worksheet(sh: Any, secrets: Mapping[str, Any] | Any) -> Any | None:
    """
    Onglet liste des experts (priorité : nom exact dans secrets, sinon noms usuels).
    N’utilise pas **Expert_Disponibilite** (disponibilité temps réel — autre logique).
    """
    custom = None
    try:
        if hasattr(secrets, "get"):
            custom = secrets.get("experts_worksheet_name") or secrets.get("experts_tab_name")
    except Exception:
        custom = None
    if custom and str(custom).strip():
        try:
            return sh.worksheet(str(custom).strip())
        except Exception:
            pass
    for name in ("Experts", "Expert", "Liste_Experts", "Liste experts", "EXPERTS", "Artisans"):
        try:
            return sh.worksheet(name)
        except Exception:
            continue
    try:
        for ws in sh.worksheets():
            t = ws.title.strip().lower()
            if "expert" in t and "dispon" not in t:
                return ws
    except Exception:
        pass
    return None


def load_experts_from_sheets(
    repo_root: Path,
    secrets: Mapping[str, Any],
    *,
    gsheet_id: str | None = None,
) -> list[dict[str, Any]] | None:
    """
    Retourne une liste d’experts au format prototype : id, nom, email, types, ordre.
    `None` si chargement impossible (pas d’ID classeur, erreur API, onglet vide).
    """
    try:
        import gspread
    except ImportError:
        return None

    sid = (gsheet_id or resolve_gsheet_id(repo_root, secrets)).strip()
    if not sid:
        return None

    try:
        info = get_service_account_info(repo_root, secrets)
        creds = credentials_for_sheets(info)
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(sid)
        ws = _open_experts_worksheet(sh, secrets)
        if ws is None:
            return None
        rows = _expert_rows_from_sheet(ws)
    except Exception:
        return None

    if not rows:
        return None

    merged: dict[str, dict[str, Any]] = {}
    order = 0
    for row in rows:
        order += 1
        nr = row
        eid = _row_expert_id(nr)
        if not eid:
            continue
        actif_raw = _flex_get(nr, "actif", "active", "enabled", "on")
        if not _row_actif_ok(actif_raw if actif_raw is not None else "OUI"):
            continue
        nom_raw = _flex_get(nr, "nom", "name", "expert_nom")
        nom = str(nom_raw).strip() if nom_raw is not None else ""
        nom = nom or eid
        email_raw = _flex_get(nr, "email", "mail", "courriel")
        email = str(email_raw).strip() if email_raw is not None else ""
        tel_raw = _flex_get(nr, "telephone", "téléphone", "tel", "tél", "phone", "mobile", "portable")
        telephone = str(tel_raw).strip() if tel_raw is not None else ""
        types = _row_types(nr)
        if eid not in merged:
            merged[eid] = {
                "id": eid,
                "nom": nom,
                "email": email or f"{eid.lower().replace(' ', '_')}@sereno.pilote.local",
                "telephone": telephone,
                "types": list(types),
                "ordre": order,
            }
        else:
            m = merged[eid]
            m["ordre"] = min(int(m.get("ordre", 99)), order)
            for t in types:
                if t not in m["types"]:
                    m["types"].append(t)
            if email and "@" in email:
                m["email"] = email
            if telephone and len(telephone) >= 6:
                m["telephone"] = telephone

    out = list(merged.values())
    out.sort(key=lambda x: int(x.get("ordre", 99)))
    return out if out else None


def disponibilite_expert_options(
    artisans: list[Mapping[str, Any]],
) -> tuple[list[str], dict[str, str]]:
    """
    Menus **disponibilités** : une entrée par couple (expert, type d’intervention).
    Libellé du type : libellé français (EAU → Eau, …).
    """
    options: list[str] = []
    mapping: dict[str, str] = {}
    for a in artisans:
        eid = str(a.get("id") or "").strip()
        if not eid:
            continue
        nom = str(a.get("nom") or eid).strip()
        types = list(a.get("types") or [])
        if not types:
            lab = f"{nom} ({eid})"
            options.append(lab)
            mapping[lab] = eid
            continue
        for t in sorted(types):
            lib = URGENCE_LABELS.get(str(t), str(t))
            lab = f"{nom} — {lib} ({eid})"
            options.append(lab)
            mapping[lab] = eid
    return options, mapping


def load_experts_from_streamlit_secrets(repo_root: Path) -> list[dict[str, Any]] | None:
    try:
        return load_experts_from_sheets(repo_root, dict(st.secrets))
    except Exception:
        return None
