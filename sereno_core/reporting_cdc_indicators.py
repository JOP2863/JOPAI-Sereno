"""
Indicateurs de pilotage prévus au cahier des charges — grille type « canevas » (3 colonnes).

Les valeurs affichées sont des **placeholders** jusqu’au branchement des sources (BDD, Sheets, analytics).
On varie les **composants Streamlit** (métriques, `line_chart`, `area_chart`, `scatter_chart`, `progress`)
plutôt que d’empiler des barres verticales partout.
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
    cell_kind: Literal[
        "metric",
        "metrics_pair",
        "progress_rows",
        "progress_single",
        "line_trend",
        "area_trend",
        "scatter_demo",
    ]


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
        "progress_single",
    ),
    IndicatorSpec(
        "Couverture par type d’urgence",
        "Pour chaque bouton (eau, élec, …), part des créneaux couverts.",
        "Équilibrer le réseau par métier.",
        "progress_rows",
    ),
    IndicatorSpec(
        "Délai médian de première réponse",
        "Temps entre « demande lancée » et « expert joint / salle ouverte ».",
        "Qualité perçue.",
        "metric",
    ),
    IndicatorSpec(
        "Taux d’abandon (tendance)",
        "Arrêt avant fin checklist / avant visio / avant paiement — suivi dans le temps.",
        "Frictions UX.",
        "line_trend",
    ),
    IndicatorSpec(
        "Durée médiane de session visio",
        "Temps passé en visio (profil journalier type).",
        "Charge experts.",
        "area_trend",
    ),
    IndicatorSpec(
        "Satisfaction (NPS 0–10)",
        "Après session.",
        "Qualité du service.",
        "metrics_pair",
    ),
    IndicatorSpec(
        "Résolution perçue vs volume",
        "« Problème mieux maîtrisé » croisé avec le nombre de sessions (exemple).",
        "Efficacité à distance.",
        "scatter_demo",
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
            st.metric("Note moyenne", "—", help="Étoiles 1–5 (à brancher)")
        with c2:
            st.metric("NPS moyen", "—", help="0–10 (à brancher)")

    elif spec.cell_kind == "progress_single":
        st.progress(0.72, text="Ex. 72 % — données fictives")
        st.caption("Jauge unique (`st.progress`) — à relier à la vraie mesure 24/7.")

    elif spec.cell_kind == "progress_rows":
        df = pd.DataFrame(
            {
                "Type": ["Eau", "Élec", "Gaz", "Chauff.", "Serr."],
                "Couverture (%)": [72, 65, 58, 70, 80],
            }
        )
        for _, row in df.iterrows():
            st.caption(f"**{row['Type']}** — {int(row['Couverture (%)'])} %")
            st.progress(min(1.0, float(row["Couverture (%)"]) / 100.0))
        st.caption("Préférable aux barres verticales quand on compare **plusieurs petits taux**.")

    elif spec.cell_kind == "line_trend":
        df = pd.DataFrame(
            {
                "Semaine": [f"S{i}" for i in range(1, 9)],
                "Abandon % (ex.)": [12.0, 14.0, 11.0, 15.0, 13.0, 12.0, 10.0, 9.0],
            }
        )
        st.line_chart(df.set_index("Semaine"), height=200)
        st.caption("Série temporelle (`st.line_chart`) — données d’exemple.")

    elif spec.cell_kind == "area_trend":
        df = pd.DataFrame(
            {
                "Jour": [f"J{i}" for i in range(1, 15)],
                "Minutes médianes (ex.)": [4 + (i % 5) for i in range(14)],
            }
        )
        st.area_chart(df.set_index("Jour"), height=200)
        st.caption("Profil lissé (`st.area_chart`) — à remplacer par agrégation réelle.")

    elif spec.cell_kind == "scatter_demo":
        df = pd.DataFrame(
            {
                "Sessions (ex.)": [10, 25, 40, 8, 30, 18, 22],
                "% résolution perçue (ex.)": [62, 71, 68, 55, 74, 66, 70],
            }
        )
        st.scatter_chart(df, x="Sessions (ex.)", y="% résolution perçue (ex.)", height=220)
        st.caption("Nuage (`st.scatter_chart`) — utile pour repérer anomalies volume / qualité.")


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
