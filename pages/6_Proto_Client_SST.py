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

from sereno_core.proto_checklists import CHECKLISTS, URGENCE_LABELS
from sereno_core.proto_state import enforce_client_journey, log_event, p_get, p_set, sync_session_sheet
from sereno_core.proto_ui import proto_page_start, reassurance, step_indicator

proto_page_start(
    title="Sécurité avant la visio",
    subtitle="Chaque point compte : lisez, puis confirmez par un geste clair.",
)
step_indicator(3, 7)

enforce_client_journey(require_step=2)

ut = p_get("urgence_type")
if not ut:
    st.stop()

items = CHECKLISTS.get(ut, [])

st.markdown(
    "<div class='sereno-sst-reassure'><strong>Rassurance :</strong> ces étapes vous protègent "
    "vous et l’expert. En cas de danger immédiat (incendie, gaz fort, blessure), "
    "<strong>contactez les secours</strong> avant toute visio.</div>",
    unsafe_allow_html=True,
)

reassurance(
    f"**{URGENCE_LABELS.get(ut, ut)}** — validez **chaque** point ci-dessous pour continuer."
)

all_ok = True
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
            p_set(key_done, True)
            st.rerun()

st.divider()

# Première complétion : passage automatique. Retour depuis la file : même écran, bouton manuel.
was_complete = bool(p_get("_sst_mark_complete", False))
if items and all_ok:
    if not was_complete:
        p_set("_sst_mark_complete", True)
        p_set("sst_validated", True)
        log_event("sst_validee", session_id=p_get("session_id"), urgence=ut)
        sync_session_sheet({"type_code": ut, "statut": "SST_VALIDE"})
        st.switch_page("pages/7_Proto_Client_file_visio.py")
    elif st.button("Continuer vers la mise en relation", type="primary", use_container_width=True):
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
    st.caption("Validez **tous** les points sécurité pour passer à la suite.")
