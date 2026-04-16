"""
Gestion de la charge visuelle (libellés) du parcours client.

Objectif : permettre au propriétaire de basculer entre
- standard : tout afficher
- minimal : masquer les éléments d’aide / debug / démo
- custom : choix fin par libellé (cases à cocher)

Les réglages sont lus depuis l’onglet Google Sheets **Config** (clés `SERENO_UI_*`).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import streamlit as st

from sereno_core.config_kv import (
    config_upsert_pairs,
    read_config_kv_cached,
    resolve_gsheet_id_from_secrets,
)

MODE_STANDARD = "standard"
MODE_MINIMAL = "minimal"
MODE_CUSTOM = "custom"

KEY_MODE = "SERENO_UI_LABELS_MODE"
KEY_PREFIX_CUSTOM = "SERENO_UI_LABEL_"


@dataclass(frozen=True)
class UILabel:
    """Un libellé optionnel (peut être masqué en mode minimal / custom)."""

    id: str
    owner_label: str
    default_in_minimal: bool


# Liste initiale (ciblée sur l’écran Visio + quelques éléments d’aide).
# Étendre au besoin : ajouter un item ici + l’utiliser dans les pages.
UI_LABELS: tuple[UILabel, ...] = (
    # Accueil / infos / SST / mise en relation / paiement / satisfaction
    UILabel(
        id="accueil_reassurance",
        owner_label="Accueil — bloc réassurance (pas d’engagement immédiat, etc.)",
        default_in_minimal=False,
    ),
    UILabel(
        id="infos_urgence_reassurance",
        owner_label="Informations — rappel urgence sélectionnée (réassurance)",
        default_in_minimal=True,
    ),
    UILabel(
        id="infos_consigne_band",
        owner_label="Informations — bandeau “consignes pour votre situation” (texte long)",
        default_in_minimal=False,
    ),
    UILabel(
        id="infos_phone_help",
        owner_label="Informations — explication indicatif +33 / exemple",
        default_in_minimal=False,
    ),
    UILabel(
        id="sst_rassurance_html",
        owner_label="SST — bloc “Rassurance : ces étapes vous protègent…”",
        default_in_minimal=True,
    ),
    UILabel(
        id="sst_reassurance_block",
        owner_label="SST — réassurance secondaire (validation de chaque point)",
        default_in_minimal=False,
    ),
    UILabel(
        id="sst_footer_caption",
        owner_label="SST — rappel en bas “Validez tous les points…”",
        default_in_minimal=False,
    ),
    UILabel(
        id="file_wait_reassurance",
        owner_label="Mise en relation — message temps d’attente indicatif",
        default_in_minimal=True,
    ),
    UILabel(
        id="file_no_expert_diagnostic",
        owner_label="Mise en relation — diagnostic détaillé si aucun expert (expander + conseils)",
        default_in_minimal=False,
    ),
    UILabel(
        id="file_multi_expert_explain",
        owner_label="Mise en relation — explication choix prestataire + sous-titre",
        default_in_minimal=False,
    ),
    UILabel(
        id="file_expert_priority_line",
        owner_label="Mise en relation — ligne « Priorité d’appel n°… » sous chaque prestataire",
        default_in_minimal=False,
    ),
    UILabel(
        id="file_order_expander",
        owner_label="Mise en relation — expander “Voir l’ordre d’appel des experts (démo)”",
        default_in_minimal=False,
    ),
    UILabel(
        id="paiement_reassurance",
        owner_label="Paiement — explication pilote (carte de test, saisie locale)",
        default_in_minimal=False,
    ),
    UILabel(
        id="paiement_controls_info",
        owner_label="Paiement — encart contrôles (Luhn, MM/YY, CVC)",
        default_in_minimal=False,
    ),
    UILabel(
        id="paiement_recap_card",
        owner_label="Paiement — bloc récapitulatif (session, montant, statut pilote)",
        default_in_minimal=True,
    ),
    UILabel(
        id="satisfaction_intro",
        owner_label="Satisfaction — sous-titre / explication “quelques secondes”",
        default_in_minimal=False,
    ),
    UILabel(
        id="satisfaction_help_caption",
        owner_label="Satisfaction — aide sous la note (NPS ou étoiles)",
        default_in_minimal=False,
    ),
    UILabel(
        id="satisfaction_contact_block",
        owner_label="Satisfaction — bloc contact fin (mailto + texte long)",
        default_in_minimal=False,
    ),
    UILabel(
        id="satisfaction_new_request_link",
        owner_label="Satisfaction — lien “Nouvelle demande” (retour accueil)",
        default_in_minimal=False,
    ),

    UILabel(
        id="visio_demo_warning",
        owner_label="Visio — avertissements / explications démo (public, secrets, etc.)",
        default_in_minimal=False,
    ),
    UILabel(
        id="visio_secondary_links",
        owner_label="Visio — liens secondaires (ex: lien cible intégration, expander, etc.)",
        default_in_minimal=False,
    ),
    UILabel(
        id="visio_in_page_iframe",
        owner_label="Visio — afficher la visio dans la page (iframe) au lieu d’un bouton unique",
        default_in_minimal=False,
    ),
    UILabel(
        id="visio_sdk_mock",
        owner_label="Visio — maquette “SDK natif” (bloc plein écran mobile)",
        default_in_minimal=False,
    ),
    UILabel(
        id="visio_demo_toggles",
        owner_label="Visio — interrupteurs démo (micro, lampe torche)",
        default_in_minimal=False,
    ),
    UILabel(
        id="visio_urls_box",
        owner_label="Visio — encart technique (URLs Jitsi / cible prod)",
        default_in_minimal=False,
    ),
)


def _as_bool(v: Any) -> bool:
    s = str(v or "").strip().lower()
    return s in ("1", "true", "vrai", "oui", "yes", "on", "o")


def invalidate_ui_labels_cache() -> None:
    # Cache global Config partagé
    from sereno_core.config_kv import invalidate_config_kv_cache

    invalidate_config_kv_cache()


def _resolve_gsheet_id(repo_root: Path, secrets: Mapping[str, Any] | Any) -> str:
    return resolve_gsheet_id_from_secrets(repo_root, secrets)


def ui_labels_mode() -> str:
    """Mode effectif: standard | minimal | custom (défaut: standard)."""
    repo = Path(__file__).resolve().parent.parent
    try:
        secrets = dict(st.secrets)
    except Exception:
        secrets = {}
    gsid = _resolve_gsheet_id(repo, secrets)
    kv = read_config_kv_cached(gsid) if gsid else None
    mode = str((kv or {}).get(KEY_MODE, "")).strip().lower()
    if mode in (MODE_MINIMAL, MODE_CUSTOM):
        return mode
    return MODE_STANDARD


def _label_def(label_id: str) -> UILabel | None:
    for it in UI_LABELS:
        if it.id == label_id:
            return it
    return None


def ui_label_on(label_id: str) -> bool:
    """
    True si le libellé doit être affiché, selon:
    - standard: toujours
    - minimal: seulement ceux `default_in_minimal=True`
    - custom: lecture clé `SERENO_UI_LABEL_<ID>` (true/false). Si absent → fallback minimal.
    """
    lid = str(label_id or "").strip()
    if not lid:
        return True
    mode = ui_labels_mode()
    if mode == MODE_STANDARD:
        return True
    ld = _label_def(lid)
    if ld is None:
        # Si la page demande un id inconnu, rester “safe” : l’afficher en standard, le masquer en minimal.
        return mode != MODE_MINIMAL
    if mode == MODE_MINIMAL:
        return bool(ld.default_in_minimal)

    # custom
    repo = Path(__file__).resolve().parent.parent
    try:
        secrets = dict(st.secrets)
    except Exception:
        secrets = {}
    gsid = _resolve_gsheet_id(repo, secrets)
    kv = read_config_kv_cached(gsid) if gsid else None
    key = f"{KEY_PREFIX_CUSTOM}{lid}".upper()
    if kv and key in kv:
        return _as_bool(kv.get(key))
    return bool(ld.default_in_minimal)


def persist_ui_labels_config(
    repo_root: Path,
    secrets: Mapping[str, Any] | Any,
    *,
    mode: str,
    custom_values: dict[str, bool],
) -> tuple[bool, str]:
    """
    Écrit le mode + les valeurs custom dans l’onglet **Config**.
    On réutilise l’approche “upsert” : mise à jour si clé existante, sinon append.
    """
    # Normaliser mode
    m = str(mode or "").strip().lower()
    if m not in (MODE_STANDARD, MODE_MINIMAL, MODE_CUSTOM):
        m = MODE_STANDARD

    pairs: list[tuple[str, str]] = [(KEY_MODE, m)]
    # En mode minimal / standard, ne pas réécrire les clés SERENO_UI_LABEL_* (sinon confusion dans la feuille).
    if m == MODE_CUSTOM:
        for lid, val in (custom_values or {}).items():
            lid_n = str(lid or "").strip()
            if not lid_n:
                continue
            pairs.append((f"{KEY_PREFIX_CUSTOM}{lid_n}", "true" if bool(val) else "false"))

    ok, err = config_upsert_pairs(repo_root, secrets, pairs=pairs)
    if ok:
        invalidate_ui_labels_cache()
    return ok, err

