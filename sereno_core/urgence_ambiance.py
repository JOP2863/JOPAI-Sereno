"""Fond pastel et repère visuel selon le type d’urgence (parcours client prototype)."""

from __future__ import annotations

import base64
from pathlib import Path

import streamlit as st

from sereno_core.jopai_brand_html import page_title_h1_html
from sereno_core.proto_checklists import URGENCE_LABELS

# Pastels encore plus lisibles (~30–40 % plus soutenus)
_URGENCE_STYLE: dict[str, dict[str, str]] = {
    "EAU": {
        "gradient": "linear-gradient(180deg, #7eb0de 0%, #b2d0ef 36%, #dce8f4 100%)",
        "chip_bg": "#1565c0",
        "chip_border": "#0d47a1",
    },
    "ELEC": {
        "gradient": "linear-gradient(180deg, #ffb347 0%, #ffd088 36%, #f0e8df 100%)",
        "chip_bg": "#ef6c00",
        "chip_border": "#e65100",
    },
    "GAZ": {
        "gradient": "linear-gradient(180deg, #ff8a90 0%, #ffc0c4 36%, #ebe4e4 100%)",
        "chip_bg": "#c62828",
        "chip_border": "#b71c1c",
    },
    "CHAUFF": {
        "gradient": "linear-gradient(180deg, #7ab8bc 0%, #aed9d6 36%, #dcecea 100%)",
        "chip_bg": "#00695c",
        "chip_border": "#004d40",
    },
    "SERR": {
        "gradient": "linear-gradient(180deg, #98aab4 0%, #c5d0d6 36%, #e2e6e9 100%)",
        "chip_bg": "#455a64",
        "chip_border": "#37474f",
    },
}

_REPO = Path(__file__).resolve().parent.parent
_URGENCE_IMG_DIRS = (
    _REPO / "assets" / "urgence",
    _REPO / "logo" / "urgence",
)

_GCS_ICON_STEM: dict[str, str] = {
    "EAU": "JOPAI-icone-EAU",
    "ELEC": "JOPAI-icone-ELEC",
    "GAZ": "JOPAI-icone-GAZ",
    "CHAUFF": "JOPAI-icone-CHAUFFAGE",
    "SERR": "JOPAI-icone-SERRURERIE",
}


def _load_local_urgence_icon(ut: str) -> tuple[bytes, str] | None:
    for d in _URGENCE_IMG_DIRS:
        for ext, mime in ((".png", "image/png"), (".webp", "image/webp"), (".jpg", "image/jpeg")):
            p = d / f"{ut}{ext}"
            if p.is_file():
                try:
                    return (p.read_bytes(), mime)
                except OSError:
                    continue
    return None


def _load_gcs_urgence_icon(ut: str) -> tuple[bytes, str] | None:
    stem = _GCS_ICON_STEM.get(ut)
    if not stem:
        return None
    cache_key = f"_sereno_urg_icon_gcs_tuple_{ut}"
    if cache_key in st.session_state:
        hit = st.session_state[cache_key]
        if hit is False:
            return None
        return hit  # type: ignore[return-value]
    try:
        from google.cloud import storage

        from sereno_core.gcp_credentials import credentials_for_gcp_clients, get_service_account_info

        bucket_name = (st.secrets.get("gcs_bucket_name") or "").strip()
        if not bucket_name:
            st.session_state[cache_key] = False
            return None
        prefix = (st.secrets.get("gcs_icones_prefix") or "icones").strip().strip("/")
        info = get_service_account_info(_REPO, st.secrets)
        creds = credentials_for_gcp_clients(info)
        client = storage.Client(credentials=creds, project=info.get("project_id"))
        bucket = client.bucket(bucket_name)
        data: bytes | None = None
        mime = "image/jpeg"
        for ext in (".jpg", ".jpeg", ".png", ".webp"):
            blob = bucket.blob(f"{prefix}/{stem}{ext}")
            try:
                data = blob.download_as_bytes()
            except Exception:
                data = None
            if data:
                if ext == ".png":
                    mime = "image/png"
                elif ext == ".webp":
                    mime = "image/webp"
                break
        if not data:
            st.session_state[cache_key] = False
            return None
        tup = (data, mime)
        st.session_state[cache_key] = tup
        return tup
    except Exception:
        st.session_state[cache_key] = False
        return None


def get_urgence_icon_bytes(ut: str) -> tuple[bytes, str] | None:
    """
    Icône urgence pour affichage Streamlit (`st.image`) ou HTML : (octets, mime).
    Ordre : fichiers locaux `assets/urgence/{CODE}.*`, puis GCS `icones/JOPAI-icone-*.jpg`.
    """
    loc = _load_local_urgence_icon(ut)
    if loc:
        return loc
    return _load_gcs_urgence_icon(ut)


JOURNEY_TAGLINE = "Un seul geste suffit. Nous vous guidons ensuite, étape par étape."


