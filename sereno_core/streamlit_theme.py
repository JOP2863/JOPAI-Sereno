"""
Styles globaux Streamlit SÉRÉNO : charte SÉRÉNO Core + footer JOPAI + logo (local ou GCS).
"""

from __future__ import annotations

import base64
from pathlib import Path

import streamlit as st

from sereno_core import design_tokens as dt
from sereno_core.jopai_brand_html import filigrane_second_line_html, footer_brand_block_html, sidebar_brand_line_html
from sereno_core.experience_settings import show_watermark


def _busy_overlay_card_inner_html(*, use_assigned_expert: bool = True) -> str:
    """Ligne centrale de la carte overlay : **prénom** + photo ronde si disponibles (sinon message générique)."""
    from html import escape

    if use_assigned_expert:
        try:
            from pathlib import Path

            from sereno_core.proto_state import p_get

            ex = p_get("assigned_expert") or {}
            prenom = str(ex.get("prenom") or "").strip()
            eid = str(ex.get("id") or "").strip()
            photo = ""
            if eid:
                try:
                    root = Path(__file__).resolve().parent.parent
                    sec = dict(st.secrets)
                    from sereno_core.gcs_artisan_photo import expert_photo_data_url

                    photo = expert_photo_data_url(root, sec, expert_id=eid) or ""
                except Exception:
                    photo = ""
            if not photo:
                photo = str(ex.get("photo_url") or "").strip()
            # URL console « authentifiée » : ne fonctionne pas en balise <img> pour les clients.
            if "storage.cloud.google.com" in photo:
                photo = ""
            img = ""
            if photo:
                img = (
                    "<div style='margin:0 auto 10px;width:44px;height:44px;border-radius:50%;overflow:hidden;"
                    "border:2px solid rgba(0,51,102,0.15);'>"
                    f"<img src='{escape(photo)}' alt='' "
                    "style='width:100%;height:100%;object-fit:cover;display:block;'/>"
                    "</div>"
                )
            if prenom:
                return img + f"<strong>{escape(prenom)}</strong> travaille pour vous…"
            return img + escape("Votre artisan SÉRÉNO travaille pour vous…")
        except Exception:
            pass
    return escape("Votre artisan SÉRÉNO travaille pour vous…")

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


def _sereno_logo_gcs_candidates() -> list[str]:
    custom = ""
    try:
        custom = (st.secrets.get("gcs_logo_blob_path") or "").strip()
    except Exception:
        custom = ""
    out: list[str] = []
    if custom:
        out.append(custom)
    out.extend(
        [
            "Logos/JOPAI-LogoSereno.jpg",
            "Logos/JOPAI-LogoSereno.jpeg",
            "Logos/JOPAI-LogoSereno.png",
            "Logos/JOPAI-LogoSereno.jp",
        ]
    )
    return out


def _mime_for_blob_path(used: str) -> str:
    ext = Path(used).suffix.lower()
    if ext == ".png":
        return "image/png"
    if ext == ".webp":
        return "image/webp"
    if ext in (".jpg", ".jpeg", ".jp"):
        return "image/jpeg"
    return "image/jpeg"


def _logo_html_from_gcs(root: Path) -> str:
    """Objet attendu : `Logos/JOPAI-LogoSereno.jpg` (bucket `gcs_bucket_name`)."""
    try:
        from google.cloud import storage

        from sereno_core.gcp_credentials import credentials_for_gcp_clients, get_service_account_info

        bucket_name = (st.secrets.get("gcs_bucket_name") or "").strip()
        if not bucket_name:
            return ""
        candidates = _sereno_logo_gcs_candidates()
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
        mime = _mime_for_blob_path(used)
        return _logo_html_from_bytes(data, mime)
    except Exception:
        return ""


def get_sereno_logo_bytes() -> tuple[bytes, str] | None:
    """
    Logo marque **SÉRÉNO** (mêmes sources que le logo page : dossier ``logo/`` puis GCS).
    Retour ``(octets, mime)`` pour ``st.image`` / data-URL, ou ``None``.
    """
    key = "_sereno_logo_bytes_tuple_v1"
    if key in st.session_state:
        hit = st.session_state[key]
        return hit if isinstance(hit, tuple) else None

    root = _repo_root()
    logo_dir = root / "logo"
    if logo_dir.is_dir():
        all_files = sorted(
            p for p in logo_dir.iterdir() if p.is_file() and p.suffix.lower() in _LOGO_EXTENSIONS
        )
        preferred = [p for p in all_files if "sereno" in p.name.lower()]
        for lp in preferred or all_files:
            try:
                mime = {
                    ".png": "image/png",
                    ".jpg": "image/jpeg",
                    ".jpeg": "image/jpeg",
                    ".webp": "image/webp",
                }.get(lp.suffix.lower(), "image/png")
                tup = (lp.read_bytes(), mime)
                st.session_state[key] = tup
                return tup
            except OSError:
                continue

    try:
        from google.cloud import storage

        from sereno_core.gcp_credentials import credentials_for_gcp_clients, get_service_account_info

        bucket_name = (st.secrets.get("gcs_bucket_name") or "").strip()
        if not bucket_name:
            st.session_state[key] = False
            return None
        info = get_service_account_info(root, st.secrets)
        creds = credentials_for_gcp_clients(info)
        client = storage.Client(credentials=creds, project=info.get("project_id"))
        bucket = client.bucket(bucket_name)
        data: bytes | None = None
        used = ""
        for blob_path in _sereno_logo_gcs_candidates():
            blob = bucket.blob(blob_path)
            try:
                data = blob.download_as_bytes()
            except Exception:
                data = None
            if data:
                used = blob_path
                break
        if not data:
            st.session_state[key] = False
            return None
        mime = _mime_for_blob_path(used)
        tup = (data, mime)
        st.session_state[key] = tup
        return tup
    except Exception:
        st.session_state[key] = False
        return None


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
    """À appeler dans `st.sidebar` (ex. `Home.py`) : logo + ligne marque JOPAI© SÉRÉNO."""
    html = _build_sidebar_logo_html()
    if html:
        st.markdown(html, unsafe_allow_html=True)
    st.markdown(sidebar_brand_line_html(), unsafe_allow_html=True)


