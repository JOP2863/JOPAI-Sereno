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

from sereno_core.proto_state import log_event, p_get, p_set, sync_session_sheet

def _secret_get(key: str) -> str:
    try:
        v = st.secrets.get(key)
        return str(v).strip() if v else ""
    except Exception:
        return ""
from sereno_core.proto_ui import proto_page_start, reassurance, step_indicator

proto_page_start(
    title="Visio-assistance",
    subtitle="Salle de session : aperçu **réel** (Jitsi Meet, démo) + lien technique pour intégration Daily / Twilio.",
)
step_indicator(5, 7)

if not p_get("assigned_expert"):
    st.warning("Passez d’abord par la **mise en relation**.")
    st.stop()

ex = p_get("assigned_expert")
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
    f"Vous êtes en ligne avec **{ex.get('nom', 'l’expert')}**. "
    "Gardez le téléphone à portée de main au cas où la connexion saute."
)

if _integrated:
    st.success(
        "**Salle configurée (pilote) :** lien **Daily** ou **Twilio** lu depuis les secrets Streamlit — "
        "prévoir en production des **jetons** à durée courte générés côté serveur."
    )
    st.link_button("Ouvrir la salle (Daily / Twilio — secrets)", _integrated, type="primary")
    with st.expander("Démo publique Jitsi (sans secrets)"):
        st.caption("Ne pas y partager d’infos sensibles.")
        st.link_button("Ouvrir Jitsi (nouvel onglet)", jitsi_url, type="secondary")
else:
    st.warning(
        "**Démonstration :** la salle Jitsi ci-dessous est **publique** (ne pas y partager d’infos sensibles en vrai usage). "
        "Pour brancher **Daily** ou **Twilio** sans code lourd : renseigner **`daily_room_url`** ou **`twilio_video_room_url`** "
        "dans `.streamlit/secrets.toml` (voir `config/streamlit-secrets.EXAMPLE.toml`)."
    )
    c1, c2 = st.columns(2)
    with c1:
        st.link_button("Ouvrir Jitsi (nouvel onglet)", jitsi_url, type="primary")
    with c2:
        st.link_button("Lien cible intégration (exemple)", spec_url, type="secondary")

st.markdown("**Visio dans la page** (Jitsi — autoriser caméra / micro si le navigateur demande) :")
if not _integrated:
    components.iframe(jitsi_url, height=440)
else:
    st.caption("Avec une salle Daily/Twilio en **nouvel onglet**, l’iframe Jitsi est masquée pour éviter deux salles concurrentes.")

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

c1, c2, c3 = st.columns(3)
with c1:
    mic = st.toggle("Micro activé (démo)", value=True)
with c2:
    torch = st.toggle("Lampe torche (démo)", value=False)
with c3:
    st.caption("Les interrupteurs sont **factices** ici ; ils montreront l’UX cible sur mobile.")

st.code(f"Jitsi : {jitsi_url}\nCible prod : {spec_url}", language="text")

c1, c2 = st.columns(2)
with c1:
    if st.button("← Retour file d’attente", type="secondary"):
        st.switch_page("pages/7_Proto_Client_file_visio.py")
with c2:
    if st.button("J’ai terminé la visio", type="primary"):
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
        st.switch_page("pages/9_Proto_Client_paiement.py")
