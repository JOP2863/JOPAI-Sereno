"""
Administration · pilote — création / mise à jour d’artisans (onglet **Experts** + photo GCS).

- **Experts** (Google Sheets) : colonnes attendues ``expert_id, prenom, nom, email, telephone, actif, types_autorises, photo, ...``
- **Photo** : upload JPG vers GCS au format ``{prefix}/{expert_id}.jpg`` (ex. ``artisan/EXP-001.jpg``)
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
from sereno_core.sheets_experts import load_experts_from_sheets, resolve_gsheet_id
from sereno_core.sheets_experts_write import try_upsert_expert_row


def _norm_id(s: str) -> str:
    s = str(s or "").strip()
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"[^A-Za-z0-9_-]+", "", s)
    return s


def _types_to_cell(v: str) -> str:
    raw = str(v or "").strip()
    if not raw:
        return ""
    # Autoriser ; ou , dans l’UI, stocker en `;` (comme seed sheets_schema.py)
    parts = re.split(r"[;,]+", raw)
    clean = []
    for p in parts:
        t = str(p or "").strip().upper()
        if t:
            clean.append(t)
    # dédoublonner en conservant l’ordre
    out = []
    for t in clean:
        if t not in out:
            out.append(t)
    return ";".join(out)


st.markdown(page_title_h1_html("Administration · Artisans (fiche)"), unsafe_allow_html=True)
st.caption(
    "Crée ou met à jour une ligne dans l’onglet **Experts** du classeur Google, et permet d’uploader une "
    "photo **JPG** dans Google Cloud Storage (convention ``artisan/{expert_id}.jpg``)."
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
    eid = pick.split("(")[-1].rstrip(")").strip()
    for e in experts:
        if str(e.get("id") or "").strip() == eid:
            current = dict(e)
            break

st.divider()

left, right = st.columns([0.68, 0.32])

with left:
    st.subheader("Identité")
    if is_new:
        expert_id = _norm_id(st.text_input("expert_id", value="EXP-NEW", help="Ex. EXP-002"))
    else:
        expert_id = str(current.get("id") or "").strip()
        st.text_input("expert_id", value=expert_id, disabled=True)

    c1, c2 = st.columns([0.5, 0.5])
    with c1:
        prenom = st.text_input("prenom", value=str(current.get("prenom") or ""))
    with c2:
        nom = st.text_input("nom (famille)", value=str(current.get("nom") or ""))

    st.subheader("Contact & statut")
    email = st.text_input("email", value=str(current.get("email") or ""))
    tel = st.text_input("telephone", value=str(current.get("telephone") or ""), help="Ex. +33600000000")
    actif = st.checkbox("actif", value=True if is_new else True, help="Désactiver = masqué du choix côté client.")

    st.subheader("Interventions")
    types_autorises = st.text_input(
        "types_autorises",
        value=_types_to_cell(";".join(list(current.get("types") or []))) if not is_new else "EAU;ELEC;GAZ;CHAUFF;SERR",
        help="Codes séparés par ; (ex. EAU;GAZ).",
    )

    st.subheader("Notes / intégrations")
    notes = st.text_area("notes_internes", value=str(current.get("notes_internes") or ""), height=110, max_chars=1200)
    stripe = st.text_input("stripe_connect_account_id", value=str(current.get("stripe_connect_account_id") or ""))

    save = st.button("Enregistrer l’artisan", type="primary", use_container_width=True)

with right:
    st.subheader("Photo")
    if not is_new and expert_id:
        tup = download_artisan_photo_bytes(_REPO, _secrets, expert_id=expert_id)
        if tup:
            data, _mime = tup
            st.image(data, caption="Aperçu", use_container_width=True)
        st.caption(f"Chemin objet : `{artisan_photo_blob_path(expert_id, _secrets)}`")
    else:
        st.caption("Créez d’abord l’artisan (expert_id), puis uploadez la photo.")

    up = st.file_uploader("Uploader une photo (JPG)", type=["jpg", "jpeg"])
    do_upload = st.button("Uploader la photo", type="secondary", use_container_width=True, disabled=(not up or not expert_id))

if save:
    if not expert_id or len(expert_id) < 3:
        st.error("expert_id invalide.")
    elif not (prenom.strip() or nom.strip()):
        st.error("Renseignez au moins `prenom` ou `nom`.")
    else:
        updates = {
            "prenom": prenom.strip(),
            "nom": nom.strip(),
            "email": email.strip(),
            "telephone": tel.strip(),
            "actif": "OUI" if actif else "NON",
            "types_autorises": _types_to_cell(types_autorises),
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
        # Facultatif : écrire la colonne "photo" si présente (chemin objet)
        blob = artisan_photo_blob_path(expert_id, _secrets)
        try_upsert_expert_row(_REPO, _secrets, expert_id=expert_id, updates={"photo": blob})
        st.success("Photo uploadée.")
        st.rerun()
    else:
        st.error(f"Upload impossible : {err}")

