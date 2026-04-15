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

### 2026-04-15 — Experts : session figée, photos liste admin, filtre urgence

- **Contexte :** après optimisation perf, la **liste admin** artisans n’affichait plus les vignettes (bucket souvent privé) ; certains utilisateurs voyaient **« Aucun expert référencé »** sur la file / visio alors que l’onglet **Experts** était rempli.
- **Décision :**
  1. **Recharger** les experts depuis **Sheets à chaque** `ensure_demo_seed()` (pages prototype), **sans** téléchargement GCS massif en session (`eager_gcs_photo=False`) pour limiter la latence.
  2. Utiliser l’**URL https** saisie dans la colonne **`photo`** quand elle est présente (vignettes liste admin + `photo_url` session).
  3. Normaliser les **types** avec **`coerce_expert_types`** (évite le piège `list("EAU")` → caractères si une chaîne remplace une liste) et normaliser le **code urgence** sur la page file visio via **`canonicalize_type_list`**.
  4. En-têtes Sheets : retirer un **BOM** éventuel sur la première colonne pour ne pas casser la détection **`expert_id`**.
- **Complément (même lot) :** page **Choisir votre prestataire** (file / visio) en **tableau HTML** étroit + liens `?pick_expert=` ; pages **Administration · Artisans (liste / fiche)** : densité UI, liste en tableau (expertises + téléphone) ; règle **`.cursor/rules/sereno-streamlit-ux.mdc`** (tableaux admin au plus étroit, colonnes alignées).
- **Impact :** technique (`sereno_core/sheets_experts.py`, `proto_state.py`, pages **7**, **21**, **22**) ; documentation **CDC § 3.6 / § 3.9** et révision **1.32** ; règle Cursor UX.

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
