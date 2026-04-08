"""
Utilitaires gspread : limiter les **429** (quota « read requests » Google Sheets).
"""

from __future__ import annotations

import random
import sys
import time
from collections.abc import Callable
from typing import TypeVar

import gspread

T = TypeVar("T")


def gspread_retry(fn: Callable[[], T], *, what: str, max_attempts: int = 8) -> T:
    """Relance en cas de 429 / quota API (délai croissant)."""
    delay = 2.5
    last_err: Exception | None = None
    for attempt in range(max_attempts):
        try:
            return fn()
        except gspread.exceptions.APIError as e:
            last_err = e
            err = str(e)
            if "429" not in err and "Quota exceeded" not in err and "quota" not in err.lower():
                raise
            if attempt == max_attempts - 1:
                break
            print(
                f"[gspread] Quota / 429 — attente {delay:.0f}s puis nouvel essai "
                f"({what}, {attempt + 1}/{max_attempts})…",
                file=sys.stderr,
            )
            time.sleep(delay + random.uniform(0, 1.5))
            delay = min(delay * 1.65, 95.0)
    assert last_err is not None
    raise last_err


def worksheet_index_by_title(sh: gspread.Spreadsheet) -> dict[str, gspread.Worksheet]:
    """
    Index titre → onglet en **un** chargement métadonnées.
    Évite N appels à ``Spreadsheet.worksheet(titre)`` (chacun refetch les métadonnées → 429).
    """
    return {w.title: w for w in sh.worksheets()}


def tab_throttle_seconds() -> None:
    """Petite pause entre onglets pour rester sous les limites « par minute »."""
    time.sleep(0.45)
