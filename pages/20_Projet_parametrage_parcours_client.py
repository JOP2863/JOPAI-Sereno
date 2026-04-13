"""
Projet — paramètres du parcours prototype **client** (partagés via Google Sheets **Config**).
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import streamlit as st

from sereno_core.jopai_brand_html import page_title_h1_html
from sereno_core.proto_state import (
    JOURNEY_PRESET_CUSTOM,
    JOURNEY_PRESET_SIMPLIFIED,
    JOURNEY_PRESET_STANDARD,
    journey_merged_settings,
    journey_nps_active,
    journey_payment_active,
    journey_sst_active,
    p_set,
)
from sereno_core.sheets_experts import resolve_gsheet_id
from sereno_core.sheets_journey_config import persist_journey_config

st.markdown(page_title_h1_html("Paramétrage parcours client"), unsafe_allow_html=True)
st.caption(
    "Les choix sont **enregistrés automatiquement** dans l’onglet **Config** du classeur Google "
    "(clés dont le préfixe est **SERENO_JOURNEY_**). **Toutes les personnes** qui ouvrent l’app voient alors le même parcours "
    "(menu latéral et enchaînement). Si le classeur n’est pas accessible, les réglages restent **locaux** à la session. "
    "Après un changement enregistré, la page se **recharge une fois** pour mettre à jour le menu (votre connexion pilote reste active)."
)

cfg = journey_merged_settings()
preset0 = str(cfg.get("preset") or JOURNEY_PRESET_STANDARD)

main, _ = st.columns([0.72, 0.28])
with main:
    st.markdown(
        "Le **parcours standard** reprend toutes les étapes actuelles (sécurité **SST**, **paiement** simulé, **NPS**). "
        "Le **parcours simplifié** **désactive** ces trois étapes optionnelles : le client enchaîne après les informations "
        "directement vers la mise en relation, puis après la visio retourne à l’accueil **sans** paiement ni questionnaire. "
        "Le mode **personnalisé** permet d’**activer ou non** chacune des trois étapes optionnelles."
    )

    choice = st.radio(
        "Mode de parcours",
        options=[
            JOURNEY_PRESET_STANDARD,
            JOURNEY_PRESET_SIMPLIFIED,
            JOURNEY_PRESET_CUSTOM,
        ],
        index=(
            0
            if preset0 == JOURNEY_PRESET_STANDARD
            else (1 if preset0 == JOURNEY_PRESET_SIMPLIFIED else 2)
        ),
        format_func=lambda v: {
            JOURNEY_PRESET_STANDARD: "Standard (toutes les étapes)",
            JOURNEY_PRESET_SIMPLIFIED: "Simplifié (sans SST, sans paiement, sans NPS)",
            JOURNEY_PRESET_CUSTOM: "Personnalisé (choix par étape optionnelle)",
        }[v],
        horizontal=False,
    )

    if choice == JOURNEY_PRESET_CUSTOM:
        st.markdown("**Étapes optionnelles** (cochez celles qui restent **actives** dans le parcours) :")
        c1, c2 = st.columns([0.55, 0.45])
        with c1:
            sst_on = st.checkbox(
                "Sécurité (SST) avant la visio",
                value=bool(cfg.get("custom_sst", True)),
                help="Checklist sécurité avant la mise en relation.",
            )
            pay_on = st.checkbox(
                "Paiement (simulation)",
                value=bool(cfg.get("custom_payment", True)),
            )
            nps_on = st.checkbox(
                "NPS — avis après la session",
                value=bool(cfg.get("custom_nps", True)),
            )
        with c2:
            st.caption("Astuce : tout décocher équivaut au mode **simplifié** pour le flux, tout cocher au **standard**.")
        cs, cp, cn = sst_on, pay_on, nps_on
    elif choice == JOURNEY_PRESET_STANDARD:
        cs, cp, cn = True, True, True
    else:
        cs, cp, cn = False, False, False

    p_set("journey_preset", choice)
    p_set("journey_custom_sst", cs)
    p_set("journey_custom_payment", cp)
    p_set("journey_custom_nps", cn)

    sig_ui = f"{choice}|{cs}|{cp}|{cn}"
    sig0 = f"{preset0}|{bool(cfg.get('custom_sst', True))}|{bool(cfg.get('custom_payment', True))}|{bool(cfg.get('custom_nps', True))}"
    try:
        _secrets = dict(st.secrets)
    except Exception:
        _secrets = {}
    _persist_ok = False
    if sig_ui != sig0:
        ok, err = persist_journey_config(
            _REPO,
            _secrets,
            preset=choice,
            custom_sst=cs,
            custom_payment=cp,
            custom_nps=cn,
        )
        if not ok:
            st.warning(f"Écriture **Config** impossible : {err}")
        else:
            _persist_ok = True

    # Recharger l’app : le menu latéral est recalculé dans ``Home.py`` — la session pilote (**Se connecter**) est conservée.
    _has_gsheet = bool(resolve_gsheet_id(_REPO, _secrets).strip())
    if sig_ui != sig0 and (_persist_ok or not _has_gsheet):
        st.rerun()

    st.divider()
    st.markdown("**Aperçu effectif** (menu + parcours) :")
    st.write(
        f"- Sécurité **SST** : **{'active' if journey_sst_active() else 'inactive'}**\n"
        f"- **Paiement** : **{'actif' if journey_payment_active() else 'inactif'}**\n"
        f"- **NPS** : **{'actif' if journey_nps_active() else 'inactif'}**"
    )
