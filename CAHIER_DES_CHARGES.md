# Cahier des charges — SÉRÉNO (JOPAI BTP)

**Document :** spécification produit et technique — prototype / pilote.  
**Version :** 0.5 (architecture Python + double UX ; init Sheets ; page Tests connexions ; règle Cursor CDC).  
**Classification des sections :** Partie 1 — contexte & business · Partie 2 — fonctionnel · Partie 3 — technique.

---

# Partie 1 — Business case, vision, approche & pilote

## 1.1 Synthèse exécutive

**SÉRÉNO** est une application d’**intermédiation ultra-simplifiée** entre :

- des **particuliers** (y compris **seniors** et personnes **seules**) en **situation de stress technique** (fuite, panne électrique, gaz, chauffage, serrure / accès, etc.) ;
- et des **experts du bâtiment** pour un **dépannage en visio-assistance immédiate**.

**Promesse commerciale (cible de valeur) :** permettre de **résoudre une part significative des cas** (ordre de grandeur **~50 % des problèmes** abordables à distance en **~5 minutes**) moyennant un **forfait transparent** (ex. **50 €**), en réduisant le **coût** et le **stress** liés à un déplacement incertain ou à la **méfiance** envers un prestataire inconnu.

## 1.2 Cibles

| Segment | Besoins clés |
|--------|----------------|
| **Utilisateurs finaux** | Ergonomie maximale, boutons larges, contraste élevé, parcours « court » en situation de panique. |
| **Prestataires** | Complément de revenu **sans déplacement**, cadre clair, rémunération prévisible. |

## 1.3 « Plus » JOPAI

- **Paiement sécurisé** via la plateforme (cible : **Stripe Connect**).
- **Confiance** : experts « embarqués », charte de simplicité (réponses courtes, pas de jargon inutile).
- **SST** : consignes de **sécurité immédiates** (checklists avant activation caméra et selon le type d’urgence).

## 1.4 Positionnement vs alternatives

- Différenciation vis-à-vis des annuaires classiques : **réponse rapide**, **forfait court affiché**, **télé-expertise** en premier temps ; **passage sur place** ou **partenaire terrain** en second temps si besoin.

## 1.5 Objectifs du pilote

Valider **sur le terrain** (utilisateurs réels + experts réels) :

1. Le **parcours urgence** (5 types + checklist + visio).
2. La **charge cognitive** acceptable pour des **seniors** en stress.
3. Le **modèle économique** (forfait, répartition plateforme / expert) **sans aucun encaissement réel** : parcours **100 % simulé** (voir § 2.9).
4. La **faisabilité opérationnelle** d’un petit réseau d’experts (astreinte, SLA simplifié).

**Périmètre pilote obligatoire :** **application mobile** (**React Native + Expo**), installable sur téléphone, avec **caméra** et **micro** ; **dashboard expert** (Streamlit) ; **base unique** pilotée au départ par **Google Sheets** ; visio réelle (**Daily.co** ou **Twilio Video** selon arbitrage).

## 1.6 Phases de mise en œuvre (protocole produit)

| Phase | But | Critère de passage |
|-------|-----|---------------------|
| **P0 — Spéc** | Cahier des charges stable, risques identifiés | Validation interne JOPAI |
| **P1 — Démo technique** | Flux bouton → checklist → salle visio (même mock partiel) + écriture Sheets | Équipe |
| **P2 — Pilote** | App mobile + experts + **Sheets** + visio réelle + **testeurs** | Retours qualitatifs + métriques minimales |
| **P3 — Préprod** | Base relationnelle (Supabase), auth renforcée, Stripe hors test si validé | Beta fermée |
| **P4 — Prod cible** | Durée, conformité, hébergement souverain (ex. OVH) selon stratégie | Go / no-go |

## 1.7 Cahier d’échanges (gouvernance)

Tenir **une page d’historique des décisions** (date, décision, impact produit / technique / coût). Référencer ce document (version `.md` dans le dépôt ou export).

