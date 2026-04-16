"""
Lecture de la préférence **SST** (un seul bouton de validation) dans l’onglet **Config**.

Module volontairement **léger** : les pages prototype peuvent l’importer sans dépendre du reste
de ``experience_settings`` (évite les échecs d’import ciblés sur une seule fonction).
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from sereno_core.config_kv import read_config_kv_cached, resolve_gsheet_id_from_secrets

KEY_SST_SINGLE_ACK_BUTTON = "SERENO_SST_SINGLE_ACK_BUTTON"


def _as_bool(v: str) -> bool:
    s = str(v or "").strip().lower()
    return s in ("1", "true", "vrai", "oui", "yes", "on", "o")


def sst_single_ack_button() -> bool:
    """SST : un seul bouton valide toutes les consignes d’un coup (défaut : True). Si False, un bouton par consigne."""
    repo = Path(__file__).resolve().parent.parent
    try:
        secrets = dict(st.secrets)
    except Exception:
        secrets = {}
    gsid = resolve_gsheet_id_from_secrets(repo, secrets)
    kv = read_config_kv_cached(gsid) if gsid else None
    return _as_bool((dict(kv or {}).get(KEY_SST_SINGLE_ACK_BUTTON, "true")))
