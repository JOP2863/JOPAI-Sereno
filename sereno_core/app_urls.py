"""URLs publiques SÉRÉNO (QR, liens profonds) — surcharges via secrets Streamlit."""

from __future__ import annotations

from typing import Any, Mapping

# Paramètre d’URL pour ouvrir l’accueil urgence client depuis la racine (fiable avec dossier
# `pages/` + `st.navigation`, cf. Streamlit : cold start sur un sous-chemin → « Page not found »).
CLIENT_URGENCE_QUERY_KEY = "client_urgence"


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
    - `sereno_client_entry_url` : URL complète (recommandé si besoin d’une URL fixe hors QR).
    - Sinon : racine de l’app + `?client_urgence=1` (déclenché dans `Home.py` via `st.switch_page`).
    - Ancien mode chemin relatif : `sereno_client_entry_path` (ex. `/Proto_Client_accueil`) si vous
      définissez `sereno_client_entry_use_path = true` dans les secrets (déconseillé sans test).
    """
    s = _secrets_dict()
    full = (s.get("sereno_client_entry_url") or s.get("client_journey_url") or "").strip()
    if full:
        return full
    base = streamlit_app_base_url()
    use_path = str(s.get("sereno_client_entry_use_path") or "").strip().lower() in (
        "1",
        "true",
        "oui",
        "yes",
    )
    if use_path:
        path = (s.get("sereno_client_entry_path") or "/Proto_Client_accueil").strip()
        if not path.startswith("/"):
            path = "/" + path
        return f"{base}{path}"
    return f"{base}/?{CLIENT_URGENCE_QUERY_KEY}=1"
