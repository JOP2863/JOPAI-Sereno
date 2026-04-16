"""
Prototype client — file d’attente + mise en relation (simulation).
"""

from __future__ import annotations

import re
import sys
from datetime import datetime, timezone
from html import escape
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import streamlit as st

from sereno_core.gcs_artisan_photo import download_artisan_photo_bytes
from sereno_core.proto_helpers import pick_expert_for_urgence
from sereno_core.artisan_notify import notify_expert
from sereno_core.proto_state import (
    enforce_client_journey,
    journey_sst_active,
    log_event,
    p_get,
    p_set,
    sync_session_sheet,
    urgence_display_label,
)
from sereno_core.proto_ui import (
    proto_page_start,
    proto_processing_pause,
    reassurance,
    step_indicator,
    success_box,
)
from sereno_core.sheets_experts import canonicalize_type_list, coerce_expert_types
from sereno_core.visio_recording import build_visio_object_prefix, daily_api_key_from_secrets, daily_start_recording
from sereno_core.ui_labels import ui_label_on

proto_page_start(
    title="Mise en relation avec notre expert",
    subtitle="Nous contactons les professionnels dans un **ordre défini** (priorité) parmi ceux qui couvrent votre type d’urgence.",
)
step_indicator(4, 7)

enforce_client_journey(require_step=3)

_ut_raw = p_get("urgence_type")
_ut_canon = canonicalize_type_list([_ut_raw] if _ut_raw is not None else [])
ut = _ut_canon[0] if _ut_canon else None
if not ut:
    st.stop()
if journey_sst_active() and not p_get("sst_validated"):
    st.stop()

if ui_label_on("file_wait_reassurance"):
    reassurance(
        "Temps d’attente indicatif : ~1 minute. "
        "Notre expert vous confirmera la prise en charge avant d’ouvrir la visio."
    )

artisans: list[dict] = list(p_get("artisans", []))
elig = [a for a in artisans if ut in coerce_expert_types(a.get("types"))]
elig.sort(key=lambda a: int(a.get("ordre", 99)))

# (Optionnel) lien profond ``?pick_expert=`` : conservé pour liens externes ; le choix courant passe par les boutons Streamlit.
if "pick_expert" in st.query_params:
    _raw = st.query_params["pick_expert"]
    _pv = (_raw[0] if isinstance(_raw, list) else str(_raw or "")).strip()
    if _pv and any(str(e.get("id") or "").strip() == _pv for e in elig):
        st.session_state["expert_pick_id_mise_en_relation"] = _pv
        p_set("expert_pick_user_confirmed", True)
        try:
            del st.query_params["pick_expert"]
        except Exception:
            pass
        st.rerun()

if not elig:
    st.error(
        "Aucun expert n’est référencé pour ce type d’urgence. "
        "Revenez à l’accueil et choisissez une autre situation, ou complétez la liste des artisans."
    )
    if ui_label_on("file_no_expert_diagnostic"):
        with st.expander("Diagnostic — experts chargés (pilote)"):
            st.markdown(
                "Le parcours **ne filtre pas** sur les créneaux (`Disponibilite_Mois`, `Creneau_Astreinte`) : "
                "seul l’onglet **Experts** compte ici. Il faut au moins une ligne **actif** avec le **code** "
                f"**{ut}** (ou **TOUS**) dans la colonne des types."
            )
            if not artisans:
                st.warning(
                    "Aucun expert en session : vérifier **gsheet_id** dans les secrets, le partage du classeur "
                    "avec l’e-mail du **compte de service**, et l’existence de l’onglet **Experts**."
                )
            else:
                st.write(f"**{len(artisans)}** ligne(s) en session :")
                for a in artisans:
                    ts = coerce_expert_types(a.get("types"))
                    st.write(
                        f"- **{a.get('id', '?')}** — types normalisés : `{ts}` — ordre : {a.get('ordre', '—')}"
                    )
                st.caption(
                    "Si `types` est vide : renommer la colonne en **types_autorises** ou remplir la cellule "
                    "(ex. `EAU;GAZ` ou `TOUS`). Puis **choisir à nouveau un type d’urgence** sur l’accueil pour une nouvelle session, "
                    "ou `python scripts/init_google_sheet.py --seed` si l’onglet n’a que l’en-tête."
                )
    if st.button("← Retour accueil", type="secondary"):
        st.switch_page("pages/4_Proto_Client_accueil.py")
    st.stop()

# Overlay « travaille pour vous » : message équipe tant que plusieurs artisans sans clic « Choisir ».
_eids_fp = sorted(str(e.get("id") or "").strip() for e in elig if str(e.get("id") or "").strip())
_elig_fp = "|".join(_eids_fp)
if str(p_get("_expert_elig_fp") or "") != _elig_fp:
    p_set("_expert_elig_fp", _elig_fp)
    p_set("expert_pick_user_confirmed", len(elig) <= 1)
