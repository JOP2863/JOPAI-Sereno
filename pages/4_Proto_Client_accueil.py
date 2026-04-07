"""
Prototype client — écran d’accueil : choix du type d’urgence (5 boutons, une colonne).
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import streamlit as st

from sereno_core.proto_checklists import URGENCE_LABELS
from sereno_core.proto_state import (
    clear_client_branch_after_urgence_change,
    log_event,
    new_session_id,
    p_get,
    p_set,
    reset_client_journey,
    sync_session_sheet,
)
from sereno_core.proto_ui import proto_page_start, reassurance, step_indicator
from sereno_core.urgence_ambiance import JOURNEY_TAGLINE

proto_page_start(
    title="En quoi pouvons-nous vous aider ?",
    subtitle="",
    show_urgence_ambiance=False,
)
st.markdown(
    f"""
<div style="font-size:1.28rem;font-weight:700;color:#003366;line-height:1.5;margin:0.4rem 0 1rem 0;
border-left:5px solid #003366;padding:14px 18px;background:linear-gradient(90deg,#e8f1fa 0%,#f7fafc 100%);
border-radius:10px;box-shadow:0 2px 10px rgba(0,51,102,0.08);">
{JOURNEY_TAGLINE}
</div>
""",
    unsafe_allow_html=True,
)
step_indicator(1, 7)
reassurance(
    "Vous êtes en sécurité ici : pas d’engagement immédiat, aucun paiement réel sur cette démonstration. "
    "Réponse humaine d’un expert du bâtiment."
)

with st.expander("Recommencer le parcours depuis zéro"):
    if st.button("Réinitialiser le parcours", type="secondary"):
        reset_client_journey()
        st.rerun()

st.divider()
st.markdown("### Choisissez votre situation")

for code, label in URGENCE_LABELS.items():
    if st.button(label, key=f"urg_{code}", type="primary", use_container_width=True):
        if not p_get("session_id"):
            new_session_id()
        clear_client_branch_after_urgence_change()
        p_set("urgence_type", code)
        log_event("urgence_choisie", urgence=code, session_id=p_get("session_id"))
        sync_session_sheet({"type_code": code, "statut": "URGENCE_CHOISIE"})
        st.switch_page("pages/5_Proto_Client_informations.py")