**Règle projet (Cursor) :** le dépôt inclut une règle **always-on** (`.cursor/rules/sereno-maintain-cdc.mdc`) : à chaque **évolution structurante** (fonctionnel, technique, infra, données, parcours, conventions), **mettre à jour** `CAHIER_DES_CHARGES.md` et la **table des révisions** — **sans** y copier de secrets.

## 1.8 Indicateurs pilote (minimum)

- Taux d’**abandon** avant checklist / avant visio.
- **Durée médiane** de session.
- **Satisfaction** utilisateur (1 question post-session).
- **Taux de résolution perçue** (« problème mieux maîtrisé oui/non »).

---

# Partie 2 — Description fonctionnelle

## 2.1 Périmètre fonctionnel MVP pilote

| Inclus | Hors périmètre MVP pilote (évolutif) |
|--------|--------------------------------------|
| 5 boutons métier d’accueil | Couverture nationale élargie sans réseau |
| Checklists SST par type | IA « danger » avancée |
| File d’attente / prise en charge expert | Marketplace ouverte large |
| Visio (SDK Daily ou Twilio) | Annotations vidéo très avancées |
| Enregistrement consentements + mentions SST | Archivage légal complet auto |
| Paiement **100 % simulé** (écrans « comme la vraie vie », **aucun** appel PSP) | Stripe **test** puis **live** |
| Compte rendu **manuel** ou PDF simple | Rapport PDF complet Vertex |

## 2.2 Les cinq boutons « urgence » (écran d’accueil)

Un **seul tap** lance le **type d’urgence** (libellés courts, pictogrammes, contraste élevé).

| ID | Libellé utilisateur | Rôle |
|----|---------------------|------|
| `EAU` | Eau | Fuites, coupure d’arrivée d’eau, inondation locale. |
| `ELEC` | Électricité | Disjoncteur, panne, risque électrique. |
| `GAZ` | Gaz | Odeur, coupure, consignes gaz (dont orientation urgence si besoin). |
| `CHAUFF` | Chauffage | Chaudière, radiateur, absence de chauffage / ECS (recoupe souvent gaz/élec — le bouton suit l’**intention** utilisateur). |
| `SERR` | Serrurerie / accès | Porte bloquée, cylindre, situation d’accès (sécurité d’abord). |

**Règle UX :** pas de liste de 20 métiers à l’écran 1 ; tout le reste pourra aller vers **« orientation »** ou **partenaires** en phase ultérieure.

## 2.3 Parcours utilisateur (grand public)

1. **Accueil** — Sélection du type (`EAU` … `SERR`).
2. **Checklist SST** — Affichage des items **obligatoires** selon le type ; **blocage** de la caméra si non validé où la règle l’impose.
3. **Mise en file / appariement** — Message de **réassurance** (temps d’attente, statut).
4. **Session visio** — Audio / vidéo ; actions prévues côté produit : **activation flash** à distance si le SDK le permet ; **annotations** : cible produit (niveau de richesse à calibrer en P3).
5. **Clôture** — Récap **forfait** (ex. 50 €), conditions courtes ; **flux paiement simulé** (§ 2.9).
6. **Après session** — Envoi ou téléchargement d’un **compte rendu** (template simple) ; option **« besoin d’un passage sur place »** (renvoi vers partenaire / prise de contact — au minimum texte + coordonnées en pilote).

## 2.4 Parcours expert (dashboard)

- Voir la **liste des demandes** ouvertes.
- **Prendre** une session (verrou : une session = un expert à la fois).
- Accéder au **lien / salle** visio.
- Saisir un **compte rendu court** post-session.
- Voir **historique** basique et statut **rémunération** (indicatif en pilote).

## 2.5 Règles métier transverses (moteur de règles — logique)

- **Avant visio :** application des **règles SST** (cf. feuille `Checklist_SST` + `Regles_Moteur` côté données).
- **Forfait :** montant paramétrable (feuille `Config`).
- **Statuts de session :** `CREEE`, `EN_FILE`, `EN_COURS`, `TERMINEE`, `ANNULEE`, `LITIGE` (affiner si besoin).