p_set("expert_pick_required", len(elig) > 1)


def _expert_display_name(a: dict) -> str:
    pn = str(a.get("prenom") or "").strip()
    nm = str(a.get("nom") or "").strip()
    if pn and nm:
        return f"{pn} {nm}"
    return str(a.get("nom_affichage") or nm or pn or "?").strip()


def _fmt_expert(a: dict) -> str:
    return f"{_expert_display_name(a)} ({a.get('id')}) — priorité d’appel {a.get('ordre', '—')}"


def _render_expert_picker(*, elig: list[dict], default_id: str) -> dict:
    """
    Tableau aligné **à gauche** : zone resserrée (colonne gauche du layout) ; boutons **sans**
    ``use_container_width`` pour éviter le libellé écrasé en colonne trop étroite.
    """
    st.markdown(
        """
<style>
.sereno-pick-name { font-weight:650;color:#0b2745;line-height:1.25;font-size:0.95rem; }
.sereno-pick-bio { font-size:0.82rem;color:#334155;margin-top:3px;line-height:1.3; }
.sereno-pick-sub { font-size:0.78rem;color:#475569;margin-top:4px; }
.sereno-tbl-fit-wrap { width:max-content; max-width:100%; margin:0; }
/* Boutons d’action courts : pas de césure au milieu du mot (ex. « Éditer »). */
</style>
""",
        unsafe_allow_html=True,
    )

    key = "expert_pick_id_mise_en_relation"
    sel = str(st.session_state.get(key) or default_id or "").strip()
    if sel not in {str(e.get("id") or "").strip() for e in elig}:
        sel = default_id

    sec = dict(st.secrets)
    eids_sorted = sorted({str(e.get("id") or "").strip() for e in elig if str(e.get("id") or "").strip()})
    _thumb_ck = "_sereno_pick_thumbs_" + "|".join(eids_sorted)
    if _thumb_ck not in st.session_state:
        _buf: dict[str, tuple | None] = {}
        for _eid in eids_sorted:
            _buf[_eid] = download_artisan_photo_bytes(_REPO, sec, expert_id=_eid)
        st.session_state[_thumb_ck] = _buf
    thumbs: dict[str, tuple | None] = st.session_state[_thumb_ck]

    # Colonne gauche = zone « tableau » ; droite laisse le vide (alignement gauche visuel).
    _tbl_col, _rest = st.columns([0.46, 0.54])
    with _tbl_col:
        # Photo + texte (nom, bio courte, priorité) + action ; bouton en largeur intrinsèque.
        _W_PH, _W_TX, _W_BT = 0.14, 0.62, 0.24

        rows = [e for e in elig if str(e.get("id") or "").strip()]
        for idx, e in enumerate(rows):
            eid = str(e.get("id") or "").strip()
            nm = _expert_display_name(e)
            pr = str(e.get("ordre") or "—")
            bio = str(e.get("essentiel_bio") or "").strip()
            cimg, ctext, cbtn = st.columns([_W_PH, _W_TX, _W_BT], vertical_alignment="center")
            with cimg:
                tup = thumbs.get(eid)
                if tup:
                    st.image(tup[0], width=44)
                else:
                    st.markdown(
                        "<div style='width:44px;height:44px;border-radius:50%;background:rgba(11,39,69,0.08);"
                        "border:2px solid rgba(0,51,102,0.10);margin:0 auto;'></div>",
                        unsafe_allow_html=True,
                    )
            with ctext:
                bio_blk = (
                    f'<div class="sereno-pick-bio">{escape(bio)}</div>' if bio else ""
                )
                pr_blk = (
                    f'<div class="sereno-pick-sub">Priorité d’appel n°{escape(pr)}</div>'
                    if ui_label_on("file_expert_priority_line")
                    else ""
                )
                st.markdown(
                    f'<div class="sereno-pick-name">{escape(nm)}</div>'
                    f"{bio_blk}"
                    f"{pr_blk}",
                    unsafe_allow_html=True,
                )
            with cbtn:
                if eid == sel:
                    st.button(
                        "Sélectionné",
                        key=f"pick_expert_sel_{eid}",
                        type="primary",
                        disabled=True,
                        use_container_width=False,
                    )
                else:
                    if st.button("Choisir", key=f"pick_expert_btn_{eid}", type="secondary", use_container_width=False):
                        st.session_state[key] = eid
                        p_set("expert_pick_user_confirmed", True)
                        st.rerun()
            if idx < len(rows) - 1:
                st.markdown(
                    "<div style='height:0;margin:0.15rem 0 0.25rem 0;"
                    "border-bottom:1px solid #e2e8f0;'></div>",
                    unsafe_allow_html=True,
                )
        if rows:
            st.markdown(
                "<div style='height:0;margin:0;border-bottom:1px solid #e2e8f0;"
                "border-radius:0 0 8px 8px;box-shadow:0 1px 4px rgba(0,51,102,0.06);'></div>",
                unsafe_allow_html=True,
            )

    sel = str(st.session_state.get(key) or default_id or "").strip()
    return next((e for e in elig if str(e.get("id") or "").strip() == sel), elig[0])


