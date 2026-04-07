"""
Carnet d’échange — journal des décisions et fil de discussion projet (Markdown léger).
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import streamlit as st

from sereno_core.streamlit_markdown_book import render_markdown_book_page

st.title("Carnet d’échange")

render_markdown_book_page(
    repo_root=_REPO,
    doc_path=_REPO / "docs" / "CAHIER_ECHANGES.md",
    session_prefix="carnet",
    page_caption=(
        "Notes des **échanges** et **décisions** au fil du projet (complément du cahier des charges). "
        "Même navigation : recherche, chapitres **##**, sections **###**."
    ),
    footer_markdown=(
        "Éditer **`docs/CAHIER_ECHANGES.md`** puis rafraîchir. "
        "Référence normative : **`CAHIER_DES_CHARGES.md`** (page **Cahier des charges**)."
    ),
)
