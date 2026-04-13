"""
État de session du parcours prototype (client / reporting).
Préfixe `sereno_proto_` pour éviter les collisions.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

import streamlit as st

_PREFIX = "sereno_proto_"

# Préréglages parcours client (pilote) — conservés au « reset » session (voir `reset_client_journey`).
JOURNEY_PRESET_STANDARD = "standard"
JOURNEY_PRESET_SIMPLIFIED = "simplified"
JOURNEY_PRESET_CUSTOM = "custom"

_JOURNEY_CONFIG_KEYS = frozenset(
    {
        "journey_preset",
        "journey_custom_sst",
        "journey_custom_payment",
        "journey_custom_nps",
    }
)


def _k(key: str) -> str:
    return f"{_PREFIX}{key}"


def p_get(key: str, default: Any = None) -> Any:
    return st.session_state.get(_k(key), default)


def p_set(key: str, value: Any) -> None:
    st.session_state[_k(key)] = value


def ensure_demo_seed() -> None:
    """Experts : priorité à l’onglet **Experts** Google Sheets (secrets) ; sinon repli démo local."""
    if p_get("_demo_seeded"):
        return
    p_set("_demo_seeded", True)
    repo = Path(__file__).resolve().parent.parent
    loaded: list[dict[str, Any]] | None = None
    try:
        from sereno_core.sheets_experts import load_experts_from_streamlit_secrets

        loaded = load_experts_from_streamlit_secrets(repo)
    except Exception:
        loaded = None

    if loaded:
        try:
            from sereno_core.sheets_experts import canonicalize_type_list

            for row in loaded:
                row["types"] = canonicalize_type_list(list(row.get("types") or []))
        except Exception:
            pass
        p_set("artisans", loaded)
    else:
        # Repli hors Sheets : un vivier minimal couvrant tous les types (démo uniquement).
        p_set(
            "artisans",
            [
                {
                    "id": "EXP-DEMO-01",
                    "nom": "Expert démo (hors Sheets)",
                    "email": "demo@jopai-sereno.local",
                    "types": ["EAU", "ELEC", "GAZ", "CHAUFF", "SERR"],
                    "ordre": 1,
                },
            ],
        )
    p_set("queue_waiting", 2)
    p_set("events", [])


def new_session_id() -> str:
    sid = str(uuid4())[:8].upper()
    p_set("session_id", sid)
    p_set("_audit_last_expert_id", None)
    return sid


def log_event(action: str, **fields: Any) -> None:
    ensure_demo_seed()
    ev = {
        "ts": datetime.now(UTC).isoformat(timespec="seconds"),
        "action": action,
        **fields,
    }
    events: list[dict[str, Any]] = list(p_get("events", []))
    events.append(ev)
    p_set("events", events)


def _journey_session_fallback() -> dict[str, Any]:
    pr = str(p_get("journey_preset") or "").strip().lower()
    if pr not in (JOURNEY_PRESET_SIMPLIFIED, JOURNEY_PRESET_CUSTOM):
        pr = JOURNEY_PRESET_STANDARD
    return {
        "preset": pr,
        "custom_sst": bool(p_get("journey_custom_sst", True)),
        "custom_payment": bool(p_get("journey_custom_payment", True)),
        "custom_nps": bool(p_get("journey_custom_nps", True)),
    }


def journey_merged_settings() -> dict[str, Any]:
    """
    Réglages effectifs du parcours : **Google Sheets / Config** (clés ``SERENO_JOURNEY_*``) si présentes,
    sinon **session** (repli sans classeur ou avant première écriture).
    """
    repo = Path(__file__).resolve().parent.parent
    try:
        secrets = dict(st.secrets)
    except Exception:
        secrets = {}
    try:
        from sereno_core.sheets_journey_config import load_global_journey_dict

        gd = load_global_journey_dict(repo, secrets)
    except Exception:
        gd = None
    if gd is not None:
        return gd
    return _journey_session_fallback()


def journey_preset() -> str:
    """`standard` | `simplified` | `custom` (défaut : parcours complet)."""
    v = str(journey_merged_settings().get("preset") or "").strip().lower()
    if v in (JOURNEY_PRESET_SIMPLIFIED, JOURNEY_PRESET_CUSTOM):
        return v
    return JOURNEY_PRESET_STANDARD


def journey_sst_active() -> bool:
    c = journey_merged_settings()
    pr = str(c.get("preset") or JOURNEY_PRESET_STANDARD).strip().lower()
    if pr == JOURNEY_PRESET_STANDARD:
        return True
    if pr == JOURNEY_PRESET_SIMPLIFIED:
        return False
    return bool(c.get("custom_sst", True))


def journey_payment_active() -> bool:
    c = journey_merged_settings()
    pr = str(c.get("preset") or JOURNEY_PRESET_STANDARD).strip().lower()
    if pr == JOURNEY_PRESET_STANDARD:
        return True
    if pr == JOURNEY_PRESET_SIMPLIFIED:
        return False
    return bool(c.get("custom_payment", True))


def journey_nps_active() -> bool:
    c = journey_merged_settings()
    pr = str(c.get("preset") or JOURNEY_PRESET_STANDARD).strip().lower()
    if pr == JOURNEY_PRESET_STANDARD:
        return True
    if pr == JOURNEY_PRESET_SIMPLIFIED:
        return False
    return bool(c.get("custom_nps", True))


def journey_next_after_infos() -> str:
    return (
        "pages/6_Proto_Client_SST.py"
        if journey_sst_active()
        else "pages/7_Proto_Client_file_visio.py"
    )


def journey_next_after_visio_done() -> str:
    """Cible après « J’ai terminé la visio » (paiement / NPS / accueil selon config)."""
    if journey_payment_active():
        return "pages/9_Proto_Client_paiement.py"
    p_set("payment_done", True)
    if journey_nps_active():
        return "pages/10_Proto_Client_satisfaction.py"
    log_event("parcours_fin_sans_paiement_nps", session_id=p_get("session_id"))
    try:
        sync_session_sheet(
            {
                "type_code": p_get("urgence_type"),
                "statut": "CLOTUREE_PARCOURS_COURT",
            }
        )
    except Exception:
        pass
    return "pages/4_Proto_Client_accueil.py"


def journey_next_after_payment_success() -> str:
    if journey_nps_active():
        return "pages/10_Proto_Client_satisfaction.py"
    return "pages/4_Proto_Client_accueil.py"


def enforce_client_journey(*, require_step: int) -> None:
    """
    Garde-fou « parcours client » : si l’utilisateur arrive sur une page trop avancée,
    redirige vers la première étape manquante (sans afficher « commencez par… »).

    Étapes de référence (7) ; **SST**, **paiement** et **NPS** peuvent être désactivés
    (page **Paramétrage parcours client**, `journey_*` dans ``proto_state``) :

    1. urgence choisie + ``session_id``
    2. infos saisies (téléphone au minimum)
    3. SST validée (si l’étape est active)
    4. expert assigné
    5. visio (page session)
    6. paiement après visio (si l’étape est active)
    7. avis NPS (si l’étape est active ; sinon pas d’exigence de paiement simulé si paiement inactif)
    """
    # Step 1
    if require_step >= 1:
        if not p_get("urgence_type") or not p_get("session_id"):
            st.switch_page("pages/4_Proto_Client_accueil.py")
            return
    # Step 2
    if require_step >= 2:
        tel = str(p_get("client_tel") or "").strip()
        if not tel or tel == "+33":
            st.switch_page("pages/5_Proto_Client_informations.py")
            return
    # Step 3 (SST) — ignorée si l’étape est désactivée dans les paramètres parcours
    if require_step >= 3 and journey_sst_active():
        if not p_get("sst_validated"):
            st.switch_page("pages/6_Proto_Client_SST.py")
            return
    # Step 4
    if require_step >= 4:
        if not p_get("assigned_expert"):
            st.switch_page("pages/7_Proto_Client_file_visio.py")
            return
    # Step 6: visio terminée
    if require_step >= 6:
        if not p_get("visio_done"):
            st.switch_page("pages/8_Proto_Client_visio.py")
            return
    # Step 7 (page NPS) : exiger le paiement simulé seulement si l’étape paiement est active
    if require_step >= 7:
        if journey_payment_active() and not p_get("payment_done"):
            st.switch_page("pages/9_Proto_Client_paiement.py")
            return


def _sheet_write_debug() -> bool:
    try:
        return bool(st.secrets.get("debug_sheets") or st.secrets.get("debug_sessions_sheet"))
    except Exception:
        return False


def sync_session_sheet(updates: dict[str, Any | None]) -> None:
    """
    Met à jour l’onglet Google Sheets **Sessions** (une ligne par `session_id`).
    Silencieux en cas d’erreur ; `debug_sheets` ou `debug_sessions_sheet` = true → avertissement.
    """
    sid = p_get("session_id")
    if not sid:
        return
    try:
        repo = Path(__file__).resolve().parent.parent
        from sereno_core.sheets_sessions_write import try_upsert_session_row

        ok, msg = try_upsert_session_row(
            repo,
            dict(st.secrets),
            session_id=str(sid),
            updates=updates,
        )
        if not ok and _sheet_write_debug():
            st.warning(f"[Sessions Sheets] {msg}")
    except Exception:
        pass


def append_paiement_sheet_row(
    *,
    montant_centimes: int,
    mode_paiement: str,
    statut: str = "SIMULE",
    notes: str = "",
) -> None:
    """Ajoute une ligne dans l’onglet **Paiements** (best-effort, silencieux sauf `debug_sheets`)."""
    sid = p_get("session_id")
    if not sid:
        return
    try:
        repo = Path(__file__).resolve().parent.parent
        from sereno_core.sheets_paiements_write import try_append_paiement_row

        ok, msg = try_append_paiement_row(
            repo,
            dict(st.secrets),
            session_id=str(sid),
            montant_centimes=int(montant_centimes),
            mode_paiement=mode_paiement,
            statut=statut,
            notes=notes,
        )
        if not ok and _sheet_write_debug():
            st.warning(f"[Paiements Sheets] {msg}")
    except Exception:
        pass


def reset_client_journey() -> None:
    """Remet le parcours client à zéro (garde les événements ; recharge les experts depuis Sheets)."""
    keep = {_k("events")}
    keep.update(_k(k) for k in _JOURNEY_CONFIG_KEYS)
    for key in list(st.session_state.keys()):
        if isinstance(key, str) and key.startswith(_PREFIX) and key not in keep:
            del st.session_state[key]
    ensure_demo_seed()


def clear_client_branch_after_urgence_change() -> None:
    """
    Nouveau choix à l’accueil : invalide expert, SST, visio, paiement, satisfaction
    pour éviter un expert « collé » à une ancienne panne.
    """
    drop_keys = (
        "assigned_expert",
        "_audit_last_expert_id",
        "sst_validated",
        "_sst_mark_complete",
        "visio_done",
        "visio_demo_mic",
        "visio_demo_torch",
        "payment_done",
        "satisfaction_stars",
        "satisfaction_nps",
        "satisfaction_comment",
        "stars_selected",
        "nps_selected",
    )
    for name in drop_keys:
        kk = _k(name)
        if kk in st.session_state:
            del st.session_state[kk]
    for key in list(st.session_state.keys()):
        if isinstance(key, str) and key.startswith(_PREFIX + "sst_line_"):
            del st.session_state[key]
