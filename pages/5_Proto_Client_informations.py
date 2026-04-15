"""
Prototype client — collecte minimale d’informations (réassurance + contact).
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import streamlit as st

# Bandeau d’accroche : couleurs alignées sur les boutons d’accueil (eau = bleu, élec = orange, etc.)
_URG_BAND = {
    "EAU": ("#1565c0", "#e3f2fd", "#0d47a1"),
    "ELEC": ("#ef6c00", "#fff3e0", "#e65100"),
    "GAZ": ("#c62828", "#ffebee", "#b71c1c"),
    "CHAUFF": ("#00695c", "#e0f2f1", "#004d40"),
    "SERR": ("#455a64", "#eceff1", "#37474f"),
}
from sereno_core.proto_state import (
    enforce_client_journey,
    journey_next_after_infos,
    journey_sst_active,
    log_event,
    p_get,
    p_set,
    sync_session_sheet,
    urgence_display_label,
)
from sereno_core.proto_ui import proto_page_start, proto_processing_pause, reassurance, step_indicator
from sereno_core.ui_labels import ui_label_on

proto_page_start(
    title="Quelques informations utiles",
    subtitle="Ces données servent uniquement à vous recontacter pendant la session.",
)
step_indicator(2, 7)

enforce_client_journey(require_step=1)

ut = p_get("urgence_type")
if not ut:
    st.stop()

if ui_label_on("infos_urgence_reassurance"):
    reassurance(
        f"Urgence sélectionnée : **{urgence_display_label(ut)}**. "
        "Vous pourrez préciser le détail avec l’expert en visio."
    )

_accent, _bg, _text = _URG_BAND.get(ut, ("#003366", "#f4f7f9", "#003366"))
if ui_label_on("infos_consigne_band"):
    st.markdown(
        f"<div class='sereno-infos-panne-band' style='border-left-color:{_accent};background:{_bg};color:{_text};'>"
        f"<strong>Consignes pour votre situation ({urgence_display_label(ut)})</strong> — "
        "restez prudent·e : les prochaines étapes rappellent la sécurité avant d’ouvrir la visio.</div>",
        unsafe_allow_html=True,
    )

if ui_label_on("infos_phone_help"):
    st.markdown(
        "<div class='sereno-sst-reassure'>Indicatif <strong>+33</strong> prérempli : complétez avec votre numéro "
        "sans le 0 initial du portable français (ex. <strong>+33 6 12 34 56 78</strong>).</div>",
        unsafe_allow_html=True,
    )

with st.form("infos_client"):
    fp, _ = st.columns([0.5, 0.5])
    with fp:
        prenom = st.text_input("Prénom ou pseudo", value="JOP", max_chars=80)
    t1, t2 = st.columns([0.14, 0.86])
    with t1:
        st.text_input("Indicatif", value="+33", disabled=True, help="France métropolitaine")
    with t2:
        tel_suffix = st.text_input(
            "Numéro (sans répéter +33)",
            value="6 16 73 10 09",
            max_chars=32,
            help="Saisissez le reste du numéro ; le +33 est déjà pris en compte.",
        )
    email_opt = st.text_input(
        "E-mail (optionnel)",
        placeholder="exemple@mail.com — si vous préférez être recontacté par message",
        max_chars=120,
    )
    st.checkbox(
        "Je confirme avoir lu les consignes de prudence avant la visio (rappel à l’étape suivante).",
        value=True,
        key="confirm_prudence",
    )
    submitted = st.form_submit_button(
        "Continuer vers la sécurité" if journey_sst_active() else "Continuer",
        type="primary",
    )

if submitted:
    suffix = (tel_suffix or "").strip().replace(" ", "")
    # Google Sheets interprète souvent "+33 ..." comme un nombre (→ "33"). On force un texte stable.
    full_tel = f"+33{suffix}" if suffix else "+33"
    with proto_processing_pause():
        p_set("client_prenom", (prenom or "").strip() or "—")
        p_set("client_tel", full_tel)
        p_set("client_email", (email_opt or "").strip())
        log_event(
            "infos_client",
            session_id=p_get("session_id"),
            urgence=ut,
            type_intervention=urgence_display_label(ut),
            prenom=p_get("client_prenom"),
        )
        em = str(p_get("client_email") or "").strip()
        contact = str(p_get("client_tel") or "").strip()
        if em:
            contact = f"{contact} | {em}" if contact else em
        # Forcer texte dans Sheets si ça commence par "+" (sinon Sheets peut le convertir en nombre).
        if contact.startswith("+") and not contact.startswith("'"):
            contact = "'" + contact
        sync_session_sheet(
            {
                "user_pseudo": str(p_get("client_prenom") or ""),
                "user_contact": contact,
                "type_code": ut,
                "statut": "INFOS_SAISIES",
            }
        )
        st.switch_page(journey_next_after_infos())

if st.button("← Retour au choix du type"):
    st.switch_page("pages/4_Proto_Client_accueil.py")
