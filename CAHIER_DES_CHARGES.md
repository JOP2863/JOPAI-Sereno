# Cahier des charges — SÉRÉNO (JOPAI BTP)

**Document :** spécification produit et technique — prototype / pilote.  
**Version :** 1.7 (reporting indicateurs CDC ; conformité Pappers / table `papers` ; menus Projet / Admin pilote ; sélection expert **nom — spécialité (id)** ; PDF accueil novices ; dispos via Admin pilote).  
**Classification des sections :** Partie 1 — contexte & business · Partie 2 — fonctionnel · Partie 3 — technique · **Partie 4 — avancements** (idée → pilote → produit).

**Comment lire ce cahier :**

- **Partie 1 et 2** sont rédigées pour des **intervenants terrain** (artisans, responsables réseau, partenaires) : on évite le jargon informatique quand on peut, et on **explique les sigles** à la première occurrence utile.
- **Partie 3** reste **technique** : elle s’adresse aux **développeurs**, intégrateurs et équipe JOPAI qui posent l’architecture (noms d’outils, APIs, fichiers).
- **Partie 4** sert au **suivi** du projet (jalons, MVP, environnement de travail).

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

**JOPAI** est une **marque** spécialisée dans l’**intelligence artificielle** et les **services numériques** ; elle s’adresse en particulier aux **métiers de l’artisanat** et du **BTP** (accompagnement, outils, prototypes produits comme SÉRÉNO).

- **Paiement sécurisé** via la plateforme (cible : **Stripe Connect** — système qui **répartit** l’argent entre la plateforme et l’expert après une vraie transaction ; **hors pilote** simulé).
- **Confiance** : experts « embarqués », charte de simplicité (réponses courtes, pas de jargon inutile).
- **SST** : consignes de **sécurité immédiates** (checklists avant activation caméra et selon le type d’urgence).

## 1.4 Positionnement vs alternatives

- Différenciation vis-à-vis des annuaires classiques : **réponse rapide**, **forfait court affiché**, **télé-expertise** en premier temps ; **passage sur place** ou **partenaire terrain** en second temps si besoin.

## 1.5 Objectifs du pilote

Valider **sur le terrain** (utilisateurs réels + experts réels) :

1. Le **parcours urgence** (5 types + checklist + visio).
2. La **charge cognitive** acceptable pour des **seniors** en stress.
3. Le **modèle économique** (forfait, répartition plateforme / expert) **sans aucun encaissement réel** : parcours **100 % simulé** (voir § 2.9).
4. La **faisabilité opérationnelle** d’un petit réseau d’experts (**astreinte**, **délais de réponse** raisonnables et simples — en informatique on dit parfois *SLA*, *Service Level Agreement* : « ce qu’on s’engage à tenir comme délai »).

**Périmètre pilote obligatoire :** une **application sur téléphone** (techniquement : **React Native + Expo** = boîte à outils pour fabriquer l’app mobile), avec **caméra** et **micro** ; un **tableau de bord sur le web pour les experts** (outil **Streamlit**) ; une **base de données simple** au départ sous forme de **tableur Google (Sheets)** ; une **vraie visioconférence** branchée sur un **prestataire visio** (**Daily.co** ou **Twilio Video** — deux fournisseurs possibles, comme choisir un opérateur téléphonique).

## 1.6 Phases de mise en œuvre (protocole produit)

Ce tableau décrit les **étapes de construction** du service, du cahier des charges jusqu’à une **mise en production** : ce sont des **jalons** pour l’équipe, pas des étapes que le particulier voit à l’écran.

| Phase | But | Critère de passage |
|-------|-----|---------------------|
| **P0 — Spéc** | Cahier des charges stable, risques identifiés | Validation interne JOPAI |
| **P1 — Démo technique** | **Pour un plombier ou tout intervenant terrain :** vous appuyez sur **un gros bouton** (ex. « Eau ») → l’appli vous pose **quelques questions courtes** (téléphone, prénom) → puis une **liste de sécurité** (coupure d’eau, électricité mouillée…) à valider **une ligne après l’autre** → ensuite seulement l’écran « **salle de visio** » (même en **maquette** sans vraie vidéo au début) ; en parallèle le système **écrit une ligne** dans **Google Sheets** pour suivre la demande. | Équipe |
| **P2 — Pilote** | App mobile + experts + **Sheets** + visio réelle + **testeurs** | Retours qualitatifs + métriques minimales |
| **P3 — Préprod** | Base relationnelle (Supabase), auth renforcée, Stripe hors test si validé | Beta fermée |
| **P4 — Prod cible** | Durée, conformité, hébergement souverain (ex. OVH) selon stratégie | Go / no-go |

## 1.7 Indicateurs pilote (cible complète, même si tout n’est pas mesurable au jour 1)

Les indicateurs ci-dessous servent de **grille de lecture** pour la phase pilote et la montée en charge ; plusieurs pourront rester à **zéro** ou **non instrumentés** au tout début.

| Indicateur (exemple) | Définition courte | Intérêt opérationnel |
|----------------------|-------------------|----------------------|
| **Artisans référencés** | Nombre d’experts actifs dans le réseau | Taille du vivier |
| **Taux de couverture 24/7** | Part du temps (sur une semaine type) où **au moins un** artisan éligible est **joignable** ou en **astreinte** | Rassurer l’usager sur la disponibilité |
| **Taux de couverture par type d’urgence** | Pour chaque bouton (eau, élec, …), part des créneaux couverts | Équilibrer le réseau par métier |
| **Délai médian de première réponse** | Temps entre « demande lancée » et « expert joint / salle ouverte » | Qualité perçue |
| **Taux d’abandon** | Arrêt avant fin checklist / avant visio / avant l’étape paiement (pilote) | Frictions UX |
| **Durée médiane de session visio** | Temps passé en visio | Charge experts |
| **Satisfaction** (étoiles + NPS) | Après session | Qualité du service |
| **Taux de résolution perçue** | « Problème mieux maîtrisé » oui/non | Efficacité à distance |
| **Taux de recontact sous 24 h** | Nouvelle demande liée au même dossier | Suivi / qualité |
| **Taux de passage au déplacement** | Visio insuffisante → intervention terrain | Complémentarité |
| **Revenu moyen par session** (cible) | Après monétisation réelle | Viabilité |

### 1.7.1 Disponibilité des artisans — calendrier, astreinte, verrouillage

**Besoin métier :** savoir **qui est disponible** et **quand**, y compris pour des **astreintes** (soir, week-end), sans imposer une saisie jour par jour au début.

**Règles produit (cible) :**

