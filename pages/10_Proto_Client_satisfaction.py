"""
Prototype client — satisfaction : grosses étoiles cliquables + NPS par boutons.
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
from sereno_core.proto_state import log_event, p_get, p_set
from sereno_core.proto_ui import (
    proto_page_start,
    proto_processing_pause,
    reassurance,
    render_interactive_stars,
    render_nps_buttons,
    step_indicator,
)

proto_page_start(
    title="Votre avis compte",
    subtitle="Quelques secondes — cela nous aide à améliorer le service.",
)
step_indicator(7, 7)

if not p_get("payment_done"):
    st.warning("Complétez d’abord l’étape **Paiement simulé**.")
    st.stop()

reassurance("Les réponses sont agrégées dans les tableaux de suivi (démo navigateur).")

stars = render_interactive_stars()
if stars < 1:
    st.caption("Touchez une **étoile** pour noter de 1 à 5.")

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
    if stars < 1:
        st.error("Merci de donner une **note en étoiles**.")
    elif nps is None:
        st.error("Merci de choisir une note **NPS** (0 à 10).")
    else:
        with proto_processing_pause():
            p_set("satisfaction_stars", stars)
            p_set("satisfaction_nps", nps)
            p_set("satisfaction_comment", (comment or "").strip())
            ut = p_get("urgence_type")
            log_event(
                "satisfaction",
                session_id=p_get("session_id"),
                stars=stars,
                nps=nps,
                commentaire=((comment or "").strip()[:500]),
                urgence=ut,
                type_intervention=URGENCE_LABELS.get(ut, ut),
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
            f"<p>Écrire à : <strong><a href=\"{mail_href}\">jopai-sereno@hotmail.com</a></strong><br/>"
            "<small>Pilote : le message est adressé à la boîte de test opérationnelle ; "
            "une copie peut être proposée vers l’expert démo si une adresse est renseignée.</small></p>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<p style="font-size:0.95rem;"><a href="{mail_href}">Ouvrir ma messagerie</a></p>',
            unsafe_allow_html=True,
        )
        st.page_link("pages/4_Proto_Client_accueil.py", label="→ Nouvelle demande", icon="🏠")

