#!/usr/bin/env python3
"""
Initialise les onglets du classeur SÉRÉNO : en-têtes (ligne 1) et lignes de graine si l’onglet est vide.

Lit la configuration dans `.streamlit/secrets.toml` :
  gsheet_id, et compte de service via [gcp_service_account] ou service_account_json_path

Usage (depuis la racine du dépôt) :
  python scripts/init_google_sheet.py
  python scripts/init_google_sheet.py --seed          # graines si aucune donnée sous l’en-tête (lignes vides ignorées)
  python scripts/init_google_sheet.py --force-headers # réécrit la ligne 1 (attention si vous aviez modifié les titres à la main)

Classeur déjà rempli : pour ajouter des colonnes sans écraser les données, préférer :
  python scripts/migrate_google_sheet_schema.py --dry-run
  python scripts/migrate_google_sheet_schema.py --apply

Quota Google Sheets (429) : le script charge la liste des onglets **une fois** et espace les appels.
En cas de **Quota exceeded**, attendre 1–2 minutes et relancer la même commande ; les relais automatiques
s’affichent sur stderr.

Prérequis : pip install -r requirements.txt
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore[no-redef]

import gspread
from gspread.utils import rowcol_to_a1

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sereno_core.gcp_credentials import credentials_for_sheets, get_service_account_info
from sereno_core.gspread_helpers import gspread_retry, tab_throttle_seconds, worksheet_index_by_title
from sereno_core.sheets_schema import SHEET_TABS, SheetTab


def load_streamlit_secrets() -> dict:
    path = ROOT / ".streamlit" / "secrets.toml"
    if not path.is_file():
        raise FileNotFoundError(f"Fichier introuvable : {path}")
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("secrets.toml invalide")
    return data


def header_range(ncols: int) -> str:
    end = rowcol_to_a1(1, ncols)
    return f"A1:{end}"


def write_headers(ws, headers: list[str], *, force: bool) -> bool:
    row1 = ws.row_values(1)
    if row1 and row1[0] and not force:
        return False
    ws.update(
        range_name=header_range(len(headers)),
        values=[headers],
        value_input_option="USER_ENTERED",
    )
    return True


def _sheet_has_data_below_header(all_vals: list[list[str]]) -> bool:
    if len(all_vals) <= 1:
        return False
    for row in all_vals[1:]:
        if any(str(c).strip() for c in row):
            return True
    return False


def _norm_seed_header(s: str) -> str:
    t = str(s).strip().lower().replace(" ", "_")
    return re.sub(r"[^a-z0-9_]+", "", t)


def _seed_row_for_sheet_headers(
    sheet_headers: list[str],
    schema_headers: list[str],
    seed_tuple: tuple,
    *,
    filled_iso: str,
) -> list[str]:
    """Mappe une graine définie dans l’ordre du **schéma** vers les colonnes réelles de la ligne 1 du classeur."""
    sch_key_to_idx = {_norm_seed_header(h): i for i, h in enumerate(schema_headers)}
    row_out: list[str] = []
    for h_sheet in sheet_headers:
        kn = _norm_seed_header(h_sheet)
        idx = sch_key_to_idx.get(kn)
        if idx is not None and idx < len(seed_tuple):
            val = seed_tuple[idx]
        else:
            val = ""
        sval = "" if val is None else str(val)
        if kn in ("enregistre_le", "maj_le") and not str(sval).strip():
            sval = filled_iso
        row_out.append(sval)
    return row_out


def append_seeds(ws, tab: SheetTab) -> int:
    rows = tab.seed_rows
    if not rows:
        return 0
    all_vals = ws.get_all_values()
    if _sheet_has_data_below_header(all_vals):
        return 0
    sheet_headers = [str(x).strip() for x in (all_vals[0] if all_vals else [])]
    if not sheet_headers:
        sheet_headers = list(tab.headers)
    filled_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    for r in rows:
        line = _seed_row_for_sheet_headers(sheet_headers, list(tab.headers), r, filled_iso=filled_iso)
        ws.append_row(line, value_input_option="USER_ENTERED")
    return len(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Init Google Sheets SÉRÉNO")
    parser.add_argument(
        "--force-headers",
        action="store_true",
        help="Réécrit la ligne 1 même si elle est déjà remplie",
    )
    parser.add_argument(
        "--seed",
        action="store_true",
        help="Insère les lignes de graine si l’onglet n’a qu’une seule ligne (en-tête)",
    )
    args = parser.parse_args()

    secrets = load_streamlit_secrets()
    gsheet_id = secrets.get("gsheet_id")
    if not gsheet_id:
        print("Erreur : gsheet_id manquant dans .streamlit/secrets.toml", file=sys.stderr)
        return 1
    try:
        sa_info = get_service_account_info(ROOT, secrets)
    except ValueError as e:
        print(f"Erreur : {e}", file=sys.stderr)
        return 1

    creds = credentials_for_sheets(sa_info)
    gc = gspread.authorize(creds)
    sh = gspread_retry(lambda: gc.open_by_key(str(gsheet_id)), what="ouverture classeur")
    by_title = gspread_retry(lambda: worksheet_index_by_title(sh), what="liste des onglets")

    for tab in SHEET_TABS:
        ws = by_title.get(tab.title)
        if ws is None:
            cols = max(len(tab.headers), 12)
            ws = gspread_retry(
                lambda: sh.add_worksheet(title=tab.title, rows=200, cols=cols),
                what=f"creation onglet {tab.title}",
            )
            by_title[tab.title] = ws

        wrote = write_headers(ws, tab.headers, force=args.force_headers)
        status = "entetes ecrits" if wrote else "entetes conserves (deja presents ou pas de --force-headers)"
        print(f"[{tab.title}] {status}")
        if args.seed and tab.seed_rows:
            n = append_seeds(ws, tab)
            if n:
                print(f"  -> {n} ligne(s) de graine ajoutee(s)")
            elif tab.seed_rows:
                print("  -> graine ignoree (donnees deja presentes sous l'en-tete)")
        tab_throttle_seconds()

    print("Termine.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