- Saisie par **mois** : l’artisan indique pour chaque **mois** (sur une **fenêtre glissante de 12 mois** à l’avance) son **niveau de disponibilité** ou des **créneaux d’astreinte** (ex. plage horaire + jours de semaine).
- **Verrouillage à J−30** : au-delà de **30 jours** avant le début d’un mois, les créneaux de ce mois deviennent **figés** pour l’usager (sauf action administrateur / cas exceptionnel à définir) — cela stabilise la planification côté plateforme.

**Structure de données (schéma relationnel cible — équivalent possible en onglets Sheets puis migration Supabase)**

- Table **`experts`** : `expert_id`, `nom`, `email`, `telephone`, `types_autorises` (liste de codes urgence), `actif` (bool), `timezone`, …
- Table **`disponibilite_mois`** : `id`, `expert_id`, `annee_mois` (ex. `2026-04`), `mode` (`enum` : `indisponible` | `standard` | `astreinte` | `sur_rdv`), `commentaire_interne` (texte court), `saisi_le`, `verrouille_le` (nullable tant que non figé).
- Table **`creneau_astreinte`** (optionnel si le mode mois suffit) : `id`, `expert_id`, `annee_mois`, `jour_semaine` (0–6) ou `date_specifique`, `heure_debut`, `heure_fin`, `fuseau`, `priorite_appel` (entier).
- Table **`indisponibilite_exception`** : `id`, `expert_id`, `debut_ts`, `fin_ts`, `motif` (congés, formation, etc.).

**Interface pilote (Streamlit) — saisie et sélection :**

- **Où saisir les disponibilités :** menu **Administration · Pilote** — **Dispo. artisan** (`pages/16_Admin_artisan_disponibilites.py`) et **Dispo. réseau (proprio)** (`pages/17_Admin_proprietaire_disponibilites.py`). Les lignes sont **ajoutées** dans l’onglet Sheets **`Disponibilite_Mois`** (même mécanisme pour l’artisan et le propriétaire ; règles de **fenêtre sensible** & accord propriétaire / artisan décrites dans l’UI et rappelées ci-dessous).
- **Règle d’affichage des experts dans les listes :** une **entrée par couple (expert, type d’intervention autorisé)** — format **`Nom — Libellé urgence (expert_id)`** (ex. *ROBERT Sébastien — Gaz (EXP-002)* et *ROBERT Sébastien — Eau (EXP-002)* si l’expert a plusieurs `types_autorises` dans Sheets). Même logique sur la page **Conformité réseau (SIREN / Pappers)** pour rattacher une requête à un **contexte métier** clair.
- **Fenêtre sensible (< 30 jours avant le 1ᵉʳ du mois concerné, ou mois passé) :** l’artisan ne doit **pas** modifier seul sans **notifier le propriétaire** (case à cocher en pilote) ; le propriétaire doit confirmer un **accord artisan** pour agir sur ces mois — aligné gouvernance § 1.7.1.
- **Page `pages/15_Disponibilite_artisans.py` :** conservée comme **vue / maintenance** sur la structure Sheets ; **elle n’apparaît plus** dans le menu **Projet** (menu allégé — la saisie opérationnelle passe par **Administration · Pilote**).

**Indicateurs dérivés :** couverture 24/7, taux de « mois complets » renseignés par expert, respect du verrouillage J−30.

**Règle projet (Cursor) :** le dépôt inclut une règle **always-on** (`.cursor/rules/sereno-maintain-cdc.mdc`) : à chaque **évolution structurante**, **mettre à jour** `CAHIER_DES_CHARGES.md` et la **table des révisions** — **sans** y copier de secrets.

## 1.8 Certifications, assurance et cadre MAIF (référentiel externe)

Le document Word **« certifications et MAIF »** (version équipe JOPAI, hors dépôt Git) complète ce cahier pour :

- les **exigences assurance** et de responsabilité (intervenants, plateforme, télé-expertise) ;
- les **certifications** ou référentiels qualité pertinents pour le BTP et les services numériques associés ;
- les **exigences de contenu** (dont **prompts** validés pour icônes urgence, schémas pédagogiques et supports grand public) alignés sur le discours **MAIF** et les partenaires concernés.

**Règle projet :** toute évolution touchant l’assurance, les labels ou les engagements vis-à-vis des usagers doit **croiser** trois sources : ce cahier, le document Word susnommé et le carnet d’échange (`docs/CAHIER_ECHANGES.md`). Les polices **DejaVu** utilisées pour l’export PDF du CDC sont des fichiers **TTF** techniques (lisibilité UTF-8) : elles ne remplacent pas les exigences rédactionnelles ou graphiques du référentiel MAIF.

---

# Partie 2 — Description fonctionnelle

## 2.1 Périmètre fonctionnel MVP pilote

Le **MVP** (*Minimum Viable Product* — « première version suffisante pour tester sur le terrain ») du **pilote** fixe ce qui est **livré tout de suite** et ce qui est **volontairement repoussé** pour aller vite et apprendre sans sur-complexifier.

### 2.1.1 Tableau — Inclus / Hors périmètre MVP pilote (évolutif)

| **Inclus (dans le pilote)** | **Hors périmètre MVP pilote (évolutif)** |
|-----------------------------|------------------------------------------|
| 5 boutons métier d’accueil | Couverture nationale élargie sans réseau |
| Checklists SST par type | IA « danger » avancée |
| File d’attente / prise en charge expert | Marketplace ouverte large |
| Visio (SDK Daily ou Twilio) | Annotations vidéo très avancées |
| Enregistrement consentements + mentions SST | Archivage légal complet auto |
| Paiement **100 % simulé** (écrans « comme la vraie vie », **aucun** appel PSP) | Stripe **test** puis **live** |
| Compte rendu **manuel** ou PDF simple | Rapport PDF complet Vertex |

*Remarque :* une **synthèse par domaine** (UX, données, IA, etc.) figure aussi en **§ 4.2** ; le tableau ci-dessus reste la **référence détaillée** ligne à ligne.

### 2.1.2 Mini-glossaire — sigles du tableau (pour un lecteur non informaticien)

