"""
Prototype client — session visio (aperçu opérationnel léger + lien salle).
"""

from __future__ import annotations

import re
import sys
from datetime import UTC, datetime
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import streamlit as st
import streamlit.components.v1 as components

from sereno_core.proto_state import (
    enforce_client_journey,
    journey_next_after_visio_done,
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
from sereno_core.visio_recording import daily_api_key_from_secrets, daily_stop_recording
from sereno_core.ui_labels import ui_label_on


def _secret_get(key: str) -> str:
    try:
        v = st.secrets.get(key)
        return str(v).strip() if v else ""
    except Exception:
        return ""

proto_page_start(
    title="Visio-assistance",
    subtitle="Échange vidéo avec l’expert.",
)
proto_nav_overlay_once("_sereno_overlay_visio")
step_indicator(5, 7)

enforce_client_journey(require_step=4)

if not p_get("assigned_expert"):
    st.stop()

ex = p_get("assigned_expert")
_visio_call = str(ex.get("prenom") or "").strip() or str(ex.get("nom") or "l’expert").strip()
_sid = str(p_get("session_id") or "DEMO")
_room = re.sub(r"[^a-zA-Z0-9]", "", f"Sereno{_sid}")[:48] or "SerenoDemo"
jitsi_url = f"https://meet.jit.si/{_room}#config.prejoinPageEnabled=false"
spec_url = f"https://visio.sereno.example/session/{_sid}"
_integrated = (
    _secret_get("daily_room_url")
    or _secret_get("DAILY_ROOM_URL")
    or _secret_get("twilio_video_room_url")
)

reassurance(
    f"Vous êtes en ligne avec **{_visio_call}**. "
    "Gardez le téléphone à portée de main au cas où la connexion saute."
)

if _integrated:
    if ui_label_on("visio_demo_warning"):
        st.success(
            "**Salle configurée (pilote) :** lien **Daily** ou **Twilio** lu depuis les secrets Streamlit — "
            "prévoir en production des **jetons** à durée courte générés côté serveur."
        )
    st.link_button(
        f"Démarrer la visio avec {_visio_call}",
        _integrated,
        type="primary",
    )
    if ui_label_on("visio_secondary_links"):
        with st.expander("Démo publique Jitsi (sans secrets)"):
            st.caption("Ne pas y partager d’infos sensibles.")
            st.link_button("Ouvrir Jitsi (nouvel onglet)", jitsi_url, type="secondary")
else:
    if ui_label_on("visio_demo_warning"):
        st.warning(
            "**Démonstration :** la salle Jitsi ci-dessous est **publique** (ne pas y partager d’infos sensibles en vrai usage). "
            "Pour brancher **Daily** ou **Twilio** sans code lourd : renseigner **`daily_room_url`** ou **`twilio_video_room_url`** "
            "dans `.streamlit/secrets.toml` (voir `config/streamlit-secrets.EXAMPLE.toml`)."
        )
    if ui_label_on("visio_secondary_links"):
        c1, c2 = st.columns(2)
        with c1:
            st.link_button("Ouvrir Jitsi (nouvel onglet)", jitsi_url, type="primary")
        with c2:
            st.link_button("Lien cible intégration (exemple)", spec_url, type="secondary")
    else:
        st.link_button(
            f"Démarrer la visio avec {_visio_call}",
            jitsi_url,
            type="primary",
        )

if ui_label_on("visio_in_page_iframe"):
    st.markdown("**Visio dans la page** (Jitsi — autoriser caméra / micro si le navigateur demande) :")
    if not _integrated:
        components.iframe(jitsi_url, height=440)
    else:
        st.caption(
            "Avec une salle Daily/Twilio en **nouvel onglet**, l’iframe Jitsi est masquée pour éviter deux salles concurrentes."
        )

if ui_label_on("visio_sdk_mock"):
    st.markdown("**Maquette réservée au produit final** (plein écran mobile, lampe torche, etc.) :")
    components.html(
        f"""
        <div style="height:120px;background:linear-gradient(180deg,#1a237e 0%,#0d1642 100%);color:#e8eaf6;
                    display:flex;flex-direction:column;align-items:center;justify-content:center;
                    font-family:Inter,Segoe UI,sans-serif;border-radius:12px;border:2px solid #3949ab;font-size:0.95rem;">
          Emplacement SDK visio natif (Daily / Twilio) · session <strong>{_sid}</strong>
        </div>
        """,
        height=140,
    )

mic = True
torch = False
if ui_label_on("visio_demo_toggles"):
    c1, c2, c3 = st.columns(3)
    with c1:
        mic = st.toggle("Micro activé (démo)", value=True)
    with c2:
        torch = st.toggle("Lampe torche (démo)", value=False)
    with c3:
        st.caption("Les interrupteurs sont **factices** ici ; ils montreront l’UX cible sur mobile.")

if ui_label_on("visio_urls_box"):
    st.code(f"Jitsi : {jitsi_url}\nCible prod : {spec_url}", language="text")

c1, c2 = st.columns(2)
with c1:
    if st.button("← Retour file d’attente", type="secondary"):
        st.switch_page("pages/7_Proto_Client_file_visio.py")
with c2:
    if st.button("Terminer la visio", type="primary"):
        with proto_processing_pause():
            p_set("visio_done", True)
            p_set("visio_demo_mic", mic)
            p_set("visio_demo_torch", torch)
            log_event("visio_fin", session_id=p_get("session_id"))
            _room_url = (_integrated or jitsi_url).strip()
            _fin = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
            sync_session_sheet(
                {
                    "fin_visio": _fin,
                    "room_url": _room_url,
                    "type_code": p_get("urgence_type"),
                    "statut": "VISIO_TERMINEE",
                }
            )

            # Stop recording Daily si démarré (optionnel)
            try:
                api_key = daily_api_key_from_secrets(dict(st.secrets))
                if api_key and ".daily.co/" in _room_url:
                    ok_stop, _data = daily_stop_recording(api_key=api_key, room_url=_room_url)
                    if ok_stop:
                        sync_session_sheet({"statut": "VISIO_TERMINEE_RECORDING_STOP"})
            except Exception:
                pass

            _nxt = journey_next_after_visio_done()
            if _nxt.endswith("Proto_Client_paiement.py"):
                st.session_state["_sereno_overlay_paiement"] = True
            st.switch_page(_nxt)
