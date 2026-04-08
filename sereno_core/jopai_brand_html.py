"""
Segments HTML **inline** pour la marque **JOP** + *AI* + © (turquoise) et **SÉRÉNO** (pétrole), alignés JOPAI-BTP.

Aucune dépendance Streamlit : réutilisable dans `streamlit_theme`, `proto_ui`, pages.
"""

from __future__ import annotations

from html import escape

COLOR_JOPAI_TURQUOISE = "#0d9488"
COLOR_JOPAI_TITLE_NAVY = "#0b2745"


def jopai_copyright_inline_html() -> str:
    """**JOP** gras + *AI* italique + © exposant, tout en turquoise."""
    t = COLOR_JOPAI_TURQUOISE
    return (
        f'<span style="font-weight:800;color:{t};">JOP</span>'
        f'<span style="font-style:italic;color:{t};">AI</span>'
        f'<sup style="color:{t};font-size:0.68em;line-height:0;vertical-align:super;">©</sup>'
    )


def sereno_word_inline_html() -> str:
    """Mot produit en majuscules accentuées, pétrole."""
    n = COLOR_JOPAI_TITLE_NAVY
    return f'<span style="font-weight:750;color:{n};">SÉRÉNO</span>'


def by_jopai_sereno_suffix_html() -> str:
    """Suffixe type titre JOPAI-BTP : « by » + JOPAI© + SÉRÉNO."""
    n = COLOR_JOPAI_TITLE_NAVY
    return (
        f' <span style="color:{n};font-weight:600;">by</span> '
        + jopai_copyright_inline_html()
        + " "
        + sereno_word_inline_html()
    )


def page_title_h1_html(title: str, *, brand_suffix: bool = True) -> str:
    """
    Titre principal : texte échappé + suffixe marque.
    Afficher avec ``st.markdown(..., unsafe_allow_html=True)``.
    """
    esc = escape((title or "").strip())
    n = COLOR_JOPAI_TITLE_NAVY
    suf = by_jopai_sereno_suffix_html() if brand_suffix else ""
    return (
        f'<h1 style="font-family:Inter,\'Segoe UI\',system-ui,sans-serif;line-height:1.28;color:{n};margin-bottom:0.25rem;">'
        f"{esc}{suf}</h1>"
    )


def nps_recommend_question_html() -> str:
    """Bloc question NPS (Recommanderiez-vous JOPAI© SÉRÉNO…)."""
    t, n = COLOR_JOPAI_TURQUOISE, COLOR_JOPAI_TITLE_NAVY
    j = jopai_copyright_inline_html()
    s = sereno_word_inline_html()
    return (
        f'<div style="color:{n};font-family:Inter,\'Segoe UI\',system-ui,sans-serif;line-height:1.5;">'
        '<p style="margin:0 0 0.35rem 0;font-size:1.06rem;">'
        '<strong>Recommanderiez-vous</strong> '
        f"{j} {s} "
        '<strong>à un proche ?</strong>'
        "</p>"
        f'<p style="margin:0;font-size:0.92rem;color:{n};opacity:0.92;">'
        "<em>(note 0 à 10 : 0–6 insatisfait, 7–8 correct, 9–10 très satisfait — rouge / jaune / vert)</em>"
        "</p></div>"
    )


def sidebar_brand_line_html() -> str:
    """Ligne compacte sous le logo menu (JOPAI© SÉRÉNO)."""
    n = COLOR_JOPAI_TITLE_NAVY
    return (
        f'<div style="text-align:center;font-size:0.88rem;margin:0.15rem 0 0.5rem 0;color:{n};line-height:1.35;">'
        f"{jopai_copyright_inline_html()}&nbsp;{sereno_word_inline_html()}"
        "</div>"
    )


def filigrane_second_line_html() -> str:
    """Deuxième ligne du filigrane « chantier » (HTML) — tons **pastel** (ne pas concurrencer le contenu utile)."""
    # Pastels dérivés de la charte (lisibles sur fond très léger du filigrane).
    t = "#7dd3c0"
    n = "#94a3b8"
    demo = "#a8b8c8"
    jop = f'<span style="font-weight:800;color:{t};">JOP</span>'
    ai = f'<span style="font-style:italic;color:{t};">AI</span>'
    sup = f'<sup style="color:{t};font-size:0.68em;line-height:0;vertical-align:super;">©</sup>'
    ser = f'<span style="font-weight:650;color:{n};">SÉRÉNO</span>'
    # Le parent `.jopai-construction-filigrane__stripe` impose `text-transform: uppercase` :
    # neutraliser pour garder **SÉRÉNO** et la casse voulue.
    return (
        f'<span style="text-transform:none;">Prototype {ser} — {jop}{ai}{sup} '
        f'<span style="color:{demo};font-weight:600;">· démonstration non commerciale</span></span>'
    )


def footer_brand_block_html() -> str:
    """Bloc marque + mention légale pour le footer fixe global (classes `.jopai-mark` déjà en CSS)."""
    return (
        '<span class="jopai-mark">JOP</span><span><i>AI</i><sup>©</sup></span> '
        f"{sereno_word_inline_html()} "
        '<span style="color:#7a7a85;font-weight:normal;letter-spacing:1px;">'
        "&nbsp;&nbsp;PRODUCTION © 2026 | TOUS DROITS RÉSERVÉS</span>"
    )