def render_proto_header_with_urgence(
    *,
    title: str,
    subtitle: str = "",
    ut: str | None,
    show_journey_tagline: bool = True,
    title_brand_suffix: bool = True,
) -> None:
    """
    Titre + sous-titre + accroche parcours à gauche ; à droite **icône urgence** + **logo SÉRÉNO**
    (même taille, bords arrondis), alignés en **haut** avec le titre.
    """
    if not ut or ut not in _URGENCE_STYLE:
        st.markdown(
            page_title_h1_html(title, brand_suffix=title_brand_suffix, show_sereno_suffix=not title_brand_suffix),
            unsafe_allow_html=True,
        )
        if subtitle:
            st.caption(subtitle)
        return
    stl = _URGENCE_STYLE[ut]
    try:
        left, right = st.columns([3.55, 1.45], vertical_alignment="top")
    except TypeError:
        left, right = st.columns([3.55, 1.45])
    with left:
        st.markdown(
            page_title_h1_html(title, brand_suffix=title_brand_suffix, show_sereno_suffix=not title_brand_suffix),
            unsafe_allow_html=True,
        )
        if subtitle:
            st.caption(subtitle)
        if show_journey_tagline:
            st.markdown(
                "<p style='font-size:1.14rem;font-weight:650;color:#0d395e;margin:0.55rem 0 1.35rem 0;"
                "line-height:1.45;border-left:4px solid #003366;padding:11px 15px;background:#e8f0f9;"
                "border-radius:9px;'>"
                f"{JOURNEY_TAGLINE}"
                "</p>",
                unsafe_allow_html=True,
            )
    with right:
        ib = get_urgence_icon_bytes(ut)
        try:
            from sereno_core.streamlit_theme import get_sereno_logo_bytes

            sb = get_sereno_logo_bytes()
        except Exception:
            sb = None

        def _data_url(b: bytes, mime: str) -> str:
            return f"data:{mime};base64,{base64.b64encode(b).decode('ascii')}"

        # Même taille visuelle pour urgence + SÉRÉNO, côte à côte (flex ; petits écrans : pas de wrap).
        chip_wrap = (
            "flex:0 0 auto;width:88px;height:88px;border-radius:14px;overflow:hidden;"
            "background:rgba(255,255,255,0.55);box-shadow:0 1px 6px rgba(0,51,102,0.12);"
            "display:flex;align-items:center;justify-content:center;"
        )
        img_tile = (
            "flex:0 0 auto;width:88px;height:88px;object-fit:contain;border-radius:14px;padding:4px;"
            "box-sizing:border-box;background:rgba(255,255,255,0.55);"
            "box-shadow:0 1px 6px rgba(0,51,102,0.12);"
        )

        parts: list[str] = []
        if ib:
            b0, m0 = ib
            parts.append(f"<img src='{_data_url(b0, m0)}' alt='' style='{img_tile}' />")
        else:
            short = ut[:4] if len(ut) > 4 else ut
            parts.append(
                f"<div style='{chip_wrap}'>"
                f"<span style='background:{stl['chip_bg']};color:#fff;font-weight:800;font-size:1.02rem;"
                f"padding:0.55rem 0.65rem;border-radius:12px;border:2px solid {stl['chip_border']};'>"
                f"{short}</span></div>"
            )
        if sb:
            b1, m1 = sb
            parts.append(f"<img src='{_data_url(b1, m1)}' alt='SÉRÉNO' style='{img_tile}' />")

        if parts:
            st.markdown(
                "<div class='sereno-header-dual-logos' style='display:flex;flex-direction:row;flex-wrap:nowrap;"
                "gap:10px;justify-content:flex-end;align-items:flex-start;margin-top:0.05rem;max-width:100%;'>"
                + "".join(parts)
                + "</div>",
                unsafe_allow_html=True,
            )


def inject_urgence_ambiance_css(ut: str | None) -> None:
    """Applique un fond pastel sur le conteneur central (~70 %) si un type d’urgence est choisi."""
    sel = (
        '[data-testid="stAppViewContainer"] section[data-testid="stMain"] div.block-container'
    )
    if not ut or ut not in _URGENCE_STYLE:
        st.markdown(
            f"""
            <style>
            {sel} {{
                background: transparent !important;
                box-shadow: none !important;
            }}
            .sereno-header-dual-logos {{
                overflow-x: auto;
                -webkit-overflow-scrolling: touch;
            }}
            </style>
            """,
            unsafe_allow_html=True,
        )
        return
    g = _URGENCE_STYLE[ut]["gradient"]
    st.markdown(
        f"""
        <style>
        {sel} {{
            background: {g} !important;
            border-radius: 14px;
            padding: 1.1rem 1.35rem 2rem 1.35rem !important;
            box-shadow: inset 0 0 0 1px rgba(0, 51, 102, 0.06);
        }}
        .sereno-header-dual-logos {{
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