## 2.6 Extrait de user stories (critiques)

- **U1** — En tant qu’utilisateur, je sélectionne **un** des 5 types en **un** geste.
- **U2** — En tant qu’utilisateur, je ne peux pas activer la **caméra** tant que les **obligations SST** ne sont pas validées.
- **U3** — En tant qu’utilisateur, je vois le **prix forfaitaire** avant de confirmer le **flux paiement** ; en pilote, l’écran indique clairement la **simulation** (§ 2.9).
- **E1** — En tant qu’expert, je **réserve** une session de façon **exclusive**.
- **E2** — En tant qu’expert, je **complète** un compte rendu lié à la session.

## 2.7 Urgences vitale / collective (hors monétisation)

- Affichage **clair** des **numéros d’urgence** et **conduites à tenir** lorsque les réponses SST indiquent un **danger critique** (gaz fort, incendie, risque électrique majeur, violence).  
- **Ne pas** remplacer les services publics ; **limiter** la visio / le paiement dans ces cas.

## 2.8 Conformité & contenus (responsabilité)

Les **textes SST**, **CGU**, **mentions légales** et **politique de remboursement** doivent être **validés** par un **référent métier / juridique** avant passage en **Stripe live** et communication large.

## 2.9 Paiement pilote — simulation « plein écran » (fake)

**Objectif :** le testeur vit le **même enchaînement visuel** que le futur paiement réel (récap montant, saisie carte, validation), **sans** connexion à un prestataire de paiement et **sans** débit.

**Règles UX / produit :**

- **Bandeau ou badge permanent** sur les écrans concernés : *« Simulation — aucun paiement réel »* (ou équivalent très visible).
- **Même nombre d’étapes** que le design cible (montant, moyen de paiement, champs carte si prévus, confirmation).
- **Saisie carte :** l’utilisateur peut entrer un **numéro « type carte bleue »** ; le pilote **n’effectue aucune vérification bancaire**. Indication optionnelle en aide : exemple de type **carte de test** (ex. `4242 4242 4242 4242` — convention courante d’exemple, **sans valeur monétaire**), ou tout numéro au **format plausible** accepté pour la démo.
- **Comportement technique :** après « Payer », le code exécute une **boucle / branche locale** (succès simulé) : **aucun** appel **Stripe** (ni autre PSP) en pilote.
- **Retour utilisateur :** écran de **succès** aligné sur le futur produit, avec **rappel** que la transaction est **factice**.
- **Traçabilité :** enregistrer en base (Sheets, onglet `Paiements`) un statut du type **`SIMULE`** ou **`FAKE_OK`**, montant affiché, `session_id`, horodatage (pas de `payment_intent` réel).

**Hors pilote :** passage à **Stripe test** puis **live** + mentions légales et CGU adaptées.

---

# Partie 3 — Sujets techniques

## 3.1 Stack imposée (cible documentaire v0, adaptée pilote)

| Couche | Technologie |
|--------|-------------|
| **App mobile (usager)** | **React Native + Expo** |
| **Dashboard expert** | **Python + Streamlit** |
| **Base de données (pilote)** | **Google Sheets** (API) — **unique source de vérité** pour la phase pilote |
| **Base de données (cible)** | **Supabase** (PostgreSQL, Auth, temps réel) |
| **Visioconférence** | **Daily.co** ou **Twilio Video** |
| **IA (cible)** | **Vertex AI** (auth via **compte de service** GCP / ADC) — transcription, aide compte rendu / PDF |
| **IA (optionnel)** | **API Gemini** (clé dédiée) si besoin d’appels directs en parallèle de Vertex |
| **Stockage fichiers** | **Google Cloud Storage** — bucket pilote `jopai-sereno` (audio, exports, etc.) |
| **Paiements (pilote)** | **Simulation locale** — écrans complets, **aucun** encaissement (§ 2.9) |
| **Paiements (cible)** | **Stripe Connect** |
| **Hébergement cible** | Compatible **OVHcloud** à terme |

