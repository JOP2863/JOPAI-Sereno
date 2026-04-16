"""
Page évolutive : tests unitaires manuels des connexions Google (Sheets, GCS, Vertex AI).
Lancer l’app depuis la racine du dépôt : streamlit run Home.py

Compte de service : priorité à la section [gcp_service_account] dans .streamlit/secrets.toml
(copie du JSON GCP), sinon fichier JSON via service_account_json_path.
"""

from __future__ import annotations

import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import streamlit as st

from sereno_core.artisan_notify import notify_expert
from sereno_core.proto_state import ensure_demo_seed, p_get, p_set
from sereno_core.proto_ui import proto_processing_pause
from sereno_core.jopai_brand_html import page_title_h1_html
from sereno_core.vertex_iam_hints import markdown_vertex_model_not_found, markdown_vertex_predict_denied
from sereno_core.vertex_media_summary import summarize_gcs_media_with_vertex, upload_bytes_to_gcs
from sereno_core.streamlit_theme import inject_button_zoom_resilience_css

inject_button_zoom_resilience_css()

from sereno_core.gcp_credentials import (
    credentials_for_gcp_clients,
    credentials_for_sheets,
    get_service_account_info,
    gcp_project_id,
)

st.markdown(page_title_h1_html("Tests connexions"), unsafe_allow_html=True)
st.caption(
    "Vérifications manuelles : Google Sheets (lecture / écriture), bucket GCS, Vertex AI (Gemini). "
    "Les erreurs s’affichent avec le détail pour diagnostic."
)


def project_root() -> Path:
    return _REPO_ROOT


def execute_sheets_tests(sa_info: dict, gsheet_id: str, allow_write: bool) -> None:
    import gspread

    creds = credentials_for_sheets(sa_info)
    gc = gspread.authorize(creds)
    sh = gc.open_by_key(gsheet_id)

    ws_list = [w.title for w in sh.worksheets()]
    st.success(f"Sheets : classeur ouvert — {len(ws_list)} onglet(s) : {', '.join(ws_list[:8])}{'…' if len(ws_list) > 8 else ''}")

    target = "Config" if "Config" in ws_list else ws_list[0]
    ws = sh.worksheet(target)
    a1 = ws.acell("A1").value
    st.success(f"Lecture **{target}!A1** = `{a1!r}`")

    if allow_write:
        test_title = "Connexions_Test"
        try:
            tws = sh.worksheet(test_title)
        except Exception:
            tws = sh.add_worksheet(title=test_title, rows=50, cols=5)
            tws.append_row(["horodatage_utc", "source", "statut", "note"])
        row = [
            datetime.now(timezone.utc).isoformat(),
            "streamlit_1_Tests_connexions",
            "ecriture_ok",
            "ligne de test ; supprimable",
        ]
        tws.append_row(row)
        st.success(f"Écriture : ligne ajoutée dans l’onglet **{test_title}**.")


def execute_gcs_test(sa_info: dict, bucket_name: str) -> None:
    from google.api_core import exceptions as gexc
    from google.cloud import storage

    creds = credentials_for_gcp_clients(sa_info)
    client = storage.Client(credentials=creds, project=sa_info.get("project_id"))
    bucket = client.bucket(bucket_name)
    try:
        blobs = list(bucket.list_blobs(max_results=5))
    except gexc.Forbidden as e:
        st.error(
            f"**GCS 403** sur `{bucket_name}` : la SA n’a pas les droits attendus sur les **objets** "
            f"(`storage.objects.list` au minimum), ou le bucket / projet est incorrect."
        )
        st.markdown(
            "**À faire (console GCP → Cloud Storage → bucket → Permissions) :** ajouter la SA "
            "avec par ex. **Storage Object Viewer** ou **Storage Object Admin**. "
            "Pour `bucket.exists()` : **Storage Legacy Bucket Reader** ou **roles/storage.bucketViewer**."
        )
        st.caption(str(e))
        return
    except gexc.NotFound:
        st.error(f"Bucket **{bucket_name}** introuvable (nom ou projet incorrect).")
        return

    names = [b.name for b in blobs]
    st.success(
        f"GCS : bucket **{bucket_name}** OK (liste d’objets, sans `buckets.get`) — "
        f"jusqu’à 5 objets : {names if names else '(vide)'}"
    )


