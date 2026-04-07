"""
Prototype artisan — vue restreinte + synthèse des avis sur ses sessions.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import pandas as pd
import streamlit as st

from sereno_core.proto_state import ensure_demo_seed, p_get
from sereno_core.proto_ui import proto_page_start, reassurance

proto_page_start(
    title="Espace artisan",
    subtitle="Vous ne voyez que **vos** prises en charge et les **avis** liés à ces sessions.",
    show_urgence_ambiance=False,
)

ensure_demo_seed()
reassurance(
    "En production, cet écran est servi avec **compte nominatif** et **filtrage serveur** ; ici les données restent dans la session navigateur du pilote."
)

artisans: list[dict] = list(p_get("artisans", []))
if not artisans:
    st.warning("Aucun expert fictif — rechargez l’app.")
    st.stop()

labels = {a["id"]: f"{a['nom']} ({a['id']})" for a in artisans}
choice = st.selectbox("Expert connecté (pilote)", options=list(labels.keys()), format_func=lambda x: labels[x])

st.subheader("Outils & reporting")
c_link1, c_link2, c_link3 = st.columns(3)
with c_link1:
    st.page_link(
        "pages/16_Admin_artisan_disponibilites.py",
        label="Déclarer mes disponibilités (par mois)",
        icon="📆",
        help="Règles CDC § 1.7.1 : mois proche (< 30 jours) = fenêtre sensible ; notifier le propriétaire avant modification seul.",
    )
with c_link2:
    st.page_link(
        "pages/19_Projet_reporting_indicateurs.py",
        label="Reporting indicateurs (CDC)",
        icon="📈",
    )
with c_link3:
    st.page_link(
        "pages/14_Projet_stats.py",
        label="Métriques code / CDC",
        icon="📊",
    )
st.caption(
    "**Disponibilités** : format mois `AAAA-MM`, modes standard / astreinte / sur rendez-vous / indisponible ; "
    "écriture dans l’onglet **Disponibilite_Mois** si le classeur est configuré."
)
st.divider()

events: list[dict] = list(p_get("events", []))

session_ids: set[str] = set()
for e in events:
    if e.get("expert_id") == choice:
        sid = e.get("session_id")
        if sid:
            session_ids.add(str(sid))

filtered = [e for e in events if e.get("session_id") in session_ids or e.get("expert_id") == choice]

st.subheader("Activité — mes sessions")
if not filtered:
    st.info("Aucun événement pour cet expert — faites un parcours **client** complet.")
else:
    df = pd.DataFrame(filtered)
    st.dataframe(df, use_container_width=True, hide_index=True)

st.subheader("Avis reçus (sessions où vous avez été assigné)")
satisfaction_rows = [
    e
    for e in events
    if e.get("action") == "satisfaction" and e.get("session_id") in session_ids
]
if not satisfaction_rows:
    st.caption("Pas encore d’avis sur vos sessions dans cette session démo.")
else:
    sdf = pd.DataFrame(satisfaction_rows)
    _cols = [c for c in ("ts", "session_id", "stars", "nps", "commentaire") if c in sdf.columns]
    st.dataframe(sdf[_cols], use_container_width=True, hide_index=True)
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Note moyenne (étoiles)", f"{sdf['stars'].mean():.1f} / 5")
    with c2:
        st.metric("NPS moyen", f"{sdf['nps'].mean():.1f} / 10")

st.divider()
st.subheader("Synthèse")
n_sess = len(session_ids)
st.metric("Sessions touchées", n_sess)
by_action = (
    pd.DataFrame(filtered).groupby("action").size().rename("nombre").reset_index()
    if filtered
    else pd.DataFrame(columns=["action", "nombre"])
)
if not by_action.empty:
    st.markdown("**Répartition des événements (vos lignes)**")
    st.bar_chart(by_action.set_index("action"))
