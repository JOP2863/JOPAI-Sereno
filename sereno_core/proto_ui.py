"""Composants légers pour les pages prototype (réassurance, en-têtes)."""

from __future__ import annotations

import time
from contextlib import contextmanager

import streamlit as st

from sereno_core.jopai_brand_html import nps_recommend_question_html, page_title_h1_html
from sereno_core.proto_state import ensure_demo_seed, p_get, p_set
from sereno_core.streamlit_theme import inject_sereno_prototype_css
from sereno_core.urgence_ambiance import inject_urgence_ambiance_css, render_proto_header_with_urgence


def proto_page_start(
    *,
    title: str,
    subtitle: str = "",
    show_urgence_ambiance: bool = True,
    show_journey_tagline: bool = True,
    title_brand_suffix: bool = True,
    busy_overlay_use_assigned_expert: bool = True,
) -> None:
    inject_sereno_prototype_css(busy_overlay_use_assigned_expert=busy_overlay_use_assigned_expert)
    ensure_demo_seed()
    ut = p_get("urgence_type")
    if show_urgence_ambiance:
        inject_urgence_ambiance_css(ut)
    else:
        inject_urgence_ambiance_css(None)
    if show_urgence_ambiance and ut:
        render_proto_header_with_urgence(
            title=title,
            subtitle=subtitle,
            ut=ut,
            show_journey_tagline=show_journey_tagline,
            title_brand_suffix=title_brand_suffix,
        )
    else:
        st.markdown(page_title_h1_html(title, brand_suffix=title_brand_suffix), unsafe_allow_html=True)
        if subtitle:
            st.caption(subtitle)


def reassurance(msg: str) -> None:
    st.markdown(
        f"<div class='sereno-reassure'>{msg}</div>",
        unsafe_allow_html=True,
    )


def success_box(msg: str) -> None:
    """Bloc succès (fond vert pâle + bordure verte)."""
    st.markdown(
        f"<div class='sereno-success-box'>{msg}</div>",
        unsafe_allow_html=True,
    )


def step_indicator(current: int, total: int = 6) -> None:
    st.markdown("<div style='margin-top:0.35rem' aria-hidden='true'></div>", unsafe_allow_html=True)
    st.progress(current / float(total), text=f"Étape {current} / {total}")


@contextmanager
def proto_processing_pause():
    """
    Affiche le spinner Streamlit → overlay pastel (carte : **nom de l’expert** assigné si connu,
    sinon « Votre artisan travaille pour vous… » — voir `inject_sereno_prototype_css`).
    À utiliser autour des traitements après soumission.
    """
    with st.spinner(" "):
        time.sleep(0.65)
        yield


def proto_nav_overlay_once(flag_key: str) -> None:
    """
    Si ``st.session_state[flag_key]`` est vrai, affiche une fois l’overlay (spinner minimal) puis supprime la clé.
    À poser **après** ``proto_page_start`` (CSS prototype déjà injecté). Définir le flag avant ``st.switch_page``.
    """
    if not st.session_state.pop(flag_key, False):
        return
    with st.spinner(" "):
        time.sleep(0.65)


def render_interactive_stars(*, state_key: str = "stars_selected") -> int:
    """Note 1–5 : étoiles regroupées au centre ; sélection en or + halo léger (sans encadrement)."""
    current = int(p_get(state_key, 0) or 0)
    gold_rules = "".join(
        f'div[class*="st-key-star_pick_{i}"] button, div[class*="st-key-star_pick_{i}"] button p {{ '
        f"color: #f9a825 !important; -webkit-text-fill-color: #f9a825 !important; "
        f"font-weight: 900 !important; outline: none !important; border: none !important; "
        f"text-shadow: 0 0 12px rgba(255, 193, 7, 0.85), 0 0 2px rgba(245, 124, 0, 0.35) !important; "
        f"transform: scale(1.07) !important; transition: color 0.15s ease, transform 0.15s ease !important; }}"
        for i in range(1, current + 1)
    )
    if gold_rules:
        st.markdown(f"<style>{gold_rules}</style>", unsafe_allow_html=True)
    st.markdown("**Votre note** *(1 à 5)*")
    _pad, mid, _pad2 = st.columns([0.22, 0.56, 0.22])
    with mid:
        cols = st.columns(5)
        for i in range(1, 6):
            with cols[i - 1]:
                label = "★" if i <= current else "☆"
                if st.button(label, key=f"star_pick_{i}"):
                    p_set(state_key, i)
                    st.rerun()
    return int(p_get(state_key, 0) or 0)


def render_nps_buttons(*, state_key: str = "nps_selected") -> int | None:
    """NPS 0–10 : une seule rangée, couleurs détracteurs / passifs / promoteurs (CSS global)."""
    current = p_get(state_key, None)
    st.markdown(nps_recommend_question_html(), unsafe_allow_html=True)
    st.caption("Échelle de **0** (pas du tout) à **10** (tout à fait).")
    _l, row, _r = st.columns([0.04, 0.92, 0.04])
    with row:
        cols = st.columns(11)
        for n in range(0, 11):
            with cols[n]:
                is_sel = current == n
                if st.button(str(n), key=f"nps_{n}", type="primary" if is_sel else "secondary"):
                    p_set(state_key, n)
                    st.rerun()
    return int(current) if current is not None else None
