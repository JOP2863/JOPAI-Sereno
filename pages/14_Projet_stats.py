"""
Métriques projet — lignes cahier des charges + lignes de code (même esprit que JOPAI-BTP `cdc_viewer`).
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import pandas as pd
import streamlit as st

from sereno_core.formatting import format_thousands_int
from sereno_core.jopai_brand_html import page_title_h1_html
from sereno_core.project_line_counts import count_project_source_lines, top_py_files_by_lines
from sereno_core.streamlit_theme import inject_button_zoom_resilience_css

inject_button_zoom_resilience_css()

st.markdown(page_title_h1_html("Métriques projet"), unsafe_allow_html=True)
st.caption(
    "Compteurs **lignes cahier des charges** et **lignes de code** sur le dépôt local "
    "(hors `.venv`, `build/`, etc.)."
)

cdc_path = _REPO / "CAHIER_DES_CHARGES.md"
if cdc_path.is_file():
    md_text = cdc_path.read_text(encoding="utf-8")
    lines_total = len(md_text.splitlines())
    lines_non_empty = sum(1 for ln in md_text.splitlines() if ln.strip())
else:
    lines_total = lines_non_empty = 0

counts = count_project_source_lines(str(_REPO))
top_py = top_py_files_by_lines(str(_REPO), limit=10)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Lignes cahier des charges", format_thousands_int(lines_total))
with c2:
    st.metric("Lignes non vides (CDC)", format_thousands_int(lines_non_empty))
with c3:
    st.metric("Lignes de code (total)", format_thousands_int(counts["total"]))
with c4:
    st.metric("Lignes de commentaires", format_thousands_int(counts["comments_total"]))

st.caption(
    f"Lignes code non vides : **{format_thousands_int(counts['non_empty'])}** "
    f"(Python : {format_thousands_int(counts['py_non_empty'])} / hors Python : "
    f"{format_thousands_int(counts['hors_py_non_empty'])}). "
    f"Total : Py {format_thousands_int(counts['py_total'])} / hors Py {format_thousands_int(counts['hors_py_total'])}."
)

if top_py:
    st.subheader("Top 10 fichiers Python (lignes + taille disque)")
    rows = []
    for x in top_py:
        rel = str(x["path"])
        sz = int(x.get("size_bytes") or 0)
        parts = rel.replace("\\", "/").split("/")
        label = "/".join(parts[-2:]) if len(parts) >= 2 else parts[-1]
        rows.append(
            {
                "Chemin": rel,
                "Résumé": label,
                "Taille (Ko)": round(sz / 1024, 1),
                "Lignes": int(x.get("loc_total") or 0),
            }
        )
    df = pd.DataFrame(rows)
    df = df.sort_values("Lignes", ascending=False)
    _, tbl, _ = st.columns([0.15, 0.62, 0.23])
    with tbl:
        st.dataframe(df, use_container_width=True, hide_index=True)
    _, chart_col, _ = st.columns([0.2, 0.55, 0.25])
    with chart_col:
        st.caption("Histogramme condensé (lisible sans occuper toute la largeur).")
        st.bar_chart(df.set_index("Résumé")[["Lignes"]], height=280)
