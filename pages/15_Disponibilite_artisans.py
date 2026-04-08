"""
Outil Projet — disponibilités artisans (onglets Sheets alignés CDC § 1.7.1).
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import pandas as pd
import streamlit as st

from sereno_core.gcp_credentials import credentials_for_sheets, get_service_account_info
from sereno_core.jopai_brand_html import page_title_h1_html
from sereno_core.sheets_schema import SHEET_TABS

st.markdown(page_title_h1_html("Disponibilités artisans (Sheets)"), unsafe_allow_html=True)
st.caption(
    "Structure prévue pour la **fenêtre glissante 12 mois**, saisie par **mois**, **astreinte** et **verrouillage J−30** "
    "(voir **CAHIER_DES_CHARGES.md § 1.7.1**). Les onglets sont créés par **`scripts/init_google_sheet.py`**."
)

st.markdown(
    """
| Onglet | Rôle |
|--------|------|
| **Disponibilite_Mois** | Par expert et mois (`AAAA-MM`) : mode `indisponible` · `standard` · `astreinte` · `sur_rdv`, dates de saisie / verrouillage. |
| **Creneau_Astreinte** | Détail optionnel : jour de semaine ou date, plage horaire, fuseau, priorité d’appel. |
| **Indisponibilite_Exception** | Congés, formation, etc. (début / fin, motif). |

**Règle métier (cible) :** au-delà de **30 jours** avant le début d’un mois, les créneaux de ce mois sont **figés** pour l’usager
(sauf action admin — à paramétrer en prod).
"""
)

st.subheader("En-têtes attendus (copier dans Sheets)")
for title in ("Disponibilite_Mois", "Creneau_Astreinte", "Indisponibilite_Exception"):
    tab = next((t for t in SHEET_TABS if t.title == title), None)
    if tab:
        st.markdown(f"**{title}** : `{chr(9).join(tab.headers)}`")

st.divider()
st.subheader("Lecture du classeur (si secrets configurés)")

try:
    sid = (st.secrets.get("gsheet_id") or "").strip()
except Exception:
    sid = ""

if not sid:
    st.info("Renseignez **`gsheet_id`** dans `.streamlit/secrets.toml` et le compte de service pour charger les tableaux ici.")
else:
    try:
        import gspread

        info = get_service_account_info(_REPO, st.secrets)
        creds = credentials_for_sheets(info)
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(sid)
        titles = [w.title for w in sh.worksheets()]
        for name in ("Disponibilite_Mois", "Creneau_Astreinte", "Indisponibilite_Exception"):
            if name not in titles:
                st.warning(f"Onglet **{name}** absent — lancez `python scripts/init_google_sheet.py` pour le créer.")
                continue
            ws = sh.worksheet(name)
            rows = ws.get_all_records()
            st.markdown(f"#### {name} ({len(rows)} ligne(s))")
            if rows:
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            else:
                st.caption("_Aucune donnée sous l’en-tête._")
    except Exception as e:
        st.error(f"Lecture Sheets impossible : {e}")

st.divider()
st.caption("Édition des lignes : pour l’instant via **Google Sheets** ; une saisie Streamlit pourra compléter le pilote.")
