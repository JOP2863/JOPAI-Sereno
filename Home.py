"""
SÉRÉNO — point d’entrée Streamlit.
Lancer : streamlit run Home.py

Navigation selon le rôle pilote (**Utilisateurs_Acces**) : accès **public** par défaut (parcours client
uniquement), menu complet après **Se connecter**.
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

from sereno_core.app_urls import CLIENT_URGENCE_QUERY_KEY
from sereno_core import pilot_auth
from sereno_core.streamlit_theme import apply_global_styles, render_sidebar_branding

_REPO_ROOT = Path(__file__).resolve().parent

st.set_page_config(page_title="SÉRÉNO — pilote JOPAI©", page_icon="🔧", layout="wide")
apply_global_styles()

if "sereno_pilot_role" not in st.session_state:
    st.session_state["sereno_pilot_role"] = pilot_auth.ROLE_PUBLIC

with st.sidebar:
    render_sidebar_branding()
    pilot_auth.render_auth_top_bar(_REPO_ROOT)
    st.divider()


def _client_flow_pages(*, accueil_default: bool) -> list[st.Page]:
    return [
        st.Page("pages/13_Proto_Guide_parcours.py", title="Guide parcours", icon="🗺️"),
        st.Page(
            "pages/4_Proto_Client_accueil.py",
            title="Accueil urgence",
            icon="🚨",
            url_path="accueil_urgence",
            default=accueil_default,
        ),
        st.Page("pages/5_Proto_Client_informations.py", title="Informations", icon="📝"),
        st.Page("pages/6_Proto_Client_SST.py", title="Sécurité (SST)", icon="🛡️"),
        st.Page("pages/7_Proto_Client_file_visio.py", title="Mise en relation & visio", icon="📞"),
        st.Page("pages/8_Proto_Client_visio.py", title="Session visio", icon="📹"),
        st.Page("pages/9_Proto_Client_paiement.py", title="Paiement", icon="💳"),
        st.Page("pages/10_Proto_Client_satisfaction.py", title="NPS (avis)", icon="📈"),
    ]


_projet = [
    st.Page("pages/0_Accueil.py", title="Accueil", icon="🏠", default=True),
    st.Page("pages/14_Projet_stats.py", title="Métriques (lignes CDC / code)", icon="📊"),
    st.Page("pages/19_Projet_reporting_indicateurs.py", title="Reporting (indicateurs CDC)", icon="📈"),
    st.Page("pages/2_Cahier_des_charges.py", title="Cahier des charges", icon="📋"),
    st.Page("pages/3_Carnet_echange.py", title="Carnet d’échange", icon="📒"),
    st.Page("pages/1_Tests_connexions.py", title="Tests connexions", icon="🔌"),
]

_prototype_client = _client_flow_pages(accueil_default=False)

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

_admin_artisan_seulement = [
    st.Page("pages/16_Admin_artisan_disponibilites.py", title="Dispo. artisan", icon="📆"),
]

_prototype_client_public = _client_flow_pages(accueil_default=True)


def _navigation_pages() -> dict[str, list[st.Page]]:
    role = pilot_auth.session_role()
    if role in (pilot_auth.ROLE_PUBLIC, "CLIENT_COMPTE", "CLIENT_PUBLIC"):
        return {"Prototype · Client": _prototype_client_public}
    if role == "ARTISAN":
        return {
            "Prototype · Artisan": _prototype_artisan,
            "Administration · Pilote": _admin_artisan_seulement,
        }
    # Propriétaire, compagnon, client inscrit (pilote) : accès complet menu Streamlit.
    return {
        "Projet": _projet,
        "Prototype · Client": _prototype_client,
        "Prototype · Artisan": _prototype_artisan,
        "Prototype · Propriétaire": _prototype_proprietaire,
        "Administration · Pilote": _admin_pilote,
    }


nav = st.navigation(
    _navigation_pages(),
    expanded=True,
)
# QR / lien direct : racine + ?client_urgence=1
if CLIENT_URGENCE_QUERY_KEY in st.query_params:
    st.switch_page("pages/4_Proto_Client_accueil.py")
nav.run()
