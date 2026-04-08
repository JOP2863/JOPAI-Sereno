"""
Enregistrements visio — règles de nommage + déclenchement (Daily, optionnel).

Objectif : pouvoir stocker les médias dans le bucket GCS avec un nom stable, lisible et unique.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Mapping


def _slug(s: str) -> str:
    s2 = re.sub(r"\s+", "-", (s or "").strip())
    s2 = re.sub(r"[^a-zA-Z0-9_-]+", "", s2)
    s2 = re.sub(r"-{2,}", "-", s2).strip("-_")
    return s2 or "NA"


def build_visio_object_prefix(
    *,
    client_pseudo: str,
    session_id: str,
    urgence_code: str,
    urgence_label: str,
    started_at_utc: datetime | None = None,
) -> str:
    """
    Format (dossiers) :
    `visio/YYYY/MM/DD/<pseudo>__<session>__<code>-<label>/`
    """
    dt = started_at_utc or datetime.now(timezone.utc)
    y = dt.strftime("%Y")
    m = dt.strftime("%m")
    d = dt.strftime("%d")
    pseudo = _slug(client_pseudo)[:32]
    sid = _slug(session_id)[:24]
    u = f"{_slug(urgence_code)[:8]}-{_slug(urgence_label)[:24]}"
    return f"visio/{y}/{m}/{d}/{pseudo}__{sid}__{u}/"


def daily_api_key_from_secrets(secrets: Mapping[str, Any]) -> str:
    for k in ("DAILY_API_KEY", "daily_api_key"):
        try:
            v = secrets.get(k)
        except Exception:
            v = None
        if v and str(v).strip():
            return str(v).strip()
    sub = None
    try:
        sub = secrets.get("daily")
    except Exception:
        sub = None
    if isinstance(sub, dict):
        for k in ("api_key", "DAILY_API_KEY"):
            v = sub.get(k)
            if v and str(v).strip():
                return str(v).strip()
    return ""


def _daily_room_name_from_url(room_url: str) -> str:
    """
    Extrait le nom de room Daily depuis une URL typique : https://<domain>.daily.co/<room>
    """
    s = (room_url or "").strip()
    m = re.match(r"^https?://[^/]+/([^?#/]+)", s)
    return m.group(1) if m else ""


def daily_start_recording(
    *,
    api_key: str,
    room_url: str,
    instance_id: str | None = None,
) -> tuple[bool, dict[str, Any]]:
    """
    POST /rooms/:name/recordings/start (Daily REST API).
    Retourne (ok, json).
    """
    name = _daily_room_name_from_url(room_url)
    if not name:
        return False, {"error": "URL Daily invalide (room name introuvable)."}
    if not api_key:
        return False, {"error": "DAILY_API_KEY manquante."}
    try:
        import requests
    except Exception:
        return False, {"error": "Paquet `requests` manquant."}
    url = f"https://api.daily.co/v1/rooms/{name}/recordings/start"
    payload: dict[str, Any] = {"type": "cloud"}
    if instance_id:
        payload["instanceId"] = instance_id
    try:
        r = requests.post(
            url,
            json=payload,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=35,
        )
        data = r.json() if "application/json" in (r.headers.get("content-type") or "") else {"raw": r.text}
        return (200 <= r.status_code < 300), {"http": r.status_code, **(data if isinstance(data, dict) else {"data": data})}
    except Exception as e:
        return False, {"error": str(e)}


def daily_stop_recording(
    *,
    api_key: str,
    room_url: str,
    instance_id: str | None = None,
) -> tuple[bool, dict[str, Any]]:
    name = _daily_room_name_from_url(room_url)
    if not name:
        return False, {"error": "URL Daily invalide (room name introuvable)."}
    if not api_key:
        return False, {"error": "DAILY_API_KEY manquante."}
    try:
        import requests
    except Exception:
        return False, {"error": "Paquet `requests` manquant."}
    url = f"https://api.daily.co/v1/rooms/{name}/recordings/stop"
    payload: dict[str, Any] = {"type": "cloud"}
    if instance_id:
        payload["instanceId"] = instance_id
    try:
        r = requests.post(
            url,
            json=payload,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=35,
        )
        data = r.json() if "application/json" in (r.headers.get("content-type") or "") else {"raw": r.text}
        return (200 <= r.status_code < 300), {"http": r.status_code, **(data if isinstance(data, dict) else {"data": data})}
    except Exception as e:
        return False, {"error": str(e)}

