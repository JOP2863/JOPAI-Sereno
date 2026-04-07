"""
Prototype propriétaire — conformité artisan : SIREN, cache Pappers, pistes certifications / MAIF.

Les appels API sont facturés : en production, persister chaque réponse dans la table **`papers`**
(voir `scripts/sql/create_papers_cache_table.sql`). Ici, réutilisation en **session** pour limiter les doublons.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import streamlit as st

from sereno_core.pappers_client import (
    fetch_entreprise_by_siren,
    pappers_api_key_from_secrets,
    row_for_papers_table,
)
from sereno_core.proto_state import ensure_demo_seed, p_get
from sereno_core.proto_ui import proto_page_start
from sereno_core.sheets_experts import disponibilite_expert_options

proto_page_start(
    title="Conformité réseau (SIREN & données entreprise)",
    subtitle="Interrogation **Pappers** pour enrichir le dossier artisan ; certifications et **MAIF** à croiser ensuite.",
    show_urgence_ambiance=False,
)

ensure_demo_seed()
secrets = dict(st.secrets)
api_key = pappers_api_key_from_secrets(secrets)

st.markdown(
    """
### Parcours cible (production)

1. Le **propriétaire** sélectionne un **artisan** du réseau et saisit son **SIREN** (9 chiffres).
2. **Premier appel** : interrogation Pappers ; la **réponse JSON complète** est stockée en base (**table `papers`**).
3. **Lectures suivantes** : servir le cache si la donnée est encore valide (politique de fraîcheur à définir),
   pour **ne pas repayer** le même SIREN inutilement.
4. **Certifications** : comparer les qualifications attendues au profil entreprise / dirigeants ; proposer des manques.
5. **MAIF** : vérifier l’inscription / couverture selon votre process (API, fichier d’adhérents, ou saisie manuelle contrôlée).
"""
)

if not api_key:
    st.warning(
        "Ajoutez **`PAPPERS_API_KEY`** dans les secrets Streamlit (fichier TOML) pour activer les appels réels."
    )

artisans: list = list(p_get("artisans", []))
opt_labels, opt_to_expert = disponibilite_expert_options(artisans)
if not opt_labels:
    st.stop()

pick = st.selectbox(
    "Artisan et spécialité concernés",
    options=opt_labels,
    help="Une ligne par type d’intervention autorisé pour l’expert (comme sur la page Dispo. artisan).",
)
expert_id = opt_to_expert[pick]

siren_in = st.text_input("SIREN (9 chiffres)", max_chars=11, placeholder="123456789")
force_refresh = st.checkbox("Forcer un nouvel appel API (ignore le cache session)", value=False)

if "pappers_session_cache" not in st.session_state:
    st.session_state.pappers_session_cache = {}

cache: dict = st.session_state.pappers_session_cache
siren_clean = "".join(c for c in siren_in if c.isdigit())

col_a, col_b = st.columns(2)
with col_a:
    go = st.button("Interroger Pappers", type="primary", disabled=len(siren_clean) != 9 or not api_key)
with col_b:
    st.caption("Chaque consultation API consomme des crédits — privilégier le cache base + session.")

if go:
    if len(siren_clean) != 9:
        st.error("SIREN invalide : exactement 9 chiffres.")
    elif not force_refresh and siren_clean in cache:
        st.info("Données déjà en cache session — cochez « Forcer » pour rappeler l’API.")
    else:
        status, payload = fetch_entreprise_by_siren(api_token=api_key, siren=siren_clean)
        cache[siren_clean] = {"http_status": status, "payload": payload}
        st.session_state.pappers_session_cache = cache

entry = cache.get(siren_clean) if len(siren_clean) == 9 else None
if entry and api_key:
    status = entry.get("http_status")
    payload = entry.get("payload") or {}
    st.subheader("Dernière réponse (cache session)")
    st.metric("HTTP", str(status))
    if status and int(status) >= 400:
        st.error("Réponse API en erreur — vérifier le SIREN et les crédits Pappers.")
    row = row_for_papers_table(
        siren=siren_clean,
        expert_id=expert_id,
        http_status=int(status or 0),
        payload=payload,
    )
    with st.expander("Ligne type pour insertion SQL (extrait du JSON pour l’aperçu)"):
        pj = row["payload_json"]
        preview = {**row, "payload_json": (pj[:800] + "…") if len(pj) > 800 else pj}
        st.code(json.dumps(preview, ensure_ascii=False, indent=2), language="json")
    with st.expander("JSON complet API"):
        st.json(payload)

st.divider()
st.subheader("Certifications & MAIF (pistes produit)")
st.markdown(
    """
- **Certifications** : table métier des qualifications requises par métier (eau, gaz, élec…) ; scoring par rapport
  aux libellés / activités dans le JSON Pappers et aux pièces uploadées par l’artisan.
- **MAIF** : statut « inscrit / non trouvé / à valider » stocké côté SÉRÉNO ; pas fourni par Pappers — source
  process interne ou partenaire.
"""
)