## 3.2 Compromis technique pour Cursor : l’app hybride (Expo)

**Choix :** **React Native (Expo)** pour le prototype et le pilote.

- **Langage :** **JavaScript / TypeScript** — itération rapide avec assistance IA (Cursor).
- **Résultat :** **application installable** sur téléphone, avec accès **natif** au **micro** et à la **caméra**, adaptée au **contexte d’urgence** (icône dédiée).

### Comparatif stratégique (référence produit)

| Critère | Site web (PWA) | App hybride (choix JOPAI) |
|--------|----------------|---------------------------|
| **Accès en urgence** | Moyen (navigateur) | **Excellent** (icône, lancement direct) |
| **Confiance / crédibilité** | Standard | **Renforcé** (perçu institutionnel) |
| **Visio (stabilité)** | Variable | **Meilleure** (pile mobile dédiée) |
| **Coût d’acquisition** | Faible (SEO) | Plus élevé (stores / ads), **fidélisation** souvent meilleure |

## 3.3 Architecture logique (pilote) — couches

**Accord d’architecture :** la **logique métier** (accès Sheets, règles SST, sessions, intégrations GCP, etc.) vit dans des **modules Python** (`sereno_core/`, scripts, futurs services). Les **interfaces** ne font qu’**orchestrer** et afficher : elles appellent cette logique, sans la dupliquer.

| Couche UX | Public | Technologie | Rôle |
|-----------|--------|-------------|------|
| **Web** | **Administrateurs**, **artisans / experts** | **Streamlit** (`Home.py`, `pages/…`) | File d’attente, prise de session, outils internes, **tests de connexion** |
| **Mobile** | **Clients** (grand public, seniors) | **React Native + Expo** | Parcours urgence, checklist, visio, paiement simulé pilote |

```
                    ┌─────────────────────────────────────────┐
                    │  sereno_core/ (Python) — logique métier │
                    │  schéma Sheets, règles, accès données   │
                    └─────────────────┬───────────────────────┘
          ┌───────────────────────────┼───────────────────────────┐
          ▼                           ▼                           ▼
   ┌──────────────┐           ┌──────────────┐           ┌─────────────────┐
   │  Streamlit   │           │  App Expo    │           │  APIs externes  │
   │  web admin / │           │  clients     │           │  GCS, Vertex,   │
   │  artisans    │           │              │           │  Daily, …       │
   └──────┬───────┘           └──────┬───────┘           └────────┬────────┘
          │                          │                            │
          └──────────────────────────┴────────────────────────────┘
                                     │
                            ┌────────▼────────┐
                            │  Google Sheets  │
                            │  (vérité pilote)│
                            └─────────────────┘
```

**Principes :**

- **Une base de données logique** (Sheets pilote puis Supabase) ; **deux canaux UX** (web Streamlit / mobile Expo) passant par la **même logique Python** autant que possible.
- **Moteur de règles :** tables `Regles_Moteur` / `Checklist_SST` + code dans `sereno_core` (éviter la logique métier uniquement dans les callbacks UI).
- **Limites Sheets :** pas de transactions ACID fortes, **concurrence** et **RGPD** — pilote limité dans le temps.

### 3.3.1 Arborescence code (référence)

| Élément | Rôle |
|---------|------|
| `sereno_core/` | Paquet Python : schéma Sheets (`sheets_schema.py`), futurs services (sessions, règles, clients API). |
| `scripts/init_google_sheet.py` | Crée les onglets manquants, écrit la **ligne 1** (en-têtes) et optionnellement les **lignes de graine** (voir § 3.9). |
| `Home.py` | Entrée Streamlit. |
| `pages/` | Pages multipages (ex. `1_Tests_connexions.py`). |

### 3.3.2 Interface Streamlit — navigation

L’accès aux pages du dossier `pages/` exige **`showSidebarNavigation = true`** dans `.streamlit/config.toml`. Sinon, seule la page d’accueil est visible et le texte « utilisez la barre latérale » prête à confusion. L’icône **≡** en haut à gauche permet d’**ouvrir** le menu si la barre est repliée.

