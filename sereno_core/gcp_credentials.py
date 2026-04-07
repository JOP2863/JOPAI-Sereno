"""
Chargement du compte de service Google pour Sheets, GCS, Vertex.

Priorité :
1. Table `[gcp_service_account]` dans l’objet `secrets` passé (Streamlit ou dict TOML).
2. **Repli disque :** relire `.streamlit/secrets.toml` avec `tomllib` — nécessaire car `st.secrets`
   n’expose parfois pas correctement les tables imbriquées selon versions / hébergeur.
3. Fichier JSON : clé `service_account_json_path` (chemin relatif au dépôt).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from google.oauth2.service_account import Credentials

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore[no-redef, unused-ignore]


def _section_to_dict(section: Any) -> dict[str, Any]:
    if section is None:
        return {}
    if isinstance(section, dict):
        return {str(k): v for k, v in section.items()}
    out: dict[str, Any] = {}
    try:
        for k in section:
            out[str(k)] = section[k]
    except Exception:
        pass
    return out


def _sa_dict_valid(info: Mapping[str, Any]) -> bool:
    pk = info.get("private_key")
    em = info.get("client_email")
    if not pk or not em:
        return False
    if isinstance(pk, str):
        pk = pk.strip()
    return bool(pk) and bool(str(em).strip())


def _get_nested(secrets: Any, key: str) -> Any:
    """Streamlit `st.secrets` : préférer `secrets[key]` si `.get` ne voit pas la table."""
    if secrets is None:
        return None
    try:
        if hasattr(secrets, "get"):
            v = secrets.get(key)
            if v is not None:
                return v
    except Exception:
        pass
    try:
        return secrets[key]
    except Exception:
        return None


def _from_gcp_table(raw: Any) -> dict[str, Any] | None:
    if raw is None:
        return None
    info = _section_to_dict(raw)
    return info if _sa_dict_valid(info) else None


def _load_sa_from_streamlit_toml(repo_root: Path) -> dict[str, Any] | None:
    path = repo_root / ".streamlit" / "secrets.toml"
    if not path.is_file():
        return None
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    nested = data.get("gcp_service_account")
    if not isinstance(nested, dict):
        return None
    info = {str(k): nested[k] for k in nested}
    return info if _sa_dict_valid(info) else None


def get_service_account_info(repo_root: Path, secrets: Mapping[str, Any] | Any) -> dict[str, Any]:
    """
    Retourne le dict « service account JSON » attendu par google-auth
    (type, project_id, private_key_id, private_key, client_email, …).
    """
    got = _from_gcp_table(_get_nested(secrets, "gcp_service_account"))
    if got:
        return got

    got = _load_sa_from_streamlit_toml(repo_root)
    if got:
        return got

    rel = None
    try:
        rel = secrets.get("service_account_json_path") if hasattr(secrets, "get") else None
    except Exception:
        rel = None
    if rel is None:
        p = repo_root / ".streamlit" / "secrets.toml"
        if p.is_file():
            try:
                data = tomllib.loads(p.read_text(encoding="utf-8"))
                rel = data.get("service_account_json_path")
            except Exception:
                rel = None

    if rel:
        path = repo_root / str(rel)
        if path.is_file():
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict) and data.get("private_key"):
                return data

    hint = (
        "Vérifier que `.streamlit/secrets.toml` contient bien une section "
        "`[gcp_service_account]` avec au minimum `private_key` et `client_email` "
        "(copie du JSON téléchargé dans la console GCP). "
        "Si vous utilisez Streamlit Cloud, collez la même section dans **Settings → Secrets**. "
        "Alternative : `service_account_json_path` pointant vers un fichier `.json`."
    )
    raise ValueError(f"Compte de service introuvable. {hint}")


def gcp_project_id(secrets: Mapping[str, Any], info: Mapping[str, Any]) -> str:
    """Projet GCP pour les APIs : clé racine ou champ du compte de service."""
    for key in ("gcp_project_id", "project_id"):
        v = secrets.get(key)
        if v:
            return str(v)
    v = info.get("project_id")
    return str(v) if v else ""


def credentials_for_sheets(info: dict[str, Any]) -> Credentials:
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    return Credentials.from_service_account_info(info, scopes=scopes)


def credentials_for_gcp_clients(info: dict[str, Any]) -> Credentials:
    """GCS, Vertex, etc. — scope cloud-platform."""
    return Credentials.from_service_account_info(
        info,
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )
