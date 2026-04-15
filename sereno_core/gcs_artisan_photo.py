"""
Upload photo artisan vers Google Cloud Storage (pilote).

Convention objet : ``{prefix}/{expert_id}.jpg`` (ex. ``artisan/EXP-001.jpg``).
"""

from __future__ import annotations

import base64
from pathlib import Path
from typing import Any, Mapping


def _artisan_prefix(secrets: Mapping[str, Any] | Any) -> str:
    pref = "artisan"
    try:
        pref = str(secrets.get("gcs_artisan_prefix") or secrets.get("gcs_artisan_photo_prefix") or "artisan").strip().strip("/")
    except Exception:
        pass
    return pref or "artisan"


def artisan_photo_blob_variants(expert_id: str, secrets: Mapping[str, Any] | Any) -> list[str]:
    """
    Chemins d’objets possibles dans le bucket (GCS est **sensible à la casse** sur le nom d’objet).
    Ex. fichier déposé en ``artisan/EXP-001.JPG`` vs code qui cherchait ``.jpg``.
    """
    eid = str(expert_id or "").strip()
    if not eid:
        return []
    base = f"{_artisan_prefix(secrets)}/{eid}"
    return [f"{base}.jpg", f"{base}.JPG", f"{base}.jpeg", f"{base}.JPEG"]


def artisan_photo_blob_path(expert_id: str, secrets: Mapping[str, Any] | Any) -> str:
    """Convention d’écriture / colonne Sheets : toujours ``…/{expert_id}.jpg`` (minuscules)."""
    eid = str(expert_id or "").strip()
    if not eid:
        return ""
    return f"{_artisan_prefix(secrets)}/{eid}.jpg"


def artisan_bucket_name(secrets: Mapping[str, Any] | Any) -> str:
    try:
        b = str(secrets.get("gcs_artisan_bucket") or secrets.get("gcs_bucket_name") or "jopai-sereno").strip()
    except Exception:
        b = "jopai-sereno"
    return b or "jopai-sereno"


def expert_photo_public_url(expert_id: str, secrets: Mapping[str, Any] | Any) -> str:
    """URL publique (objet doit être lisible en lecture publique ou via CDN)."""
    bid = artisan_bucket_name(secrets)
    blob = artisan_photo_blob_path(expert_id, secrets)
    if not blob:
        return ""
    return f"https://storage.googleapis.com/{bid}/{blob}"


def download_artisan_photo_bytes(
    repo_root: Path,
    secrets: Mapping[str, Any] | Any,
    *,
    expert_id: str,
) -> tuple[bytes, str] | None:
    """
    Télécharge la photo depuis GCS via le compte de service (ne dépend pas d’un bucket public).
    Retourne (bytes, mime) ou None.
    """
    eid = str(expert_id or "").strip()
    if not eid:
        return None
    cache_key = f"_sereno_artisan_photo_bytes_v2_{eid}"
    try:
        import streamlit as st

        if cache_key in st.session_state:
            hit = st.session_state[cache_key]
            return hit if isinstance(hit, tuple) else None
    except Exception:
        st = None  # type: ignore[assignment]

    variants = artisan_photo_blob_variants(eid, secrets)
    if not variants:
        return None
    try:
        from google.cloud import storage

        from sereno_core.gcp_credentials import credentials_for_gcp_clients, get_service_account_info

        info = get_service_account_info(repo_root, secrets)
        creds = credentials_for_gcp_clients(info)
        client = storage.Client(credentials=creds, project=info.get("project_id"))
        bucket = client.bucket(artisan_bucket_name(secrets))
        data: bytes | None = None
        used = ""
        for blob_path in variants:
            blob = bucket.blob(blob_path)
            try:
                data = blob.download_as_bytes()
                used = blob_path
            except Exception:
                data = None
            if data:
                break
        if not data:
            try:
                if st is not None:
                    st.session_state[cache_key] = False  # type: ignore[attr-defined]
            except Exception:
                pass
            return None
        mime = "image/jpeg"
        if used.lower().endswith(".png"):
            mime = "image/png"
        tup = (data, mime)
        try:
            if st is not None:
                st.session_state[cache_key] = tup  # type: ignore[attr-defined]
        except Exception:
            pass
        return tup
    except Exception:
        try:
            if st is not None:
                st.session_state[cache_key] = False  # type: ignore[attr-defined]
        except Exception:
            pass
        return None


def clear_artisan_photo_session_cache(expert_id: str) -> None:
    """Après upload / renommage d’objet dans GCS, invalider le cache navigateur-session."""
    eid = str(expert_id or "").strip()
    if not eid:
        return
    try:
        import streamlit as st

        for k in (
            f"_sereno_artisan_photo_bytes_v2_{eid}",
            f"_sereno_artisan_photo_bytes_{eid}",
        ):
            st.session_state.pop(k, None)
    except Exception:
        pass


def expert_photo_data_url(
    repo_root: Path,
    secrets: Mapping[str, Any] | Any,
    *,
    expert_id: str,
) -> str:
    """Data-URL (base64) pour usage HTML (`<img src=...>`)."""
    tup = download_artisan_photo_bytes(repo_root, secrets, expert_id=expert_id)
    if not tup:
        return ""
    data, mime = tup
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:{mime};base64,{b64}"


def upload_artisan_photo_jpg(
    repo_root: Path,
    secrets: Mapping[str, Any] | Any,
    *,
    expert_id: str,
    data: bytes,
) -> tuple[bool, str]:
    """Écrit l’image en ``image/jpeg`` sur le chemin conventionnel."""
    eid = str(expert_id or "").strip()
    if not eid:
        return False, "expert_id vide"
    if not data:
        return False, "fichier vide"
    try:
        from google.cloud import storage

        from sereno_core.gcp_credentials import credentials_for_gcp_clients, get_service_account_info

        info = get_service_account_info(repo_root, secrets)
        creds = credentials_for_gcp_clients(info)
        client = storage.Client(credentials=creds, project=info.get("project_id"))
        bucket = client.bucket(artisan_bucket_name(secrets))
        blob = bucket.blob(artisan_photo_blob_path(eid, secrets))
        blob.upload_from_string(data, content_type="image/jpeg")
        clear_artisan_photo_session_cache(eid)
        return True, ""
    except Exception as e:
        return False, str(e)
