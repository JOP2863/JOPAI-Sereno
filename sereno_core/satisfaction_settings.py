"""
Réglage global de mesure de satisfaction client (propriétaire) :
- étoiles (1–5) par défaut
- NPS (0–10)

Stocké dans l’onglet Google Sheets **Config**.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit as st

from sereno_core.config_kv import config_upsert_pairs, read_config_kv_cached, resolve_gsheet_id_from_secrets


MODE_STARS = "stars"
MODE_NPS = "nps"

KEY_MODE = "SERENO_SATISFACTION_MODE"


def satisfaction_mode() -> str:
    """Mode effectif: stars | nps (défaut: stars)."""
    repo = Path(__file__).resolve().parent.parent
    try:
        secrets = dict(st.secrets)
    except Exception:
        secrets = {}
    gsid = resolve_gsheet_id_from_secrets(repo, secrets)
    kv = read_config_kv_cached(gsid) if gsid else None
    mode = str((kv or {}).get(KEY_MODE, "")).strip().lower()
    return MODE_NPS if mode == MODE_NPS else MODE_STARS


def persist_satisfaction_mode(repo_root: Path, secrets: Any, *, mode: str) -> tuple[bool, str]:
    m = str(mode or "").strip().lower()
    if m not in (MODE_STARS, MODE_NPS):
        m = MODE_STARS
    return config_upsert_pairs(repo_root, secrets, pairs=[(KEY_MODE, m)])