def execute_vertex_test(
    sa_info: dict,
    project_id: str,
    location: str,
    model_id: str,
    gemini_api_key: str | None,
) -> None:
    import vertexai
    from google.api_core import exceptions as gexc
    from vertexai.generative_models import GenerativeModel

    creds = credentials_for_gcp_clients(sa_info)
    vertexai.init(project=project_id, location=location, credentials=creds)
    model = GenerativeModel(model_id)
    prompt = "Réponds uniquement par le mot OK, sans ponctuation ni espace supplémentaire."
    try:
        resp = model.generate_content(prompt)
        text = (resp.text or "").strip()
        st.success(f"Vertex AI : modèle **{model_id}** — réponse brute : `{text!r}`")
    except gexc.PermissionDenied as e:
        st.warning(
            "**Vertex AI 403** — permission `aiplatform.endpoints.predict` refusée sur le modèle "
            f"dans la région **{location}**."
        )
        st.caption(str(e)[:520] + ("…" if len(str(e)) > 520 else ""))
        sa_mail = str(sa_info.get("client_email") or "").strip()
        st.markdown(
            markdown_vertex_predict_denied(
                project_id=project_id,
                client_email=sa_mail,
                location=str(location),
                model_id=str(model_id),
            )
        )
        if gemini_api_key and gemini_api_key.strip():
            st.info("Repli : test via **API Gemini** (clé `GEMINI_API_KEY`, hors Vertex).")
            _execute_gemini_api_test(gemini_api_key.strip(), model_hint=model_id)
        else:
            st.caption(
                "Optionnel : renseigner `GEMINI_API_KEY` dans `.streamlit/secrets.toml` "
                "pour un test IA sans passer par Vertex."
            )
    except gexc.NotFound as e:
        st.warning(
            f"**Vertex AI 404** — le modèle **`{model_id}`** n’existe pas (ou n’est pas exposé) "
            f"dans **`{location}`** pour ce projet."
        )
        st.caption(str(e)[:520] + ("…" if len(str(e)) > 520 else ""))
        st.markdown(
            markdown_vertex_model_not_found(
                project_id=project_id,
                location=str(location),
                model_id=str(model_id),
            )
        )
        if gemini_api_key and gemini_api_key.strip():
            st.info("Repli : test via **API Gemini** (clé `GEMINI_API_KEY`, hors Vertex).")
            _execute_gemini_api_test(gemini_api_key.strip(), model_hint=model_id)


def _list_gemini_generate_models(api_key: str) -> list[str]:
    """Modèles disponibles pour generateContent (évite les noms obsolètes type …-8b en 404)."""
    import google.generativeai as genai

    genai.configure(api_key=api_key)
    names: list[str] = []
    try:
        for m in genai.list_models():
            methods = getattr(m, "supported_generation_methods", None) or []
            if "generateContent" not in methods:
                continue
            mid = m.name
            if mid.startswith("models/"):
                mid = mid[len("models/") :]
            names.append(mid)
    except Exception:
        return []

    def score(n: str) -> tuple:
        x = n.lower()
        if "embedding" in x:
            return (100, x)
        if "gemini-2.5" in x and "flash" in x:
            return (0, x)
        if "gemini-2" in x and "flash" in x:
            return (1, x)
        if "gemini-1.5" in x and "flash" in x:
            return (2, x)
        if "gemini" in x and "flash" in x:
            return (3, x)
        if "gemini" in x:
            return (5, x)
        return (10, x)

    return sorted(set(names), key=score)


