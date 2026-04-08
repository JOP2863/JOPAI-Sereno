"""
Aide diagnostic **Vertex AI** (IAM, région) — texte réutilisable par la page Tests connexions et les appels média.
"""

from __future__ import annotations


def markdown_vertex_predict_denied(
    *,
    project_id: str,
    client_email: str,
    location: str,
    model_id: str,
) -> str:
    """Bloc Markdown pour afficher après un 403 ``aiplatform.endpoints.predict``."""
    sa = (client_email or "").strip() or "l’e-mail de votre compte de service"
    pid = (project_id or "").strip() or "VOTRE_PROJET"
    loc = (location or "").strip() or "europe-west1"
    mid = (model_id or "").strip() or "gemini-1.5-flash"
    iam = f"https://console.cloud.google.com/iam-admin/iam?project={pid}"
    api = f"https://console.cloud.google.com/apis/library/aiplatform.googleapis.com?project={pid}"
    return (
        f"**Compte de service concerné :** `{sa}`  \n"
        f"**Projet :** `{pid}` · **Région actuelle (`vertex_location`) :** `{loc}` · **Modèle :** `{mid}`  \n\n"
        f"1. Ouvrir [IAM du projet]({iam}) → **Accorder un accès** → ajouter la **même** adresse de compte de service "
        "avec le rôle **Vertex AI User** (`roles/aiplatform.user`).  \n"
        f"2. Vérifier que l’[**API Vertex AI**]({api}) est **activée** sur ce projet.  \n"
        "3. Si l’erreur persiste : essayer `vertex_location = \"europe-west4\"` ou `\"us-central1\"` dans les secrets, "
        "et un identifiant de modèle **versionné** supporté dans cette région "
        "(ex. `gemini-1.5-flash-002`, `gemini-2.0-flash-001` — voir la doc des versions)."
    )


_MODEL_VERSIONS_URL = "https://cloud.google.com/vertex-ai/generative-ai/docs/learn/model-versions"


def markdown_vertex_model_not_found(
    *,
    project_id: str,
    location: str,
    model_id: str,
) -> str:
    """Bloc Markdown après une erreur 404 « Publisher Model … was not found » (nom ou région incorrects)."""
    pid = (project_id or "").strip() or "VOTRE_PROJET"
    loc = (location or "").strip() or "europe-west1"
    mid = (model_id or "").strip() or "gemini-1.5-flash"
    return (
        f"Le modèle **`{mid}`** n’est pas disponible sous ce nom dans **`{loc}`** pour le projet **`{pid}`** "
        "(identifiant obsolète, ou région sans ce modèle).  \n\n"
        f"1. Consulter les [versions de modèles Vertex AI]({_MODEL_VERSIONS_URL}) et copier un **model ID** exact.  \n"
        "2. Dans `.streamlit/secrets.toml`, essayer par exemple `vertex_model = \"gemini-2.0-flash-001\"` ou "
        "`\"gemini-1.5-flash-002\"` (les noms courts type `gemini-1.5-flash` peuvent renvoyer **404** selon la région).  \n"
        "3. Si besoin, changer `vertex_location` (ex. `europe-west4`, `us-central1`) pour une région où le modèle choisi est listé."
    )


def plain_vertex_model_not_found_suffix(
    *,
    project_id: str,
    location: str,
    model_id: str,
) -> str:
    """Version texte pour concaténation (ex. retour `summarize_gcs_media_with_vertex`)."""
    return (
        f"Modèle Vertex introuvable dans cette région : vérifier vertex_model (ID versionné, ex. gemini-1.5-flash-002) "
        f"et vertex_location. Doc versions : {_MODEL_VERSIONS_URL} "
        f"(projet={project_id!r} location={location!r} model={model_id!r})."
    )


def plain_vertex_predict_denied_suffix(
    *,
    project_id: str,
    client_email: str,
    location: str,
    model_id: str,
) -> str:
    """Version texte brut pour concaténation dans un message d’erreur (sans Markdown)."""
    return (
        "À faire : IAM du projet GCP → rôle Vertex AI User (roles/aiplatform.user) pour le compte de service ; "
        "API Vertex AI activée ; éventuellement changer vertex_location (europe-west4, us-central1) ou vertex_model. "
        f"Projet={project_id!r} SA={client_email!r} location={location!r} model={model_id!r}."
    )
