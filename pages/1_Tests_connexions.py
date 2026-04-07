"""
Page évolutive : tests unitaires manuels des connexions Google (Sheets, GCS, Vertex AI).
Lancer l’app depuis la racine du dépôt : streamlit run Home.py
"""

from __future__ import annotations

import json
import traceback
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="Tests connexions", page_icon="🧪", layout="wide")
st.title("Tests connexions")
st.caption(
    "Vérifications manuelles : Google Sheets (lecture / écriture), bucket GCS, Vertex AI (Gemini). "
    "Les erreurs s’affichent avec le détail pour diagnostic."
)


def project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def service_account_path() -> Path:
    rel = st.secrets.get("service_account_json_path", ".streamlit/google-service-account.json")
    p = project_root() / rel
    if not p.is_file():
        raise FileNotFoundError(f"Fichier compte de service introuvable : {p}")
    return p


def execute_sheets_tests(sa_file: Path, gsheet_id: str, allow_write: bool) -> None:
    import gspread
    from google.oauth2.service_account import Credentials

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_file(str(sa_file), scopes=scopes)
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


def execute_gcs_test(sa_file: Path, bucket_name: str) -> None:
    from google.cloud import storage
    from google.oauth2 import service_account

    info = json.loads(sa_file.read_text(encoding="utf-8"))
    creds = service_account.Credentials.from_service_account_info(info)
    client = storage.Client(credentials=creds, project=info.get("project_id"))
    bucket = client.bucket(bucket_name)
    if not bucket.exists():
        st.error(f"Bucket **{bucket_name}** : introuvable ou pas d’accès.")
        return
    blobs = list(bucket.list_blobs(max_results=5))
    names = [b.name for b in blobs]
    st.success(f"GCS : bucket **{bucket_name}** OK — jusqu’à 5 objets : {names if names else '(vide)'}")


def execute_vertex_test(sa_file: Path, project_id: str, location: str, model_id: str) -> None:
    import os

    import vertexai
    from vertexai.generative_models import GenerativeModel

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(sa_file.resolve())
    vertexai.init(project=project_id, location=location)
    model = GenerativeModel(model_id)
    resp = model.generate_content("Réponds uniquement par le mot OK, sans ponctuation ni espace supplémentaire.")
    text = (resp.text or "").strip()
    st.success(f"Vertex AI : modèle **{model_id}** — réponse brute : `{text!r}`")


# ——— UI ———
try:
    sa = service_account_path()
except Exception as e:
    st.error(str(e))
    st.stop()

gsheet_id = st.secrets.get("gsheet_id", "")
bucket_name = st.secrets.get("gcs_bucket_name", "jopai-sereno")
project_id = st.secrets.get("gcp_project_id", "")
vertex_location = st.secrets.get("vertex_location", "europe-west1")
vertex_model = st.secrets.get("vertex_model", "gemini-1.5-flash")

st.markdown(f"- Compte de service : `{sa}`")
st.markdown(f"- Classeur Sheets : `{gsheet_id or '(manquant)'}`")
st.markdown(f"- Bucket : `{bucket_name}` · Projet GCP : `{project_id or '(manquant)'}` · Vertex : `{vertex_location}` / `{vertex_model}`")

col1, col2 = st.columns(2)
with col1:
    btn_sheets = st.button("Tester Google Sheets", type="primary", use_container_width=True)
with col2:
    sheets_write = st.checkbox("Autoriser écriture test (onglet Connexions_Test)", value=False)

btn_gcs = st.button("Tester Google Cloud Storage", use_container_width=True)
btn_vertex = st.button("Tester Vertex AI (Gemini)", use_container_width=True)
btn_all = st.button("Tout lancer (Sheets + GCS + Vertex)", use_container_width=True)

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
            execute_sheets_tests(sa, gsheet_id, allow_write=sheets_write)
        except Exception:
            st.code(traceback.format_exc())

if run_gcs:
    st.subheader("Résultat — GCS")
    try:
        execute_gcs_test(sa, bucket_name)
    except Exception:
        st.code(traceback.format_exc())

if run_vertex:
    st.subheader("Résultat — Vertex AI")
    if not project_id:
        st.warning("Définissez `gcp_project_id` dans `.streamlit/secrets.toml`.")
    else:
        try:
            execute_vertex_test(sa, project_id, vertex_location, vertex_model)
        except Exception:
            st.code(traceback.format_exc())

if not (run_sheets or run_gcs or run_vertex):
    st.info("Cliquez sur un bouton ci-dessus pour lancer un test.")