| Sigle ou terme | Explication courte |
|----------------|-------------------|
| **MVP** | *Minimum Viable Product* : **première version de l’app** qui permet déjà de faire le vrai parcours pilote, sans toutes les fonctions futures. |
| **Pilote** | Phase où de **vrais utilisateurs** et **vrais experts** testent, avec un périmètre **contrôlé** (souvent une région / un petit réseau). |
| **SST** | *Santé et Sécurité au Travail* : tout ce qui protège **vous** et le **particulier** avant qu’il allume la caméra (couper l’eau, ne pas toucher à l’élec mouillée, etc.). |
| **SDK** | *Software Development Kit* : en pratique, le **kit fourni par l’éditeur de visio** pour **brancher** la visioconférence dans l’app (ici **Daily** ou **Twilio**). |
| **IA** | *Intelligence artificielle* : ici, des fonctions **automatiques** (détection de danger, texte…) — **pas** dans le MVP pilote sauf mention contraire. |
| **Marketplace** | **Grand catalogue ouvert** où plein d’artisans inconnus se présentent ; le pilote vise au contraire un **petit réseau de confiance**. |
| **PSP** | *Payment Service Provider* : **prestataire de paiement** en ligne (carte bancaire). Au pilote : **aucun** vrai PSP n’est appelé. |
| **Stripe** | **Service de paiement** courant sur Internet (comme un TPE virtuel pour sites et apps). Prévu **après** le pilote (mode test puis réel). |
| **Vertex** | Nom d’un **service Google** pour l’IA « entreprise » ; sert notamment à des **rapports ou aides rédigées** plus tard — **pas** le cœur du pilote visio. |
| **PDF** | Fichier **document lisible partout** ; au pilote on vise un compte rendu **simple** ou **saisi à la main**, pas un rapport IA de 20 pages. |
| **Évolutif** | « **Plus tard**, quand le produit aura grandi » — ce n’est **pas** une promesse pour le premier pilote. |

### 2.1.3 Q / R — comprendre chaque ligne du tableau (novice)

**Ligne : 5 boutons métier d’accueil / couverture nationale sans réseau**

- **Q.** Pourquoi seulement cinq boutons ?  
  **R.** En urgence, il faut **choisir vite** sans se perdre dans une liste de métiers. Les cinq types couvrent les **urgences les plus fréquentes** (eau, élec, gaz, chauffage, serrure).  
- **Q.** Qu’est-ce qu’on ne fait pas encore ?  
  **R.** Couvrir **toute la France** avec un **grand réseau** d’artisans vérifiés : ça demande **organisation et volume** ; ce n’est **pas** l’objectif du premier pilote.

**Ligne : Checklists SST / IA « danger » avancée**

- **Q.** À quoi servent les checklists ?  
  **R.** À **éviter l’accident** avant la visio : rappels du type « couper l’arrivée d’eau », « ne pas forcer la serrure si… ».  
- **Q.** Et l’IA « danger » ?  
  **R.** Plus tard, l’app pourrait **analyser l’image** ou le son pour **signaler un danger** ; c’est **technique et risqué** si mal réglé — **hors** MVP pilote.

**Ligne : File d’attente / prise en charge expert — marketplace large**

- **Q.** C’est quoi la file ?  
  **R.** Le particulier **attend** qu’un **expert disponible** prenne sa demande ; un seul expert par session pour **clarté** et **responsabilité**.  
- **Q.** Pourquoi pas une marketplace ouverte ?  
  **R.** Une marketplace = **beaucoup d’inconnus** ; SÉRÉNO vise d’abord la **confiance** avec un **petit groupe** d’experts **identifiés**.

**Ligne : Visio Daily ou Twilio / annotations vidéo avancées**

- **Q.** Qu’est-ce qu’on livre ?  
  **R.** Une **vraie conversation vidéo** stable sur téléphone, via un **fournisseur spécialisé** (Daily ou Twilio).  
- **Q.** Qu’est-ce qu’on repousse ?  
  **R.** Dessiner, flécher, annoter la vidéo comme sur un **outil pro de visio** : utile plus tard, **pas indispensable** pour valider le pilote.

**Ligne : Consentements + mentions SST / archivage légal complet auto**

- **Q.** Qu’est-ce qui est inclus ?  
  **R.** Le particulier **accepte** clairement (case, texte court) d’être filmé / enregistré selon les règles prévues, avec les **mentions SST** affichées.  
- **Q.** Qu’est-ce qui manque encore ?  
  **R.** Un **archivage juridique « clé en main »** (preuves, conservation X années, procédures) : métier **avocat / conformité** — **après** le pilote.

**Ligne : Paiement simulé / Stripe test puis live**

- **Q.** Le pilote encaisse-t-il de l’argent ?  
  **R.** **Non.** L’écran **ressemble** au futur paiement réel, mais **aucun** lien avec une **banque en ligne** (PSP) : c’est une **simulation** pour tester le **ressenti** utilisateur.  
- **Q.** Et Stripe ?  
  **R.** C’est le **futur** moyen de paiement probable ; on passera par des **cartes de test**, puis le **réel**, quand le **juridique** et le **produit** seront prêts.

**Ligne : Compte rendu manuel ou PDF simple / rapport Vertex complet**

- **Q.** Qu’attend-on de l’expert après la visio ?  
  **R.** Un **résumé court** (saisi dans l’outil ou petit PDF) pour le particulier — **l’essentiel**, pas un **rapport d’expertise** de chantier.  
- **Q.** Qu’est-ce que « rapport Vertex complet » ?  
  **R.** Un **document long** généré par **l’IA Google Vertex** : intéressant **plus tard** pour industrialiser ; **pas** le besoin du pilote.

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
4. **Session visio** — Audio / vidéo ; actions prévues côté produit : **activation lampe torche** à distance si l’outil visio le permet ; **dessins / flèches sur l’image** : prévu plus tard (phase **P3** — voir § 1.6).
5. **Clôture** — Récap **forfait** (ex. 50 €), conditions courtes ; **flux paiement simulé** (§ 2.9).
6. **Après session** — Envoi ou téléchargement d’un **compte rendu** (template simple) ; option **« besoin d’un passage sur place »** (renvoi vers partenaire / prise de contact — au minimum texte + coordonnées en pilote).

## 2.4 Parcours expert (dashboard)

- Voir la **liste des demandes** ouvertes.
- **Prendre** une session (verrou : une session = un expert à la fois).
- Accéder au **lien / salle** visio.
- Saisir un **compte rendu court** post-session.
- Voir **historique** basique et statut **rémunération** (indicatif en pilote).

## 2.5 Règles métier transverses (logique automatique dans l’app)

Ici, « **moteur de règles** » = l’**ensemble des conditions automatiques** dans le programme : par exemple « si la checklist n’est pas cochée, la caméra reste bloquée ». Ce n’est pas vous qui les codez à la main sur le chantier ; c’est **paramétré** dans les données (voir feuilles **Checklist_SST** et **Regles_Moteur** côté tableur — détail **§ 3.6**).

- **Avant visio :** application des **règles SST** (cf. feuille `Checklist_SST` + `Regles_Moteur` côté données).
- **Forfait :** montant paramétrable (feuille `Config`).
- **Statuts de session :** `CREEE`, `EN_FILE`, `EN_COURS`, `TERMINEE`, `ANNULEE`, `LITIGE` (affiner si besoin).

