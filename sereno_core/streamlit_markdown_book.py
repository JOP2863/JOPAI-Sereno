"""Affichage Streamlit : document Markdown en chapitres repliables + recherche."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from sereno_core.md_chapters import (
    highlight_snippet,
    parse_cdc_by_parties,
    parse_chapters,
    parse_subsections,
)


def render_markdown_book_page(
    *,
    repo_root: Path,
    doc_path: Path,
    session_prefix: str,
    page_caption: str,
    footer_markdown: str = "",
    outline: str = "flat",
    show_outline_meta: bool = True,
) -> None:
    """
    session_prefix : préfixe unique pour st.session_state (ex. 'cdc' ou 'carnet').
    show_outline_meta : affiche le compteur parties/sections (désactivé pour le CDC).
    footer_markdown : vide = pas de pied de page.
    """
    expand_key = f"{session_prefix}_expand_all"
    search_key = f"{session_prefix}_search"
    last_key = f"{session_prefix}_last_search"
    clear_pending_key = f"{session_prefix}_clear_search_pending"

    if expand_key not in st.session_state:
        st.session_state[expand_key] = None

    if st.session_state.get(clear_pending_key):
        st.session_state[search_key] = ""
        st.session_state[last_key] = ""
        st.session_state[expand_key] = None
        st.session_state[clear_pending_key] = False

    if page_caption:
        st.caption(page_caption)

    if not doc_path.is_file():
        st.error(f"Fichier introuvable : `{doc_path}`.")
        st.stop()

    raw = doc_path.read_text(encoding="utf-8")
    parties: list[tuple[str, list[tuple[str, str]]]] | None = None
    if outline == "cdc_parties":
        parties = parse_cdc_by_parties(raw)
    chapters = parse_chapters(raw)

    # Barre d’outils : recherche + boutons alignés (même hauteur de ligne)
    c_search, c_btn1, c_btn2, c_btn3, c_meta = st.columns([3.2, 1, 1, 1, 1.2])
    with c_search:
        st.text_input(
            "Rechercher",
            key=search_key,
            placeholder="Mot ou phrase dans tout le document…",
            label_visibility="visible",
        )
        query = (st.session_state.get(search_key) or "").strip()

    if last_key not in st.session_state:
        st.session_state[last_key] = ""
    if query != st.session_state[last_key]:
        st.session_state[expand_key] = None
        st.session_state[last_key] = query

    with c_btn1:
        st.markdown("<div style='height:1.65rem'></div>", unsafe_allow_html=True)
        if st.button("Tout déplier", use_container_width=True, key=f"{session_prefix}_all_open"):
            st.session_state[expand_key] = True
            st.rerun()

    with c_btn2:
        st.markdown("<div style='height:1.65rem'></div>", unsafe_allow_html=True)
        if st.button("Tout replier", use_container_width=True, key=f"{session_prefix}_all_close"):
            st.session_state[expand_key] = False
            st.rerun()

    with c_btn3:
        st.markdown("<div style='height:1.65rem'></div>", unsafe_allow_html=True)
        if st.button("Effacer recherche", use_container_width=True, key=f"{session_prefix}_search_reset"):
            st.session_state[clear_pending_key] = True
            st.rerun()

    with c_meta:
        if show_outline_meta:
            try:
                rel = doc_path.relative_to(repo_root)
            except ValueError:
                rel = doc_path
            if parties is not None:
                n_sec = sum(len(secs) for _, secs in parties)
                st.caption(f"**{len(parties)}** partie(s) · **{n_sec}** section(s) `##` · `{rel}`")
            else:
                st.caption(f"**{len(chapters)}** chapitre(s) · `{rel}`")

    if query:
        st.caption(
            "Les chapitres affichés ci-dessous sont **filtrés** : seules les parties ou sections "
            f"contenant « **{query}** » apparaissent (recherche non sensible à la casse)."
        )

    q = query
    exp = st.session_state[expand_key]

    if parties is not None:
        _render_parties_outline(parties, q, exp, footer_markdown)
        return

    filtered: list[tuple[int, str, str]] = []
    for i, (title, body) in enumerate(chapters):
        blob = f"{title}\n{body}"
        if not q or q.lower() in blob.lower():
            filtered.append((i, title, body))

    if q and not filtered:
        st.warning(f"Aucun chapitre ne correspond à « {q} ».")
        st.stop()

    if q:
        st.info(f"**{len(filtered)}** chapitre(s) correspondent à la recherche.")

    for _idx, title, body in filtered:
        blob = f"{title}\n{body}"
        match = not q or q.lower() in blob.lower()
        if exp is True:
            expanded = True
        elif exp is False:
            expanded = False
        else:
            expanded = bool(q and match)

        snippet = highlight_snippet(blob, q) if q else ""

        with st.expander(f"## {title}", expanded=expanded):
            if snippet:
                st.markdown(f"*Extrait :* {snippet}")
                st.divider()

            subs = parse_subsections(body)
            if not subs:
                st.markdown(body or "_vide_")
                continue

            for sub_title, sub_body in subs:
                if not sub_title:
                    st.markdown(sub_body)
                    continue
                sub_match = not q or q.lower() in (sub_title + sub_body).lower()
                sub_expanded = expanded or (bool(q) and sub_match)
                with st.expander(f"### {sub_title}", expanded=sub_expanded):
                    st.markdown(sub_body or "_vide_")

    if footer_markdown.strip():
        st.divider()
        st.markdown(footer_markdown)


def _render_parties_outline(
    parties: list[tuple[str, list[tuple[str, str]]]],
    q: str,
    exp: bool | None,
    footer_markdown: str,
) -> None:
    """CDC : 1er niveau = parties (0 intro + Partie 1…4), 2e = ## ; ### reste en Markdown."""
    ql = q.lower() if q else ""

    def part_blob(ptitle: str, sections: list[tuple[str, str]]) -> str:
        parts = [ptitle]
        for stitle, sbody in sections:
            parts.append(f"{stitle}\n{sbody}")
        return "\n".join(parts)

    filtered = []
    for ptitle, sections in parties:
        blob = part_blob(ptitle, sections)
        if not ql or ql in blob.lower():
            filtered.append((ptitle, sections))

    if q and not filtered:
        st.warning(f"Aucune partie ne correspond à « {q} ».")
        st.stop()

    if q:
        st.info(f"**{len(filtered)}** partie(s) correspondent à la recherche.")

    for ptitle, sections in filtered:
        blob = part_blob(ptitle, sections)
        match = not ql or ql in blob.lower()
        if exp is True:
            part_open = True
        elif exp is False:
            part_open = False
        else:
            part_open = bool(q and match)

        snippet = highlight_snippet(blob, q) if q else ""
        with st.expander(f"# {ptitle}", expanded=part_open):
            if snippet:
                st.markdown(f"*Extrait :* {snippet}")
                st.divider()

            for sec_title, sec_body in sections:
                if not sec_title:
                    st.markdown(sec_body or "_vide_")
                    continue
                sec_blob = f"{sec_title}\n{sec_body}"
                sec_match = not ql or ql in sec_blob.lower()
                if exp is True:
                    sec_open = True
                elif exp is False:
                    sec_open = False
                else:
                    sec_open = bool(q and sec_match)

                with st.expander(f"## {sec_title}", expanded=sec_open):
                    st.markdown(sec_body or "_vide_")

    if footer_markdown.strip():
        st.divider()
        st.markdown(footer_markdown)