def _execute_gemini_api_test(api_key: str, model_hint: str) -> None:
    try:
        import google.generativeai as genai
    except ImportError:
        st.error(
            "Paquet **google-generativeai** absent (non installé sur Cloud pour éviter les conflits pip). "
            "En local : `pip install -r requirements-gemini.txt`."
        )
        return

    genai.configure(api_key=api_key)
    candidates = _list_gemini_generate_models(api_key)
    if not candidates:
        # Repli si list_models indisponible (réseau / vieille lib)
        fallback = ["gemini-2.0-flash", "gemini-2.0-flash-001", "gemini-1.5-flash", "gemini-1.5-flash-latest"]
        if "2.5" in model_hint:
            fallback.insert(0, "gemini-2.5-flash-preview-05-20")
        candidates = list(dict.fromkeys(fallback))

    last_err: Exception | None = None
    for name in candidates:
        try:
            model = genai.GenerativeModel(name)
            resp = model.generate_content(
                "Réponds uniquement par le mot OK, sans ponctuation ni espace supplémentaire."
            )
            text = (resp.text or "").strip()
            st.success(f"API Gemini (clé) : modèle **{name}** — réponse : `{text!r}`")
            return
        except Exception as e:
            last_err = e
            continue
    st.error(f"Échec API Gemini (clé) après essai des modèles : {last_err}")
    st.caption(
        "Vérifier la clé sur [Google AI Studio](https://aistudio.google.com/). "
        "Les noms de modèles évoluent : le test interroge **list_models** pour n’utiliser que des modèles "
        "supportant **generateContent**."
    )


# ——— UI ———
root = project_root()
try:
    sa_info = get_service_account_info(root, st.secrets)
    resolved_project_id = gcp_project_id(st.secrets, sa_info)
except ValueError as e:
    st.error(str(e))
    st.stop()

gsheet_id = st.secrets.get("gsheet_id", "")
bucket_name = st.secrets.get("gcs_bucket_name", "jopai-sereno")
vertex_location = st.secrets.get("vertex_location", "europe-west1")
vertex_model = st.secrets.get("vertex_model", "gemini-1.5-flash")
gemini_key = st.secrets.get("GEMINI_API_KEY", "") or ""

st.markdown(f"- Compte de service : **`{sa_info.get('client_email', '?')}`** (source : TOML `[gcp_service_account]` ou JSON)")
st.markdown(f"- Classeur Sheets : `{gsheet_id or '(manquant)'}`")
st.markdown(
    f"- Bucket : `{bucket_name}` · Projet GCP : `{resolved_project_id or '(déduit du compte de service)'}` "
    f"· Vertex : `{vertex_location}` / `{vertex_model}`"
)

col1, col2 = st.columns(2)
with col1:
    btn_sheets = st.button("Tester Google Sheets", type="primary", use_container_width=True)
with col2:
    sheets_write = st.checkbox("Autoriser écriture test (onglet Connexions_Test)", value=False)

btn_gcs = st.button("Tester Google Cloud Storage", use_container_width=True)
btn_vertex = st.button("Tester Vertex AI (Gemini)", use_container_width=True)
btn_all = st.button("Tout lancer (Sheets + GCS + Vertex)", use_container_width=True)

