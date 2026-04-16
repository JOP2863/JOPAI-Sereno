"""
Accueil SÉRÉNO — outillage projet (menu **Projet**).
"""

from __future__ import annotations

import io

import streamlit as st

from sereno_core.streamlit_theme import inject_button_zoom_resilience_css

inject_button_zoom_resilience_css()

from sereno_core.app_urls import client_urgency_entry_url
from sereno_core.jopai_brand_html import page_title_h1_html
from sereno_core.projet_navigation_intro import COVER_INTRO_MARKDOWN, NAVIGATION_INTRO_MARKDOWN

st.markdown(page_title_h1_html("Accueil"), unsafe_allow_html=True)

st.markdown(COVER_INTRO_MARKDOWN)
st.markdown(NAVIGATION_INTRO_MARKDOWN)

CLIENT_ENTRY_URL = client_urgency_entry_url()

try:
    import qrcode

    qr = qrcode.QRCode(version=1, box_size=3, border=2)
    qr.add_data(CLIENT_ENTRY_URL)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#003366", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    st.image(buf.getvalue(), width=200, caption="Flashez pour ouvrir l’accueil urgence client")
except Exception:
    st.caption(
        f"Parcours client : **{CLIENT_ENTRY_URL}** (installez `qrcode[pil]` pour afficher le QR code)."
    )

with st.expander("Comment simuler « l’installation sur le téléphone » ?"):
    st.markdown(
        f"""
- **Parcours client direct :** ouvrir **[{CLIENT_ENTRY_URL}]({CLIENT_ENTRY_URL})** dans le **navigateur** du téléphone
  (Safari, Chrome) — vous arrivez sur **« En quoi pouvons-nous vous aider ? »** sans page intermédiaire inutile.
- **Application native (cible pilote) :** avec **Expo Go** sur le téléphone, un développeur peut publier un **QR code**
  ou un lien de développement pour charger le projet SÉRÉNO ; vous installez **Expo Go** depuis le store, puis vous scannez le QR.
- **Raccourci sur l’écran d’accueil :** sur iPhone ou Android, depuis le navigateur, menu « **Ajouter à l’écran d’accueil** »
  pour une icône qui relance la démo web en un clic (toujours sans store).
"""
    )
