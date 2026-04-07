#!/usr/bin/env python3
"""
Initialise les onglets du classeur SÉRÉNO : en-têtes (ligne 1) et lignes de graine si l’onglet est vide.

Lit la configuration dans `.streamlit/secrets.toml` :
  gsheet_id, et compte de service via [gcp_service_account] ou service_account_json_path

Usage (depuis la racine du dépôt) :
  python scripts/init_google_sheet.py
  python scripts/init_google_sheet.py --seed          # ajoute les lignes d’exemple si l’onglet n’avait que l’en-tête
  python scripts/init_google_sheet.py --force-headers # réécrit la ligne 1 (attention si vous aviez modifié les titres à la main)

Prérequis : pip install -r requirements.txt
"""

from __future__ import annotations

import argparse
import sys
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


def ensure_worksheet(sh: gspread.Spreadsheet, tab: SheetTab):
    try:
        return sh.worksheet(tab.title)
    except gspread.WorksheetNotFound:
        cols = max(len(tab.headers), 12)
        return sh.add_worksheet(title=tab.title, rows=200, cols=cols)


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


def append_seeds(ws, rows: tuple[tuple, ...]) -> int:
    if not rows:
        return 0
    all_vals = ws.get_all_values()
    n = len(all_vals)
    if n > 1:
        return 0
    for r in rows:
        ws.append_row([str(c) if c is not None else "" for c in r], value_input_option="USER_ENTERED")
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
    sh = gc.open_by_key(str(gsheet_id))

    for tab in SHEET_TABS:
        ws = ensure_worksheet(sh, tab)
        wrote = write_headers(ws, tab.headers, force=args.force_headers)
        status = "entetes ecrits" if wrote else "entetes conserves (deja presents ou pas de --force-headers)"
        print(f"[{tab.title}] {status}")
        if args.seed and tab.seed_rows:
            n = append_seeds(ws, tab.seed_rows)
            if n:
                print(f"  -> {n} ligne(s) de graine ajoutee(s)")
            elif tab.seed_rows:
                print("  -> graine ignoree (onglet deja rempli au-dela de la ligne 1)")

    print("Termine.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
