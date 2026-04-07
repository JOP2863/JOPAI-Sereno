"""
Indicateurs de pilotage prévus au cahier des charges — grille type « canevas » (3 colonnes).

Les valeurs affichées sont des **placeholders** jusqu’à branchement des sources (BDD, Sheets, analytics).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import pandas as pd
import streamlit as st


@dataclass(frozen=True)
class IndicatorSpec:
    title: str
    definition: str
    operational: str
    cell_kind: Literal["metric", "chart", "metrics_pair"]


# Ordre = remplissage ligne par ligne (3 colonnes)
INDICATORS: list[IndicatorSpec] = [
    IndicatorSpec(
        "Artisans référencés",
        "Nombre d’experts actifs dans le réseau.",
        "Taille du vivier.",
        "metric",
    ),
    IndicatorSpec(
        "Taux de couverture 24/7",
        "Part du temps (semaine type) où au moins un artisan éligible est joignable ou en astreinte.",
        "Rassurer l’usager sur la disponibilité.",
        "metric",
    ),
    IndicatorSpec(
        "Couverture par type d’urgence",
        "Pour chaque bouton (eau, élec, …), part des créneaux couverts.",
        "Équilibrer le réseau par métier.",
        "chart",
    ),
    IndicatorSpec(
        "Délai médian de première réponse",
        "Temps entre « demande lancée » et « expert joint / salle ouverte ».",
        "Qualité perçue.",
        "metric",
    ),
    IndicatorSpec(
        "Taux d’abandon",
        "Arrêt avant fin checklist / avant visio / avant paiement.",
        "Frictions UX.",
        "metric",
    ),
    IndicatorSpec(
        "Durée médiane de session visio",
        "Temps passé en visio.",
        "Charge experts.",
        "metric",
    ),
    IndicatorSpec(
        "Satisfaction (étoiles + NPS)",
        "Après session.",
        "Qualité du service.",
        "metrics_pair",
    ),
    IndicatorSpec(
        "Taux de résolution perçue",
        "« Problème mieux maîtrisé » oui/non.",
        "Efficacité à distance.",
        "metric",
    ),
    IndicatorSpec(
        "Taux de recontact sous 24 h",
        "Nouvelle demande liée au même dossier.",
        "Suivi / qualité.",
        "metric",
    ),
    IndicatorSpec(
        "Taux de passage au déplacement",
        "Visio insuffisante → intervention terrain.",
        "Complémentarité.",
        "metric",
    ),
    IndicatorSpec(
        "Revenu moyen par session (cible)",
        "Après monétisation réelle.",
        "Viabilité.",
        "metric",
    ),
]


def _placeholder_metric(title: str, operational: str) -> None:
    st.metric(label=title, value="—", help=f"{operational} (source à brancher)")


def _render_cell(spec: IndicatorSpec) -> None:
    st.markdown(f"**{spec.title}**")
    st.caption(spec.definition)
    st.caption(f"*Intérêt :* {spec.operational}")

    if spec.cell_kind == "metric":
        _placeholder_metric(spec.title, spec.operational)

    elif spec.cell_kind == "metrics_pair":
        c1, c2 = st.columns(2)
        with c1:
            st.metric("Note moyenne", "—", help="Étoiles 1–5")
        with c2:
            st.metric("NPS moyen", "—", help="0–10")

    elif spec.cell_kind == "chart":
        df = pd.DataFrame(
            {
                "Type": ["Eau", "Élec", "Gaz", "Chauff.", "Serr."],
                "Couverture (ex.)": [72, 65, 58, 70, 80],
            }
        )
        st.bar_chart(df.set_index("Type"), height=200)
        st.caption("Données d’exemple — à remplacer par les vraies mesures.")


def render_reporting_cdc_grid() -> None:
    """Affiche la grille 3 × N dans Streamlit."""
    chunks: list[list[IndicatorSpec]] = []
    for i in range(0, len(INDICATORS), 3):
        chunks.append(INDICATORS[i : i + 3])

    for ri, row_specs in enumerate(chunks):
        cols = st.columns(3)
        for j in range(3):
            with cols[j]:
                if j < len(row_specs):
                    _render_cell(row_specs[j])
                else:
                    st.empty()
        if ri < len(chunks) - 1:
            st.divider()