st.divider()
st.subheader("Test notification artisan (Twilio)")
st.caption(
    "Envoie un SMS (puis appel, puis push) à l’artisan choisi, selon `notification_priority` et les secrets Twilio."
)
with st.expander("SMS / appels en échec (30044, 21608, 21219…) — que faire ?", expanded=False):
    st.markdown(
        "- **30044** : (1) **Géo SMS** — expéditeur **+1** vers **+33** sans **France** dans **Messaging → Geo permissions** ; "
        "(2) compte **Trial** — message **trop long** (plusieurs segments) : Twilio peut refuser ; le pilote envoie un SMS **court** "
        "ou passez en compte **actif**. [Doc 30044](https://www.twilio.com/docs/errors/30044).  \n"
        "- **21608** (SMS, **Trial**) / **21219** (appel) : le numéro dans **Verified Caller IDs** doit être **exactement** "
        "le même que celui de l’**artisan** dans **Sheets** (colonne téléphone, format **E.164** `+33…`) — un autre mobile, "
        "même proche, fera encore échouer l’envoi. "
        "[Numéros vérifiés](https://console.twilio.com/us1/develop/phone-numbers/manage/verified) · "
        "[21608](https://www.twilio.com/docs/errors/21608) · [21219](https://www.twilio.com/docs/errors/21219)."
    )
    st.caption(
        "**Important :** vider le **cache Streamlit** ou recharger l’app **ne change rien** côté Twilio. "
        "Si ça « marchait avant » puis plus maintenant, revérifiez la console (France toujours cochée), "
        "l’état du compte (essai vs actif), et le détail du message dans **Messaging Logs** (code exact, pays destinataire)."
    )

ensure_demo_seed()
artisans = list(p_get("artisans", []))
if artisans:
    labels = {f"{a.get('nom','?')} ({a.get('id')})": a for a in artisans if a.get("id")}
    pick = st.selectbox("Artisan destinataire", options=list(labels.keys()), key="test_twilio_expert_pick")
    test_room_url = st.text_input(
        "Room URL à envoyer",
        value="https://meet.jit.si/SerenoTEST#config.prejoinPageEnabled=false",
        help="URL de la salle visio envoyée dans le SMS (démo Jitsi meet.jit.si ; en prod : Daily ou Twilio selon secrets).",
    )
    if st.button("Envoyer une notification test", type="primary"):
        ex = labels[pick]
        # Assurer une session_id fictive pour le texte SMS
        if not p_get("session_id"):
            p_set("session_id", "TEST0001")
        res = notify_expert(
            secrets=st.secrets,
            expert=ex,
            room_url=test_room_url.strip(),
            session_id=str(p_get("session_id")),
            urgence_label="Test",
            client_display=str(p_get("client_prenom") or "Démo test").strip(),
        )
        st.write([r.__dict__ for r in res])
else:
    st.info("Aucun artisan chargé (onglet Experts) — configurez Sheets puis rechargez.")

st.divider()

run_sheets = btn_sheets or btn_all
run_gcs = btn_gcs or btn_all
run_vertex = btn_vertex or btn_all

st.divider()

if run_sheets:
    st.subheader("Résultat — Google Sheets")
    if not gsheet_id:
        st.warning("Définissez `gsheet_id` dans `.streamlit/secrets.toml`.")
    else:
        try:
            execute_sheets_tests(sa_info, gsheet_id, allow_write=sheets_write)
        except Exception:
            st.code(traceback.format_exc())

if run_gcs:
    st.subheader("Résultat — GCS")
    try:
        execute_gcs_test(sa_info, bucket_name)
    except Exception:
        st.code(traceback.format_exc())

if run_vertex:
    st.subheader("Résultat — Vertex AI")
    pid = resolved_project_id or str(sa_info.get("project_id") or "")
    if not pid:
        st.warning("Définissez `gcp_project_id` à la racine du TOML ou `project_id` dans `[gcp_service_account]`.")
    else:
        try:
            execute_vertex_test(
                sa_info,
                pid,
                vertex_location,
                vertex_model,
                gemini_api_key=gemini_key.strip() or None,
            )
        except Exception:
            st.code(traceback.format_exc())