default = p_get("assigned_expert")
if not default or default.get("id") not in {e.get("id") for e in elig}:
    default = pick_expert_for_urgence(ut, artisans) or elig[0]
    p_set("assigned_expert", default)

if len(elig) > 1:
    st.subheader("Choisir votre artisan disponible")
    if ui_label_on("file_multi_expert_explain"):
        st.caption(
            "Plusieurs professionnels couvrent votre urgence. Celui affiché en **premier** est le plus prioritaire "
            "par défaut ; vous pouvez en choisir un **autre** dans la liste."
        )
    chosen = _render_expert_picker(elig=elig, default_id=str(default.get("id") or ""))
else:
    chosen = elig[0]

p_set("assigned_expert", chosen)
assigned = chosen

if assigned.get("id") != p_get("_audit_last_expert_id"):
    log_event(
        "expert_assigne",
        session_id=p_get("session_id"),
        expert_id=assigned.get("id"),
        expert_nom=assigned.get("nom"),
    )
    p_set("_audit_last_expert_id", assigned.get("id"))
    sync_session_sheet(
        {
            "expert_id": str(assigned.get("id") or ""),
            "type_code": ut,
            "statut": "EXPERT_ASSIGNE",
        }
    )

_disp = _expert_display_name(assigned)
_urg = urgence_display_label(ut)
_ok_html = (
    f"<strong>{escape(_disp)}</strong> est sélectionné pour votre demande "
    f"({escape(_urg)})."
)
if len(elig) == 1:
    _bio_one = str(assigned.get("essentiel_bio") or "").strip()
    if _bio_one:
        _ok_html += (
            "<div style='margin-top:0.65rem;padding-top:0.55rem;border-top:1px solid rgba(22,101,52,0.28);"
            "font-size:0.92rem;line-height:1.42;font-weight:500;color:#0f172a;'>"
            f"{escape(_bio_one)}</div>"
        )
success_box(_ok_html)

if st.button("Ouvrir la salle de visio", type="primary"):
    with proto_processing_pause():
        _sid = str(p_get("session_id") or "")
        _room = re.sub(r"[^a-zA-Z0-9]", "", f"Sereno{_sid}")[:48] or "SerenoDemo"
        _jitsi = f"https://meet.jit.si/{_room}#config.prejoinPageEnabled=false"
        _integrated = ""
        try:
            _integrated = str(
                st.secrets.get("daily_room_url")
                or st.secrets.get("DAILY_ROOM_URL")
                or st.secrets.get("twilio_video_room_url")
                or ""
            ).strip()
        except Exception:
            _integrated = ""
        _room_url = _integrated or _jitsi
        _debut = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        log_event("visio_debut", session_id=p_get("session_id"))
        sync_session_sheet(
            {
                "debut_visio": _debut,
                "room_url": _room_url,
                "type_code": ut,
                "statut": "VISIO_DEMARREE",
            }
        )

        # Notifier l’artisan (SMS → appel → push selon secrets)
        try:
            ex = p_get("assigned_expert") or {}
            results = notify_expert(
                secrets=st.secrets,
                expert=ex,
                room_url=_room_url,
                session_id=str(p_get("session_id") or ""),
                urgence_label=str(urgence_display_label(ut)),
                client_display=str(p_get("client_prenom") or "").strip(),
            )
            if results:
                first_ok = next((r for r in results if r.ok), None)
                if first_ok:
                    sync_session_sheet({"statut": f"ARTISAN_NOTIFIE_{first_ok.channel.upper()}"})
                else:
                    sync_session_sheet({"statut": "ARTISAN_NOTIFIE_ECHEC"})
        except Exception:
            pass

        # Enregistrement visio (Daily) — optionnel
        try:
            api_key = daily_api_key_from_secrets(dict(st.secrets))
            if api_key and ".daily.co/" in _room_url:
                prefix = build_visio_object_prefix(
                    client_pseudo=str(p_get("client_prenom") or "client"),
                    session_id=str(p_get("session_id") or ""),
                    urgence_code=str(ut),
                    urgence_label=str(urgence_display_label(ut)),
                )
                ok_rec, rec = daily_start_recording(api_key=api_key, room_url=_room_url)
                if ok_rec:
                    p_set("daily_recording", rec)
                    p_set("visio_object_prefix", prefix)
                    sync_session_sheet({"notes_cloture": f"DAILY_RECORDING_START {prefix}"})
        except Exception:
            pass

        st.session_state["_sereno_overlay_visio"] = True
        st.switch_page("pages/8_Proto_Client_visio.py")

if st.button("← Retour"):
    st.switch_page(
        "pages/6_Proto_Client_SST.py" if journey_sst_active() else "pages/5_Proto_Client_informations.py"
    )
