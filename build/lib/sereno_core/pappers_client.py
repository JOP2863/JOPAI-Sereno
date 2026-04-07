"""Client minimal API Pappers (fiche entreprise par SIREN) — cache côté app à prévoir en base."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Mapping

PAPPERS_ENTREPRISE_URL = "https://api.pappers.fr/v2/entreprise"


def fetch_entreprise_by_siren(
    *,
    api_token: str,
    siren: str,
    timeout_s: float = 45.0,
) -> tuple[int, dict[str, Any]]:
    """
    Appelle `GET /v2/entreprise` (paramètres `api_token`, `siren`).
    Retourne (code HTTP, corps JSON parsé ou dict d’erreur avec clé `error`).
    """
    siren9 = "".join(c for c in str(siren) if c.isdigit())[:9]
    token = str(api_token).strip()
    if len(siren9) != 9:
        return 400, {"error": "SIREN doit comporter 9 chiffres."}
    if not token:
        return 401, {"error": "Clé API manquante (PAPPERS_API_KEY)."}

    try:
        import requests
    except ImportError:
        return 500, {"error": "Paquet `requests` requis pour appeler l’API Pappers."}

    try:
        r = requests.get(
            PAPPERS_ENTREPRISE_URL,
            params={"api_token": token, "siren": siren9},
            timeout=timeout_s,
        )
    except requests.RequestException as e:
        return 599, {"error": str(e)}

    try:
        data = r.json()
    except Exception:
        data = {"error": "Réponse non JSON", "raw": (r.text or "")[:2000]}

    if isinstance(data, dict) and r.status_code >= 400 and "error" not in data:
        data = {**data, "http_status": r.status_code}
    return r.status_code, data if isinstance(data, dict) else {"data": data}


def pappers_api_key_from_secrets(secrets: Mapping[str, Any]) -> str:
    """Lit `PAPPERS_API_KEY` à la racine des secrets ou sous `[pappers] api_key`."""
    for k in ("PAPPERS_API_KEY", "pappers_api_key", "api_token"):
        v = secrets.get(k) if hasattr(secrets, "get") else None
        if v and str(v).strip():
            return str(v).strip()
    sub = secrets.get("pappers") if hasattr(secrets, "get") else None
    if isinstance(sub, dict):
        for k in ("api_key", "PAPPERS_API_KEY", "api_token"):
            v = sub.get(k)
            if v and str(v).strip():
                return str(v).strip()
    return ""


def row_for_papers_table(
    *,
    siren: str,
    expert_id: str | None,
    http_status: int,
    payload: Mapping[str, Any],
) -> dict[str, Any]:
    """Champs prêts à insérer (côté app / SQL) — `payload_json` = réponse API complète."""
    siren9 = "".join(c for c in str(siren) if c.isdigit())[:9]
    return {
        "siren": siren9,
        "expert_id": (expert_id or "").strip() or None,
        "http_status": http_status,
        "payload_json": json.dumps(payload, ensure_ascii=False),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "api_path": "/v2/entreprise",
    }
