"""
Administration — paramètres d’expérience prototype **client** (Google Sheets **Config**).
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import streamlit as st

from sereno_core.experience_settings import (
    persist_experience_flags,
    show_brand_suffix_in_titles,
    show_guide_page,
    show_watermark,
)
from sereno_core.jopai_brand_html import page_title_h1_html
from sereno_core.proto_state import (
    JOURNEY_PRESET_CUSTOM,
    JOURNEY_PRESET_SIMPLIFIED,
    JOURNEY_PRESET_STANDARD,
    journey_merged_settings,
    p_set,
)
from sereno_core.satisfaction_settings import MODE_NPS, MODE_STARS, persist_satisfaction_mode, satisfaction_mode
from sereno_core.sheets_experts import resolve_gsheet_id
from sereno_core.sheets_journey_config import persist_journey_config
from sereno_core.ui_labels import (
    MODE_CUSTOM,
    MODE_MINIMAL,
    MODE_STANDARD,
    UI_LABELS,
    persist_ui_labels_config,
    ui_label_on,
    ui_labels_mode,
)

st.markdown(
    """
<style>
.sereno-param-page-compact section.main h3 { font-size: 1.05rem !important; margin: 0.1rem 0 0.15rem 0 !important; }
.sereno-param-page-compact section.main .stMarkdown p { margin-bottom: 0.25rem !important; line-height: 1.35 !important; }
.sereno-param-page-compact section.main [data-testid="stCaptionContainer"] p { font-size: 0.82rem !important; margin-bottom: 0.2rem !important; }
.sereno-param-page-compact section.main [data-testid="stVerticalBlock"] > div { gap: 0.35rem !important; }
.sereno-param-summary { border-collapse: collapse; width: auto; max-width: min(420px, 100%); font-size: 0.86rem; margin: 0 0 0.5rem 0; }
.sereno-param-summary th { background: #f1f5f9; border: 1px solid #e2e8f0; padding: 6px 10px; text-align: left; font-weight: 750; color: #0b2745; white-space: nowrap; }
.sereno-param-summary td { border: 1px solid #e2e8f0; padding: 6px 10px; vertical-align: middle; }
</style>
""",
    unsafe_allow_html=True,
)
st.markdown('<div class="sereno-param-page-compact">', unsafe_allow_html=True)

st.markdown(
    page_title_h1_html(
        "Paramétrage expérience client",
        brand_suffix=show_brand_suffix_in_titles(),
    ),
    unsafe_allow_html=True,
)
st.caption(
    "Les choix sont **enregistrés** dans l’onglet **Config** du classeur Google (clés **SERENO_***). "
    "Sans classeur, les réglages restent **locaux** à la session."
)

cfg = journey_merged_settings()
preset0 = str(cfg.get("preset") or JOURNEY_PRESET_STANDARD)


def _pill(text: str, bg: str, fg: str = "#0b2745") -> str:
    return (
        f"<span style='display:inline-block;padding:0.12rem 0.45rem;border-radius:999px;"
        f"background:{bg};color:{fg};font-weight:750;font-size:0.82rem;'>{text}</span>"
    )


def _summary_html(*, journey: str, labels: str, satisfaction: str, extra: str) -> str:
    c_ok = "#d1fae5"
    c_info = "#e0f2fe"
    c_neutral = "#f1f5f9"

    def _bg(v: str) -> str:
        v = (v or "").lower()
        if "minimal" in v:
            return c_ok
        if "custom" in v or "personnalis" in v:
            return c_info
        if "standard" in v:
            return c_neutral
        if "nps" in v:
            return c_info
        if "étoile" in v or "stars" in v:
            return c_ok
        return c_neutral

    rows = [
        ("Parcours", journey),
        ("Libellés", labels),
        ("Satisfaction", satisfaction),
        ("Affichage", extra),
    ]
    tr = "".join(
        f"<tr><th scope='row'>{k}</th><td>{_pill(v, _bg(v))}</td></tr>" for k, v in rows
    )
    return f"<table class='sereno-param-summary'>{tr}</table>"


try:
    _secrets = dict(st.secrets)
except Exception:
    _secrets = {}
_has_gsheet = bool(resolve_gsheet_id(_REPO, _secrets).strip())

preset_effectif = str(cfg.get("preset") or JOURNEY_PRESET_STANDARD)
labels_effectif = ui_labels_mode()
sat_effectif = satisfaction_mode()
wm0, br0, gd0 = show_watermark(), show_brand_suffix_in_titles(), show_guide_page()

journey_label = {
    JOURNEY_PRESET_STANDARD: "Standard",
    JOURNEY_PRESET_SIMPLIFIED: "Simplifié",
    JOURNEY_PRESET_CUSTOM: "Personnalisé",
}.get(preset_effectif, preset_effectif)
labels_label = {
    MODE_STANDARD: "Standard",
    MODE_MINIMAL: "Minimaliste",
    MODE_CUSTOM: "Personnalisé",
}.get(labels_effectif, labels_effectif)
sat_label = "5 étoiles" if sat_effectif == MODE_STARS else "NPS (0–10)"
extra_label = (
    f"Filigrane {'oui' if wm0 else 'non'} · Titres « by » {'oui' if br0 else 'non'} · Guide {'oui' if gd0 else 'non'}"
)

st.markdown(
    _summary_html(
        journey=journey_label,
        labels=labels_label,
        satisfaction=sat_label,
        extra=extra_label,
    ),
    unsafe_allow_html=True,
)

st.divider()

row1_l, row1_r = st.columns(2)
row2_l, row2_r = st.columns(2)

with row1_l:
    st.markdown("### Parcours")
    st.caption("Étapes optionnelles : sécurité SST, paiement simulé, avis.")
    choice = st.radio(
        "Mode de parcours",
        options=[JOURNEY_PRESET_STANDARD, JOURNEY_PRESET_SIMPLIFIED, JOURNEY_PRESET_CUSTOM],
        index=0 if preset0 == JOURNEY_PRESET_STANDARD else (1 if preset0 == JOURNEY_PRESET_SIMPLIFIED else 2),
        format_func=lambda v: {
            JOURNEY_PRESET_STANDARD: "Standard (toutes les étapes)",
            JOURNEY_PRESET_SIMPLIFIED: "Simplifié (sans SST, sans paiement, sans avis)",
            JOURNEY_PRESET_CUSTOM: "Personnalisé (choix par étape)",
        }[v],
        horizontal=False,
        label_visibility="collapsed",
    )
    st.caption("Mode de parcours")

    if choice == JOURNEY_PRESET_CUSTOM:
        sst_on = st.checkbox("Sécurité (SST) avant la visio", value=bool(cfg.get("custom_sst", True)))
        pay_on = st.checkbox("Paiement (simulation)", value=bool(cfg.get("custom_payment", True)))
        nps_on = st.checkbox("Avis après la session", value=bool(cfg.get("custom_nps", True)))
        cs, cp, cn = sst_on, pay_on, nps_on
    elif choice == JOURNEY_PRESET_STANDARD:
        cs, cp, cn = True, True, True
    else:
        cs, cp, cn = False, False, False

    p_set("journey_preset", choice)
    p_set("journey_custom_sst", cs)
    p_set("journey_custom_payment", cp)
    p_set("journey_custom_nps", cn)

    sig_ui = f"{choice}|{cs}|{cp}|{cn}"
    sig0 = f"{preset0}|{bool(cfg.get('custom_sst', True))}|{bool(cfg.get('custom_payment', True))}|{bool(cfg.get('custom_nps', True))}"
    if sig_ui != sig0:
        ok, err = persist_journey_config(
            _REPO,
            _secrets,
            preset=choice,
            custom_sst=cs,
            custom_payment=cp,
            custom_nps=cn,
        )
        if not ok and _has_gsheet:
            st.warning(f"Écriture **Config** impossible : {err}")
        else:
            st.rerun()

with row1_r:
    st.markdown("### Charge visuelle (libellés)")
    st.caption("Réduit textes d’aide / démo / technique.")
    mode0 = ui_labels_mode()
    mode_choice = st.radio(
        "Version libellés",
        options=[MODE_STANDARD, MODE_MINIMAL, MODE_CUSTOM],
        index=0 if mode0 == MODE_STANDARD else (1 if mode0 == MODE_MINIMAL else 2),
        format_func=lambda v: {
            MODE_STANDARD: "Standard (tout afficher)",
            MODE_MINIMAL: "Minimaliste (le moins possible)",
            MODE_CUSTOM: "Personnalisé (cases)",
        }[v],
        horizontal=False,
        key="labels_mode_choice",
        label_visibility="collapsed",
    )
    st.caption("Version libellés")

    custom_vals: dict[str, bool] = {}
    if mode_choice == MODE_CUSTOM:
        st.markdown("**Libellés optionnels** (2 colonnes) :")
        half = (len(UI_LABELS) + 1) // 2
        c1, c2 = st.columns(2)
        for i, it in enumerate(UI_LABELS):
            tgt = c1 if i < half else c2
            with tgt:
                custom_vals[it.id] = st.checkbox(
                    it.owner_label,
                    value=bool(ui_label_on(it.id)),
                    key=f"ui_label_{it.id}",
                )

    _mode_changed = mode_choice != mode0
    if _mode_changed:
        ok2, err2 = persist_ui_labels_config(_REPO, _secrets, mode=mode_choice, custom_values=custom_vals)
        if not ok2 and _has_gsheet:
            st.warning(f"Écriture **Config** impossible (libellés) : {err2}")
        else:
            st.rerun()
    elif mode_choice == MODE_CUSTOM and st.button("Enregistrer les libellés", type="secondary"):
        ok2, err2 = persist_ui_labels_config(_REPO, _secrets, mode=mode_choice, custom_values=custom_vals)
        if not ok2 and _has_gsheet:
            st.warning(f"Écriture **Config** impossible (libellés) : {err2}")
        else:
            st.rerun()

with row2_l:
    st.markdown("### Mesure de satisfaction client")
    st.caption("Par défaut : **5 étoiles**. Commentaire libre toujours optionnel.")
    sat0 = satisfaction_mode()
    sat_choice = st.radio(
        "Mode de mesure",
        options=[MODE_STARS, MODE_NPS],
        index=0 if sat0 == MODE_STARS else 1,
        format_func=lambda v: {MODE_STARS: "5 étoiles (simple)", MODE_NPS: "NPS (0–10)"}[v],
        horizontal=False,
        key="sat_mode_choice",
        label_visibility="collapsed",
    )
    st.caption("Mode de mesure")
    if sat_choice != sat0:
        ok3, err3 = persist_satisfaction_mode(_REPO, _secrets, mode=sat_choice)
        if not ok3 and _has_gsheet:
            st.warning(f"Écriture **Config** impossible (satisfaction) : {err3}")
        else:
            st.rerun()

with row2_r:
    st.markdown("### Affichage global")
    st.caption("Filigrane, titres « by JOPAI© », menu Guide.")
    wm = st.checkbox("Filigrane « site en construction »", value=wm0, key="cfg_wm")
    br = st.checkbox("Titres avec « by JOPAI© SÉRÉNO »", value=br0, key="cfg_br")
    gd = st.checkbox("Page « Guide du parcours » dans le menu client", value=gd0, key="cfg_gd")
    if st.button("Appliquer l’affichage global", type="primary"):
        ok4, err4 = persist_experience_flags(
            _REPO, _secrets, watermark=wm, brand_suffix=br, guide_page=gd
        )
        if not ok4 and _has_gsheet:
            st.warning(f"Écriture **Config** impossible : {err4}")
        else:
            st.rerun()

st.markdown("</div>", unsafe_allow_html=True)
