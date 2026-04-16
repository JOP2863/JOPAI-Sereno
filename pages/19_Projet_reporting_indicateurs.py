"""
Reporting — canevas des indicateurs de pilotage (cahier des charges).

Grille **3 colonnes** : métriques, graphiques ou doubles jauges selon l’indicateur.
Les valeurs sont des **placeholders** jusqu’au branchement des sources (BDD, analytics, Sheets).
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import streamlit as st

from sereno_core.jopai_brand_html import page_title_h1_html
from sereno_core.reporting_cdc_indicators import INDICATORS, render_reporting_cdc_grid
from sereno_core.streamlit_theme import inject_button_zoom_resilience_css

inject_button_zoom_resilience_css()

st.markdown(page_title_h1_html("Reporting — indicateurs de pilotage"), unsafe_allow_html=True)
st.caption(
    "Source : **cahier des charges** (indicateurs prévus à date). "
    "Canevas 3 colonnes — à alimenter avec les données réelles."
)

with st.expander("Tableau de synthèse (définitions)", expanded=False):
    rows = [
        {
            "Indicateur": x.title,
            "Définition (courte)": x.definition,
            "Intérêt opérationnel": x.operational,
        }
        for x in INDICATORS
    ]
    st.dataframe(rows, use_container_width=True, hide_index=True)

render_reporting_cdc_grid()

st.divider()
st.info(
    "**Administration pilote** : la saisie des disponibilités artisans / réseau se fait via le menu "
    "**Administration · Pilote** (pages Dispo. artisan / propriétaire)."
)