## 3.4 Stratégie de migration Supabase (après pilote)

- Reproduire les **entités** ci-dessous en tables PostgreSQL.
- Remplacer les appels Sheets par **API Supabase** ; conserver **Streamlit** ou le faire évoluer.
- **Auth** utilisateurs / experts **avant** ouverture large.

## 3.5 Style UI (rappel)

- **Couleurs :** Bleu profond `#002366`, bleu électrique `#007BFF`, orange alerte `#FF8C00`.
- **Typographie :** sans-serif, **grande taille**, lisibilité senior.
- **Feedback :** animations de connexion **rassurantes** (non intrusives).

## 3.6 Modèle de données Google Sheets (pilote)

### 3.6.1 Liste des onglets recommandés

| Onglet (nom exact suggéré) | Rôle |
|----------------------------|------|
| `Config` | Paramètres globaux (forfait, devise, messages). |
| `Types_Urgence` | Les 5 types + métadonnées (ordre d’affichage, libellé, icône). |
| `Checklist_SST` | Lignes de questions par `type_code` + ordre + obligatoire oui/non. |
| `Regles_Moteur` | Règles simples (clé / condition / action) pour évolutions sans redéploiement lourd. |
| `Sessions` | Instances d’appels / visios. |
| `Experts` | Comptes pilote des artisans. |
| `Expert_Disponibilite` | (Optionnel) créneaux ou statut astreinte. |
| `Paiements` | (Optionnel) trace des intents Stripe test. |

### 3.6.2 Prêt à copier-coller — ligne d’en-tête par onglet

Créer **un onglet par bloc** ci-dessous. Coller **la ligne 1** telle quelle dans la **ligne 1** du nouvel onglet (séparer les colonnes : Google Sheets reconnaît les tabulations si vous collez depuis un éditeur de texte, ou utilisez **Données > Fractionner le texte en colonnes** avec séparateur **tabulation**).

---

#### Onglet : `Config`

Copier la ligne suivante → **ligne 1** :

```
cle	valeur	description
```

**Lignes d’exemple (lignes 2+, à adapter) :**

```
FORFAIT_CENTIMES	5000	Montant forfait session en centimes (ex: 50 EUR)
DEVISE	EUR	Code ISO devise
MESSAGE_FILE	Merci de patienter, un expert vous rejoint.	Réassurance file d attente
VERSION_REGLES	1	Incrementer si changement majeur checklist
PILOTE_PAIEMENT_MODE	FAKE	Simulation sans PSP — aligne le code sur le flux fake
```

---

#### Onglet : `Types_Urgence`

```
type_code	ordre		libelle_affichage		description_courte	actif
```

**Exemples lignes 2–6 :**

```
EAU	1	Eau	Fuites arret eau inondation locale	OUI
ELEC	2	Électricité	Disjoncteur panne risque	OUI
GAZ	3	Gaz	Odeur coupure consignes	OUI
CHAUFF	4	Chauffage	Chaudiere radiateur ECS	OUI
SERR	5	Serrurerie	Porte bloccee acces	OUI
```

---

#### Onglet : `Checklist_SST`

```
checklist_id	type_code	ordre	texte_question	type_reponse	obligatoire	bloquant_si	danger_niveau	notes_internes
```

* `type_reponse` : `OUI_NON` | `CHOIX` (prévoir extension).  
* `bloquant_si` : valeur qui **bloque** la visio (ex. `OUI` sur « odeur de gaz forte ») — laisser vide si non applicable.  
* `danger_niveau` : `0` aucun · `1` prudent · `2` critique (orientation urgence).

**Exemples (à compléter métier / juriste) :**

