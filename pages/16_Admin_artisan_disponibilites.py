"""
Administration · pilote — saisie des disponibilités **côté artisan** (auto-déclarée).

Pas d’authentification réelle : choix d’un **expert_id** dans la liste chargée depuis Sheets.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import pandas as pd
import streamlit as st

from sereno_core.disponibilite_calendar_ui import (
    append_recap_to_comment_key,
    filter_disponibilite_df,
    render_disponibilite_mois_chart,
    render_month_unavailability_assistant,
    render_week_unavailability_assistant,
)
from sereno_core.gcp_credentials import credentials_for_sheets, get_service_account_info
from sereno_core.jopai_brand_html import page_title_h1_html
from sereno_core.proto_state import ensure_demo_seed, p_get
from sereno_core.sheets_disponibilite_write import append_disponibilite_mois_row, mois_sous_verrouillage_artisan
from sereno_core.sheets_experts import disponibilite_expert_options, resolve_gsheet_id

_COM_KEY = "com_dispo_artisan_16"
_RECAP_KEY = "sereno_dispo_week_recap_16"
_RECAP_MONTH_KEY = "sereno_dispo_month_recap_16"

st.markdown(page_title_h1_html("Administration · Mes disponibilités (artisan)"), unsafe_allow_html=True)
st.caption(
    "Premier jet — règles cibles décrites dans le CDC § 1.7.1 ; la table **utilisateur** réelle viendra avec l’auth."
)

st.markdown(
    """
### Règles prévues (pilote)

- **Mois proche** : si le **1ᵉʳ jour du mois** choisi est dans **moins de 30 jours**, la saisie est considérée comme **sensible** :
  l’artisan ne doit **pas** la modifier seul sans **notifier le propriétaire** (case à cocher ci-dessous — simulation).
- **Au-delà** : l’artisan peut **pré-renseigner** les mois plus lointains sans cette contrainte.
- **Propriétaire** : ne modifie pas les disponibilités d’un artisan **sans interaction** avec lui (voir page dédiée).

*Ce formulaire écrit une ligne dans l’onglet **Disponibilite_Mois** si les secrets Sheets sont valides.*
"""
)

ensure_demo_seed()
artisans: list = list(p_get("artisans", []))
opt_labels, opt_to_expert = disponibilite_expert_options(artisans)

if not opt_labels:
    st.warning("Aucun expert en session — configurez **Experts** dans Sheets et rechargez l’app.")
    st.stop()

st.subheader("Déclarer une disponibilité pour un mois")
c1, c2, c3 = st.columns(3)
with c1:
    pick = st.selectbox(
        "Expert et corps de métier (simulation connexion)",
        options=opt_labels,
        help="Une ligne par type d’intervention autorisé pour l’expert (ex. Gaz et Eau → deux lignes).",
    )
    expert_id = opt_to_expert[pick]
with c2:
    mois = st.text_input("Mois (AAAA-MM)", value="2026-06", help="Ex. 2026-06")
with c3:
    mode = st.selectbox(
        "Mode",
        options=["standard", "astreinte", "sur_rdv", "indisponible"],
    )

commentaire = st.text_input("Commentaire interne (optionnel)", "", key=_COM_KEY)

with st.expander("Assistant **semaine** (décocher = indisponible par créneau) — texte pour le commentaire", expanded=False):
    render_week_unavailability_assistant(recap_state_key=_RECAP_KEY)
    append_recap_to_comment_key(recap_state_key=_RECAP_KEY, comment_session_key=_COM_KEY)

with st.expander("Assistant **mois** (calendrier type planning — décocher = jour indisponible)", expanded=False):
    render_month_unavailability_assistant(recap_state_key=_RECAP_MONTH_KEY, key_prefix="dispo_cal_16")
    append_recap_to_comment_key(recap_state_key=_RECAP_MONTH_KEY, comment_session_key=_COM_KEY)

verrou = mois_sous_verrouillage_artisan(mois) if re.fullmatch(r"\d{4}-\d{2}", mois.strip()) else True
if verrou:
    st.warning(
        "Ce mois est dans la **fenêtre sensible** (< 30 jours avant son début, ou mois passé). "
        "Cochez la case si vous confirmez avoir **notifié le propriétaire** (simulation)."
    )
    notif = st.checkbox("J’ai notifié le propriétaire (pilote / simulation)")
else:
    notif = True

submitted = st.button("Enregistrer dans Disponibilite_Mois", type="primary")

if submitted:
    if not re.fullmatch(r"\d{4}-\d{2}", mois.strip()):
        st.error("Format mois invalide : utilisez AAAA-MM.")
    elif verrou and not notif:
        st.error("Cochez la notification propriétaire pour ce mois, ou choisissez un mois plus lointain.")
    else:
        ok, msg = append_disponibilite_mois_row(
            _REPO,
            dict(st.secrets),
            expert_id=expert_id,
            annee_mois=mois.strip(),
            mode=mode,
            commentaire_interne=str(st.session_state.get(_COM_KEY, commentaire) or ""),
        )
        if ok:
            st.success(msg)
        else:
            st.error(msg)

st.divider()
st.subheader("Lecture du classeur (Disponibilite_Mois)")
sid = resolve_gsheet_id(_REPO, dict(st.secrets)).strip()
if not sid:
    st.info("**gsheet_id** manquant — lecture impossible.")
else:
    try:
        import gspread

        info = get_service_account_info(_REPO, st.secrets)
        creds = credentials_for_sheets(info)
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(sid)
        ws = sh.worksheet("Disponibilite_Mois")
        rows = ws.get_all_records()
        df = pd.DataFrame(rows)
        df_show = filter_disponibilite_df(df, str(expert_id)) if len(df) and "expert_id" in df.columns else df
        render_disponibilite_mois_chart(
            df_show if len(df_show) else df,
            title="Synthèse temporelle (lignes affichées — volume par mode et par mois)",
        )
        st.dataframe(df_show if len(df_show) else df, use_container_width=True, hide_index=True)
    except Exception as e:
        st.warning(f"Lecture impossible : {e}")
