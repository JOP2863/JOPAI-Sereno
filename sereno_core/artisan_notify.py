"""
Notification artisan — multi-canaux (priorité configurable) : SMS → appel → push.

Objectif pilote : quand le client ouvre la salle, prévenir l’artisan avec un lien de visio.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Mapping, Sequence


@dataclass(frozen=True)
class NotifyResult:
    ok: bool
    channel: str
    message: str


def _digits_only(s: str) -> str:
    return re.sub(r"\D+", "", (s or "").strip())


def normalize_phone_e164(raw: str, *, default_country_code: str = "33") -> str:
    """
    Normalisation simple vers E.164.
    - Si commence par '+' → conserve.
    - Si commence par '00' → remplace par '+'.
    - Si commence par '0' (France) → +33 + reste sans le 0.
    - Sinon si 9–12 chiffres → +33 + digits (par défaut).
    """
    s = (raw or "").strip()
    if not s:
        return ""
    if s.startswith("+"):
        return "+" + _digits_only(s)
    if s.startswith("00"):
        return "+" + _digits_only(s[2:])
    d = _digits_only(s)
    if not d:
        return ""
    if d.startswith("0") and len(d) >= 9:
        return f"+{default_country_code}{d[1:]}"
    if len(d) >= 9:
        return f"+{default_country_code}{d}"
    return ""


def _secrets_get(secrets: Mapping[str, Any], key: str) -> str:
    try:
        v = secrets.get(key)
    except Exception:
        v = None
    return str(v).strip() if v is not None else ""


def notification_priority_from_secrets(secrets: Mapping[str, Any]) -> list[str]:
    """
    `notification_priority = ["sms","call","push"]` dans secrets TOML.
    Repli : "sms,call,push" (string) ou priorité défaut.
    """
    try:
        v = secrets.get("notification_priority")
    except Exception:
        v = None
    if isinstance(v, (list, tuple)):
        out = [str(x).strip().lower() for x in v if str(x).strip()]
        return out or ["sms", "call", "push"]
    if isinstance(v, str) and v.strip():
        out = [p.strip().lower() for p in v.split(",") if p.strip()]
        return out or ["sms", "call", "push"]
    return ["sms", "call", "push"]


def send_sms_twilio(
    *,
    secrets: Mapping[str, Any],
    to_phone_e164: str,
    body: str,
) -> NotifyResult:
    sid = _secrets_get(secrets, "TWILIO_ACCOUNT_SID")
    token = _secrets_get(secrets, "TWILIO_AUTH_TOKEN")
    from_num = _secrets_get(secrets, "TWILIO_FROM_NUMBER")
    if not (sid and token and from_num):
        return NotifyResult(False, "sms", "Secrets Twilio SMS manquants (SID/TOKEN/FROM).")
    if not to_phone_e164:
        return NotifyResult(False, "sms", "Numéro destinataire vide.")
    try:
        from twilio.rest import Client  # type: ignore
    except Exception:
        return NotifyResult(False, "sms", "Paquet `twilio` manquant.")
    try:
        c = Client(sid, token)
        msg = c.messages.create(from_=from_num, to=to_phone_e164, body=body)
        return NotifyResult(True, "sms", f"SMS envoyé ({msg.sid})")
    except Exception as e:
        return NotifyResult(False, "sms", str(e))


def call_twilio(
    *,
    secrets: Mapping[str, Any],
    to_phone_e164: str,
    say_text: str,
) -> NotifyResult:
    """
    Appel vocal « réveil » : annonce vocale (TwiML inline). L’appel ne rejoint pas la visio.
    """
    sid = _secrets_get(secrets, "TWILIO_ACCOUNT_SID")
    token = _secrets_get(secrets, "TWILIO_AUTH_TOKEN")
    from_num = _secrets_get(secrets, "TWILIO_FROM_NUMBER")
    if not (sid and token and from_num):
        return NotifyResult(False, "call", "Secrets Twilio Voice manquants (SID/TOKEN/FROM).")
    if not to_phone_e164:
        return NotifyResult(False, "call", "Numéro destinataire vide.")
    try:
        from twilio.rest import Client  # type: ignore
        from twilio.twiml.voice_response import VoiceResponse  # type: ignore
    except Exception:
        return NotifyResult(False, "call", "Paquet `twilio` manquant.")
    try:
        vr = VoiceResponse()
        vr.say(say_text, voice="alice", language="fr-FR")
        twiml = str(vr)
        c = Client(sid, token)
        call = c.calls.create(from_=from_num, to=to_phone_e164, twiml=twiml)
        return NotifyResult(True, "call", f"Appel lancé ({call.sid})")
    except Exception as e:
        return NotifyResult(False, "call", str(e))


def push_placeholder(*, to_expert_id: str) -> NotifyResult:
    # Cible produit : Expo push token + backend ; ici stub.
    if not to_expert_id:
        return NotifyResult(False, "push", "expert_id vide.")
    return NotifyResult(False, "push", "Push non implémenté (cible app Expo).")


def notify_expert(
    *,
    secrets: Mapping[str, Any],
    expert: Mapping[str, Any],
    room_url: str,
    session_id: str,
    urgence_label: str,
    priority: Sequence[str] | None = None,
) -> list[NotifyResult]:
    """
    Tente les canaux dans l’ordre (par défaut secrets).
    Retourne la liste des résultats (1 par tentative).
    """
    prio = [p.strip().lower() for p in (priority or notification_priority_from_secrets(secrets)) if str(p).strip()]
    prio = prio or ["sms", "call", "push"]
    eid = str(expert.get("id") or "").strip()
    name = str(expert.get("nom") or eid or "l’expert").strip()
    tel = normalize_phone_e164(str(expert.get("telephone") or ""))

    sms_body = (
        f"SÉRÉNO — nouvelle demande ({urgence_label}).\\n"
        f"Session {session_id}.\\n"
        f"Rejoindre la visio : {room_url}"
    )
    call_say = (
        f"SÉRÉNO. Nouvelle demande {urgence_label}. Session {session_id}. "
        "Vous avez reçu un message avec le lien de visio."
    )

    results: list[NotifyResult] = []
    for ch in prio:
        if ch == "sms":
            r = send_sms_twilio(secrets=secrets, to_phone_e164=tel, body=sms_body)
        elif ch == "call":
            r = call_twilio(secrets=secrets, to_phone_e164=tel, say_text=call_say)
        elif ch == "push":
            r = push_placeholder(to_expert_id=eid)
        else:
            r = NotifyResult(False, ch, "Canal inconnu.")
        results.append(r)
        if r.ok:
            break
    return results

