"""
Administration · pilote — consultation compacte des artisans (photo + prénom/nom) + accès édition.
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

_REPO = Path(__file__).resolve().parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from sereno_core.gcs_artisan_photo import download_artisan_photo_bytes
from sereno_core.jopai_brand_html import page_title_h1_html
from sereno_core.sheets_experts import load_experts_from_sheets, resolve_gsheet_id

st.markdown(page_title_h1_html("Administration · Artisans (liste)"), unsafe_allow_html=True)
st.caption("Liste compacte : photo + nom. Cliquez pour ouvrir la fiche d’édition.")
st.page_link("pages/21_Admin_artisans.py", label="→ Retour à la fiche artisan", icon="🧑‍🔧")

try:
    _secrets = dict(st.secrets)
except Exception:
    _secrets = {}

gsid = resolve_gsheet_id(_REPO, _secrets).strip()
if not gsid:
    st.info("**gsheet_id** manquant — lecture Experts indisponible.")
    st.stop()

experts = load_experts_from_sheets(_REPO, _secrets) or []
if not experts:
    st.info("Aucun artisan chargé depuis l’onglet **Experts**.")
    st.stop()

st.markdown(
    """
<style>
.sereno-expert-row { display:flex; align-items:center; gap:10px; padding:6px 8px;
  border:1px solid rgba(15,23,42,0.08); border-radius:10px; background:rgba(255,255,255,0.55); }
.sereno-expert-name { font-weight:650; color:#0b2745; line-height:1.2; }
.sereno-expert-sub { font-size:0.82rem; color:#334155; opacity:0.95; }
</style>
""",
    unsafe_allow_html=True,
)

for e in experts:
    eid = str(e.get("id") or "").strip()
    if not eid:
        continue
    pn = str(e.get("prenom") or "").strip()
    nm = str(e.get("nom") or "").strip()
    display = (f"{pn} {nm}".strip() if pn and nm else str(e.get("nom_affichage") or nm or pn or eid)).strip()

    cimg, ctext, cbtn = st.columns([0.12, 0.68, 0.20], vertical_alignment="center")
    with cimg:
        tup = download_artisan_photo_bytes(_REPO, _secrets, expert_id=eid)
        if tup:
            data, _mime = tup
            st.image(data, width=44)
        else:
            st.markdown(
                "<div style='width:44px;height:44px;border-radius:50%;background:rgba(11,39,69,0.08);"
                "border:2px solid rgba(0,51,102,0.10);'></div>",
                unsafe_allow_html=True,
            )
    with ctext:
        st.markdown(
            f"<div class='sereno-expert-name'>{display}</div>"
            f"<div class='sereno-expert-sub'>{eid}</div>",
            unsafe_allow_html=True,
        )
    with cbtn:
        if st.button("Éditer", key=f"edit_{eid}", use_container_width=True):
            st.session_state["admin_artisans_edit_id"] = eid
            st.switch_page("pages/21_Admin_artisans.py")

