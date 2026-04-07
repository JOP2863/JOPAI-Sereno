"""
SÉRÉNO — point d’entrée Streamlit.
Lancer : streamlit run Home.py

Navigation : **Projet** (outillage) · **Prototype** (Client / Artisan / Propriétaire).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def _ensure_sereno_core_importable() -> None:
    """
    Ajoute la racine du dépôt sur sys.path si `sereno_core` n’est pas déjà importable
    (pip install . / -e . peut échouer ou différer selon l’hébergeur).
    """
    try:
        import sereno_core  # noqa: F401
        return
    except ModuleNotFoundError:
        pass
    here = Path(__file__).resolve().parent
    candidates: list[Path] = []
    env_root = (os.environ.get("JOPAI_SERENO_REPO_ROOT") or "").strip()
    if env_root:
        candidates.append(Path(env_root))
    candidates.extend([here, here.parent, Path.cwd()])
    seen: set[Path] = set()
    for p in candidates:
        try:
            rp = p.resolve()
        except OSError:
            continue
        if rp in seen:
            continue
        seen.add(rp)
        if not (rp / "sereno_core" / "__init__.py").is_file():
            continue
        s = str(rp)
        if s not in sys.path:
            sys.path.insert(0, s)
        return


_ensure_sereno_core_importable()

import streamlit as st

from sereno_core.streamlit_theme import apply_global_styles, render_sidebar_branding

st.set_page_config(page_title="SÉRÉNO — JOPAI BTP", page_icon="🔧", layout="wide")
apply_global_styles()

with st.sidebar:
    render_sidebar_branding()

_projet = [
    st.Page("pages/0_Accueil.py", title="Accueil", icon="🏠", default=True),
    st.Page("pages/14_Projet_stats.py", title="Métriques (lignes CDC / code)", icon="📊"),
    st.Page("pages/19_Projet_reporting_indicateurs.py", title="Reporting (indicateurs CDC)", icon="📈"),
    st.Page("pages/2_Cahier_des_charges.py", title="Cahier des charges", icon="📋"),
    st.Page("pages/3_Carnet_echange.py", title="Carnet d’échange", icon="📒"),
    st.Page("pages/1_Tests_connexions.py", title="Tests connexions", icon="🔌"),
]

_prototype_client = [
    st.Page("pages/13_Proto_Guide_parcours.py", title="Guide parcours", icon="🗺️"),
    st.Page("pages/4_Proto_Client_accueil.py", title="Accueil urgence", icon="🚨"),
    st.Page("pages/5_Proto_Client_informations.py", title="Informations", icon="📝"),
    st.Page("pages/6_Proto_Client_SST.py", title="Sécurité (SST)", icon="🛡️"),
    st.Page("pages/7_Proto_Client_file_visio.py", title="Mise en relation & visio", icon="📞"),
    st.Page("pages/8_Proto_Client_visio.py", title="Session visio", icon="📹"),
    st.Page("pages/9_Proto_Client_paiement.py", title="Paiement", icon="💳"),
    st.Page("pages/10_Proto_Client_satisfaction.py", title="Satisfaction", icon="⭐"),
]

_prototype_artisan = [
    st.Page("pages/11_Proto_Artisan_dashboard.py", title="Tableau de bord", icon="🛠️"),
]

_prototype_proprietaire = [
    st.Page("pages/12_Proto_Proprietaire_activity.py", title="Activité", icon="📊"),
    st.Page("pages/18_Proto_Proprietaire_conformite.py", title="Conformité (SIREN / Pappers)", icon="🏛️"),
]

_admin_pilote = [
    st.Page("pages/16_Admin_artisan_disponibilites.py", title="Dispo. artisan", icon="📆"),
    st.Page("pages/17_Admin_proprietaire_disponibilites.py", title="Dispo. réseau (proprio)", icon="🏢"),
]

nav = st.navigation(
    {
        "Projet": _projet,
        "Prototype · Client": _prototype_client,
        "Prototype · Artisan": _prototype_artisan,
        "Prototype · Propriétaire": _prototype_proprietaire,
        "Administration · Pilote": _admin_pilote,
    },
    expanded=True,
)
nav.run()
