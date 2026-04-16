"""Utilitaires prototype : carte bancaire (Luhn), choix expert, helpers UX."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

# Carte de test Stripe (succès) — aucun encaissement réel hors Stripe ; ici pilote 100 % local.
# Doc : https://stripe.com/docs/testing
STRIPE_TEST_CARD_SUCCESS = "4242424242424242"


def luhn_valid(number: str) -> bool:
    digits = re.sub(r"\D", "", number)
    if not digits or len(digits) < 13 or len(digits) > 19:
        return False
    s = 0
    alt = False
    for d in reversed(digits):
        n = int(d)
        if alt:
            n *= 2
            if n > 9:
                n -= 9
        s += n
        alt = not alt
    return s % 10 == 0


def validate_card_fields(number: str, expiry_mm_yy: str, cvc: str) -> tuple[bool, str]:
    """
    Validation locale (pilote) : longueur / Luhn, date MM/YY future, CVC 3–4 chiffres.
    Compatible avec la carte de test 4242…
    """
    num = re.sub(r"\s+", "", number.strip())
    if not re.fullmatch(r"\d{13,19}", num):
        return False, "Numéro : 13 à 19 chiffres (espaces autorisés)."
    if not luhn_valid(num):
        return False, "Numéro : contrôle (algorithme de Luhn) invalide."
    exp = expiry_mm_yy.strip().replace(" ", "")
    m = re.fullmatch(r"(\d{2})/?(\d{2})", exp)
    if not m:
        return False, "Date : indiquez MM/YY (ex. 12/28)."
    mm, yy = int(m.group(1)), int(m.group(2))
    if mm < 1 or mm > 12:
        return False, "Mois invalide."
    now = datetime.now(timezone.utc)
    exp_year = 2000 + yy
    if (exp_year, mm) < (now.year, now.month):
        return False, "La carte semble expirée."
    cvc_clean = re.sub(r"\D", "", cvc.strip())
    if len(cvc_clean) not in (3, 4):
        return False, "CVC : 3 ou 4 chiffres."
    return True, ""


def pick_expert_for_urgence(urgence: str, artisans: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Experts capables sur le type d’urgence, triés par **ordre** d’appel (plus petit = prioritaire)."""
    from sereno_core.sheets_experts import canonicalize_type_list

    if not artisans:
        return None
    u = str(urgence).strip().upper()
    eligible: list[dict[str, Any]] = []
    for a in artisans:
        types_c = canonicalize_type_list(list(a.get("types") or []))
        if u in types_c:
            eligible.append(a)
    if not eligible:
        return None
    return sorted(eligible, key=lambda a: int(a.get("ordre", 99)))[0]
