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

from sereno_core.gcp_credentials import (
    credentials_for_gcp_clients,
    credentials_for_sheets,
    get_service_account_info,
    gcp_project_id,
)

st.title("Tests connexions")
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
    except gexc.PermissionDenied:
        st.warning(
            "**Vertex AI 403** : la SA n’a pas `aiplatform.endpoints.predict` sur le modèle "
            f"dans **{location}**."
        )
        st.markdown(
            "**Console GCP → IAM** : ajouter à la SA le rôle **Vertex AI User** "
            "(`roles/aiplatform.user`). Activer l’**API Vertex AI**. "
            "Tester une autre **vertex_location** (`europe-west4`, `us-central1`) si besoin."
        )
        if gemini_api_key and gemini_api_key.strip():
            st.info("Repli : test via **API Gemini** (clé `GEMINI_API_KEY`, hors Vertex).")
            _execute_gemini_api_test(gemini_api_key.strip(), model_hint=model_id)
        else:
            st.caption(
                "Optionnel : renseigner `GEMINI_API_KEY` dans `.streamlit/secrets.toml` "
                "pour un test IA sans passer par Vertex."
            )


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

ensure_demo_seed()
artisans = list(p_get("artisans", []))
if artisans:
    labels = {f"{a.get('nom','?')} ({a.get('id')})": a for a in artisans if a.get("id")}
    pick = st.selectbox("Artisan destinataire", options=list(labels.keys()), key="test_twilio_expert_pick")
    test_room_url = st.text_input(
        "Room URL à envoyer",
        value="https://meet.jit.si/SerenoTEST#config.prejoinPageEnabled=false",
        help="Lien qui sera envoyé à l’artisan (SMS).",
    )
    if st.button("Envoyer une notification test", type="primary"):
        ex = labels[pick]
        # Assurer une session_id fictive pour le texte SMS
        if not p_get("session_id"):
            p_set("session_id", "TEST0001")
        res = notify_expert(
            secrets=dict(st.secrets),
            expert=ex,
            room_url=test_room_url.strip(),
            session_id=str(p_get("session_id")),
            urgence_label="Test",
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

if not (run_sheets or run_gcs or run_vertex):
    st.info("Cliquez sur un bouton ci-dessus pour lancer un test.")
