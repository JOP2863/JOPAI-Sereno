"""
Réglages globaux d’expérience (propriétaire) stockés dans l’onglet **Config**.
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from sereno_core.config_kv import config_upsert_pairs, invalidate_config_kv_cache, read_config_kv_cached, resolve_gsheet_id_from_secrets
from sereno_core.sst_ack_settings import KEY_SST_SINGLE_ACK_BUTTON, sst_single_ack_button

KEY_SHOW_WATERMARK = "SERENO_UI_SHOW_WATERMARK"
KEY_SHOW_BRAND_SUFFIX = "SERENO_UI_SHOW_BRAND_SUFFIX"
KEY_SHOW_GUIDE_PAGE = "SERENO_UI_SHOW_GUIDE_PAGE"


def _as_bool(v: str) -> bool:
    s = str(v or "").strip().lower()
    return s in ("1", "true", "vrai", "oui", "yes", "on", "o")


def _kv() -> dict[str, str]:
    repo = Path(__file__).resolve().parent.parent
    try:
        secrets = dict(st.secrets)
    except Exception:
        secrets = {}
    gsid = resolve_gsheet_id_from_secrets(repo, secrets)
    kv = read_config_kv_cached(gsid) if gsid else None
    return dict(kv or {})


def show_watermark() -> bool:
    """Filigrane “site en construction / démonstration” (défaut : False)."""
    kv = _kv()
    return _as_bool(kv.get(KEY_SHOW_WATERMARK, "false"))


def show_brand_suffix_in_titles() -> bool:
    """Suffixe 'by JOPAI© SÉRÉNO' dans les titres (défaut : False)."""
    kv = _kv()
    return _as_bool(kv.get(KEY_SHOW_BRAND_SUFFIX, "false"))


def show_guide_page() -> bool:
    """Page 'Guide du parcours' visible dans le menu client (défaut : False)."""
    kv = _kv()
    return _as_bool(kv.get(KEY_SHOW_GUIDE_PAGE, "false"))


def persist_experience_flags(
    repo_root: Path,
    secrets: object,
    *,
    watermark: bool,
    brand_suffix: bool,
    guide_page: bool,
    sst_single_ack: bool = True,
) -> tuple[bool, str]:
    ok, err = config_upsert_pairs(
        repo_root,
        secrets,
        pairs=[
            (KEY_SHOW_WATERMARK, "true" if watermark else "false"),
            (KEY_SHOW_BRAND_SUFFIX, "true" if brand_suffix else "false"),
            (KEY_SHOW_GUIDE_PAGE, "true" if guide_page else "false"),
            (KEY_SST_SINGLE_ACK_BUTTON, "true" if sst_single_ack else "false"),
        ],
    )
    if ok:
        invalidate_config_kv_cache()
    return ok, err

