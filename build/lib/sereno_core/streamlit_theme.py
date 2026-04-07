"""
Styles globaux Streamlit SÉRÉNO : charte SÉRÉNO Core + footer JOPAI + logo (local ou GCS).
"""

from __future__ import annotations

import base64
from pathlib import Path

import streamlit as st

from sereno_core import design_tokens as dt

_LOGO_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _logo_html_from_bytes(data: bytes, mime: str, alt: str = "SÉRÉNO") -> str:
    b64 = base64.b64encode(data).decode("ascii")
    return (
        "<div class='jopai-page-logo-wrap'>"
        f"<img class='jopai-page-logo' src='data:{mime};base64,{b64}' alt='{alt}' />"
        "</div>"
    )


def _logo_from_local_dir(logo_dir: Path) -> str:
    if not logo_dir.is_dir():
        return ""
    candidates = sorted(
        p for p in logo_dir.iterdir() if p.is_file() and p.suffix.lower() in _LOGO_EXTENSIONS
    )
    for lp in candidates:
        try:
            mime = {
                ".png": "image/png",
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".webp": "image/webp",
            }.get(lp.suffix.lower(), "image/png")
            return _logo_html_from_bytes(lp.read_bytes(), mime)
        except OSError:
            continue
    return ""


def _logo_html_from_gcs(root: Path) -> str:
    """Objet attendu : `Logos/JOPAI-LogoSereno.jpg` (bucket `gcs_bucket_name`)."""
    try:
        from google.cloud import storage

        from sereno_core.gcp_credentials import credentials_for_gcp_clients, get_service_account_info

        bucket_name = (st.secrets.get("gcs_bucket_name") or "").strip()
        if not bucket_name:
            return ""
        custom = (st.secrets.get("gcs_logo_blob_path") or "").strip()
        candidates: list[str] = []
        if custom:
            candidates.append(custom)
        candidates.extend(
            [
                "Logos/JOPAI-LogoSereno.jpg",
                "Logos/JOPAI-LogoSereno.jpeg",
                "Logos/JOPAI-LogoSereno.png",
                "Logos/JOPAI-LogoSereno.jp",
            ]
        )
        info = get_service_account_info(root, st.secrets)
        creds = credentials_for_gcp_clients(info)
        client = storage.Client(credentials=creds, project=info.get("project_id"))
        bucket = client.bucket(bucket_name)
        data: bytes | None = None
        used = ""
        for blob_path in candidates:
            blob = bucket.blob(blob_path)
            try:
                data = blob.download_as_bytes()
            except Exception:
                data = None
            if data:
                used = blob_path
                break
        if not data:
            return ""
        ext = Path(used).suffix.lower()
        mime = "image/jpeg"
        if ext == ".png":
            mime = "image/png"
        elif ext == ".webp":
            mime = "image/webp"
        elif ext in (".jpg", ".jpeg", ".jp"):
            mime = "image/jpeg"
        return _logo_html_from_bytes(data, mime)
    except Exception:
        return ""


def _build_page_logo_html() -> str:
    root = _repo_root()
    local = _logo_from_local_dir(root / "logo")
    if local:
        return local
    cache_key = "sereno_logo_gcs_html"
    try:
        if cache_key not in st.session_state:
            st.session_state[cache_key] = _logo_html_from_gcs(root)
        return str(st.session_state.get(cache_key) or "")
    except Exception:
        return ""


def _build_sidebar_logo_html() -> str:
    """Même source que le logo haut-droite (dossier `logo/` ou GCS), classes dédiées barre latérale."""
    page = _build_page_logo_html()
    if not page:
        return ""
    return (
        page.replace("jopai-page-logo-wrap", "jopai-sidebar-logo-wrap")
        .replace("jopai-page-logo", "jopai-sidebar-logo")
    )


def render_sidebar_branding() -> None:
    """À appeler dans `st.sidebar` (ex. `Home.py`) : logo SÉRÉNO en tête du menu."""
    html = _build_sidebar_logo_html()
    if html:
        st.markdown(html, unsafe_allow_html=True)
    else:
        st.markdown("##### SÉRÉNO", unsafe_allow_html=True)