def inject_sereno_prototype_css(*, busy_overlay_use_assigned_expert: bool = True) -> None:
    """Styles prototype SÉRÉNO — pages parcours client et composants `.sereno-*`."""
    busy_inner = _busy_overlay_card_inner_html(use_assigned_expert=busy_overlay_use_assigned_expert)
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

        /* Marque JOPAI© (turquoise) + SÉRÉNO (pétrole en inline hors ces classes) — alias JOPAI-BTP : .brand-jop / .brand-ai */
        section.main .brand-job,
        section.main .brand-jop,
        [data-testid="stAppViewContainer"] .brand-job,
        [data-testid="stAppViewContainer"] .brand-jop {{
            font-weight: 800 !important;
            color: {dt.COLOR_JOPAI_TURQUOISE} !important;
        }}
        section.main .brand-sereno,
        section.main .brand-ai,
        [data-testid="stAppViewContainer"] .brand-sereno,
        [data-testid="stAppViewContainer"] .brand-ai {{
            font-style: italic !important;
            color: {dt.COLOR_JOPAI_TURQUOISE} !important;
        }}
        section.main .brand-job + .brand-sereno + sup,
        section.main .brand-jop + .brand-ai + sup,
        [data-testid="stAppViewContainer"] .brand-job + .brand-sereno + sup,
        [data-testid="stAppViewContainer"] .brand-jop + .brand-ai + sup {{
            color: {dt.COLOR_JOPAI_TURQUOISE} !important;
            font-size: 0.65em !important;
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
        .sereno-reassure.sereno-reassure--tight {{
            margin: 6px 0 8px 0;
            padding: 14px 18px;
        }}
        .sereno-accueil-urgence-choix h3 {{
            margin-top: 0.35rem;
            margin-bottom: 0.5rem;
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

        /* Étoiles satisfaction : alignées à gauche, serrées, non sélectionnées plus lisibles */
        section.main [data-testid="stHorizontalBlock"]:has(div[class*="st-key-star_pick_1"]) {{
            justify-content: flex-start !important;
            width: fit-content !important;
            max-width: 100% !important;
        }}
        div[class*="st-key-star_pick_"] button {{
            font-size: 1.85rem !important;
            line-height: 1 !important;
            min-height: 2.55rem !important;
            padding: 0.08rem 0.12rem !important;
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            outline: none !important;
            color: #546e7a !important;
            -webkit-text-fill-color: #546e7a !important;
            text-shadow: 0 0 0.55px #263238, 0 0 1px rgba(38, 50, 56, 0.45) !important;
            transition: color 0.15s ease, transform 0.15s ease !important;
        }}
        div[class*="st-key-star_pick_"] button:focus-visible {{
            outline: 2px solid #003366 !important;
            outline-offset: 2px !important;
            border-radius: 6px !important;
        }}
        div[class*="st-key-star_pick_"] button p {{
            font-size: 1.85rem !important;
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
            <div class="sereno-busy-card">{busy_inner}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def apply_global_styles() -> None:
    """Typo globale, barre bleu souverain, logo, footer JOPAI."""
    page_logo_html = _build_page_logo_html()
    wm = show_watermark()

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

        .sereno-pilot-auth-sidebar-title {{
            font-family: {dt.FONT_UI};
            font-weight: 700;
            font-size: 0.85rem;
            margin: 0.15rem 0 0.35rem 0;
            color: #1e3a5f;
        }}

        /* Popovers (ex. connexion pilote) au-dessus du filigrane / footer */
        div[data-testid="stPopover"],
        div[data-testid="stPopover"] > button,
        [data-baseweb="popover"],
        div[data-testid="stPopoverContent"] {{
            z-index: 100000 !important;
        }}

        .jopai-construction-filigrane {{
            position: fixed;
            inset: 0;
            z-index: 9995;
            pointer-events: none;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .jopai-construction-filigrane__stripe {{
            position: absolute;
            top: 50%;
            left: 50%;
            width: 160%;
            transform: translate(-50%, -50%) rotate(-20deg);
            transform-origin: center center;
            text-align: center;
            font-family: {dt.FONT_UI};
            font-weight: 560;
            font-size: clamp(16px, 2.9vw, 27px);
            letter-spacing: 0.06em;
            line-height: 1.45;
            color: rgba(0, 51, 102, 0.088);
            text-transform: uppercase;
            user-select: none;
            white-space: normal;
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
        {"<div class=\"jopai-construction-filigrane\" aria-hidden=\"true\">"
         "<div class=\"jopai-construction-filigrane__stripe\">Site en construction<br />"
         + filigrane_second_line_html()
         + "</div></div>" if wm else ""}
        __JOPAI_PAGE_LOGO__
        <div class="jopai-footer">
            {footer_brand_block_html()}
        </div>
        """.replace(
            "__JOPAI_PAGE_LOGO__", page_logo_html
        ),
        unsafe_allow_html=True,
    )
