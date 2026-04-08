"""
Prototype — carte du parcours (documentation vivante dans la nav).
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import streamlit as st  # noqa: E402 — après insertion sys.path

from sereno_core.jopai_brand_html import page_title_h1_html
from sereno_core.proto_state import ensure_demo_seed
from sereno_core.streamlit_theme import inject_sereno_prototype_css

inject_sereno_prototype_css()
ensure_demo_seed()

st.markdown(page_title_h1_html("Guide du parcours"), unsafe_allow_html=True)
st.caption("Vue d’ensemble des écrans **client** et des espaces **artisan** / **propriétaire**.")
st.info(
    "Dans le menu latéral, le **Prototype** est regroupé en trois sections : "
    "**Prototype · Client**, **Prototype · Artisan**, **Prototype · Propriétaire**."
)

st.markdown(
    """
Avant la visio, une étape **sécurité** : consignes simples (eau, électricité, gaz…). Dans le menu, l’intitulé reprend l’abréviation
**SST**, qui signifie en toutes lettres **Sécurité et Santé au travail** (vocabulaire habituel sur les chantiers ; ici appliqué aux **gestes sûrs** chez soi avant d’allumer la caméra).

### Parcours client

1. **Accueil urgence** — choix du type (eau, élec, gaz, chauffage, serrurerie).
2. **Informations** — prénom / téléphone (réassurance), e-mail optionnel.
3. **Sécurité (SST)** — checklist obligatoire avant visio.
4. **Mise en relation & visio** — attente courte, appel des experts dans l’ordre défini, puis **lien vers la salle** de visio.
5. **Session visio** — échange vidéo (salle fournie par le fournisseur configuré : Daily, Twilio, etc.).
6. **Paiement** — forfait affiché et passage au moyen de paiement selon l’intégration en production.
7. **Satisfaction** — **NPS** 0–10, commentaire optionnel.

### Côté artisan

- **Tableau de bord** : activité et avis filtrés par expert ; liens vers le **reporting** (métriques projet) et la **saisie des disponibilités** (règles CDC § 1.7.1, fenêtre sensible & notification propriétaire).

### Côté propriétaire

- **Activité** : vision transverse des sessions et export des données utiles au pilotage.
- **Conformité réseau** : saisie **SIREN** par artisan, interrogation **Pappers** (cache en base pour limiter les coûts), puis enrichissement **certifications** et contrôle **MAIF** selon le process métier.

"""
)
