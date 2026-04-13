"""
Authentification **pilote** SÉRÉNO : lecture de l’onglet **Utilisateurs_Acces** (Google Sheets),
session Streamlit, filtrage du menu (accès public par défaut).

Ce n’est **pas** une sécurité production : un **code pilote** (colonne **`code_pilote`**) permet de
choisir le bon **profil** lorsque le même **e-mail** apparaît sur plusieurs lignes.
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from typing import Any, Mapping

import streamlit as st

from sereno_core.gcp_credentials import credentials_for_sheets, get_service_account_info
from sereno_core.sheets_experts import resolve_gsheet_id

ROLE_PUBLIC = "PUBLIC"

# Valeurs par défaut du formulaire « Se connecter » (pilote — pas une sécurité production).
_DEFAULT_PILOT_LOGIN_EMAIL = "jop28@hotmail.com"
_DEFAULT_PILOT_LOGIN_CODE = "JOP28"


def _norm_header_key(key: str) -> str:
    n = unicodedata.normalize("NFKD", str(key).strip().lower())
    n = "".join(c for c in n if not unicodedata.combining(c))
    n = re.sub(r"[^a-z0-9]+", "_", n)
    return n.strip("_")


def _rows_from_worksheet(ws: Any) -> list[dict[str, Any]]:
    vals = ws.get_all_values()
    if len(vals) < 2:
        return []
    headers_raw = vals[0]
    out: list[dict[str, Any]] = []
    for ri in range(1, len(vals)):
        cells = vals[ri]
        row: dict[str, Any] = {}
        for ci, h_raw in enumerate(headers_raw):
            hs = str(h_raw).strip()
            if not hs:
                continue
            hk = _norm_header_key(hs)
            if not hk:
                continue
            row[hk] = cells[ci] if ci < len(cells) else ""
        if any(str(v).strip() for v in row.values()):
            out.append(row)
    return out


def _flex(norm_row: Mapping[str, Any], *names: str) -> str:
    for n in names:
        k = _norm_header_key(n)
        if k in norm_row and str(norm_row[k]).strip():
            return str(norm_row[k]).strip()
    return ""


def load_utilisateurs_acces(repo_root: Path, secrets: Mapping[str, Any] | Any) -> list[dict[str, str]] | None:
    """Retourne des lignes normalisées (clés : email, role, nom_affichage, actif, …) ou None."""
    try:
        import gspread
    except ImportError:
        return None

    sid = resolve_gsheet_id(repo_root, secrets).strip()
    if not sid:
        return None
    try:
        info = get_service_account_info(repo_root, secrets)
        creds = credentials_for_sheets(info)
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(sid)
        ws = sh.worksheet("Utilisateurs_Acces")
        raw = _rows_from_worksheet(ws)
    except Exception:
        return None

    out: list[dict[str, str]] = []
    for r in raw:
        email = _flex(r, "email", "mail", "courriel").lower().strip()
        role = _flex(r, "role", "profil", "type_acces").upper().strip()
        actif = _flex(r, "actif", "active", "enabled").upper()
        if not email or not role:
            continue
        if actif in ("NON", "NO", "0", "FALSE", "FAUX"):
            continue
        out.append(
            {
                "email": email,
                "role": role,
                "nom_affichage": _flex(r, "nom_affichage", "nom", "display_name"),
                "user_id": _flex(r, "user_id", "id", "utilisateur_id"),
                "expert_id_lie": _flex(r, "expert_id_lie", "expert_id"),
                "telephone": _flex(r, "telephone", "tel", "mobile"),
                "code_pilote": _flex(r, "code_pilote", "code_acces", "mot_de_passe_pilote", "mdp_pilote"),
                "notes": _flex(r, "notes", "note", "commentaire"),
            }
        )
    return out if out else None


def session_role() -> str:
    return str(st.session_state.get("sereno_pilot_role") or ROLE_PUBLIC).upper()


def session_claims() -> dict[str, str]:
    return {
        "email": str(st.session_state.get("sereno_pilot_email") or ""),
        "nom": str(st.session_state.get("sereno_pilot_nom") or ""),
        "role": session_role(),
    }


def _claims_from_row(r: dict[str, str]) -> dict[str, str]:
    return {
        "email": r["email"],
        "role": str(r["role"]).upper().strip(),
        "nom_affichage": r.get("nom_affichage") or "",
        "user_id": r.get("user_id") or "",
    }


def resolve_login(
    rows: list[dict[str, str]],
    email: str,
    code_pilote: str,
) -> tuple[dict[str, str] | None, str]:
    """
    Sélectionne une ligne pour cet e-mail. **Code pilote** obligatoire si plusieurs lignes
    partagent le même e-mail ; pour une seule ligne, le code n’est exigé que s’il est renseigné dans Sheets.
    Retourne ``(claims, message_erreur)`` avec ``message_erreur`` vide en cas de succès.
    """
    em = email.strip().lower()
    code_in = (code_pilote or "").strip()
    if not em:
        return None, "Saisissez un e-mail."
    matches = [r for r in rows if r["email"] == em]
    if not matches:
        return None, "E-mail inconnu ou profil inactif."
    if len(matches) == 1:
        r0 = matches[0]
        need = (r0.get("code_pilote") or "").strip()
        if need and code_in != need:
            return None, "Code pilote incorrect."
        return _claims_from_row(r0), ""
    if not code_in:
        return (
            None,
            "Plusieurs profils utilisent cet e-mail : saisissez le **code pilote** "
            "(colonne **code_pilote** dans **Utilisateurs_Acces**).",
        )
    sub = [r for r in matches if (r.get("code_pilote") or "").strip() == code_in]
    if not sub:
        return None, "Code pilote incorrect (aucun profil ne correspond à ce code)."
    if len(sub) > 1:
        return None, "Plusieurs lignes partagent le même code pilote : corrigez la feuille."
    return _claims_from_row(sub[0]), ""


def logout() -> None:
    for k in (
        "sereno_pilot_role",
        "sereno_pilot_email",
        "sereno_pilot_nom",
        "sereno_users_sheet_cache",
        "sereno_pilot_login_email",
        "sereno_pilot_login_code",
    ):
        st.session_state.pop(k, None)
    st.session_state["sereno_pilot_role"] = ROLE_PUBLIC


def login_with_row(claims: dict[str, str]) -> None:
    st.session_state["sereno_pilot_role"] = str(claims.get("role") or ROLE_PUBLIC).upper()
    st.session_state["sereno_pilot_email"] = str(claims.get("email") or "")
    st.session_state["sereno_pilot_nom"] = str(claims.get("nom_affichage") or "")
    st.session_state.pop("sereno_users_sheet_cache", None)


def render_auth_top_bar(repo_root: Path) -> None:
    """Connexion / déconnexion pilote — prévu pour la **barre latérale** (lisible, au-dessus du filigrane)."""
    role = session_role()
    nom = str(st.session_state.get("sereno_pilot_nom") or "")
    email = str(st.session_state.get("sereno_pilot_email") or "")

    st.markdown('<p class="sereno-pilot-auth-sidebar-title">Compte (pilote)</p>', unsafe_allow_html=True)
    if role != ROLE_PUBLIC and email:
        st.caption(f"**{nom or email}** · *{role}*")
        if st.button("Se déconnecter", key="sereno_pilot_logout", use_container_width=True):
            logout()
            st.rerun()
    else:
        use_popover = hasattr(st, "popover")
        if use_popover:
            with st.popover("Se connecter"):
                _login_form(repo_root)
        else:
            with st.expander("Se connecter", expanded=False):
                _login_form(repo_root)


def _login_form(repo_root: Path) -> None:
    if "sereno_pilot_login_email" not in st.session_state:
        st.session_state["sereno_pilot_login_email"] = _DEFAULT_PILOT_LOGIN_EMAIL
    if "sereno_pilot_login_code" not in st.session_state:
        st.session_state["sereno_pilot_login_code"] = _DEFAULT_PILOT_LOGIN_CODE
    st.caption(
        "Pilote : **e-mail** + éventuellement **code pilote** (une même adresse peut avoir plusieurs "
        "lignes : propriétaire, compagnon par périmètre, etc.)."
    )
    mail = st.text_input("E-mail", key="sereno_pilot_login_email")
    code = st.text_input(
        "Code pilote",
        type="password",
        help="Obligatoire si l’e-mail a plusieurs profils dans Utilisateurs_Acces. "
        "Valeur = colonne code_pilote dans la feuille.",
        key="sereno_pilot_login_code",
    )
    if st.button("Valider", type="primary", key="sereno_pilot_login_submit"):
        if not mail.strip():
            st.warning("Saisissez un e-mail.")
            return
        if "sereno_users_sheet_cache" not in st.session_state:
            st.session_state["sereno_users_sheet_cache"] = load_utilisateurs_acces(
                repo_root, st.secrets
            )
        rows = st.session_state.get("sereno_users_sheet_cache")
        if not rows:
            st.error(
                "Impossible de lire **Utilisateurs_Acces** (Sheets ou onglet absent). "
                "Vérifiez `gsheet_id` et la migration schéma."
            )
            return
        claims, err = resolve_login(rows, mail, code)
        if not claims:
            st.error(err or "Connexion impossible.")
            return
        login_with_row(claims)
        st.rerun()
