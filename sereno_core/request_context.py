"""
Accès “best-effort” au contexte requête Streamlit (headers) pour extraire des infos utiles.

Important : selon l’hébergement, l’IP visible peut être celle du proxy.
On essaye plusieurs headers (X-Forwarded-For, etc.) quand disponibles.
"""

from __future__ import annotations

from typing import Any

import streamlit as st


def _headers() -> dict[str, str]:
    # Streamlit récent expose `st.context.headers` (Mapping[str, str])
    try:
        h = getattr(st, "context", None)
        hdrs = getattr(h, "headers", None) if h is not None else None
        if hdrs:
            return {str(k).lower(): str(v) for k, v in dict(hdrs).items()}
    except Exception:
        pass
    return {}


def _first_ip_from_xff(xff: str) -> str:
    # "client, proxy1, proxy2" → garder le premier
    parts = [p.strip() for p in str(xff or "").split(",") if p.strip()]
    return parts[0] if parts else ""


def get_user_ip() -> str:
    """
    Retourne une IP (string) si détectable, sinon "".
    """
    h = _headers()
    if not h:
        return ""

    # Ordre de préférence (CDN / reverse proxy usuels)
    candidates: list[Any] = [
        h.get("cf-connecting-ip"),
        h.get("x-real-ip"),
        _first_ip_from_xff(h.get("x-forwarded-for", "")),
        h.get("x-client-ip"),
        h.get("fastly-client-ip"),
        h.get("true-client-ip"),
    ]
    for c in candidates:
        ip = str(c or "").strip()
        if ip:
            return ip
    return ""

