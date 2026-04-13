"""
Prototype — carte du parcours (documentation vivante dans la nav), alignée sur le paramétrage actuel.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import streamlit as st  # noqa: E402 — après insertion sys.path

from sereno_core.jopai_brand_html import page_title_h1_html
from sereno_core.proto_state import (
    JOURNEY_PRESET_CUSTOM,
    JOURNEY_PRESET_SIMPLIFIED,
    JOURNEY_PRESET_STANDARD,
    journey_nps_active,
    journey_payment_active,
    journey_preset,
    journey_sst_active,
    ensure_demo_seed,
)
from sereno_core.streamlit_theme import inject_sereno_prototype_css

inject_sereno_prototype_css()
ensure_demo_seed()

st.markdown(page_title_h1_html("Guide du parcours"), unsafe_allow_html=True)
st.caption("Vue d’ensemble des écrans **client** et des espaces **artisan** / **propriétaire**.")
st.info(
    "Dans le menu latéral, le **Prototype** est regroupé en trois sections : "
    "**Prototype · Client**, **Prototype · Artisan**, **Prototype · Propriétaire**."
)

_preset = journey_preset()
if _preset == JOURNEY_PRESET_STANDARD:
    _parcours_resume = (
        "vous suivez le parcours **standard** : toutes les étapes « démo » sont actives "
        "(sécurité **SST**, paiement simulé, questionnaire **NPS** — note de satisfaction 0 à 10)."
    )
elif _preset == JOURNEY_PRESET_SIMPLIFIED:
    _parcours_resume = (
        "vous suivez le parcours **simplifié** : après la visio, retour direct à l’accueil **sans** "
        "étape sécurité **SST**, **sans** paiement simulé et **sans** **NPS**."
    )
else:
    _parts = []
    _parts.append("**SST** (sécurité avant visio) **active**" if journey_sst_active() else "**SST** **inactive**")
    _parts.append("**Paiement** simulé **actif**" if journey_payment_active() else "**Paiement** **inactif**")
    _parts.append("**NPS** **actif**" if journey_nps_active() else "**NPS** **inactif**")
    _parcours_resume = "vous suivez un parcours **personnalisé** : " + " ; ".join(_parts) + "."

st.success(
    f"**Parcours client actuel (pilote)** — {_parcours_resume} "
    "Ce réglage est fixé par le **propriétaire** (page **Paramétrage parcours client** dans **Projet** ; "
    "valeurs partagées via la feuille **Config** du classeur Google lorsque celui-ci est joignable)."
)

if _preset != JOURNEY_PRESET_STANDARD:
    st.caption(
        "Un parcours **standard** existe aussi : il ajoute seulement trois étapes courtes "
        "(consignes de sécurité, paiement de démonstration, avis) tout en restant simple à enchaîner."
    )

if journey_sst_active():
    st.markdown(
        """
Avant la visio, une étape **sécurité** : consignes simples (eau, électricité, gaz…). Dans le menu, l’intitulé reprend l’abréviation
**SST**, qui signifie en toutes lettres **Sécurité et Santé au travail** (vocabulaire habituel sur les chantiers ; ici appliqué aux **gestes sûrs** chez soi avant d’allumer la caméra).
"""
    )
else:
    st.markdown(
        """
Pour ce pilote, l’étape **sécurité (SST)** n’est **pas** affichée dans le menu : les consignes « eau, électricité, gaz… »
ne sont pas demandées ici ; en **parcours standard**, elles reviennent avant la mise en relation.
"""
    )

st.markdown("### Parcours client (dans l’ordre affiché)")

_steps: list[str] = []
_n = 1
_steps.append(
    f"{_n}. **Accueil urgence** — choix du type (eau, élec, gaz, chauffage, serrurerie)."
)
_n += 1
_steps.append(
    f"{_n}. **Informations** — prénom / téléphone (réassurance), e-mail optionnel."
)
_n += 1
if journey_sst_active():
    _steps.append(
        f"{_n}. **Sécurité (SST)** — checklist obligatoire avant la visio (gestes sûrs selon le type d’urgence)."
    )
    _n += 1
_steps.append(
    f"{_n}. **Mise en relation & visio** — attente courte, appel des experts dans l’ordre défini, puis **lien vers la salle** de visio."
)
_n += 1
_steps.append(
    f"{_n}. **Session visio** — échange vidéo (salle fournie par le fournisseur configuré : Daily, Twilio, etc.)."
)
_n += 1
if journey_payment_active():
    _steps.append(
        f"{_n}. **Paiement** — forfait affiché et passage au moyen de paiement selon l’intégration en production (ici : simulation)."
    )
    _n += 1
if journey_nps_active():
    _steps.append(
        f"{_n}. **Satisfaction** — **NPS** 0–10, commentaire optionnel."
    )

st.markdown("\n\n".join(_steps))

st.markdown(
    """
### Côté artisan

- **Tableau de bord** : activité et avis filtrés par expert ; liens vers le **reporting** (métriques projet) et la **saisie des disponibilités** (cahier des charges, partie **1.7.1**, fenêtre sensible et notification propriétaire).

### Côté propriétaire

- **Activité** : vision transverse des sessions et export des données utiles au pilotage.
- **Conformité réseau** : saisie **SIREN** par artisan, interrogation **Pappers** (cache en base pour limiter les coûts), puis enrichissement **certifications** et contrôle **MAIF** selon le process métier.

"""
)
