"""
Prototype client — étape paiement (forfait + saisie carte).
Validation locale (Luhn, date, CVC) ; dans ce pilote Streamlit, aucun encaissement réel.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import streamlit as st

from sereno_core.proto_helpers import STRIPE_TEST_CARD_SUCCESS, validate_card_fields
from sereno_core.proto_state import (
    append_paiement_sheet_row,
    enforce_client_journey,
    log_event,
    p_get,
    p_set,
    sync_session_sheet,
)
from sereno_core.proto_ui import (
    proto_nav_overlay_once,
    proto_page_start,
    proto_processing_pause,
    reassurance,
    step_indicator,
)

FORFAIT_EUR = 50

proto_page_start(
    title="Règlement de la session",
    subtitle=f"Montant de la session : **{FORFAIT_EUR} €**.",
)
proto_nav_overlay_once("_sereno_overlay_paiement")
step_indicator(6, 7)

enforce_client_journey(require_step=6)

if not p_get("visio_done"):
    st.stop()

reassurance(
    "Dans ce **pilote web**, la saisie reste **locale** au navigateur ; le numéro prérempli est une **carte de test** "
    "courante (Stripe **4242…**) pour valider les contrôles de formulaire."
)

st.info(
    "**Contrôles :** 13–19 chiffres, algorithme de Luhn, date d’expiration MM/YY future, CVC 3 ou 4 chiffres."
)

st.markdown(
    f"""
<div class='sereno-card'>
<strong>Récapitulatif</strong><br/>
Session : <code>{p_get("session_id", "—")}</code><br/>
Montant : <strong>{FORFAIT_EUR} €</strong> TTC (indicatif)<br/>
Statut : <em>Pilote — pas d’encaissement</em>
</div>
""",
    unsafe_allow_html=True,
)

fcol, _pad = st.columns([0.62, 0.38])
with fcol:
    with st.form("pay_fake"):
        nom = st.text_input("Nom sur la carte", value="TEST UTILISATEUR", max_chars=120)
        numero = st.text_input(
            "Numéro de carte",
            value=STRIPE_TEST_CARD_SUCCESS,
            help="Carte de test Stripe « succès » (pilote).",
        )
        e1, e2 = st.columns(2)
        with e1:
            expiry = st.text_input("Expiration MM/YY", value="12/30", max_chars=5)
        with e2:
            cvc = st.text_input("CVC", value="123", max_chars=4)
        ok = st.form_submit_button("Valider le paiement", type="primary")

if ok:
    ok_val, err = validate_card_fields(numero, expiry, cvc)
    if not ok_val:
        st.error(err)
    else:
        with proto_processing_pause():
            p_set("payment_done", True)
            p_set("payment_mode", "SIMULE")
            log_event(
                "paiement_simule",
                session_id=p_get("session_id"),
                montant_eur=FORFAIT_EUR,
                mode="SIMULE",
                carte_test=numero[:4] + "…",
            )
            sync_session_sheet(
                {
                    "prix_centimes_factures": str(int(FORFAIT_EUR * 100)),
                    "type_code": p_get("urgence_type"),
                    "statut": "PAIEMENT_PILOTE",
                }
            )
            append_paiement_sheet_row(
                montant_centimes=int(FORFAIT_EUR * 100),
                mode_paiement="SIMULE",
                statut="ENREGISTRE",
                notes="Parcours prototype Streamlit",
            )
            st.success("Paiement enregistré pour la session pilote. Merci !")
            st.switch_page("pages/10_Proto_Client_satisfaction.py")

if st.button("← Retour à la visio"):
    with proto_processing_pause():
        st.switch_page("pages/8_Proto_Client_visio.py")
