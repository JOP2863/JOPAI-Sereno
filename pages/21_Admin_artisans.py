"""
Administration · pilote — création / mise à jour d’artisans (onglet **Experts** + photo GCS).

- **Experts** (Google Sheets) : colonnes attendues ``expert_id, prenom, nom, email, telephone, actif, types_autorises, photo, ...``
- **Photo** : upload JPG vers GCS au format ``{prefix}/{expert_id}.jpg`` (ex. ``artisan/EXP-001.jpg``)
- Colonne **photo** dans Sheets : de préférence **chemin objet** (``artisan/EXP-001.jpg``) ou vide ; l’appli charge via le compte de service.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import streamlit as st

_REPO = Path(__file__).resolve().parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from sereno_core.gcs_artisan_photo import (
    artisan_photo_blob_path,
    download_artisan_photo_bytes,
    upload_artisan_photo_jpg,
)
from sereno_core.jopai_brand_html import page_title_h1_html
from sereno_core.proto_checklists import URGENCE_LABELS
from sereno_core.sheets_experts import load_experts_from_sheets, resolve_gsheet_id
from sereno_core.sheets_experts_write import try_upsert_expert_row

_TYPE_CODES = list(URGENCE_LABELS.keys())


def _next_expert_id(experts: list) -> str:
    """Prochain identifiant **EXP-###** (3 chiffres) d’après les lignes existantes."""
    nmax = 0
    for e in experts:
        raw = str(e.get("id") or "").strip().upper()
        m = re.fullmatch(r"EXP-(\d{1,5})", raw)
        if m:
            nmax = max(nmax, int(m.group(1)))
    return f"EXP-{nmax + 1:03d}"


def _types_to_cell_from_multiselect(selected: list[str]) -> str:
    out: list[str] = []
    for t in selected:
        u = str(t or "").strip().upper()
        if u and u not in out:
            out.append(u)
    return ";".join(out)


st.markdown(
    """
<style>
.sereno-admin-artisan-compact section.main h3 { font-size: 0.98rem !important; margin: 0.06rem 0 0.1rem 0 !important; }
.sereno-admin-artisan-compact section.main .stMarkdown p { margin-bottom: 0.1rem !important; line-height: 1.22 !important; }
.sereno-admin-artisan-compact section.main [data-testid="stVerticalBlock"] > div { gap: 0.22rem !important; }
.sereno-admin-artisan-compact label { margin-bottom: 0.04rem !important; }
.sereno-admin-artisan-compact section.main hr { margin: 0.28rem 0 !important; }
.sereno-admin-artisan-compact section.main [data-testid="stTextInput"] { margin-bottom: 0.08rem !important; }
.sereno-admin-artisan-compact section.main [data-testid="stTextArea"] { margin-bottom: 0.08rem !important; }
.sereno-admin-artisan-compact section.main [data-testid="stFileUploader"] { margin-bottom: 0.12rem !important; }
</style>
""",
    unsafe_allow_html=True,
)
st.markdown('<div class="sereno-admin-artisan-compact">', unsafe_allow_html=True)

st.markdown(page_title_h1_html("Administration · Artisans (fiche)"), unsafe_allow_html=True)
st.caption(
    "Crée ou met à jour une ligne dans l’onglet **Experts** du classeur Google, et permet d’uploader une "
    "photo **JPG** dans Google Cloud Storage (convention ``artisan/{expert_id}.jpg``). "
    "Pour la colonne **photo** : indiquez plutôt le **chemin objet** (ex. ``artisan/EXP-001.jpg``) ou laissez vide — "
    "les URLs **storage.cloud.google.com** ne s’affichent pas dans l’interface ; les URLs **storage.googleapis.com** "
    "ne marchent que si l’objet est **public**."
)
st.page_link("pages/22_Admin_artisans_consultation.py", label="→ Consulter les artisans (liste compacte)", icon="📇")

try:
    _secrets = dict(st.secrets)
except Exception:
    _secrets = {}

gsid = resolve_gsheet_id(_REPO, _secrets).strip()
if not gsid:
    st.info("**gsheet_id** manquant — écriture / lecture Experts indisponible.")
    st.stop()