```
CHK-EAU-01	EAU	1	Avez vous identifie le robinet darret principal ou lentree deau	OUI_NON	OUI		Ignorer interne
CHK-EAU-02	EAU	2	Leau est elle en contact avec des prises ou materiel electrique	OUI_NON	OUI	OUI	2	Fuir vers ELEC urgence si OUI
CHK-ELEC-01	ELEC	1	Observez vous des etincelles flammes ou odeur de brule	OUI_NON	OUI	OUI	2	Orientation urgence
CHK-GAZ-01	GAZ	1	Sentez vous fortement le gaz ou avez vous des maux de tete nausees	OUI_NON	OUI	OUI	2	Ne pas actionner interrupteurs
CHK-CHAUFF-01	CHAUFF	1	Le probleme concerne il une installation gaz apparente	OUI_NON	OUI			
CHK-SERR-01	SERR	1	Etes vous en securite immediate sans violence en cours	OUI_NON	OUI	NON	2	Secours si violence
```

---

#### Onglet : `Regles_Moteur`

```
regle_id	priorite	condition_champ	operateur	valeur_attendue	action	code_message
```

**Exemples :**

```
R001	10	danger_niveau	EGAL	2	BLOQUER_VISIO	MSG_URGENCE
R002	20	checklist_complete	EGAL	TRUE	AUTORISER_VISIO	
```

*(En pilote, beaucoup de logique peut rester dans le code ; cette feuille prépare l’évolution.)*

---

#### Onglet : `Sessions`

```
session_id	created_at	type_code	statut	user_pseudo	user_contact	expert_id	room_url	notes_cloture	prix_centimes_factures	debut_visio	fin_visio
```

- `session_id` : identifiant unique texte (UUID ou `SER-20250407-001`).  
- `statut` : `CREEE` | `EN_FILE` | `EN_COURS` | `TERMINEE` | `ANNULEE` | `LITIGE`.  
- Colonnes **optionnelles** si besoin : `stripe_payment_intent_id`, `user_device`.

---

#### Onglet : `Experts`

```
expert_id	nom	email	telephone	actif	types_autorises	notes_internes	stripe_connect_account_id
```

**Exemple :**

```
EXP-001	Dupont Jean	jean.dupont@example.com	+33600000000	OUI	EAU;ELEC;CHAUFF	Pilote		
```

---

#### Onglet : `Expert_Disponibilite` (optionnel pilote)

```
expert_id	disponible_maintenant	derniere_mise_a_jour	commentaire
```

---

#### Onglet : `Paiements` (recommandé en pilote fake)

```
paiement_id	session_id	montant_centimes	mode_paiement	statut	stripe_id	created_at	notes
```

- `mode_paiement` : **`FAKE`** (pilote) · `STRIPE_TEST` · `STRIPE_LIVE` (évolution).  
- `statut` : ex. **`FAKE_OK`**, `SIMULE`, ou annulation locale.  
- `stripe_id` : vide en pilote **FAKE**.

---

### 3.6.3 Référentiel Google (classeur, compte de service, Vertex, GCS)

| Élément | Valeur / convention |
|--------|----------------------|
| **Classeur Sheets** | Nom projet : *Serno* — **ID** : `1Mm-amButSAePCcuKEjoWZXQh0HgWJoVLsIXNU7ybjOk` |
| **Partage** | Le classeur est partagé avec le compte de service : `jopai-sereno-streamlit-connect@sereno-492614.iam.gserviceaccount.com` (rôle **Éditeur** ou plus selon besoin). |
| **Identité GCP** | Projet : **`sereno-492614`** (déduit du domaine du compte de service). |
| **JSON credentials** | Fichier téléchargé depuis la console GCP, stocké **localement** (ex. sous `.streamlit/`) — **jamais** versionné (voir `.gitignore`). |
| **Vertex AI** | Accès via le **même** compte de service si les rôles IAM appropriés sont accordés (Vertex User, etc.) — **pas** de clé API obligatoire pour ce chemin. |
| **API Gemini (clé)** | Option réservée aux appels **API Gemini** en direct ; à renseigner dans `config/secrets.toml` si utilisé. |
| **Bucket GCS** | `jopai-sereno` — stockage **audio**, exports, artefacts ; droits **admin objets** sur le bucket pour la SA utilisée par l’app. |

### 3.6.4 Bilan infrastructure cloud (référence pilote SÉRÉNO)