## 2.6 Cas concrets d’usage (ce que l’app doit permettre)

En équipe informatique, on appelle souvent ça des **« user stories »** (littéralement « histoires d’utilisateur ») : une phrase du type *« en tant que… je veux… afin de… »*.  
Pour un **lecteur métier** (plombier, électricien, responsable réseau), on parle plutôt de **cas concrets** ou **scénarios** : *« le client doit pouvoir faire X »*, *« l’expert doit pouvoir faire Y »* — c’est **la même idée**, sans l’anglicisme.

**Cas particulier — utilisateur (particulier en urgence)**

| ID | Cas concret | En bref |
|----|-------------|--------|
| **U1** | Choisir son type de problème **tout de suite** | **Un** appui pour dire : eau, élec, gaz, chauffage ou serrure — pas quinze menus. |
| **U2** | Ne pas allumer la caméra **trop tôt** | Tant que les **consignes de sécurité (SST)** obligatoires ne sont pas validées, la caméra reste **désactivée** si les règles le demandent. |
| **U3** | Voir le **prix** avant de « payer » | Le **forfait** est visible **avant** l’écran de paiement ; au **pilote**, un texte clair indique que c’est une **simulation** (§ 2.9) — **aucun** vrai débit. |

**Cas particulier — expert**

| ID | Cas concret | En bref |
|----|-------------|--------|
| **E1** | Prendre une demande **sans doublon** | Quand je **prends** une session, les autres experts voient qu’elle est **occupée** : **une** session = **un** expert à la fois. |
| **E2** | Clôturer proprement | Après la visio, je **remplis** un **compte rendu** lié à cette session (texte court / simple PDF selon pilote). |

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

**Public visé :** développeurs, intégrateurs, équipe JOPAI technique. Cette partie **conserve volontairement** les **noms d’outils**, **sigles** et **fichiers** du projet — ce n’est **pas** la même cible de lecture que les **parties 1 et 2**.

## 3.1 Stack imposée (cible documentaire v0, adaptée pilote)