experts = load_experts_from_sheets(_REPO, _secrets) or []
choices = ["➕ Créer un nouvel artisan"] + [f"{e.get('nom_affichage') or e.get('id')} ({e.get('id')})" for e in experts]
pre = str(st.session_state.pop("admin_artisans_edit_id", "") or "").strip()
idx_pre = 0
if pre:
    for i, ch in enumerate(choices):
        if f"({pre})" in ch:
            idx_pre = i
            break
pick = st.selectbox("Choisir un artisan à éditer", options=choices, index=idx_pre)

is_new = pick.startswith("➕")
current = {}
if not is_new:
    eid_pick = pick.split("(")[-1].rstrip(")").strip()
    for e in experts:
        if str(e.get("id") or "").strip() == eid_pick:
            current = dict(e)
            break

if is_new:
    expert_id = _next_expert_id(experts)
else:
    expert_id = str(current.get("id") or "").strip()

st.divider()

left, right = st.columns([0.68, 0.32])

with left:
    st.subheader("Identité")
    st.text_input("expert_id (attribué automatiquement)", value=expert_id, disabled=True, help="Format EXP-001, EXP-002, …")

    c1, c2 = st.columns([0.5, 0.5])
    with c1:
        prenom = st.text_input("prenom", value=str(current.get("prenom") or ""))
    with c2:
        nom = st.text_input("nom (famille)", value=str(current.get("nom") or ""))

    st.subheader("Contact & statut")
    email = st.text_input("email", value=str(current.get("email") or ""))
    tel = st.text_input("telephone", value=str(current.get("telephone") or ""), help="Ex. +33600000000")
    actif = st.checkbox("actif", value=True, help="Désactiver = masqué du choix côté client.")

    st.subheader("Interventions")
    cur_types = [str(t).strip().upper() for t in (current.get("types") or []) if str(t).strip().upper() in _TYPE_CODES]
    default_types = cur_types if cur_types else list(_TYPE_CODES)
    types_sel = st.multiselect(
        "types_autorises",
        options=_TYPE_CODES,
        default=default_types,
        format_func=lambda c: URGENCE_LABELS.get(c, c),
        help="Sélection multiple ; stockage dans Sheets sous forme EAU;ELEC;…",
    )

    st.subheader("Notes / intégrations")
    notes = st.text_area("notes_internes", value=str(current.get("notes_internes") or ""), height=72, max_chars=1200)
    stripe = st.text_input("stripe_connect_account_id", value=str(current.get("stripe_connect_account_id") or ""))

    save = st.button("Enregistrer l’artisan", type="primary", use_container_width=True)

with right:
    st.subheader("Photo")
    if expert_id:
        tup = download_artisan_photo_bytes(_REPO, _secrets, expert_id=expert_id)
        if tup:
            data, _mime = tup
            st.image(data, caption="Aperçu (GCS)", use_container_width=True)
        st.caption(f"Chemin objet attendu : `{artisan_photo_blob_path(expert_id, _secrets)}`")

    up = st.file_uploader("Uploader une photo (JPG)", type=["jpg", "jpeg"])
    do_upload = st.button("Uploader la photo", type="secondary", use_container_width=True, disabled=(not up or not expert_id))

if save:
    if not (prenom.strip() or nom.strip()):
        st.error("Renseignez au moins `prenom` ou `nom`.")
    elif not types_sel:
        st.error("Sélectionnez au moins un type d’intervention.")
    else:
        updates = {
            "prenom": prenom.strip(),
            "nom": nom.strip(),
            "email": email.strip(),
            "telephone": tel.strip(),
            "actif": "OUI" if actif else "NON",
            "types_autorises": _types_to_cell_from_multiselect(types_sel),
            "notes_internes": notes.strip(),
            "stripe_connect_account_id": stripe.strip(),
        }
        ok, msg = try_upsert_expert_row(_REPO, _secrets, expert_id=expert_id, updates=updates)
        if ok:
            st.success(msg)
            st.rerun()
        else:
            st.error(msg)

if do_upload and up and expert_id:
    data = up.getvalue()
    ok, err = upload_artisan_photo_jpg(_REPO, _secrets, expert_id=expert_id, data=data)
    if ok:
        blob = artisan_photo_blob_path(expert_id, _secrets)
        try_upsert_expert_row(_REPO, _secrets, expert_id=expert_id, updates={"photo": blob})
        st.success("Photo uploadée.")
        st.rerun()
    else:
        st.error(f"Upload impossible : {err}")

st.markdown("</div>", unsafe_allow_html=True)
