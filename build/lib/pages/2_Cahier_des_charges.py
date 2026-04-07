"""
Cahier des charges SÉRÉNO — lecture interactive du Markdown officiel + export PDF partiel.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import streamlit as st

from sereno_core.app_urls import client_urgency_entry_url
from sereno_core.cdc_pdf_export import build_cdc_pdf_bytes
from sereno_core.md_chapters import parse_cdc_by_parties
from sereno_core.streamlit_markdown_book import render_markdown_book_page

st.title("Cahier des charges — SÉRÉNO")

cdc_path = _REPO / "CAHIER_DES_CHARGES.md"
if not cdc_path.is_file():
    st.error(f"Fichier introuvable : `{cdc_path}`.")
    st.stop()

raw_cdc = cdc_path.read_text(encoding="utf-8")
parties = parse_cdc_by_parties(raw_cdc)
if parties:
    labels = [pt[0] for pt in parties]
    st.subheader("Exporter en PDF")
    st.caption(
        "Choisissez une ou plusieurs parties (ex. introduction + Partie 1 + Partie 2 pour le business case et le fonctionnel). "
        "Le fichier reprend la hiérarchie avec des bandeaux bleus proches de l’affichage écran (généré par fpdf2, sans moteur HTML). "
        "Chaque partie sélectionnée commence sur une **nouvelle page** dans le PDF."
    )
    st.markdown("**Parties à inclure dans le PDF** — cochez les lignes souhaitées *(libellés complets, une ligne par partie)* :")
    pick: list[str] = []
    for i, label in enumerate(labels):
        if st.checkbox(label, value=True, key=f"cdc_pdf_inc_{i}"):
            pick.append(label)
    if pick:
        try:
            pdf_bytes = build_cdc_pdf_bytes(parties, pick, qr_target_url=client_urgency_entry_url())
            st.download_button(
                label="Télécharger le PDF",
                data=pdf_bytes,
                file_name="Sereno_CDC_extrait.pdf",
                mime="application/pdf",
                key="cdc_dl_pdf",
            )
        except Exception as e:
            st.warning(f"Export PDF indisponible ({e!s}). Vérifiez que **fpdf2** est installé (`pip install fpdf2`).")
    st.divider()

render_markdown_book_page(
    repo_root=_REPO,
    doc_path=cdc_path,
    session_prefix="cdc",
    outline="cdc_parties",
    show_outline_meta=False,
    footer_markdown="",
    page_caption=(
        "Document de référence **produit et technique**, versionné dans le dépôt. "
        "Premier niveau : introduction et grandes parties ; second niveau : sections numérotées."
    ),
)
