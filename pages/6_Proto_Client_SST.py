"""
Prototype client — checklist SST avant visio (gros boutons, ton alerte + réassurance).
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import streamlit as st

from sereno_core.proto_checklists import CHECKLISTS
from sereno_core.proto_state import (
    enforce_client_journey,
    journey_sst_active,
    log_event,
    p_get,
    p_set,
    sync_session_sheet,
    urgence_display_label,
)
from sereno_core.sst_ack_settings import sst_single_ack_button
from sereno_core.proto_ui import proto_page_start, proto_processing_pause, reassurance, step_indicator
from sereno_core.ui_labels import ui_label_on

proto_page_start(
    title="Sécurité avant la visio",
    subtitle="Chaque point compte : lisez, puis confirmez par un geste clair.",
)
step_indicator(3, 7)

enforce_client_journey(require_step=2)

if not journey_sst_active():
    st.switch_page("pages/7_Proto_Client_file_visio.py")

ut = p_get("urgence_type")
if not ut:
    st.stop()

items = CHECKLISTS.get(ut, [])

if ui_label_on("sst_rassurance_html"):
    st.markdown(
        "<div class='sereno-sst-reassure'><strong>Rassurance :</strong> ces étapes vous protègent "
        "vous et notre expert. En cas de danger immédiat (incendie, gaz fort, blessure), "
        "<strong>contactez les secours</strong> avant toute visio.</div>",
        unsafe_allow_html=True,
    )

if ui_label_on("sst_reassurance_block"):
    reassurance(
        f"**{urgence_display_label(ut)}** — validez **chaque** point ci-dessous pour continuer."
    )

_one_btn = sst_single_ack_button()
all_ok = True

if items and _one_btn:
    for i, line in enumerate(items):
        st.markdown(
            f"<div class='sereno-sst-alert'><strong>Point sécurité {i + 1} / {len(items)}</strong><br/>{line}</div>",
            unsafe_allow_html=True,
        )
    all_ok = all(bool(p_get(f"sst_line_{ut}_{j}")) for j in range(len(items)))
    if not all_ok:
        if st.button(
            "✓ Oui — j’ai lu, compris et appliqué toutes les consignes ci-dessus",
            key=f"sst_yes_all_{ut}",
            type="primary",
            use_container_width=True,
        ):
            with proto_processing_pause():
                for j in range(len(items)):
                    p_set(f"sst_line_{ut}_{j}", True)
            st.rerun()
    else:
        st.success("Toutes les consignes sécurité sont validées.")
elif items:
    for i, line in enumerate(items):
        key_done = f"sst_line_{ut}_{i}"
        done = bool(p_get(key_done))
        st.markdown(
            f"<div class='sereno-sst-alert'><strong>Point sécurité {i + 1} / {len(items)}</strong><br/>{line}</div>",
            unsafe_allow_html=True,
        )
        if done:
            st.success("Validé pour ce point.")
        else:
            all_ok = False
            if st.button(
                "✓ Oui — j’ai lu, compris et appliqué ce qui est à ma portée",
                key=f"sst_yes_{ut}_{i}",
                type="primary",
                use_container_width=True,
            ):
                with proto_processing_pause():
                    p_set(key_done, True)
                st.rerun()

st.divider()

# Première complétion : passage automatique. Retour depuis la file : même écran, bouton manuel.
was_complete = bool(p_get("_sst_mark_complete", False))
if items and all_ok:
    if not was_complete:
        with proto_processing_pause():
            p_set("_sst_mark_complete", True)
            p_set("sst_validated", True)
            log_event("sst_validee", session_id=p_get("session_id"), urgence=ut)
            sync_session_sheet({"type_code": ut, "statut": "SST_VALIDE"})
            st.switch_page("pages/7_Proto_Client_file_visio.py")
    elif st.button("Continuer vers la mise en relation", type="primary", use_container_width=True):
        with proto_processing_pause():
            p_set("sst_validated", True)
            sync_session_sheet({"type_code": ut, "statut": "SST_VALIDE"})
            st.switch_page("pages/7_Proto_Client_file_visio.py")
elif items and not all_ok:
    p_set("_sst_mark_complete", False)

c1, _ = st.columns(2)
with c1:
    if st.button("← Retour", type="secondary"):
        st.switch_page("pages/5_Proto_Client_informations.py")

if items and not all_ok:
    if ui_label_on("sst_footer_caption"):
        st.caption("Validez **tous** les points sécurité pour passer à la suite.")
