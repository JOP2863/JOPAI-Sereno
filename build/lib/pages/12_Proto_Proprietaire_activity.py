"""
Prototype propriétaire — reporting global simple (activité + satisfaction + entonnoir).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import pandas as pd
import streamlit as st

from sereno_core.proto_state import ensure_demo_seed, log_event, p_get, p_set
from sereno_core.proto_ui import proto_page_start, reassurance

proto_page_start(
    title="Activité & pilotage (propriétaire)",
    subtitle="Vue **transverse** : tous les experts, tous les événements et **avis** de la session démo.",
    show_urgence_ambiance=False,
)

ensure_demo_seed()
reassurance("Rôle **admin / propriétaire** : pas de filtre par expert. En production : auth forte + audit.")

events: list[dict] = list(p_get("events", []))

_FUNNEL_CHAIN = [
    ("urgence_choisie", "1. Choix urgence"),
    ("infos_client", "2. Coordonnées"),
    ("sst_validee", "3. Sécurité validée"),
    ("expert_assigne", "4. Expert assigné"),
    ("visio_debut", "5. Visio démarrée"),
    ("visio_fin", "6. Visio terminée"),
    ("paiement_simule", "7. Paiement simulé"),
    ("satisfaction", "8. Avis envoyé"),
]


def _events_by_session(evts: list[dict]) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    for e in evts:
        sid = e.get("session_id")
        if not sid:
            continue
        out.setdefault(str(sid), set()).add(str(e.get("action") or ""))
    return out


c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Événements", len(events))
with c2:
    st.metric("Experts (liste)", len(p_get("artisans", [])))
with c3:
    sessions = {e.get("session_id") for e in events if e.get("session_id")}
    st.metric("Sessions", len(sessions))
with c4:
    sat = [e for e in events if e.get("action") == "satisfaction"]
    st.metric("Avis collectés", len(sat))

if events:
    by_sid = _events_by_session(events)
    st.subheader("Entonnoir (parcours démo)")
    st.caption(
        "Pour chaque étape : nombre de sessions où **toutes** les étapes précédentes **et** celle-ci ont été enregistrées "
        "(ordre logique du parcours client)."
    )
    funnel_rows = []
    chain: list[str] = []
    for action_key, label in _FUNNEL_CHAIN:
        chain.append(action_key)
        n = sum(1 for acts in by_sid.values() if all(a in acts for a in chain))
        funnel_rows.append({"Étape": label, "Sessions": n})
    fdf = pd.DataFrame(funnel_rows)
    _, fcol, _ = st.columns([0.15, 0.55, 0.3])
    with fcol:
        st.bar_chart(fdf.set_index("Étape"), height=320)
    st.dataframe(fdf, use_container_width=False, hide_index=True)

    df = pd.DataFrame(events)
    st.subheader("Volume par type d’événement")
    counts = df.groupby("action").size().rename("nombre").reset_index()
    _, bcol, _ = st.columns([0.15, 0.55, 0.3])
    with bcol:
        st.bar_chart(counts.set_index("action"), height=260)

    st.subheader("Détail des avis (tous experts)")
    if sat:
        sdf = pd.DataFrame(sat)
        cols = [
            c
            for c in ["ts", "session_id", "type_intervention", "urgence", "stars", "nps", "commentaire"]
            if c in sdf.columns
        ]
        st.dataframe(sdf[cols], use_container_width=True, hide_index=True)
        st.metric("Note moyenne globale", f"{pd.to_numeric(sdf['stars'], errors='coerce').mean():.2f} / 5")
    else:
        st.caption("Aucun avis pour l’instant.")

    st.subheader("Journal brut")
    st.dataframe(df, use_container_width=True, hide_index=True)

    json_bytes = json.dumps(events, ensure_ascii=False, indent=2).encode("utf-8")
    st.download_button(
        "Télécharger le journal (JSON)",
        data=json_bytes,
        file_name="sereno_pilot_events.json",
        mime="application/json",
    )
else:
    st.info("Encore aucun événement — exécutez un parcours **client**.")

st.divider()
st.subheader("Experts — ordre d’appel")
art_df = pd.DataFrame(p_get("artisans", []))
if not art_df.empty:
    ad = art_df.sort_values("ordre").copy()
    ad["types"] = ad["types"].apply(lambda x: ";".join(x) if isinstance(x, list) else str(x))
    show_cols = [c for c in ["ordre", "id", "nom", "email", "types"] if c in ad.columns]
    st.dataframe(ad[show_cols], use_container_width=True, hide_index=True)

st.divider()
st.subheader("Maintenance démo")
if st.button("Vider le journal d’événements (démo)", type="secondary"):
    p_set("events", [])
    log_event("admin_reset_journal", par="proprietaire")
    st.rerun()
