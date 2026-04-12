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


def _strip_ansi(text: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*m", "", str(text or ""))


def _twilio_error_hint(api_message: str) -> str:
    """Ajoute des pistes courantes (pilote FR / numéro US expéditeur) sans remplacer la réponse API."""
    m = str(api_message or "")
    hints: list[str] = []
    if "30044" in m:
        hints.append(
            "Astuce pilote — erreur **30044** peut venir de (1) **permissions géographiques** SMS : console Twilio → "
            "Messaging → **Geo permissions** — activer la **France** si expéditeur **+1** et destinataire **+33** ; "
            "ou numéro expéditeur **+33** dans TWILIO_FROM_NUMBER. "
            "(2) Compte **Trial** : message **trop long** (plusieurs segments) — Twilio bloque ; raccourcir le SMS "
            "(le pilote envoie un texte compact) ou **passer en compte actif**. "
            "Doc : https://www.twilio.com/docs/errors/30044"
        )
    if "21608" in m:
        hints.append(
            "Astuce pilote — **Twilio 21608** (SMS, **Trial**) : le **+33…** dans **Verified Caller IDs** doit être "
            "**le même** que le téléphone de l’artisan dans **Sheets** (pas un autre portable « presque » identique). "
            "Console → **Verified Caller IDs** : https://console.twilio.com/us1/develop/phone-numbers/manage/verified — "
            "ou compte **payant**. Doc : https://www.twilio.com/docs/errors/21608"
        )
    if "21219" in m:
        hints.append(
            "Astuce pilote — **Twilio 21219** (appel vocal, compte **Trial**) : les appels sortants ne peuvent cibler "
            "que des numéros **vérifiés** (même page **Verified Caller IDs**) ou il faut un compte **actif**. "
            "Doc : https://www.twilio.com/docs/errors/21219"
        )
    elif "unverified" in m.lower() and "21608" not in m and "21219" not in m:
        hints.append(
            "Astuce pilote — message « unverified » : avec un compte **Trial**, vérifier le numéro destinataire "
            "dans la console Twilio (**Verified Caller IDs**) ou passer en compte actif."
        )
    if "21211" in m and "Invalid" in m:
        hints.append(
            "Astuce pilote — vérifier le format E.164 du destinataire (éviter +3336… double indicatif)."
        )
    if not hints:
        return m
    return m + "\n\n" + "\n".join(hints)


def normalize_phone_e164(raw: str, *, default_country_code: str = "33") -> str:
    """
    Normalisation simple vers E.164 (pilote France par défaut).
    - Si commence par '+' → chiffres derrière le +.
    - Si commence par '00' → idem.
    - Corrige le cas **336…** déjà en indicatif 33 : ne **pas** rajouter un second **33**
      (évite +33336… Twilio 21211).
    - Si commence par '0' national → +33 + 9 chiffres sans le 0 initial.
    - Sinon 9 chiffres ou plus sans préfixe → +33 + chiffres (national sans 0).
    """
    s = (raw or "").strip()
    if not s:
        return ""
    if s.startswith("+"):
        d = _digits_only(s)
    elif s.startswith("00"):
        d = _digits_only(s[2:])
    else:
        d = _digits_only(s)
    if not d:
        return ""
    # Doublon fréquent : numéro déjà en « 336… » (11 chiffres) + préfixe 33 ajouté → 13 chiffres « 3336… »
    if d.startswith("33") and len(d) >= 13:
        rest = d[2:]
        if rest.startswith("33") and len(rest) == 11:
            d = rest
    if d.startswith("0") and len(d) >= 9:
        return f"+{default_country_code}{d[1:]}"
    if default_country_code == "33" and d.startswith("33") and len(d) == 11:
        return "+" + d
    if len(d) >= 9:
        return f"+{default_country_code}{d}"
    return ""


def _secrets_get(secrets: Mapping[str, Any], key: str) -> str:
    try:
        v = secrets.get(key)
    except Exception:
        v = None
    return str(v).strip() if v is not None else ""


def _twilio_section(secrets: Mapping[str, Any]) -> Mapping[str, Any] | None:
    for k in ("twilio", "TWILIO", "Twilio"):
        try:
            v = secrets.get(k)
        except Exception:
            v = None
        if isinstance(v, Mapping):
            return v
    return None


def twilio_credentials_from_secrets(secrets: Mapping[str, Any]) -> tuple[str, str, str]:
    """
    Secrets Twilio : clés à la racine du TOML **ou** sous `[twilio]`,
    **ou** (erreur TOML fréquente) sous `[gcp_service_account]` après les champs GCP.
    """
    sid = _secrets_get(secrets, "TWILIO_ACCOUNT_SID")
    token = _secrets_get(secrets, "TWILIO_AUTH_TOKEN")
    from_num = _secrets_get(secrets, "TWILIO_FROM_NUMBER")
    if sid and token and from_num:
        return sid, token, from_num
    tw = _twilio_section(secrets)
    if tw is not None:
        sid = (
            _secrets_get(tw, "TWILIO_ACCOUNT_SID")
            or _secrets_get(tw, "account_sid")
            or _secrets_get(tw, "ACCOUNT_SID")
        )
        token = (
            _secrets_get(tw, "TWILIO_AUTH_TOKEN")
            or _secrets_get(tw, "auth_token")
            or _secrets_get(tw, "AUTH_TOKEN")
        )
        from_num = (
            _secrets_get(tw, "TWILIO_FROM_NUMBER")
            or _secrets_get(tw, "from_number")
            or _secrets_get(tw, "FROM_NUMBER")
            or _secrets_get(tw, "from")
        )
        if sid and token and from_num:
            return sid, token, from_num
    try:
        sa = secrets.get("gcp_service_account")
    except Exception:
        sa = None
    if isinstance(sa, Mapping):
        sid = _secrets_get(sa, "TWILIO_ACCOUNT_SID")
        token = _secrets_get(sa, "TWILIO_AUTH_TOKEN")
        from_num = _secrets_get(sa, "TWILIO_FROM_NUMBER")
        if sid and token and from_num:
            return sid, token, from_num
    return "", "", ""


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
    sid, token, from_num = twilio_credentials_from_secrets(secrets)
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
        raw = _strip_ansi(str(e))
        return NotifyResult(False, "sms", _twilio_error_hint(raw))


def call_twilio(
    *,
    secrets: Mapping[str, Any],
    to_phone_e164: str,
    say_text: str,
) -> NotifyResult:
    """
    Appel vocal « réveil » : annonce vocale (TwiML inline). L’appel ne rejoint pas la visio.
    """
    sid, token, from_num = twilio_credentials_from_secrets(secrets)
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
        raw = _strip_ansi(str(e))
        return NotifyResult(False, "call", _twilio_error_hint(raw))


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
    client_display: str = "",
    priority: Sequence[str] | None = None,
) -> list[NotifyResult]:
    """
    Tente les canaux dans l’ordre (par défaut secrets).
    Retourne la liste des résultats (1 par tentative).

    ``client_display`` : prénom ou pseudo du demandeur (parcours client), pour personnaliser SMS / appel.
    """
    prio = [p.strip().lower() for p in (priority or notification_priority_from_secrets(secrets)) if str(p).strip()]
    prio = prio or ["sms", "call", "push"]
    eid = str(expert.get("id") or "").strip()
    name = str(expert.get("nom") or eid or "l’expert").strip()
    tel = normalize_phone_e164(str(expert.get("telephone") or ""))

    who = (client_display or "").strip()
    if not who or who in ("—", "-"):
        who = "une personne (pseudo non renseigné)"

    reassurance = (
        "Merci de vous connecter dès que possible : le client attend une aide à distance, "
        "sans engagement de déplacement immédiat."
    )

    # SMS volontairement **court** : comptes Twilio **Trial** refusent souvent les messages multi-segments (erreur 30044).
    # Détail (demandeur, réassurance) reste dans l’**appel** vocal.
    # Sur **Trial**, Twilio ajoute toujours un suffixe du type « Sent from your Twilio trial account » : non supprimable
    # tant que le compte n’est pas **actif** ; cette ligne d’accroche est *notre* texte, pas un remplacement du suffixe.
    sid_short = str(session_id or "").strip()[:10]
    intro = f"Urgence JOPAI SÉRÉNO — {urgence_label} pour vous."
    sms_body = f"{intro}\nVisio ref {sid_short}\n{room_url}"
    if len(sms_body) > 300:
        sms_body = f"JOPAI SÉRÉNO — {urgence_label}\nref {sid_short}\n{room_url}"

    call_say = (
        f"SÉRÉNO. Nouvelle demande {urgence_label}. "
        f"Demandeur : {who}. "
        f"Référence session {session_id}. "
        "Un SMS contient le lien pour ouvrir la visio. "
        "Le client attend une aide à distance."
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

