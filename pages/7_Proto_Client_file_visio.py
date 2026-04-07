"""
Prototype client — file d’attente + mise en relation (simulation).
"""

from __future__ import annotations

import re
import sys
from datetime import UTC, datetime
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import streamlit as st

from sereno_core.proto_checklists import URGENCE_LABELS
from sereno_core.proto_helpers import pick_expert_for_urgence
from sereno_core.proto_state import log_event, p_get, p_set, sync_session_sheet
from sereno_core.proto_ui import proto_page_start, reassurance, step_indicator
from sereno_core.sheets_experts import canonicalize_type_list

proto_page_start(
    title="Mise en relation avec un expert",
    subtitle="Nous contactons les professionnels dans un **ordre défini** (priorité) parmi ceux qui couvrent votre type d’urgence.",
)
step_indicator(4, 7)

ut = p_get("urgence_type")
if not ut or not p_get("sst_validated"):
    st.warning("Validez d’abord l’étape **Sécurité (SST)**.")
    st.stop()

reassurance(
    "Temps d’attente indicatif : **~1 minute**. "
    "Un expert vous confirmera la prise en charge avant d’ouvrir la visio."
)

artisans: list[dict] = list(p_get("artisans", []))
elig = [a for a in artisans if ut in canonicalize_type_list(list(a.get("types") or []))]
elig.sort(key=lambda a: int(a.get("ordre", 99)))

if not elig:
    st.error(
        "Aucun expert de démonstration n’est référencé pour ce type d’urgence. "
        "Revenez à l’accueil et choisissez une autre situation, ou complétez la liste des artisans (pilote)."
    )
    with st.expander("Diagnostic — experts chargés (pilote)"):
        st.markdown(
            "Le parcours **ne filtre pas** sur les créneaux (`Disponibilite_Mois`, `Creneau_Astreinte`) : "
            "seul l’onglet **Experts** compte ici. Il faut au moins une ligne **actif** avec le **code** "
            f"**{ut}** (ou **TOUS**) dans la colonne des types."
        )
        if not artisans:
            st.warning(
                "Aucun expert en session : vérifier **gsheet_id** dans les secrets, le partage du classeur "
                "avec l’e-mail du **compte de service**, et l’existence de l’onglet **Experts**."
            )
        else:
            st.write(f"**{len(artisans)}** ligne(s) en session :")
            for a in artisans:
                ts = canonicalize_type_list(list(a.get("types") or []))
                st.write(
                    f"- **{a.get('id', '?')}** — types normalisés : `{ts}` — ordre : {a.get('ordre', '—')}"
                )
            st.caption(
                "Si `types` est vide : renommer la colonne en **types_autorises** ou remplir la cellule "
                "(ex. `EAU;GAZ` ou `TOUS`). Puis **Réinitialiser le parcours** sur l’accueil urgence, "
                "ou `python scripts/init_google_sheet.py --seed` si l’onglet n’a que l’en-tête."
            )
    if st.button("← Retour accueil", type="secondary"):
        st.switch_page("pages/4_Proto_Client_accueil.py")
    st.stop()

def _fmt_expert(a: dict) -> str:
    return f"{a.get('nom', '?')} ({a.get('id')}) — priorité d’appel {a.get('ordre', '—')}"

default = p_get("assigned_expert")
if not default or default.get("id") not in {e.get("id") for e in elig}:
    default = pick_expert_for_urgence(ut, artisans) or elig[0]
    p_set("assigned_expert", default)

idx0 = next((i for i, e in enumerate(elig) if e.get("id") == default.get("id")), 0)

if len(elig) > 1:
    st.subheader("Choisir votre prestataire")
    st.caption(
        "Plusieurs professionnels couvrent votre urgence. Celui affiché en **premier** est le plus prioritaire "
        "par défaut ; vous pouvez en choisir un **autre** dans la liste."
    )
    pick_i = st.selectbox(
        "Expert pour la prise en charge",
        options=list(range(len(elig))),
        index=idx0,
        format_func=lambda i: _fmt_expert(elig[i]),
        key="expert_pick_mise_en_relation",
    )
    chosen = elig[int(pick_i)]
else:
    chosen = elig[0]

p_set("assigned_expert", chosen)
assigned = chosen

if assigned.get("id") != p_get("_audit_last_expert_id"):
    log_event(
        "expert_assigne",
        session_id=p_get("session_id"),
        expert_id=assigned.get("id"),
        expert_nom=assigned.get("nom"),
    )
    p_set("_audit_last_expert_id", assigned.get("id"))
    sync_session_sheet(
        {
            "expert_id": str(assigned.get("id") or ""),
            "type_code": ut,
            "statut": "EXPERT_ASSIGNE",
        }
    )

st.success(
    f"**{assigned.get('nom', 'Expert')}** est sélectionné pour votre demande "
    f"({URGENCE_LABELS.get(ut, ut)}). "
    f"*Priorité d’appel n°{assigned.get('ordre', '—')} dans la file pour ce type d’urgence.*"
)

with st.expander("Voir l’ordre d’appel des experts (démo)"):
    for a in elig:
        st.write(f"{a.get('ordre', '—')}. **{a.get('nom')}** — {', '.join(a.get('types', []))}")

if st.button("Ouvrir la salle de visio", type="primary"):
    _sid = str(p_get("session_id") or "")
    _room = re.sub(r"[^a-zA-Z0-9]", "", f"Sereno{_sid}")[:48] or "SerenoDemo"
    _jitsi = f"https://meet.jit.si/{_room}#config.prejoinPageEnabled=false"
    _debut = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    log_event("visio_debut", session_id=p_get("session_id"))
    sync_session_sheet(
        {
            "debut_visio": _debut,
            "room_url": _jitsi,
            "type_code": ut,
            "statut": "VISIO_DEMARREE",
        }
    )
    st.switch_page("pages/8_Proto_Client_visio.py")

if st.button("← Retour"):
    st.switch_page("pages/6_Proto_Client_SST.py")
