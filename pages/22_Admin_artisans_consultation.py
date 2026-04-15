"""
Administration · pilote — liste artisans (tableau aligné à gauche, colonnes resserrées).
"""

from __future__ import annotations

import sys
from html import escape
from pathlib import Path

import streamlit as st

_REPO = Path(__file__).resolve().parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from sereno_core.gcs_artisan_photo import download_artisan_photo_bytes
from sereno_core.jopai_brand_html import page_title_h1_html
from sereno_core.proto_checklists import URGENCE_LABELS
from sereno_core.sheets_experts import load_experts_from_sheets, resolve_gsheet_id

st.markdown(page_title_h1_html("Administration · Artisans (liste)"), unsafe_allow_html=True)
st.caption(
    "Tableau **à gauche**, colonnes calées sur le contenu ; bouton **Éditer** en largeur naturelle "
    "(évite le texte broyé dans une colonne trop étroite)."
)
st.page_link("pages/21_Admin_artisans.py", label="→ Retour à la fiche artisan", icon="🧑‍🔧")

if "edit" in st.query_params:
    _raw = st.query_params["edit"]
    _eid = (_raw[0] if isinstance(_raw, list) else str(_raw or "")).strip()
    if _eid:
        st.session_state["admin_artisans_edit_id"] = _eid
        try:
            del st.query_params["edit"]
        except Exception:
            pass
        st.switch_page("pages/21_Admin_artisans.py")

try:
    _secrets = dict(st.secrets)
except Exception:
    _secrets = {}

gsid = resolve_gsheet_id(_REPO, _secrets).strip()
if not gsid:
    st.info("**gsheet_id** manquant — lecture Experts indisponible.")
    st.stop()

experts = load_experts_from_sheets(_REPO, _secrets, eager_gcs_photo=False) or []
if not experts:
    st.info("Aucun artisan chargé depuis l’onglet **Experts**.")
    st.stop()


def _types_line_html(types: object) -> str:
    raw: list[str] = []
    for t in list(types or []):
        c = str(t or "").strip().upper()
        if c:
            raw.append(URGENCE_LABELS.get(c, c))
    return escape(" · ".join(raw)) if raw else escape("—")


st.markdown(
    """
<style>
.sereno-admin-list-nm { font-weight:650;color:#0b2745;line-height:1.2;font-size:0.92rem; }
.sereno-admin-list-ex { font-size:0.78rem;color:#334155;line-height:1.25; }
.sereno-admin-list-tel { font-size:0.78rem;color:#0f172a;margin-top:2px; }
.sereno-tbl-fit-wrap { width:max-content; max-width:100%; margin:0; }
.sereno-tbl-fit-hdr { width:max-content; border-collapse:collapse; table-layout:auto; margin:0;
  border:1px solid #e2e8f0; border-bottom:none; border-radius:8px 8px 0 0; background:#f1f5f9;
  font-size:0.78rem; color:#0b2745; }
.sereno-tbl-fit-hdr th { padding:8px 10px; font-weight:650; border-bottom:1px solid #e2e8f0; white-space:nowrap; }
.sereno-tbl-fit-hdr th:nth-child(1) { text-align:center; }
.sereno-tbl-fit-hdr th:nth-child(2) { text-align:left; }
.sereno-tbl-fit-hdr th:nth-child(3) { text-align:left; }
.sereno-tbl-fit-hdr th:nth-child(4) { text-align:right; }
</style>
""",
    unsafe_allow_html=True,
)

_W_PH, _W_NA, _W_ME, _W_AC = 0.11, 0.20, 0.54, 0.15
_tbl_col, _rest = st.columns([0.52, 0.48])
with _tbl_col:
    st.markdown(
        '<div class="sereno-tbl-fit-wrap"><table class="sereno-tbl-fit-hdr"><thead><tr>'
        "<th>Photo</th><th>Artisan</th><th>Expertises · Téléphone</th><th>Action</th>"
        "</tr></thead></table></div>",
        unsafe_allow_html=True,
    )

    rows = [e for e in experts if str(e.get("id") or "").strip()]
    for idx, e in enumerate(rows):
        eid = str(e.get("id") or "").strip()
        pn = str(e.get("prenom") or "").strip()
        nm = str(e.get("nom") or "").strip()
        display = (f"{pn} {nm}".strip() if pn and nm else str(e.get("nom_affichage") or nm or pn or eid)).strip()
        tel = str(e.get("telephone") or "").strip() or "—"
        ex_line = _types_line_html(e.get("types"))

        cimg, cname, cmeta, cact = st.columns(
            [_W_PH, _W_NA, _W_ME, _W_AC],
            vertical_alignment="center",
        )
        with cimg:
            tup = download_artisan_photo_bytes(_REPO, _secrets, expert_id=eid)
            if tup:
                st.image(tup[0], width=40)
            else:
                st.markdown(
                    "<div style='width:40px;height:40px;border-radius:50%;background:rgba(11,39,69,0.08);"
                    "border:2px solid rgba(0,51,102,0.10);margin:0 auto;'></div>",
                    unsafe_allow_html=True,
                )
        with cname:
            st.markdown(f'<div class="sereno-admin-list-nm">{escape(display)}</div>', unsafe_allow_html=True)
        with cmeta:
            st.markdown(
                f'<div class="sereno-admin-list-ex">{ex_line}</div>'
                f'<div class="sereno-admin-list-tel">{escape(tel)}</div>',
                unsafe_allow_html=True,
            )
        with cact:
            if st.button("Éditer", key=f"admin_list_edit_{eid}", use_container_width=False):
                st.session_state["admin_artisans_edit_id"] = eid
                st.switch_page("pages/21_Admin_artisans.py")
        if idx < len(rows) - 1:
            st.markdown(
                "<div style='height:0;margin:0.15rem 0 0.25rem 0;border-bottom:1px solid #e2e8f0;'></div>",
                unsafe_allow_html=True,
            )
    if rows:
        st.markdown(
            "<div style='height:0;margin:0;border-bottom:1px solid #e2e8f0;"
            "border-radius:0 0 8px 8px;box-shadow:0 1px 4px rgba(0,51,102,0.06);'></div>",
            unsafe_allow_html=True,
        )
