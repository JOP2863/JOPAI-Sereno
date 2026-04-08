"""
Synthèse audio / vidéo via **Vertex AI** (Gemini) à partir d’objets **gs://** ou d’un upload GCS.

Le compte de service doit pouvoir lire l’objet (Vertex lit le média depuis GCS) et appeler le modèle.
"""

from __future__ import annotations

from typing import Any


DEFAULT_SUMMARY_PROMPT = (
    "Tu es un assistant pour une plateforme de dépannage à distance (SÉRÉNO). "
    "Résume ce média en **français**, de façon concise : contenu apparent, ambiance, "
    "éventuels gestes ou objets visibles (vidéo) ou le sujet parlé (audio). "
    "Si le média est illisible ou silencieux, dis-le clairement. Pas de markdown."
)


def upload_bytes_to_gcs(
    *,
    sa_info: dict[str, Any],
    bucket_name: str,
    object_name: str,
    data: bytes,
    content_type: str,
) -> tuple[bool, str]:
    """Retourne ``(True, gs_uri)`` ou ``(False, message_erreur)``."""
    try:
        from google.cloud import storage

        from sereno_core.gcp_credentials import credentials_for_gcp_clients

        creds = credentials_for_gcp_clients(sa_info)
        pid = str(sa_info.get("project_id") or "").strip() or None
        client = storage.Client(credentials=creds, project=pid)
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(object_name)
        blob.upload_from_string(data, content_type=content_type)
        return True, f"gs://{bucket_name}/{object_name}"
    except Exception as e:
        return False, str(e)


def summarize_gcs_media_with_vertex(
    *,
    sa_info: dict[str, Any],
    project_id: str,
    location: str,
    model_id: str,
    gcs_uri: str,
    mime_type: str,
    prompt: str | None = None,
) -> tuple[bool, str]:
    """
    ``gcs_uri`` : ``gs://bucket/object`` (bucket = celui du projet, SA avec lecture objet).
    """
    try:
        import vertexai
        from google.api_core import exceptions as gexc
        from vertexai.generative_models import GenerativeModel, Part

        from sereno_core.gcp_credentials import credentials_for_gcp_clients

        creds = credentials_for_gcp_clients(sa_info)
        vertexai.init(project=project_id, location=location, credentials=creds)
        model = GenerativeModel(model_id)
        user_prompt = (prompt or DEFAULT_SUMMARY_PROMPT).strip()
        parts = [Part.from_uri(gcs_uri, mime_type=mime_type), user_prompt]
        resp = model.generate_content(parts)
        text = (getattr(resp, "text", None) or "").strip()
        if not text:
            return False, "Réponse Vertex vide (vérifiez le modèle, le MIME et les droits sur l’objet GCS)."
        return True, text
    except gexc.PermissionDenied as e:
        from sereno_core.vertex_iam_hints import plain_vertex_predict_denied_suffix

        hint = plain_vertex_predict_denied_suffix(
            project_id=project_id,
            client_email=str(sa_info.get("client_email") or ""),
            location=location,
            model_id=model_id,
        )
        return False, f"Permission refusée (Vertex / GCS) : {e}\n\n{hint}"
    except gexc.NotFound as e:
        from sereno_core.vertex_iam_hints import plain_vertex_model_not_found_suffix

        hint = plain_vertex_model_not_found_suffix(
            project_id=project_id,
            location=location,
            model_id=model_id,
        )
        return False, f"Modèle ou ressource Vertex introuvable : {e}\n\n{hint}"
    except Exception as e:
        return False, str(e)