| Couche | Technologie |
|--------|-------------|
| **App mobile (usager)** | **React Native + Expo** |
| **Dashboard expert** | **Python + Streamlit** |
| **Base de données (pilote)** | **Google Sheets** (API) — **unique source de vérité** pour la phase pilote |
| **Base de données (cible)** | **Supabase** (PostgreSQL, Auth, temps réel) |
| **Visioconférence** | **Daily.co** ou **Twilio Video** |
| **Interface client web (démo / pilote)** | **Streamlit** déployé (ex. **https://jopai-sereno.streamlit.app/**) — parcours complet dans le navigateur ; **l’app mobile cible** reste **Expo** (hors ce déploiement). |
| **IA (cible)** | **Vertex AI** (auth via **compte de service** GCP / ADC) — transcription, aide compte rendu / PDF |
| **IA (optionnel)** | **API Gemini** (clé dédiée) si besoin d’appels directs en parallèle de Vertex |
| **Stockage fichiers** | **Google Cloud Storage** — bucket pilote `jopai-sereno` (audio, exports, etc.) |
| **Paiements (pilote)** | **Simulation locale** — écrans complets, **aucun** encaissement (§ 2.9) |
| **Paiements (cible)** | **Stripe Connect** |
| **Hébergement cible** | Compatible **OVHcloud** à terme |

### 3.1.1 Visioconférence — câblage minimal (pilote sans flux vidéo obligatoire)

**Objectif :** préparer l’**intégration** sans imposer tout de suite un **flux WebRTC** complet dans Streamlit ou Expo.

- **Secrets Streamlit** (ex. `.streamlit/secrets.toml`, non versionné) : prévoir une clé **`daily_room_url`** et/ou **`twilio_video_room_url`** (URL de salle ou de page **join** fournie par le prestataire après création de salle côté backend).
- **Comportement UI :** si une URL est renseignée, le parcours client affiche un **lien principal** « ouvrir la salle » vers ce fournisseur ; sinon, **maquette** / **Jitsi public** uniquement pour la démo, avec rappel « ne pas diffuser d’infos sensibles ».
- **Étape suivante produit :** création de salles **côté serveur** (token **Daily** ou **Twilio**), durée de vie courte, enregistrement du `room_url` dans l’onglet **`Sessions`** (Sheets puis BDD).

**Notification artisan (pilote → produit) :**

- **Déclenchement :** au clic **« Ouvrir la salle de visio »**, l’app tente de prévenir l’artisan assigné (données depuis l’onglet **`Experts`**, colonne `telephone`). Cela permet qu’« ça sonne » côté artisan.
- **Canaux supportés (priorité configurable)** : **SMS**, puis **appel vocal**, puis **push** (application mobile). L’ordre est configurable via `notification_priority` dans les secrets.
- **Implémentation pilote (Streamlit)** : Twilio pour **SMS** + **appel** (réveil vocal). Le push est un stub (cible Expo).

**Enregistrement visio (optionnel) :**

- Si une salle **Daily** est utilisée et qu’une clé **`DAILY_API_KEY`** est fournie, le pilote peut déclencher le **start/stop recording** via l’API Daily.
- La cible produit consiste à **stocker** l’enregistrement (ou ses sorties) dans le bucket GCS `jopai-sereno` et à référencer le chemin objet depuis `Sessions`.

**Règle de nommage des fichiers visio (GCS) :**

Préfixe recommandé (dossiers) :

`visio/YYYY/MM/DD/<pseudo_client>__<session_id>__<code>-<libelle>/`

Exemple :

`visio/2026/04/08/Marie__636B75AD__EAU-Eau/`

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
| `sereno_core/` | Paquet Python : `sheets_schema`, **`gcp_credentials`**, **`sheets_experts`** (dont **`disponibilite_expert_options`**), **`md_chapters`**, **`streamlit_markdown_book`**, **`cdc_pdf_export`**, **`projet_navigation_intro`**, **`reporting_cdc_indicators`**, **`pappers_client`**, etc. |
| `scripts/init_google_sheet.py` | Crée les onglets manquants, écrit la **ligne 1** (en-têtes) et optionnellement les **lignes de graine** (voir § 3.9). |
| `scripts/sql/create_papers_cache_table.sql` | Script PostgreSQL — table **`papers`** (cache JSON API Pappers). |
| `Home.py` | Entrée Streamlit. |
| `pages/` | Tests, CDC, carnet, métriques (`14`), reporting (`19`), proto client / artisan / propriétaire (`4`–`13`, `18`), admin dispos (`16`–`17`), etc. |
| `docs/CAHIER_ECHANGES.md` | **Carnet d’échange** (fil décisions / discussions) — page Streamlit homonyme. |

### 3.3.2 Interface Streamlit — navigation

L’accès aux pages du dossier `pages/` exige **`showSidebarNavigation = true`** dans `.streamlit/config.toml`. Sinon, seule la page d’accueil est visible et le texte « utilisez la barre latérale » prête à confusion. L’icône **≡** en haut à gauche permet d’**ouvrir** le menu si la barre est repliée.

**Regroupements du menu (`Home.py`) :**

| Section | Contenu principal (fichiers `pages/`) |
|---------|--------------------------------------|
| **Projet** | Accueil, **Métriques** (lignes CDC / code), **Reporting** (canevas indicateurs § 1.7), Cahier des charges, Carnet d’échange, Tests connexions. |
| **Prototype · Client** | Guide parcours, flux urgence → … → satisfaction. |
| **Prototype · Artisan** | Tableau de bord expert. |
| **Prototype · Propriétaire** | Activité réseau, **Conformité (SIREN / Pappers)**. |
| **Administration · Pilote** | **Dispo. artisan**, **Dispo. réseau (proprio)** — saisie `Disponibilite_Mois` (§ 1.7.1). |

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
| `Disponibilite_Mois` | Par expert et mois (`AAAA-MM`) : mode, commentaire, dates saisie / verrouillage (**§ 1.7.1**). |
| `Creneau_Astreinte` | Détail optionnel : jour / date, plage horaire, fuseau, priorité d’appel. |
| `Indisponibilite_Exception` | Congés, formation (début / fin / motif). |
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

**Un artisan, plusieurs corps de métier :** **une seule ligne** par `expert_id` (identifiant unique). Renseigner tous les types dans **`types_autorises`**, codes séparés par **`;`** (ex. `EAU;GAZ;CHAUFF`). **Ne pas** dupliquer le même `expert_id` sur plusieurs lignes : cela casserait l’unicité et compliquerait file / sessions. Si un jour une **normalisation** est nécessaire, prévoir une feuille **`Expert_Types`** (`expert_id`, `type_code`) — une ligne par couple — en complément d’**une** ligne maîtresse dans `Experts`.

---

#### Onglet : `Disponibilite_Mois`

```
id_ligne	expert_id	annee_mois	mode	commentaire_interne	saisi_le	verrouille_le
```

`mode` : `indisponible` · `standard` · `astreinte` · `sur_rdv`.

---

#### Onglet : `Creneau_Astreinte`

```
id_ligne	expert_id	annee_mois	jour_semaine	date_specifique	heure_debut	heure_fin	fuseau	priorite_appel
```

---

#### Onglet : `Indisponibilite_Exception`

```
id_ligne	expert_id	debut_ts	fin_ts	motif
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
| **Identité GCP** | Projet : **`sereno-492614`**. |
| **Compte de service (recommandé Streamlit)** | Section **`[gcp_service_account]`** dans **`.streamlit/secrets.toml`** : copier les champs du fichier JSON téléchargé dans la console GCP (`type`, `project_id`, `private_key_id`, `private_key`, `client_email`, `client_id`, URIs, etc.). Pratique pour **Streamlit Community Cloud** (collage des secrets). **Ne jamais versionner** ce fichier rempli. |
| **Compte de service (option B)** | Fichier **JSON** local + clé **`service_account_json_path`** dans le TOML — **jamais** versionné (voir `.gitignore`). |
| **Vertex AI** | Même identité SA ; rôles IAM + région ; le code passe les **credentials** en mémoire (sans `GOOGLE_APPLICATION_CREDENTIALS` obligatoire quand le TOML suffit). |
| **API Gemini (clé)** | Option : **`GEMINI_API_KEY`** dans `.streamlit/secrets.toml` (repli hors Vertex). |
| **Bucket GCS** | `jopai-sereno` — droits **objets** sur le bucket pour la SA. |

### 3.6.4 Bilan infrastructure cloud (référence pilote SÉRÉNO)

Synthèse des **piliers** opérationnels côté Google Cloud / Google Workspace. **Aucun mot de passe ni clé secrète** ne figure dans ce document — uniquement des **noms** et **identifiants non secrets** (projet, bucket, email de compte de service, ID de classeur).

| Pilier | État (référence) | Usage pour SÉRÉNO |
|--------|------------------|-------------------|
| **Google Sheet partagé** | Configuré (accès SA) | **Base de données pilote** : configuration, types d’urgence, checklists SST, sessions, experts, paiements simulés, etc. (pas un catalogue « produits » e-commerce — données **métier urgence / artisans**). |
| **Bucket GCS `jopai-sereno`** | Autorisé (droits objets pour la SA) | Stockage **sécurisé** des **médias** liés aux pannes : **photos**, extraits **vidéo**, éventuels **fichiers audio** ; chemins d’objets référencés depuis l’app ou Sheets si besoin. |
| **Vertex AI (famille Gemini)** | Activé (projet `sereno-492614`) | **Intelligence** : analyse d’**images** / contexte, aide à la **guidance** client, **transcription** ou **compte rendu** (selon implémentation) — avec **quota** et **coûts** à surveiller. |
| **Compte de service** | Configuré | **Identité unique** : **`[gcp_service_account]`** dans `.streamlit/secrets.toml` (ou JSON + `service_account_json_path`) ; **non versionné** ; même email SA : `jopai-sereno-streamlit-connect@sereno-492614.iam.gserviceaccount.com`. |

**Complément — OpenAI / Gemini :** clés dans `.streamlit/secrets.toml` ou variables d’environnement ; **jamais** dans un fichier commité. Si la **clé privée** SA est dans le TOML local, traiter ce fichier comme **secret** (même niveau de protection qu’un JSON de clé).

### 3.6.5 Dépannage IAM (erreurs 403 des tests connexions)

| Symptôme | Cause fréquente | Action |
|----------|-----------------|--------|
| **GCS** `storage.buckets.get` refusé | Rôle **objets** seul (ex. admin **objets** du bucket) **sans** lecture des **métadonnées du bucket** | Le test Streamlit utilise désormais **`list_blobs`** (API **Objects**, permission `storage.objects.list`), pas `bucket.exists()`. Si 403 persiste : vérifier que la SA est bien **membre du bucket** `jopai-sereno` avec au minimum **Storage Object Viewer** ou **Storage Object Admin** (niveau **bucket** ou projet). |
| **Vertex** `aiplatform.endpoints.predict` refusé | SA sans droit d’**inférence** Vertex sur le projet / la région | Console **IAM** du projet `sereno-492614` : ajouter à la SA le rôle **Vertex AI User** (`roles/aiplatform.user`). Activer l’**API Vertex AI**. Vérifier que **`vertex_location`** (`europe-west1`, etc.) est une région où le modèle est disponible ; sinon essayer `europe-west4` ou `us-central1` dans `.streamlit/secrets.toml`. |
| **Vertex indisponible** + clé Gemini renseignée | Repli développeur | La page **Tests connexions** peut enchaîner un appel **API Gemini** via `GEMINI_API_KEY` (hors Vertex) pour valider l’IA sans attendre l’IAM Vertex. |

---

## 3.7 Sécurité & confidentialité (rappels)

- Pas de **clés API**, **JSON de compte de service** ni `secrets.toml` rempli dans Git (voir `.gitignore`).
- **Consentement** explicite pour enregistrement / transcription si activé plus tard.
- **RGPD** : minimisation des données dans Sheets ; durée de rétention définie.
- **Pilote fake** : aucune donnée de carte ne doit être interprétée comme un engagement de paiement réel ; éviter de logger des PAN complets en clair si possible (masquage).
- **Compte de service GCP :** la **clé privée** ne doit figurer que dans **`.streamlit/secrets.toml` (ignoré par Git)** ou un **JSON ignoré** — jamais dans un fichier versionné. En cas d’exposition (fuite, copie publique) : **révoquer** la clé IAM et **en régénérer** une.
- **Clés OpenAI / autres API :** même règle — si une clé a été copiée dans un fichier lisible par un tiers ou un historique de chat, la **révoquer** et en émettre une **nouvelle**.

## 3.8 Fichiers de configuration et secrets (TOML)

**Objectif :** centraliser **Sheets**, **compte de service GCP**, **Vertex / GCS**, **Gemini**, clés tierces — avec **priorité Streamlit** : `.streamlit/secrets.toml`.

| Fichier | Rôle |
|---------|------|
| `config/streamlit-secrets.EXAMPLE.toml` | **Modèle versionné** : structure type pour copier vers `.streamlit/secrets.toml`. |
| `.streamlit/secrets.toml` | **Réel, non versionné** — lu par Streamlit (`st.secrets`) et par `scripts/init_google_sheet.py` (tomllib). |
| `config/secrets.example.toml` | Variante pour outils hors Streamlit / `config/secrets.toml` local. |
| `config/secrets.toml` | **Réel, non versionné** si utilisé. |
| `.streamlit/*.json` | **Option B** : JSON SA seul ; `service_account_json_path` dans le TOML. **Non versionné**. |
| `config/keys/` | Optionnel ; **non versionné**. |

Le code (`sereno_core.gcp_credentials`) charge la SA ainsi : **1)** table **`[gcp_service_account]`** via l’objet `secrets` ; **2)** **repli** : relit **`.streamlit/secrets.toml`** avec `tomllib` (contourne les cas où `st.secrets` n’expose pas les tables imbriquées) ; **3)** fichier JSON via **`service_account_json_path`**.

### 3.8.1 Conventions `.streamlit/secrets.toml`

| Clé / bloc | Rôle |
|------------|------|
| `gsheet_id` | ID du classeur Sheets. |
| `gcs_bucket_name` | Bucket GCS. |
| `gcp_project_id` | Projet GCP (optionnel si `project_id` est dans `[gcp_service_account]`). |
| `[gcp_service_account]` | Champs du JSON GCP (dont `private_key` multiligne). |
| `service_account_json_path` | Repli : chemin relatif au dépôt vers un `.json` SA. |
| `vertex_location`, `vertex_model` | Région / modèle Vertex. |
| `OPENAI_API_KEY`, `GEMINI_API_KEY` | Clés API optionnelles. |
| `notification_priority` | Ordre des canaux de notification artisan (ex. `["sms","call","push"]`). |
| `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM_NUMBER` | Twilio : SMS + appel vocal (réveil artisan). |
| `DAILY_API_KEY` | Daily : déclenchement enregistrement (optionnel). |

**Streamlit Cloud :** déclarer les mêmes clés dans **Settings → Secrets** (format TOML), y compris la section `[gcp_service_account]`.

## 3.9 Outils Streamlit et initialisation Google Sheets

### 3.9.1 Page « Tests connexions »

- **Fichier :** `pages/1_Tests_connexions.py`.
- **But :** vérifications **manuelles** (boutons) : **Google Sheets**, **GCS** (liste d’objets), **Vertex AI** (credentials passés explicitement depuis `[gcp_service_account]` ; repli **Gemini** si clé définie). Charge **`sereno_core.gcp_credentials`**.
- **Lancement :** `streamlit run Home.py` depuis la racine du dépôt ; URL locale type `http://localhost:8501`.
- **Dépendance repli Gemini :** paquet **`google-generativeai`**. Le test appelle **`list_models`** et ne retient que les modèles exposant **`generateContent`** (évite les 404 sur d’anciens noms type `gemini-1.5-flash-8b`). `pip install -r requirements.txt` dans le **même** Python que Streamlit.

### 3.9.2 Script `scripts/init_google_sheet.py`

- **Source des colonnes et graines :** `sereno_core/sheets_schema.py` (aligné sur § 3.6.2).
- **Configuration :** lit `gsheet_id` et le compte de service via **`get_service_account_info`** (TOML `[gcp_service_account]` ou JSON).
- **Commandes :**
  - `python scripts/init_google_sheet.py` — crée les onglets manquants, écrit les **en-têtes** (ligne 1) si la ligne 1 est vide (sinon conserve).
  - `python scripts/init_google_sheet.py --seed` — ajoute les **lignes d’exemple** uniquement si l’onglet n’a **aucune donnée sous l’en-tête** (évite d’écraser un classeur déjà rempli).
  - `python scripts/init_google_sheet.py --force-headers` — **réécrit** la ligne 1 (à utiliser avec prudence si les titres ont été personnalisés).
- **Onglet `Connexions_Test` :** créé avec les mêmes en-têtes que la page de tests Streamlit (`horodatage_utc`, `source`, `statut`, `note`).

### 3.9.3 Pages « Cahier des charges » et « Carnet d’échange »

| Page | Fichier Streamlit | Source Markdown |
|------|-------------------|-----------------|
| **Cahier des charges** | `pages/2_Cahier_des_charges.py` | `CAHIER_DES_CHARGES.md` |
| **Carnet d’échange** | `pages/3_Carnet_echange.py` | `docs/CAHIER_ECHANGES.md` |

Même barre d’outils (recherche, déplier / replier) ; le CDC utilise en plus le découpage **parties + `##`** via `outline="cdc_parties"` dans `streamlit_markdown_book`.

### 3.9.4 Export PDF du cahier, experts prototype, pilotage

- **Export PDF (page Cahier des charges)** : sélection d’une ou plusieurs **parties** ; PDF **UTF-8** via **`fpdf2`** + polices **DejaVu** (`assets/fonts/`) pour les accents français ; mise en page épurée (`sereno_core/cdc_pdf_export.py`). **Couverture** : rappel produit + bloc **« comment lire le menu latéral »** (texte novices, titres et puces indentées — aligné sur `sereno_core/projet_navigation_intro.py`).
- **Navigation** : sections **Projet**, **Prototype · Client / Artisan / Propriétaire**, **Administration · Pilote** (`Home.py`) — détail § 3.3.2.
- **Disponibilités (Sheets + Streamlit)** : onglets **`Disponibilite_Mois`**, **`Creneau_Astreinte`**, **`Indisponibilite_Exception`** ; création / en-têtes via **`init_google_sheet.py`**. **Saisie** : pages **`16_Admin_artisan_disponibilites.py`** et **`17_Admin_proprietaire_disponibilites.py`** ; listes **expert** = **une ligne par spécialité** (`Nom — Libellé urgence (expert_id)`), fonction **`disponibilite_expert_options`** dans `sereno_core/sheets_experts.py`. La page **`15_Disponibilite_artisans.py`** reste utilisable en **maintenance / lecture** mais **n’est plus** au menu Projet.
- **Reporting indicateurs** : page **`19_Projet_reporting_indicateurs.py`** — canevas **3 colonnes** reprenant les indicateurs **§ 1.7** (valeurs **placeholders** jusqu’au branchement BDD / analytics).
- **Conformité réseau / API Pappers** : page **`18_Proto_Proprietaire_conformite.py`** ; interrogation entreprise par **SIREN** ; secret Streamlit **`PAPPERS_API_KEY`** ; client **`sereno_core/pappers_client.py`**. **Coût API** : chaque consultation est facturée — **cache** session en pilote ; en production, stocker la **réponse JSON complète** en base (table SQL **`papers`**, script **`scripts/sql/create_papers_cache_table.sql`**). **Suite produit** : croiser **certifications** et statut **MAIF** hors Pappers (§ 1.8).
- **Experts du parcours prototype** : chargement prioritaire de l’onglet **`Experts`** du classeur Google Sheets (`gsheet_id` + compte de service) ; fusion des lignes partageant le même `expert_id` ; colonne **`types_autorises`** ou **`types_autorisees`** (codes séparés par `;` ou `,`). Repli local minimal si Sheets indisponible (`sereno_core/sheets_experts.py`).
- **Propriétaire — activité** : **entonnoir** (jalons du parcours démo), avis avec **type d’intervention**, export JSON des événements.
- **Compte-rendu d’intervention (produit cible)** : après session, génération d’un **PDF de synthèse** (parcours, synthèse visio, pièces jointes) — **à concevoir** ; lien placeholder dans le mail de contact pilote.
- **Mise en page Streamlit** : largeur du bloc principal **~70 %** pour **toutes** les sections (`apply_global_styles`) ; logo SÉRÉNO en **haut de barre latérale** si disponible (dossier `logo/` ou GCS).

---

# Partie 4 — Avancements : de l’idée au produit en passant par le pilote

## 4.1 Phases cibles (rappel protocole)

| Phase | But | Critère de passage |
|-------|-----|---------------------|
| **P0 — Spéc** | Cahier des charges stable, risques identifiés | Validation interne JOPAI |
| **P1 — Démo technique** | Flux bouton → infos → checklist SST → salle visio (mock) + ligne Sheets | Équipe |
| **P2 — Pilote** | App mobile Expo + experts + Sheets + visio réelle + testeurs | Retours + métriques minimales |
| **P3 — Préprod** | Supabase, auth renforcée, Stripe hors test si validé | Bêta fermée |
| **P4 — Prod cible** | Durée, conformité, hébergement (ex. OVH) | Go / no-go |

## 4.2 Tableau MVP — périmètre **pilote** (réf. § 2.1)

Synthèse **inclus / hors** pour le **premier MVP terrain** (à cocher / actualiser dans le **carnet d’échange** ou ici).  
Pour le **détail ligne à ligne**, le **mini-glossaire** et les **questions / réponses** pour novices, voir **§ 2.1.1 à 2.1.3**.

| Domaine | Inclus dans le MVP pilote | Hors MVP pilote (évolution) |
|---------|---------------------------|----------------------------|
| **UX urgence** | 5 boutons (Eau, Élec, Gaz, Chauffage, Serrurerie), ergonomie senior | Catalogue étendu de métiers |
| **SST** | Checklists par type, garde-fous avant visio | IA « danger » avancée |
| **Données** | Google Sheets (vérité pilote), init scripts | Supabase temps réel |
| **Experts** | Dashboard Streamlit, file / prise de session (évolution) | Marketplace ouverte |
| **Visio** | SDK Daily ou Twilio (intégration à planifier) | Annotations riches |
| **Paiement** | **Simulation 100 %** (fake), traçabilité Sheets | Stripe live + Connect |
| **IA** | Vertex (cible) ; repli **Gemini API** pour tests | Rapport PDF Vertex complet |
| **Mobile** | App **Expo** (cible P2) | — |

## 4.3 Tableau d’avancement — jalons projet (suivi)

État indicatif **à mettre à jour** à chaque itération (date dans le carnet d’échange).

| Jalon | Description courte | Statut suggéré |
|-------|-------------------|----------------|
| **CDC & gouvernance** | `CAHIER_DES_CHARGES.md`, carnet, règle Cursor | En cours / Fait |
| **Secrets & GCP** | `[gcp_service_account]`, Sheets, GCS, IAM Vertex | En cours |
| **Streamlit outillage** | Home, tests connexions, CDC / carnet, **métriques** (`14`), **reporting CDC** (`19`), conformité Pappers (`18`) | En cours |
| **Schéma Sheets** | Onglets + `init_google_sheet.py` | Fait / à valider |
| **Logique Python** | `sereno_core` (credentials, schéma, MD book) | En cours |
| **App client** | Expo : parcours urgence → visio → paiement fake | Non démarré |
| **Visio intégrée** | Salle Daily/Twilio bout en bout | Non démarré |
| **Pilote terrain** | ≥ 5 testeurs, ≥ 3 experts, critères § 1.7 | Non démarré |

*Légende statut :* **Non démarré** · **En cours** · **Fait** · **Bloqué** (préciser la cause).

## 4.4 Environnement Python (`venv`) et `pip`

- **Rôle des paquets** (`requirements.txt`) : faire tourner **Streamlit**, **Google Sheets** (gspread), **GCS**, **Vertex AI** (SDK), et le **repli Gemini** (`google-generativeai`) pour la page Tests connexions. Sans ce fichier, les imports du projet échouent.
- **Si tout est déjà « Requirement already satisfied »** : l’environnement est **déjà correct** — **aucune action obligatoire**. Tu peux lancer `streamlit run Home.py` sans relancer `pip install`.
- **Si `pip install -r requirements.txt` reste bloqué longtemps** (messages *backtracking*, *looking at multiple versions*) : arrêter avec **Ctrl+C**. Le fichier `requirements.txt` fixe une contrainte **`google-api-core`** pour limiter ce comportement. Ensuite :  
  `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`  
  (optionnel : `--no-cache-dir` si besoin).
- **Revenir en arrière / repartir propre** :  
  1. Fermer les terminaux qui utilisent le venv.  
  2. Supprimer le dossier **`.venv`** à la racine du dépôt.  
  3. `python -m venv .venv` puis activer le venv (PowerShell : `.\.venv\Scripts\Activate.ps1`).  
  4. `python -m pip install --upgrade pip` puis `pip install -r requirements.txt`.  
  Aucun paquet n’est « obligatoire » **hors** de ce projet : supprimer `.venv` **ne casse pas** Windows ni les autres projets.
- **Retirer uniquement le repli Gemini** (si tu n’en veux pas) : possible de commenter **`google-generativeai`** dans `requirements.txt` et de désactiver le bouton de test associé dans le code — **non recommandé** tant que Vertex n’est pas pleinement opérationnel, car le repli sert de filet.

---

## Annexes — révisions

| Version | Date | Auteur | Résumé |
|---------|------|--------|--------|
| 1.7 | 2026-04-07 | JOPAI + assistant | **§ 1.7.1** interface pilote dispos (Admin · Pilote, sélection **nom — spécialité (id)**, fenêtre sensible, page 15 hors menu Projet) ; **§ 3.3.2** tableau des sections menu ; **§ 3.9.4** reporting `19`, Pappers / table **`papers`**, PDF accueil novices ; indicateur abandon sans « simulé » § 1.7. |
| 1.6 | 2026-04-07 | JOPAI + assistant | Fonds urgence ; Experts Sheets multi-onglets ; PDF couverture + QR ; § 1.8 MAIF / certifications ; icônes GCS `icones/`. |
| 1.5 | 2026-04-07 | JOPAI + assistant | Menu **Prototype · Client / Artisan / Propriétaire** ; PDF **DejaVu** (accents) ; recherche CDC + effacer ; onglets **Disponibilite_Mois**, **Creneau_Astreinte**, **Indisponibilite_Exception** + page **Disponibilités artisans** ; QR démo accueil ; retrait bandeau secrets accueil & métriques. |
| 1.4 | 2026-04-07 | JOPAI + assistant | **§ 3.9.4** export PDF CDC (`fpdf2`) ; experts prototype depuis Sheets ; entonnoir + avis avec type d’intervention ; e-mail contact enrichi (session, CR futur) ; logo sidebar ; **70 %** largeur globale ; accueil Projet pédagogique + simulateur mobile ; renommage étape « mise en relation & visio » ; règles Cursor (pédagogie §1–2 vs technique §3). |
| 1.3 | 2026-04-07 | JOPAI + assistant | **§ 1.7** indicateurs étendus + **§ 1.7.1** disponibilité artisans (BDD) ; suppression de l’ancien § gouvernance CDC dans la partie fonctionnelle ; **JOPAI** explicite § 1.3 ; P1 pédagogique plombier ; **§ 3.1.1** câblage visio minimal + URL Streamlit Cloud ; entrée menu métriques projet ; en-têtes replis CDC (fond bleu) dans Streamlit. |
| 1.2 | 2026-04-07 | JOPAI + assistant | § **2.1** tableau MVP explicite + glossaire + Q/R novice ; § **2.6** « cas concrets d’usage » (équivalent *user stories*) ; ton **métier** parties 1–2 ; encadré **Partie 3** = technique. |
| 1.1 | 2026-04-07 | JOPAI + assistant | **Partie 4** — avancements, tableau MVP, jalons, § 4.4 pip/venv ; contrainte `google-api-core` dans `requirements.txt`. |
| 1.0 | 2026-04-07 | JOPAI + assistant | Page **Cahier des charges** (`CAHIER_DES_CHARGES.md`) ; **Carnet d’échange** (`docs/CAHIER_ECHANGES.md`) ; Gemini repli via `list_models` + generateContent. |
| 0.9 | 2026-04-07 | JOPAI + assistant | Page Cahier d’échanges (recherche, replis) ; `docs/CAHIER_ECHANGES.md`. Repli `tomllib` sur `.streamlit/secrets.toml` si `st.secrets` masque `[gcp_service_account]`. |
| 0.8 | 2026-04-07 | JOPAI + assistant | SA dans `[gcp_service_account]` ; `sereno_core/gcp_credentials.py` ; exemple `config/streamlit-secrets.EXAMPLE.toml` ; init + tests sans JSON obligatoire. |
| 0.7 | 2026-04-07 | JOPAI + assistant | § 3.6 Experts : une ligne / expert, `types_autorises` multi ; note pip `google-generativeai` pour repli Gemini. |
| 0.6 | 2026-04-07 | JOPAI + assistant | § 3.6.5 dépannage IAM GCS/Vertex ; test GCS sans `buckets.get` ; Vertex + repli `GEMINI_API_KEY` ; `google-generativeai`. |
| 0.5 | 2026-04-07 | JOPAI + assistant | § 3.3 couches Python + double UX ; § 3.9 Tests connexions + `init_google_sheet.py` ; `sereno_core` ; navigation Streamlit ; règle `.cursor/rules/sereno-maintain-cdc.mdc`. |
| 0.4 | 2026-04-07 | JOPAI + assistant | § 3.6.4 bilan infra cloud ; conventions secrets Streamlit ; règles anti-fuite clés SA / OpenAI. |
| 0.3 | 2026-04-07 | JOPAI + assistant | Paiement pilote 100 % fake (§ 2.9) ; ID Sheets + SA + GCS ; `config/secrets.example.toml` ; Vertex vs Gemini ; onglet Paiements `mode_paiement`. |
| 0.2 | 2026-04-07 | JOPAI + assistant | 3 parties ; Sheets détaillé ; 5 boutons dont Serrurerie ; pilote mobile Expo. |
| 0.1 | (v0 source) | JOPAI | Document Word initial. |

---

*Fin du cahier des charges — SÉRÉNO.*
