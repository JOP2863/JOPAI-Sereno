# Carnet d’échange — SÉRÉNO (JOPAI BTP)

Journal des **décisions**, **arbitrages** et **fil de discussion** (échanges entre nous / équipe).  
Complément du **cahier des charges** officiel (`CAHIER_DES_CHARGES.md`). À tenir à jour lors des évolutions structurantes (cf. CDC § 1.7).

---

## Guide d’utilisation

- Un **chapitre** = section de niveau `##` (grand titre).
- Une **section** repliable à l’intérieur = `###` (sous-titre).
- Chaque entrée datée : contexte → **décision** → **impact** (produit / technique / coût).

---

## 2026 — Historique

### 2026-04-07 — Architecture secrets & compte de service

- **Contexte :** simplifier le déploiement Streamlit (Cloud) et éviter un fichier JSON séparé.
- **Décision :** compte de service décrit dans `.streamlit/secrets.toml` sous **`[gcp_service_account]`** ; chargement via `sereno_core.gcp_credentials` ; repli JSON optionnel (`service_account_json_path`).
- **Impact :** technique (auth GCP unifiée) ; documentation § 3.8 CDC v0.8.

### 2026-04-07 — Pilote paiement

- **Décision :** parcours **100 % simulé** (fake) — mêmes écrans qu’un PSP réel, aucun encaissement ; traçabilité `FAKE_OK` / `SIMULE` dans Sheets.
- **Impact :** fonctionnel § 2.9 CDC.

### 2026-04-07 — Données Experts (multi-métiers)

- **Décision :** **une ligne** par `expert_id` ; plusieurs métiers dans **`types_autorises`** séparés par `;` (pas de duplication d’ID).
- **Impact :** modèle Sheets § 3.6 CDC.

---

## Questions ouvertes

### Vertex AI — IAM & région

- Statut : rôle **Vertex AI User** et région (`vertex_location`) à valider pour lever le 403 ; repli **GEMINI_API_KEY** pour tests hors Vertex.

---

## Références rapides

- Cahier des charges : `CAHIER_DES_CHARGES.md` + page Streamlit **Cahier des charges**.
- Ce carnet : page Streamlit **Carnet d’échange**.
