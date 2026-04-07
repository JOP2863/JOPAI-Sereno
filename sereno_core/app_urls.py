"""URLs publiques SÉRÉNO (QR, liens profonds) — surcharges via secrets Streamlit."""

from __future__ import annotations

from typing import Any, Mapping


def _secrets_dict() -> Mapping[str, Any]:
    try:
        import streamlit as st

        return dict(st.secrets)
    except Exception:
        return {}


def streamlit_app_base_url() -> str:
    """Base sans slash final (ex. https://jopai-sereno.streamlit.app)."""
    s = _secrets_dict()
    for k in ("streamlit_app_url", "sereno_app_url", "public_app_url"):
        v = (s.get(k) or "").strip()
        if v:
            return v.rstrip("/")
    return "https://jopai-sereno.streamlit.app"


def client_urgency_entry_url() -> str:
    """
    Lien cible du QR « parcours client » : écran « En quoi pouvons-nous vous aider ? ».

    Secrets optionnels (priorité) :
    - `sereno_client_entry_url` : URL complète (recommandé en prod).
    - Sinon : `streamlit_app_url` + chemin page Streamlit multipage.
    """
    s = _secrets_dict()
    full = (s.get("sereno_client_entry_url") or s.get("client_journey_url") or "").strip()
    if full:
        return full
    base = streamlit_app_base_url()
    # Fichier `pages/4_Proto_Client_accueil.py` → chemin URL Streamlit (voir doc multipage).
    path = (s.get("sereno_client_entry_path") or "/4_Proto_Client_accueil").strip()
    if not path.startswith("/"):
        path = "/" + path
    return f"{base}{path}"
