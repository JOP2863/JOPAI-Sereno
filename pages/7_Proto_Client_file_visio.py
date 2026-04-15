"""
Prototype client — file d’attente + mise en relation (simulation).
"""

from __future__ import annotations

import re
import sys
from datetime import UTC, datetime
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import streamlit as st

from sereno_core.proto_checklists import URGENCE_LABELS
from sereno_core.proto_helpers import pick_expert_for_urgence
from sereno_core.artisan_notify import notify_expert
from sereno_core.proto_state import (
    enforce_client_journey,
    journey_sst_active,
    log_event,
    p_get,
    p_set,
    sync_session_sheet,
)
from sereno_core.proto_ui import proto_page_start, proto_processing_pause, reassurance, step_indicator
from sereno_core.sheets_experts import canonicalize_type_list
from sereno_core.visio_recording import build_visio_object_prefix, daily_api_key_from_secrets, daily_start_recording
from sereno_core.ui_labels import ui_label_on

proto_page_start(
    title="Mise en relation avec un expert",
    subtitle="Nous contactons les professionnels dans un **ordre défini** (priorité) parmi ceux qui couvrent votre type d’urgence.",
)
step_indicator(4, 7)

enforce_client_journey(require_step=3)

ut = p_get("urgence_type")
if not ut:
    st.stop()
if journey_sst_active() and not p_get("sst_validated"):
    st.stop()

if ui_label_on("file_wait_reassurance"):
    reassurance(
        "Temps d’attente indicatif : **~1 minute**. "
        "Un expert vous confirmera la prise en charge avant d’ouvrir la visio."
    )

artisans: list[dict] = list(p_get("artisans", []))
elig = [a for a in artisans if ut in canonicalize_type_list(list(a.get("types") or []))]
elig.sort(key=lambda a: int(a.get("ordre", 99)))

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
                    ts = canonicalize_type_list(list(a.get("types") or []))
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
    Sélection artisan avec **photo** (compact, mobile-friendly).
    Ne dépend pas d’un `selectbox` (qui ne supporte pas les vignettes).
    """
    st.markdown(
        """
<style>
.sereno-pick-row { display:flex; align-items:center; gap:10px; padding:7px 10px;
  border:1px solid rgba(15,23,42,0.08); border-radius:12px; background:rgba(255,255,255,0.55); }
.sereno-pick-name { font-weight:650; color:#0b2745; line-height:1.2; }
.sereno-pick-sub { font-size:0.82rem; color:#334155; opacity:0.95; }
.sereno-pick-photo { width:44px; height:44px; border-radius:50%; overflow:hidden;
  border:2px solid rgba(0,51,102,0.12); background:rgba(255,255,255,0.65); flex:0 0 auto; }
.sereno-pick-photo img { width:100%; height:100%; object-fit:cover; display:block; }
</style>
""",
        unsafe_allow_html=True,
    )

    key = "expert_pick_id_mise_en_relation"
    sel = str(st.session_state.get(key) or default_id or "").strip()
    if sel not in {str(e.get("id") or "").strip() for e in elig}:
        sel = default_id

    for e in elig:
        eid = str(e.get("id") or "").strip()
        if not eid:
            continue
        ph = str(e.get("photo_url") or "").strip()
        nm = _expert_display_name(e)
        pr = str(e.get("ordre") or "—")

        cimg, ctext, cbtn = st.columns([0.14, 0.60, 0.26], vertical_alignment="center")
        with cimg:
            if ph:
                st.markdown(
                    f"<div class='sereno-pick-photo'><img src='{ph}' alt='' /></div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    "<div class='sereno-pick-photo'></div>",
                    unsafe_allow_html=True,
                )
        with ctext:
            st.markdown(
                f"<div class='sereno-pick-name'>{nm}</div>"
                f"<div class='sereno-pick-sub'>Priorité d’appel n°{pr}</div>",
                unsafe_allow_html=True,
            )
        with cbtn:
            label = "Sélectionné" if eid == sel else "Choisir"
            t = "primary" if eid == sel else "secondary"
            if st.button(label, key=f"pick_{eid}", type=t, use_container_width=True):
                st.session_state[key] = eid
                sel = eid
                st.rerun()

    return next((e for e in elig if str(e.get("id") or "").strip() == sel), elig[0])


default = p_get("assigned_expert")
if not default or default.get("id") not in {e.get("id") for e in elig}:
    default = pick_expert_for_urgence(ut, artisans) or elig[0]
    p_set("assigned_expert", default)

idx0 = next((i for i, e in enumerate(elig) if e.get("id") == default.get("id")), 0)

if len(elig) > 1:
    st.subheader("Choisir votre prestataire")
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

st.success(
    f"**{_expert_display_name(assigned)}** est sélectionné pour votre demande "
    f"({URGENCE_LABELS.get(ut, ut)}). "
    f"*Priorité d’appel n°{assigned.get('ordre', '—')} dans la file pour ce type d’urgence.*"
)

# Photo + nom (compact) au moment de la sélection
ph = str(assigned.get("photo_url") or "").strip()
if ph:
    nm = _expert_display_name(assigned)
    st.markdown(
        "<div style='display:flex;gap:10px;align-items:center;margin:8px 0 2px 0;'>"
        "<div style='width:44px;height:44px;border-radius:50%;overflow:hidden;"
        "border:2px solid rgba(0,51,102,0.12);background:rgba(255,255,255,0.6);flex:0 0 auto;'>"
        f"<img src='{ph}' alt='' style='width:100%;height:100%;object-fit:cover;display:block;'/>"
        "</div>"
        f"<div style='font-weight:650;color:#0b2745;line-height:1.2;'>{nm}</div>"
        "</div>",
        unsafe_allow_html=True,
    )

if ui_label_on("file_order_expander"):
    with st.expander("Voir l’ordre d’appel des experts (démo)"):
        for a in elig:
            st.write(f"{a.get('ordre', '—')}. **{_expert_display_name(a)}** — {', '.join(a.get('types', []))}")

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
        _debut = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
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
                urgence_label=str(URGENCE_LABELS.get(ut, ut)),
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
                    urgence_label=str(URGENCE_LABELS.get(ut, ut)),
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
