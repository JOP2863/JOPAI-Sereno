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
    sync_session_sheet,
)
from sereno_core.proto_ui import proto_page_start, proto_processing_pause, reassurance, step_indicator
from sereno_core.urgence_ambiance import JOURNEY_TAGLINE

proto_page_start(
    title="En quoi pouvons-nous vous aider ?",
    subtitle="",
    show_urgence_ambiance=False,
    busy_overlay_use_assigned_expert=False,
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

st.markdown(
    """
<style>
/* Accueil urgence : boutons pleine largeur du bloc, hauteur homogène */
div.sereno-urgence-buttons button[data-testid="baseButton-primary"] {
    min-height: 2.75rem;
    width: 100%;
}
</style>
""",
    unsafe_allow_html=True,
)

st.divider()
st.markdown("### Choisissez votre situation")

_fcol, _ = st.columns([0.68, 0.32])
with _fcol:
    st.markdown('<div class="sereno-urgence-buttons">', unsafe_allow_html=True)
    for code, label in URGENCE_LABELS.items():
        if st.button(label, key=f"urg_{code}", type="primary", use_container_width=True):
            with proto_processing_pause():
                clear_client_branch_after_urgence_change()
                new_session_id()
                p_set("urgence_type", code)
                log_event("urgence_choisie", urgence=code, session_id=p_get("session_id"))
                sync_session_sheet({"type_code": code, "statut": "URGENCE_CHOISIE"})
                st.switch_page("pages/5_Proto_Client_informations.py")
    st.markdown("</div>", unsafe_allow_html=True)
