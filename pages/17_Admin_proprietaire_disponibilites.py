"""
Administration · pilote — vue **propriétaire** sur les disponibilités réseau.

Les changements « sensibles » sont conditionnés à un **accord avec l’artisan** (simulation).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import pandas as pd
import streamlit as st

from sereno_core.gcp_credentials import credentials_for_sheets, get_service_account_info
from sereno_core.proto_state import ensure_demo_seed, p_get
from sereno_core.sheets_disponibilite_write import append_disponibilite_mois_row, mois_sous_verrouillage_artisan
from sereno_core.sheets_experts import disponibilite_expert_options, resolve_gsheet_id

st.title("Administration · Disponibilités réseau (propriétaire)")
st.caption("Premier jet — pas d’auth ; même classeur Sheets que le pilote.")

st.markdown(
    """
### Règles prévues

- Le propriétaire **consulte** l’ensemble des lignes **Disponibilite_Mois** (tous experts).
- Pour **modifier** ou **ajouter** une ligne au nom d’un artisan dans la fenêtre sensible (**< 30 jours** avant le 1ᵉʳ du mois) :
  cocher **« Accord de l’artisan confirmé »** (trace de gouvernance — simulation ici).
- Hors fenêtre sensible, l’ajout reste possible pour anticiper la planification réseau.

*Écriture = même mécanisme que la page artisan (append dans **Disponibilite_Mois**).*
"""
)

ensure_demo_seed()
artisans: list = list(p_get("artisans", []))
opt_labels, opt_to_expert = disponibilite_expert_options(artisans)

st.subheader("Ajouter / corriger une ligne (pilote)")
if not opt_labels:
    st.warning("Aucun expert listé — chargez l’onglet **Experts**.")
else:
    c1, c2, c3 = st.columns(3)
    with c1:
        pick = st.selectbox(
            "Expert et corps de métier",
            options=opt_labels,
            help="Une ligne par type d’intervention pour distinguer les domaines couverts.",
        )
        expert_id = opt_to_expert[pick]
    with c2:
        mois = st.text_input("Mois (AAAA-MM)", value="2026-07")
    with c3:
        mode = st.selectbox(
            "Mode",
            options=["standard", "astreinte", "sur_rdv", "indisponible"],
            key="mode_proprio",
        )
    commentaire = st.text_input("Commentaire interne", "", key="com_proprio")

    verrou = mois_sous_verrouillage_artisan(mois) if re.fullmatch(r"\d{4}-\d{2}", mois.strip()) else True
    if verrou:
        accord = st.checkbox("Accord de l’artisan confirmé (obligatoire pour ce mois en fenêtre sensible)")
    else:
        accord = True

    if st.button("Enregistrer (propriétaire)", type="primary"):
        if not re.fullmatch(r"\d{4}-\d{2}", mois.strip()):
            st.error("Format AAAA-MM requis.")
        elif verrou and not accord:
            st.error("Obtenez l’accord de l’artisan (case à cocher) pour ce mois.")
        else:
            ok, msg = append_disponibilite_mois_row(
                _REPO,
                dict(st.secrets),
                expert_id=expert_id,
                annee_mois=mois.strip(),
                mode=mode,
                commentaire_interne=commentaire,
            )
            if ok:
                st.success(msg)
            else:
                st.error(msg)

st.divider()
st.subheader("Vue réseau — Disponibilite_Mois")
sid = resolve_gsheet_id(_REPO, dict(st.secrets)).strip()
if not sid:
    st.info("**gsheet_id** manquant.")
else:
    try:
        import gspread

        info = get_service_account_info(_REPO, st.secrets)
        creds = credentials_for_sheets(info)
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(sid)
        ws = sh.worksheet("Disponibilite_Mois")
        rows = ws.get_all_records()
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(str(e))

st.divider()
st.caption(
    "Évolutions prévues : table **utilisateurs**, rattachement **expert_id** à la connexion, "
    "historique des notifications propriétaire ↔ artisan, et respect du **verrouillage J−30** côté moteur."
)
