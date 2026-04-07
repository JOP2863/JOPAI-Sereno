"""
SÉRÉNO — point d’entrée Streamlit.
Lancer : streamlit run Home.py
"""

import streamlit as st

st.set_page_config(page_title="SÉRÉNO", page_icon="🔧", layout="wide")

st.title("SÉRÉNO — JOPAI BTP")
st.markdown(
    "Prototype **dashboard expert / artisans** et outils internes. "
    "Ouvrez le **menu latéral** (icône **≡** en haut à gauche si la barre est repliée), "
    "puis choisissez **Tests connexions**."
)
st.info(
    "Les secrets (Sheets, GCP, clés API) sont dans `.streamlit/secrets.toml` "
    "et les fichiers JSON — **non versionnés** par Git."
)