Synthèse des **piliers** opérationnels côté Google Cloud / Google Workspace. **Aucun mot de passe ni clé secrète** ne figure dans ce document — uniquement des **noms** et **identifiants non secrets** (projet, bucket, email de compte de service, ID de classeur).

| Pilier | État (référence) | Usage pour SÉRÉNO |
|--------|------------------|-------------------|
| **Google Sheet partagé** | Configuré (accès SA) | **Base de données pilote** : configuration, types d’urgence, checklists SST, sessions, experts, paiements simulés, etc. (pas un catalogue « produits » e-commerce — données **métier urgence / artisans**). |
| **Bucket GCS `jopai-sereno`** | Autorisé (droits objets pour la SA) | Stockage **sécurisé** des **médias** liés aux pannes : **photos**, extraits **vidéo**, éventuels **fichiers audio** ; chemins d’objets référencés depuis l’app ou Sheets si besoin. |
| **Vertex AI (famille Gemini)** | Activé (projet `sereno-492614`) | **Intelligence** : analyse d’**images** / contexte, aide à la **guidance** client, **transcription** ou **compte rendu** (selon implémentation) — avec **quota** et **coûts** à surveiller. |
| **Compte de service** | Configuré | **Identité unique** (fichier **JSON** local, non versionné) reliant **Sheets API**, **GCS**, **Vertex** selon les **rôles IAM** attribués : `jopai-sereno-streamlit-connect@sereno-492614.iam.gserviceaccount.com`. |

**Complément — clés API « généralistes » (hors Vertex) :** si le code utilise **OpenAI** ou **l’API Gemini** (clé développeur Google AI Studio), ces secrets se placent dans **variables d’environnement** ou dans `.streamlit/secrets.toml` **uniquement en local** ; **ne pas** dupliquer une **clé privée de compte de service** dans le TOML — utiliser **`service_account_json_path`** + fichier JSON ignoré par Git.

---

## 3.7 Sécurité & confidentialité (rappels)

- Pas de **clés API**, **JSON de compte de service** ni `secrets.toml` rempli dans Git (voir `.gitignore`).
- **Consentement** explicite pour enregistrement / transcription si activé plus tard.
- **RGPD** : minimisation des données dans Sheets ; durée de rétention définie.
- **Pilote fake** : aucune donnée de carte ne doit être interprétée comme un engagement de paiement réel ; éviter de logger des PAN complets en clair si possible (masquage).
- **Compte de service GCP :** ne **jamais** coller `private_key` / `private_key_id` dans un `.toml` versionné ou partagé ; conserver **un seul fichier JSON** hors dépôt et définir `GOOGLE_APPLICATION_CREDENTIALS` ou `service_account_json_path` en conséquence. En cas d’exposition : **révoquer la clé** dans la console IAM et **en créer une nouvelle**.
- **Clés OpenAI / autres API :** même règle — si une clé a été copiée dans un fichier lisible par un tiers ou un historique de chat, la **révoquer** et en émettre une **nouvelle**.

## 3.8 Fichiers de configuration et secrets (TOML)

**Objectif :** un seul modèle pour **Sheets**, **GCP / Vertex**, **GCS**, **Gemini (optionnel)**, **paiement pilote**, clés futures (Stripe, Daily, Twilio).

| Fichier | Rôle |
|---------|------|
| `config/secrets.example.toml` | **Modèle versionné** : copier vers `config/secrets.toml` et remplir les chemins / clés. |
| `config/secrets.toml` | **Réel, non versionné** — secrets locaux ou CI masqué. |
| `.streamlit/secrets.toml` | Utilisé nativement par **Streamlit** (`st.secrets`) : dupliquer le contenu pertinent depuis `config/secrets.toml` ou charger le même fichier en code selon choix d’implémentation. |
| `.streamlit/*.json` | **Compte de service Google** — **non versionné** ; référencer le nom exact dans `secrets.toml` (`service_account_json_path`). |
| `config/keys/` | Dossier optionnel pour clés JSON copiés ; **non versionné** (`*.json` ignorés). |