def inject_sereno_prototype_css() -> None:
    """Styles prototype SÉRÉNO — pages parcours client et composants `.sereno-*`."""
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

        /* Zone centrale ~70 % du panneau principal (pas toute la fenêtre navigateur) */
        [data-testid="stAppViewContainer"] section[data-testid="stMain"] div.block-container {{
            max-width: 70% !important;
            margin-left: auto !important;
            margin-right: auto !important;
        }}

        section.main h1, section.main h2, section.main h3 {{
            font-family: {dt.FONT_UI};
            font-weight: 700;
            letter-spacing: {dt.FONT_LETTER_SPACING_TITLES};
            color: {dt.COLOR_TEXT};
        }}
        section.main .stMarkdown, section.main p, section.main span {{
            font-family: {dt.FONT_UI};
        }}

        .sereno-reassure {{
            background: {dt.COLOR_REASSURE_BG};
            border: 1px solid {dt.COLOR_BORDER};
            border-left: 4px solid {dt.COLOR_REASSURE_BORDER};
            border-radius: {dt.RADIUS_CARD};
            padding: 16px 20px;
            margin: 10px 0 22px 0;
            font-family: {dt.FONT_UI};
            color: {dt.COLOR_TEXT};
            font-size: 1.05rem;
            line-height: 1.5;
        }}
        .sereno-card {{
            background: {dt.COLOR_SURFACE};
            border: 1px solid {dt.COLOR_BORDER};
            border-radius: {dt.RADIUS_CARD};
            padding: 18px 22px;
            margin: 12px 0;
            box-shadow: 0 4px 24px rgba(0, 51, 102, 0.07);
            font-family: {dt.FONT_UI};
        }}
        .sereno-success-box {{
            background: {dt.COLOR_SUCCESS_BG};
            border: 2px solid {dt.COLOR_SUCCESS_BORDER};
            border-radius: {dt.RADIUS_CARD};
            padding: 14px 18px;
            margin: 12px 0;
            font-family: {dt.FONT_UI};
            color: {dt.COLOR_TEXT};
        }}
        .sereno-upload-zone {{
            border: 2px dashed {dt.COLOR_DASHED_ZONE};
            border-radius: {dt.RADIUS_CARD};
            padding: 28px 16px;
            text-align: center;
            background: {dt.COLOR_SURFACE};
            color: {dt.COLOR_TEXT_MUTED};
            font-family: {dt.FONT_UI};
            margin: 12px 0;
        }}
        .sereno-accent-line {{
            height: 3px;
            width: 100%;
            background: linear-gradient(90deg, {dt.COLOR_OR_DISCRET} 0%, {dt.COLOR_OR_DISCRET} 35%, transparent 100%);
            opacity: 0.85;
            border-radius: 2px;
            margin: 8px 0 16px 0;
        }}
        .sereno-sst-alert {{
            border-left: 5px solid #b71c1c;
            background: linear-gradient(90deg, #fff5f5 0%, #fffcfc 100%);
            padding: 14px 16px;
            margin: 14px 0 6px 0;
            border-radius: {dt.RADIUS_CARD};
            font-family: {dt.FONT_UI};
            color: {dt.COLOR_TEXT};
            font-size: 1.05rem;
            line-height: 1.45;
        }}
        .sereno-sst-reassure {{
            border-left: 5px solid #2e7d32;
            background: #f1f8f4;
            padding: 12px 16px;
            margin: 8px 0 16px 0;
            border-radius: {dt.RADIUS_CARD};
            font-family: {dt.FONT_UI};
            font-size: 0.98rem;
        }}

        section.main button[kind="primary"] {{
            min-height: {dt.BTN_MIN_HEIGHT_PX}px;
            border-radius: {dt.RADIUS_BTN} !important;
            font-weight: 650 !important;
            font-size: 1.05rem !important;
            background-color: {dt.COLOR_PRIMARY} !important;
            border-color: {dt.COLOR_PRIMARY} !important;
            color: #ffffff !important;
            font-family: {dt.FONT_UI} !important;
        }}
        section.main button[kind="primary"]:hover {{
            background-color: {dt.COLOR_PRIMARY_HOVER} !important;
            border-color: {dt.COLOR_PRIMARY_HOVER} !important;
        }}
        section.main button[kind="secondary"] {{
            min-height: 48px;
            border-radius: {dt.RADIUS_BTN} !important;
            font-weight: 600 !important;
            font-family: {dt.FONT_UI} !important;
            border-color: {dt.COLOR_BLEU_ACIER} !important;
            color: {dt.COLOR_BLEU_ACIER} !important;
        }}

        @keyframes sereno-pulse-glow {{
            0%, 100% {{ box-shadow: 0 0 0 0 rgba(0, 51, 102, 0.35); }}
            50% {{ box-shadow: 0 0 0 10px rgba(0, 51, 102, 0); }}
        }}
        section.main .sereno-pulse button {{
            animation: sereno-pulse-glow 2s ease-in-out infinite;
        }}

        /* Boutons urgence : pastille centrée, moins large, texte plus massif */
        section.main div[class*="st-key-urg_"] {{
            max-width: min(380px, 92vw) !important;
            margin-left: auto !important;
            margin-right: auto !important;
        }}
        div[class*="st-key-urg_"] button {{
            min-height: 70px !important;
            font-size: 1.56rem !important;
            font-weight: 800 !important;
        }}
        div[class*="st-key-urg_"] button p {{
            font-size: 1.56rem !important;
            font-weight: 800 !important;
        }}
        .st-key-urg_EAU button {{ background-color: #1565c0 !important; border-color: #0d47a1 !important; }}
        .st-key-urg_ELEC button {{ background-color: #ef6c00 !important; border-color: #e65100 !important; }}
        .st-key-urg_GAZ button {{ background-color: #c62828 !important; border-color: #b71c1c !important; }}
        .st-key-urg_CHAUFF button {{ background-color: #00695c !important; border-color: #004d40 !important; }}
        .st-key-urg_SERR button {{ background-color: #455a64 !important; border-color: #37474f !important; }}

        /* SST : boutons « Oui, j’ai compris » larges */
        section.main [class*="st-key-sst_yes_"] button {{
            min-height: 58px !important;
            font-size: 1.08rem !important;
            width: 100% !important;
        }}

        /* Étoiles satisfaction : fond neutre, pas de cadre ; or appliqué par surcharge dynamique (proto_ui) */
        div[class*="st-key-star_pick_"] button {{
            font-size: 2.5rem !important;
            line-height: 1 !important;
            min-height: 3rem !important;
            padding: 0.2rem 0.35rem !important;
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            outline: none !important;
            color: #bdbdbd !important;
            -webkit-text-fill-color: #bdbdbd !important;
            transition: color 0.15s ease, transform 0.15s ease !important;
        }}
        div[class*="st-key-star_pick_"] button:focus-visible {{
            outline: 2px solid #003366 !important;
            outline-offset: 2px !important;
            border-radius: 6px !important;
        }}
        div[class*="st-key-star_pick_"] button p {{
            font-size: 2.5rem !important;
            line-height: 1 !important;
        }}

        /* NPS 0–10 : une ligne, code couleur détracteurs / passifs / promoteurs */
        div[class*="st-key-nps_"] button {{
            min-height: 44px !important;
            font-weight: 700 !important;
            font-size: 1rem !important;
            padding: 0.35rem 0 !important;
            transition: transform 0.12s ease, box-shadow 0.12s ease !important;
        }}
        .st-key-nps_0 button, .st-key-nps_1 button, .st-key-nps_2 button,
        .st-key-nps_3 button, .st-key-nps_4 button, .st-key-nps_5 button, .st-key-nps_6 button {{
            background-color: #ffcdd2 !important;
            border-color: #e57373 !important;
            color: #b71c1c !important;
        }}
        .st-key-nps_7 button, .st-key-nps_8 button {{
            background-color: #fff9c4 !important;
            border-color: #fbc02d !important;
            color: #5d4037 !important;
        }}
        .st-key-nps_9 button, .st-key-nps_10 button {{
            background-color: #c8e6c9 !important;
            border-color: #66bb6a !important;
            color: #1b5e20 !important;
        }}
        .st-key-nps_0 button[kind="primary"], .st-key-nps_1 button[kind="primary"], .st-key-nps_2 button[kind="primary"],
        .st-key-nps_3 button[kind="primary"], .st-key-nps_4 button[kind="primary"], .st-key-nps_5 button[kind="primary"], .st-key-nps_6 button[kind="primary"] {{
            background-color: #c62828 !important;
            border-color: #7f0000 !important;
            color: #ffffff !important;
        }}
        .st-key-nps_7 button[kind="primary"], .st-key-nps_8 button[kind="primary"] {{
            background-color: #f57f17 !important;
            border-color: #e65100 !important;
            color: #ffffff !important;
        }}
        .st-key-nps_9 button[kind="primary"], .st-key-nps_10 button[kind="primary"] {{
            background-color: #1b5e20 !important;
            border-color: #0d3d10 !important;
            color: #ffffff !important;
        }}
        /* Choix NPS actif : chiffre beaucoup plus visible (taille + graisse), léger relief — sans double cadre bleu */
        section.main [class*="st-key-nps_"] button[kind="primary"],
        section.main [class*="st-key-nps_"] button[kind="primary"] p {{
            font-size: 1.95rem !important;
            font-weight: 900 !important;
            line-height: 1.05 !important;
            letter-spacing: -0.03em !important;
        }}
        section.main [class*="st-key-nps_"] button[kind="primary"] {{
            min-height: 56px !important;
            padding: 0.45rem 0.15rem !important;
            outline: none !important;
            box-shadow: 0 6px 18px rgba(0, 0, 0, 0.28) !important;
            transform: scale(1.12) !important;
            z-index: 3 !important;
            position: relative !important;
        }}

        /* Bandeau page infos client : bordure selon urgence (couleur via inline sur la page) */
        .sereno-infos-panne-band {{
            border-left: 6px solid #003366;
            border-radius: 8px;
            padding: 14px 18px;
            margin: 0 0 18px 0;
            font-family: {dt.FONT_UI};
            font-size: 1.05rem;
            line-height: 1.45;
        }}

        /* Overlay pastel pendant st.spinner (voir règles projet) */
        .sereno-busy-overlay {{
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(200, 220, 232, 0.5);
            backdrop-filter: blur(2px);
            z-index: 2147482000;
            align-items: center;
            justify-content: center;
            pointer-events: none;
        }}
        body:has([data-testid="stSpinner"]) .sereno-busy-overlay {{
            display: flex !important;
            pointer-events: auto;
        }}
        .sereno-busy-card {{
            background: rgba(255, 255, 255, 0.95);
            padding: 1.35rem 1.85rem;
            border-radius: 16px;
            border: 1px solid rgba(0, 51, 102, 0.18);
            font-weight: 650;
            font-size: 1.15rem;
            color: #003366;
            box-shadow: 0 10px 36px rgba(0, 51, 102, 0.12);
            font-family: {dt.FONT_UI};
            text-align: center;
            max-width: 92vw;
        }}
        </style>
        <div class="sereno-busy-overlay" aria-live="polite" aria-busy="true">
            <div class="sereno-busy-card">Votre artisan travaille pour vous…</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def apply_global_styles() -> None:
    """Typo globale, barre bleu souverain, logo, footer JOPAI."""
    page_logo_html = _build_page_logo_html()

    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

        .sereno-brand-topbar {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 3px;
            background: {dt.COLOR_BLEU_SOUVERAIN};
            z-index: 10001;
            pointer-events: none;
        }}
        [data-testid="stAppViewContainer"] > .main .block-container,
        [data-testid="stAppViewContainer"] section[data-testid="stMain"] .block-container {{
            font-family: {dt.FONT_UI};
            padding-top: 1.25rem;
            max-width: 70% !important;
            margin-left: auto !important;
            margin-right: auto !important;
        }}
        [data-testid="stSidebar"] {{
            font-family: {dt.FONT_UI};
        }}

        .jopai-sidebar-logo-wrap {{
            text-align: center;
            padding: 0.35rem 0 0.85rem 0;
            margin-bottom: 0.35rem;
            border-bottom: 1px solid #e2e8f0;
        }}
        .jopai-sidebar-logo {{
            width: 100%;
            max-width: 118px;
            height: auto;
            display: block;
            margin: 0 auto;
            filter: drop-shadow(0 1px 4px rgba(0, 51, 102, 0.15));
        }}

        /* Replis CDC / carnet : en-têtes bleus (lisibles comme « antennes » de chapitre) */
        .stApp [data-testid="stExpander"] details > summary {{
            background: linear-gradient(90deg, #003366, #2c5282) !important;
            color: #ffffff !important;
            font-weight: 700 !important;
            border-radius: 8px !important;
        }}
        .stApp [data-testid="stExpander"] details > summary span,
        .stApp [data-testid="stExpander"] details > summary p {{
            color: #ffffff !important;
        }}
        .stApp [data-testid="stExpander"] details > summary:hover {{
            filter: brightness(1.05);
        }}

        .jopai-page-logo-wrap {{
            position: fixed;
            top: 18px;
            right: 14px;
            z-index: 9000;
            pointer-events: none;
            opacity: 0.95;
        }}
        .jopai-page-logo {{
            width: 88px;
            height: auto;
            display: block;
            filter: drop-shadow(0 2px 8px rgba(0, 51, 102, 0.18));
        }}

        .jopai-footer {{
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 36px;
            background-color: #f5f5f7;
            border-top: 1px solid #d0d0d5;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Segoe UI', sans-serif;
            font-size: 11px;
            letter-spacing: 1px;
            color: #7a7a85;
            z-index: 9999;
        }}
        [data-testid="stAppViewContainer"] {{
            padding-bottom: 56px;
        }}
        .jopai-footer span.jopai-mark {{
            font-weight: 800;
            color: #0d9488;
        }}
        .jopai-footer span.jopai-mark i {{
            font-style: italic;
            color: #0d9488;
        }}
        .jopai-footer sup {{
            font-size: 0.7em;
            margin-left: 0;
            color: #0d9488;
        }}
        </style>
        <div class="sereno-brand-topbar" aria-hidden="true"></div>
        __JOPAI_PAGE_LOGO__
        <div class="jopai-footer">
            <span class="jopai-mark">JOP</span><span><i>AI</i><sup>©</sup>&nbsp;&nbsp;PRODUCTION © 2026 | TOUS DROITS RÉSERVÉS</span>
        </div>
        """.replace(
            "__JOPAI_PAGE_LOGO__", page_logo_html
        ),
        unsafe_allow_html=True,
    )
