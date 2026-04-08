#!/usr/bin/env python3
"""
Met à jour le classeur Google Sheets SÉRÉNO pour aligner la **ligne 1** (en-têtes) et les lignes
de données sur `sereno_core.sheets_schema.SHEET_TABS` :

- **conserve** l’ordre des colonnes déjà présentes ;
- **ajoute** en fin de ligne les colonnes manquantes (horodatage, dates d’effet, onglet
  **Utilisateurs_Acces**, etc.) ;
- **complète** chaque ligne existante avec des cellules vides pour les nouvelles colonnes.

Ne supprime ni ne renomme de colonnes existantes (migration additive uniquement).

Configuration : même source que `init_google_sheet.py` — `.streamlit/secrets.toml` avec `gsheet_id`
et compte de service. Liste des onglets en **un** chargement + pause entre onglets + relais **429** (voir
`sereno_core/gspread_helpers.py`).

Usage (depuis la racine du dépôt) :

  python scripts/migrate_google_sheet_schema.py --dry-run    # affiche le détail sans écrire
  python scripts/migrate_google_sheet_schema.py --apply      # écrit dans le classeur

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


def merge_headers(current: list[str], canonical: list[str]) -> tuple[list[str], list[str]]:
    """
    Retourne (nouvelle_ligne_en_tetes, liste_des_colonnes_ajoutees).
    Les colonnes déjà présentes gardent leur ordre ; les manquantes sont ajoutées
    dans l’ordre du schéma canonique.
    """
    cur = [str(c or "").strip() for c in current]
    while cur and not cur[-1]:
        cur.pop()
    seen = {c for c in cur if c}
    added: list[str] = []
    out = list(cur)
    for h in canonical:
        hn = str(h).strip()
        if not hn:
            continue
        if hn not in seen:
            out.append(hn)
            seen.add(hn)
            added.append(hn)
    return out, added


def pad_row(row: list[str], ncols: int) -> list[str]:
    cells = list(row)
    if len(cells) < ncols:
        cells.extend([""] * (ncols - len(cells)))
    elif len(cells) > ncols:
        cells = cells[:ncols]
    return cells


def migrate_tab(
    ws: gspread.Worksheet,
    tab: SheetTab,
    *,
    dry_run: bool,
) -> tuple[bool, str]:
    try:
        all_vals = ws.get_all_values()
    except Exception as e:
        return False, f"lecture impossible : {e}"

    if not all_vals:
        new_h = list(tab.headers)
        msg = f"onglet vide -> en-têtes seules ({len(new_h)} col.)"
        if dry_run:
            return True, f"[DRY] {msg}"
        rng = f"A1:{rowcol_to_a1(1, len(new_h))}"
        ws.update(range_name=rng, values=[new_h], value_input_option="USER_ENTERED")
        return True, msg

    row1 = all_vals[0]
    new_headers, added = merge_headers(row1, tab.headers)
    if not added and len(new_headers) == len(row1):
        return True, "déjà aligné, rien à faire"

    body = all_vals[1:]
    new_body = [pad_row(r, len(new_headers)) for r in body]
    matrix = [new_headers] + new_body
    nrows, ncols = len(matrix), len(new_headers)
    cell = rowcol_to_a1(nrows, ncols)

    detail = f"+{len(added)} colonne(s)" if added else "redimensionnement"
    if added:
        detail += f" : {', '.join(added[:12])}" + (" …" if len(added) > 12 else "")

    if dry_run:
        return True, f"[DRY] {detail} ; matrice {nrows}x{ncols}"

    ws.update(range_name=f"A1:{cell}", values=matrix, value_input_option="USER_ENTERED")
    return True, f"{detail} ; matrice {nrows}x{ncols} écrite"


def main() -> int:
    parser = argparse.ArgumentParser(description="Migration schéma Google Sheets SÉRÉNO")
    parser.add_argument("--dry-run", action="store_true", help="Simuler sans écrire")
    parser.add_argument("--apply", action="store_true", help="Écrire dans le classeur")
    args = parser.parse_args()
    if args.dry_run == args.apply:
        print("Indiquez exactement une option : --dry-run OU --apply", file=sys.stderr)
        return 2

    try:
        secrets = load_streamlit_secrets()
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        return 1

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
    dry = args.dry_run

    ok_all = True
    for tab in SHEET_TABS:
        ws = by_title.get(tab.title)
        if ws is None:
            cols = max(len(tab.headers), 12)
            ws = gspread_retry(
                lambda: sh.add_worksheet(title=tab.title, rows=400, cols=cols),
                what=f"creation onglet {tab.title}",
            )
            by_title[tab.title] = ws
        ok, msg = migrate_tab(ws, tab, dry_run=dry)
        status = "OK" if ok else "ERREUR"
        if not ok:
            ok_all = False
        print(f"[{tab.title}] {status} — {msg}")
        tab_throttle_seconds()

    print("Terminé." if ok_all else "Terminé avec erreurs.")
    return 0 if ok_all else 1


if __name__ == "__main__":
    raise SystemExit(main())
