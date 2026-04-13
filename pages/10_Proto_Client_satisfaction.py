"""
Prototype client — satisfaction : **NPS** uniquement (0–10) + commentaire libre.
"""

from __future__ import annotations

import sys
from pathlib import Path
from urllib.parse import quote

_REPO = Path(__file__).resolve().parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import streamlit as st

from sereno_core.proto_checklists import URGENCE_LABELS
from sereno_core.proto_state import (
    enforce_client_journey,
    journey_nps_active,
    journey_payment_active,
    log_event,
    p_get,
    p_set,
    sync_session_sheet,
)
from sereno_core.proto_ui import (
    proto_page_start,
    proto_processing_pause,
    render_nps_buttons,
    step_indicator,
)

proto_page_start(
    title="Votre avis compte",
    subtitle="Quelques secondes — cela nous aide à améliorer le service.",
)
step_indicator(7, 7)

enforce_client_journey(require_step=7)

if not journey_nps_active():
    st.switch_page("pages/4_Proto_Client_accueil.py")

if journey_payment_active() and not p_get("payment_done"):
    st.stop()

nps = render_nps_buttons()
if nps is None:
    st.caption("Choisissez une note **NPS de 0 à 10** sur l’échelle colorée ci-dessous.")

ccom, _ = st.columns([0.72, 0.28])
with ccom:
    comment = st.text_area(
        "Commentaire libre (optionnel)",
        placeholder="Ex. Très rassurant, j’ai compris quoi couper en attendant le plombier.",
        height=120,
        max_chars=800,
    )

if st.button("Envoyer mon avis", type="primary"):
    if nps is None:
        st.error("Merci de choisir une note **NPS** (0 à 10).")
    else:
        with proto_processing_pause():
            p_set("satisfaction_nps", nps)
            p_set("satisfaction_comment", (comment or "").strip())
            ut = p_get("urgence_type")
            log_event(
                "satisfaction",
                session_id=p_get("session_id"),
                nps=nps,
                commentaire=((comment or "").strip()[:500]),
                urgence=ut,
                type_intervention=URGENCE_LABELS.get(ut, ut),
            )
            _cmt = (comment or "").strip()
            _notes = f"NPS={nps}"
            if _cmt:
                _notes += f" | {_cmt[:400]}"
            sync_session_sheet(
                {
                    "notes_cloture": _notes,
                    "type_code": ut,
                    "statut": "CLOTUREE_AVIS",
                }
            )
        ex = p_get("assigned_expert") or {}
        ex_mail = str(ex.get("email") or "").strip()
        cc = f"&cc={quote(ex_mail)}" if ex_mail else ""
        sid = str(p_get("session_id") or "—")
        prenom = str(p_get("client_prenom") or "—").strip()
        tel = str(p_get("client_tel") or "—").strip()
        cemail = str(p_get("client_email") or "").strip()
        subj = quote(f"SÉRÉNO — Contact [session {sid}] — {prenom}")
        body_lines = [
            "Bonjour,",
            "",
            f"Référence demande (session) : {sid}",
            f"Pseudo / prénom indiqué : {prenom}",
            f"Numéro de téléphone indiqué : {tel}",
        ]
        if cemail:
            body_lines.append(f"E-mail indiqué : {cemail}")
            body_lines.append(f"Lien pour écrire à l’utilisateur : mailto:{cemail}")
        body_lines.extend(
            [
                "",
                "Compte-rendu d’intervention (synthèse PDF à venir : parcours complet, visio, pièces jointes) :",
                f"https://jopai-sereno.streamlit.app/ — emplacement futur CR session {sid} (pilote).",
                "",
                "(Complétez librement ce message.)",
            ]
        )
        body = quote("\n".join(body_lines))
        # Pilote : libellé public jopai-sereno@hotmail.com ; message adressé à la boîte de test propriétaire.
        mail_href = f"mailto:jop28@hotmail.com?subject={subj}&body={body}{cc}"
        st.success(
            "Nous espérons que vous êtes **satisfait·e** de l’accompagnement. "
            "À tout moment, vous pouvez nous contacter via l’adresse ci-dessous."
        )
        st.markdown(
            f"<p>Écrire à : <strong><a href=\"{mail_href}\">jopai-sereno@hotmail.com</a></strong></p>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<p style="font-size:0.95rem;"><a href="{mail_href}">Ouvrir ma messagerie</a></p>',
            unsafe_allow_html=True,
        )
        st.page_link("pages/4_Proto_Client_accueil.py", label="→ Nouvelle demande", icon="🏠")