st.divider()
st.subheader("Synthèse média — Vertex (GCS + upload)")
st.caption(
    "Post-traitement **vidéo / audio** avec le même projet Vertex que ci-dessus. "
    "Placez par ex. **samplevideo1.mp4** sous le préfixe `video/` et **sampleaudio1.mp3** sous `audio/` "
    "dans le bucket (`gcs_bucket_name`). Les clés optionnelles **`gcs_sample_video_object`** et "
    "**`gcs_sample_audio_object`** surchargent les chemins par défaut."
)
obj_vid = str(st.secrets.get("gcs_sample_video_object", "video/samplevideo1.mp4") or "").strip()
obj_aud = str(st.secrets.get("gcs_sample_audio_object", "audio/sampleaudio1.mp3") or "").strip()
pid_media = resolved_project_id or str(sa_info.get("project_id") or "")
c_mv, c_ma = st.columns(2)
with c_mv:
    btn_vertex_vid = st.button("Synthèse — vidéo d’exemple (GCS)", use_container_width=True)
with c_ma:
    btn_vertex_aud = st.button("Synthèse — audio d’exemple (GCS)", use_container_width=True)

up_vid = st.file_uploader(
    "Ou uploader une **courte** vidéo (mp4) — envoi GCS puis synthèse Vertex",
    type=["mp4"],
    key="vertex_upload_mp4",
)
btn_vertex_up = st.button("Uploader + synthèse Vertex", type="primary")

if btn_vertex_vid and pid_media:
    with proto_processing_pause():
        uri = f"gs://{bucket_name}/{obj_vid.lstrip('/')}"
        ok, out = summarize_gcs_media_with_vertex(
            sa_info=sa_info,
            project_id=pid_media,
            location=str(vertex_location),
            model_id=str(vertex_model),
            gcs_uri=uri,
            mime_type="video/mp4",
        )
    if ok:
        st.success(out)
    else:
        st.error(out)

if btn_vertex_aud and pid_media:
    with proto_processing_pause():
        uri = f"gs://{bucket_name}/{obj_aud.lstrip('/')}"
        ok, out = summarize_gcs_media_with_vertex(
            sa_info=sa_info,
            project_id=pid_media,
            location=str(vertex_location),
            model_id=str(vertex_model),
            gcs_uri=uri,
            mime_type="audio/mpeg",
        )
    if ok:
        st.success(out)
    else:
        st.error(out)

if btn_vertex_up:
    if not pid_media:
        st.warning("Projet GCP manquant — voir `gcp_project_id` / compte de service.")
    elif not up_vid:
        st.warning("Choisissez d’abord un fichier **mp4**.")
    else:
        raw = up_vid.getvalue()
        if len(raw) > 25 * 1024 * 1024:
            st.error("Fichier trop volumineux pour ce test pilote (max. **25 Mo**).")
        else:
            safe_name = "".join(c for c in (up_vid.name or "clip.mp4") if c.isalnum() or c in "._-") or "clip.mp4"
            dest = f"vertex_uploads/{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}_{safe_name}"
            err_u = ""
            syn_u = ""
            with proto_processing_pause():
                up_ok, gs_msg = upload_bytes_to_gcs(
                    sa_info=sa_info,
                    bucket_name=bucket_name,
                    object_name=dest,
                    data=raw,
                    content_type="video/mp4",
                )
                if not up_ok:
                    err_u = gs_msg
                else:
                    ok2, txt = summarize_gcs_media_with_vertex(
                        sa_info=sa_info,
                        project_id=pid_media,
                        location=str(vertex_location),
                        model_id=str(vertex_model),
                        gcs_uri=gs_msg,
                        mime_type="video/mp4",
                    )
                    if ok2:
                        syn_u = txt
                    else:
                        err_u = txt
            if err_u:
                st.error(err_u)
            elif syn_u:
                st.success(syn_u)

if not (run_sheets or run_gcs or run_vertex):
    st.info(
        "Cliquez sur un bouton pour tester **Sheets**, **GCS** ou **Vertex** (bloc du haut), "
        "ou utilisez la **synthèse média Vertex** (vidéo / audio GCS + upload) plus bas."
    )