Variable d’environnement usuelle pour les libs Google : `GOOGLE_APPLICATION_CREDENTIALS` peut pointer vers le chemin absolu du JSON (alternative au chemin relatif dans le TOML).

### 3.8.1 Conventions actuelles `.streamlit/secrets.toml` (noms de clés)

| Clé (nom) | Rôle | Secret dans le CDC ? |
|-----------|------|----------------------|
| `gsheet_id` | ID du classeur Google Sheets | Non (identifiant URL). |
| `gcs_bucket_name` | Nom du bucket GCS | Non. |
| `gcp_project_id` | Projet GCP | Non. |
| `service_account_email` | Email de la SA | Non (identifiant public). |
| `service_account_json_path` | Chemin vers le fichier JSON | Le **chemin** seulement ; le **fichier** contient le secret. |
| `OPENAI_API_KEY` | API OpenAI (optionnel) | **Jamais** documenté ici — variable d’env ou local. |
| `GEMINI_API_KEY` | API Gemini hors Vertex (optionnel) | Idem. |

Le fichier `config/secrets.example.toml` peut utiliser des synonymes (`sheets_spreadsheet_id`) : à **harmoniser** dans le code pour n’avoir qu’**une** source de vérité par déploiement.

## 3.9 Outils Streamlit et initialisation Google Sheets

### 3.9.1 Page « Tests connexions »

- **Fichier :** `pages/1_Tests_connexions.py`.
- **But :** vérifications **manuelles** (boutons) : **Google Sheets** (lecture ; écriture optionnelle vers `Connexions_Test`), **GCS** (liste d’objets), **Vertex AI** (appel court au modèle configuré).
- **Lancement :** `streamlit run Home.py` depuis la racine du dépôt ; URL locale type `http://localhost:8501`.

### 3.9.2 Script `scripts/init_google_sheet.py`

- **Source des colonnes et graines :** `sereno_core/sheets_schema.py` (aligné sur § 3.6.2).
- **Configuration :** lit `gsheet_id` et `service_account_json_path` dans `.streamlit/secrets.toml`.
- **Commandes :**
  - `python scripts/init_google_sheet.py` — crée les onglets manquants, écrit les **en-têtes** (ligne 1) si la ligne 1 est vide (sinon conserve).
  - `python scripts/init_google_sheet.py --seed` — ajoute les **lignes d’exemple** uniquement si l’onglet n’a **aucune donnée sous l’en-tête** (évite d’écraser un classeur déjà rempli).
  - `python scripts/init_google_sheet.py --force-headers` — **réécrit** la ligne 1 (à utiliser avec prudence si les titres ont été personnalisés).
- **Onglet `Connexions_Test` :** créé avec les mêmes en-têtes que la page de tests Streamlit (`horodatage_utc`, `source`, `statut`, `note`).

---

## Annexes — révisions

| Version | Date | Auteur | Résumé |
|---------|------|--------|--------|
| 0.5 | 2026-04-07 | JOPAI + assistant | § 3.3 couches Python + double UX ; § 3.9 Tests connexions + `init_google_sheet.py` ; `sereno_core` ; navigation Streamlit ; règle `.cursor/rules/sereno-maintain-cdc.mdc`. |
| 0.4 | 2026-04-07 | JOPAI + assistant | § 3.6.4 bilan infra cloud ; conventions secrets Streamlit ; règles anti-fuite clés SA / OpenAI. |
| 0.3 | 2026-04-07 | JOPAI + assistant | Paiement pilote 100 % fake (§ 2.9) ; ID Sheets + SA + GCS ; `config/secrets.example.toml` ; Vertex vs Gemini ; onglet Paiements `mode_paiement`. |
| 0.2 | 2026-04-07 | JOPAI + assistant | 3 parties ; Sheets détaillé ; 5 boutons dont Serrurerie ; pilote mobile Expo. |
| 0.1 | (v0 source) | JOPAI | Document Word initial. |

---

*Fin du cahier des charges — SÉRÉNO.*
