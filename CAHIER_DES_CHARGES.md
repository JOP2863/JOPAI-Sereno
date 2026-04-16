# Cahier des charges — SÉRÉNO (JOPAI BTP)

**Document :** spécification produit et technique — prototype / pilote.  
**Version :** 1.35 (thème Streamlit : **zoom** boutons + liste admin **Bio** ; libellés **Config** / priorité d’appel ; carnet d’échange à jour).  
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

**JOPAI** est une **marque** spécialisée dans l’**intelligence artificielle** et les **services numériques** ; elle s’adresse en particulier aux **métiers de l’artisanat** et du **BTP** (accompagnement, outils, prototypes produits comme **JOP***AI*© **SÉRÉNO**).

### 1.3.1 Nom du produit affiché (**JOPAI© SÉRÉNO**)

Pour l’**affichage** (interfaces, supports grand public), on aligne la **marque maison** sur **JOPAI-BTP** : **JOP** en gras, *AI* en italique, © en exposant — le tout en **turquoise** **#0d9488** ; le nom du service **SÉRÉNO** suit en **majuscules accentuées**, en **bleu pétrole** **#0b2745** (équivalent visuel du « BTP » après JOPAI© sur le site JOPAI-BTP). Les **titres de page** Streamlit reprennent en **suffixe** la formule **by JOPAI© SÉRÉNO** (helpers dans **`sereno_core/jopai_brand_html.py`**). En **code** (fichiers, variables, préfixes `sereno_`), les formes techniques historiques peuvent rester si elles ne sont pas visibles par l’utilisateur final.

**Parcours « app » :** dans ce dépôt, le client utilise **les mêmes** pages Streamlit sur téléphone ou ordinateur ; il n’existe **pas** de jeu de pages « application » distinct ni de routage selon l’appareil — l’app **Expo** cible est **hors** ce dépôt (voir § 1.5 et règle **dual UX**).

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
| **Satisfaction** (**NPS** 0 à 10, avec commentaire libre optionnel) | Après session | Qualité du service |
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
- **Assistant semaine + graphique mensuel (pilote) :** module `sereno_core/disponibilite_calendar_ui.py` — sur **Dispo. artisan** et **Dispo. réseau (proprio)**, un replis permet de cocher des **créneaux indisponibles** (matin / après-midi / soir) sur la semaine en cours et d’**injecter** un texte récapitulatif dans le **commentaire interne** ; la **vue réseau** affiche aussi un **graphique** (volume par mois et par mode) avant le tableau brut, pour une lecture **temporelle** plus simple qu’une grille seule.
- **Assistant mois (V2, type calendrier) :** second replis avec **navigation mois par mois** (◀ ▶) et une **grille** : jour **décoché** = **indisponible** toute la journée ; génération d’un **texte récap** pour le même commentaire interne (granularité toujours **texte** côté Sheets dans le pilote).

**Indicateurs dérivés :** couverture 24/7, taux de « mois complets » renseignés par expert, respect du verrouillage J−30.

**Règle projet (Cursor) :** le dépôt inclut une règle **always-on** (`.cursor/rules/sereno-maintain-cdc.mdc`) : à chaque **évolution structurante**, **mettre à jour** `CAHIER_DES_CHARGES.md` et la **table des révisions** — **sans** y copier de secrets.

## 1.8 Certifications, assurance et cadre MAIF (référentiel externe)

Le document Word **« certifications et MAIF »** (version équipe JOPAI, hors dépôt Git) complète ce cahier pour :

- les **exigences assurance** et de responsabilité (intervenants, plateforme, télé-expertise) ;
- les **certifications** ou référentiels qualité pertinents pour le BTP et les services numériques associés ;
- les **exigences de contenu** (dont **prompts** validés pour icônes urgence, schémas pédagogiques et supports grand public) alignés sur le discours **MAIF** et les partenaires concernés.

**Règle projet :** toute évolution touchant l’assurance, les labels ou les engagements vis-à-vis des usagers doit **croiser** trois sources : ce cahier, le document Word susnommé et le carnet d’échange (`docs/CAHIER_ECHANGES.md`). Les polices **DejaVu** utilisées pour l’export PDF du CDC sont des fichiers **TTF** techniques (lisibilité UTF-8) : elles ne remplacent pas les exigences rédactionnelles ou graphiques du référentiel MAIF.

### 1.8.1 Réseau sinistres et mutuelles (ex. **MAIF**) — information grand public

*Cette sous-section résume une **démarche type** pour un artisan qui souhaite **travailler sur des dossiers de sinistres** (incendie, dégât des eaux, bris de glace, etc.) pour le compte d’une **mutuelle** ou d’un **assureur**. Elle ne remplace **ni** une convention **ni** les règles du mandataire ; elle sert de **repère pédagogique** dans le cahier des charges.*

**Pourquoi c’est intéressant pour un artisan :** être **partenaire** d’une mutuelle peut **stabiliser le carnet** en recevant des missions sur des sinistres déjà ouverts par l’assureur.

**Comment ça marche en pratique (souvent) :** la **MAIF**, comme beaucoup d’assureurs, ne gère **pas** toujours son réseau d’artisans **en direct**. Elle **délègue** la gestion à des **plateformes spécialisées** dans le suivi des sinistres, par exemple **IMAX** (groupe **Saretec**, parfois associé au réseau **IRD**) ou le réseau **Sygma**. D’autres volumes (petits dépannages) peuvent parfois transiter par des **tiers** du type **Multiassistance** ou **HomeServe**, selon les accords du moment.

**Étapes indicatives pour une candidature :**

1. **Identifier la bonne porte d’entrée** : se renseigner sur le **mandataire** qui recrute les prestataires pour le type d’intervention visé (site du mandataire, rubrique du type **« Devenir partenaire »** ou **prestataire**).
2. **Préparer un dossier « sans faille »** (exigences fréquentes) :
   - **Qualifications** : labels du bâtiment souvent demandés (**RGE** = *Reconnu garant de l’environnement*, **Qualibat**, diplômes du métier) ;
   - **Assurances** : **décennale** et **responsabilité civile professionnelle** (**RC Pro**) à jour ;
   - **Santé de l’entreprise** : **K-bis** récent (souvent **moins de trois mois**), structure pérenne ;
   - **Numérique** : capacité à **échanger des dossiers en ligne** (photos avant / après, devis dématérialisés, facturation électronique).
3. **Processus habituel** : **candidature en ligne** → si la zone géographique ou le métier **manque de prestataires**, **audit** (tarifs, capacité d’intervention) → **signature d’une convention** avec souvent une **grille tarifaire négociée** (parfois inférieure aux tarifs « particuliers », compensée par le **volume**) et des **délais d’intervention** stricts (ex. premier contact sous **24 h / 48 h**).
4. **Critères de réussite côté assureur / mandataire** : **réactivité** (réponse rapide au client ou au gestionnaire) ; **qualité du compte rendu** (photos, clarté) ; **précision du rayon d’intervention** (les assureurs comblent souvent des « trous » en zone rurale ou très dense).

**Lien avec SÉRÉNO :** le produit vise la **télé-expertise** et la **mise en relation** ; l’intégration à un **réseau sinistre** mandaté reste un **sujet métier et contractuel** distinct, à traiter avec les **plateformes** et la **conformité** (voir aussi la conformité entreprise **§ 3.8** et le document Word « certifications et MAIF »).

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

**Pilote Streamlit (réseau / propriétaire) :** une page **Paramétrage parcours client** (section **Projet**) permet de choisir un parcours **standard** (toutes les étapes ci-dessus comme aujourd’hui), **simplifié** (sans l’étape sécurité **SST**, sans **paiement** simulé, sans questionnaire **NPS** — acronyme anglais *Net Promoter Score*, la note de recommandation 0 à 10), ou **personnalisé** (activer ou non chacune de ces trois étapes). Les choix sont **écrits automatiquement** dans l’onglet **Config** du classeur Google (clés dont le préfixe est ``SERENO_JOURNEY_``) : **tous les visiteurs** de l’application voient le même parcours ; le menu latéral **ne propose plus** les entrées des étapes désactivées. Si le classeur n’est pas joignable, un **repli** garde les derniers réglages **dans la session** du navigateur.

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

## 2.10 Profils d’accès et promesse « compagnon » (cible produit — préparation pilote)

SÉRÉNO prévoit plusieurs **niveaux d’accès** pour séparer ce que voit ou modifie chaque acteur. En phase **pilote Streamlit**, l’authentification forte n’est pas encore branchée partout : les rôles ci-dessous servent de **référence produit** et sont **préfigurés** dans l’onglet Sheets **`Utilisateurs_Acces`** (voir § 3.6.1 et § 3.6.6).

| Profil | Qui | Ce qu’il peut faire (vision cible) |
|--------|-----|-------------------------------------|
| **Grand public (client)** | Particulier en urgence | **Accès sans compte** au parcours urgence (choix du type, informations, SST, mise en relation, visio, avis). Option **créer un compte** pour retrouver un historique léger, préférences ou suivi — **à activer** lors du branchement **auth** (Supabase / autre). |
| **Client inscrit** | Même usager, avec compte | Mêmes parcours + services liés au compte (historique, préférences), selon politique produit. |
| **Artisan** | Expert du réseau | **Tableau de bord** : activité, sessions, avis ; **prise d’appel** / réception des sollicitations ; **mise à jour des disponibilités** (créneaux, modes). Pas d’accès aux fonctions « réseau entier » réservées propriétaire / compagnon. |
| **Propriétaire du réseau** | Direction / opérateur plateforme | **Vision transversale** : pilotage, reporting, disponibilités réseau, conformité (ex. SIREN / Pappers), paramètres sensibles. |
| **Compagnon** | Référent dédié à la **qualité du réseau** | Rôle de **garant** : **sélectionner**, **documenter** et **suivre** les artisans **référencés** (entrée dans le vivier, critères métiers, retraits ou suspensions). Ne remplace pas le juridique ni l’assurance ; il **cadre** le référentiel humain de confiance. |

**Argumentaire commercial / crédibilité :** SÉRÉNO met en avant un **dispositif compagnon** : la plateforme ne se contente pas d’afficher des profils, elle s’appuie sur des **référents qui accompagnent la sélection** des professionnels. C’est une réponse explicite au risque « annuaire fourre-tout » : **rigueur** et **responsabilité** dans le choix des intervenants.

**Valeurs de rôle** (convention technique pilote, colonne **`role`** de **`Utilisateurs_Acces`**) :  
`CLIENT_PUBLIC`, `CLIENT_COMPTE`, `ARTISAN`, `PROPRIETAIRE`, `COMPAGNON` (libellés exacts évolutifs — seuls les **principes** sont contractuels ici).

**Même e-mail, plusieurs casquettes :** la personne qui gère le réseau peut aussi être **compagnon** sur un périmètre (ex. serrurerie). En pilote, la colonne **`code_pilote`** (mot de passe simple, voir § 3.3.2) permet de choisir **quelle ligne** du tableau s’applique après saisie de l’e-mail.

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
- **Implémentation pilote (Streamlit)** : Twilio pour **SMS** + **appel** (réveil vocal). Le texte reprend le **motif d’urgence**, le **prénom ou pseudo** saisi par le client (étape informations), une **phrase rassurante** et le **lien de la salle** ([Jitsi Meet](https://meet.jit.si/) généré dans le parcours ou URL Daily / Twilio si renseignée dans les secrets). Le push est un stub (cible Expo).

**Enregistrement visio (optionnel) :**

- Si une salle **Daily** est utilisée et qu’une clé **`DAILY_API_KEY`** est fournie, le pilote peut déclencher le **start/stop recording** via l’API Daily.
- **Twilio Video** : l’**enregistrement** des compositions (en général via **Enregistrements** / **Compositions** côté API Twilio) fournit des **fichiers média** ; ce n’est **pas** une **transcription texte** prête à l’emploi. Pour obtenir du **texte** (pour recherche, compte rendu, IA), il faut enchaîner avec un **moteur de reconnaissance vocale** (voir ci-dessous).
- La cible produit consiste à **stocker** l’enregistrement (ou ses sorties) dans le bucket GCS `jopai-sereno` et à référencer le chemin objet depuis `Sessions`.

**Transcription et post-traitement IA (hors « bouton magique » Twilio) :**

- **Twilio** (SMS / appel / Video) **ne fournit pas** une transcription **gratuite et intégrée** de toute visio comme une fonction unique ; les **coûts** dépendent des **produits** activés (**minutes Video**, **stockage** d’enregistrements, **Media Streams** pour envoyer l’audio en flux vers un autre service, etc.) — consulter la **grille tarifaire officielle** Twilio et le compte Twilio pour une estimation à jour.
- **Piste architecture** : (1) enregistrer la session (**Daily** ou **Twilio**) → (2) récupérer le fichier ou un flux audio → (3) **Speech-to-Text** (**Google Cloud Speech-to-Text**, ou **Vertex AI** / modèles **Gemini** sur fichier audio selon l’offre retenue) → (4) **post-traitement** (résumé, extraction de points clés) via **Vertex** ou API **Gemini**, avec **consentement** utilisateur et **durée de conservation** définis (cf. § conformité).
- **Media Streams (Twilio)** : permet d’**exposer l’audio** en temps réel vers un **WebSocket** applicatif ; la **transcription** et la **facturation** associées relèvent alors du **service** qui consomme ce flux (et des **minutes** / options Twilio activées), pas d’une « transcription Twilio » monolithique.

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

**Règle Cursor (double UX Web / mobile) :** le fichier `.cursor/rules/sereno-dual-ux-web-mobile.mdc` rappelle qu’une évolution doit **mettre à jour la logique dans `sereno_core` en premier**, puis les écrans **Streamlit** et, plus tard, l’**app Expo**, de façon **concomitante** (même règles métier, pas de copier-coller divergent).

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
| `sereno_core/` | Paquet Python : `sheets_schema`, **`gcp_credentials`**, **`gspread_helpers`** (quota **429** / liste d’onglets), **`sheets_experts`**, **`pilot_auth`** (session + lecture **Utilisateurs_Acces**), **`proto_state`** (dont **`journey_*`** : préréglages parcours client pilote), **`md_chapters`**, **`streamlit_markdown_book`**, **`cdc_pdf_export`**, **`projet_navigation_intro`**, **`reporting_cdc_indicators`**, **`pappers_client`**, etc. |
| `scripts/init_google_sheet.py` | Crée les onglets manquants, écrit la **ligne 1** (en-têtes) et optionnellement les **lignes de graine** (voir § 3.9). |
| `scripts/migrate_google_sheet_schema.py` | **Migration additive** du classeur : ajoute colonnes manquantes + onglet **`Utilisateurs_Acces`** selon `sheets_schema` (sans supprimer de colonnes). |
| `scripts/sql/create_papers_cache_table.sql` | Script PostgreSQL — table **`papers`** (cache JSON API Pappers). |
| `Home.py` | Entrée Streamlit. |
| `pages/` | Tests, CDC, carnet, métriques (`14`), reporting (`19`), paramétrage parcours client (`20`), proto client / artisan / propriétaire (`4`–`13`, `18`), admin dispos (`16`–`17`), etc. |
| `docs/CAHIER_ECHANGES.md` | **Carnet d’échange** (fil décisions / discussions) — page Streamlit homonyme. |

### 3.3.2 Interface Streamlit — navigation

L’accès aux pages du dossier `pages/` exige **`showSidebarNavigation = true`** dans `.streamlit/config.toml`. Sinon, seule la page d’accueil est visible et le texte « utilisez la barre latérale » prête à confusion. L’icône **≡** en haut à gauche permet d’**ouvrir** le menu si la barre est repliée.

**Regroupements du menu (`Home.py`) :**

| Section | Contenu principal (fichiers `pages/`) |
|---------|--------------------------------------|
| **Projet** | Accueil, **Métriques** (lignes CDC / code), **Reporting** (canevas indicateurs § 1.7), Cahier des charges, Carnet d’échange, Tests connexions, **Paramétrage parcours client** (`20`). |
| **Prototype · Client** | Guide parcours, flux urgence → … → satisfaction (pages **SST** / **Paiement** / **NPS** masquées si inactives selon **Config**). |
| **Prototype · Artisan** | Tableau de bord expert. |
| **Prototype · Propriétaire** | Activité réseau, **Conformité (SIREN / Pappers)**. |
| **Administration · Pilote** | **Dispo. artisan**, **Dispo. réseau (proprio)** — saisie `Disponibilite_Mois` (§ 1.7.1). |

**Connexion pilote (`pilot_auth`, `Home.py`) :** par défaut, seule la section **Prototype · Client** est visible (**accès public**). Le bouton **Se connecter** figure dans la **barre latérale** (sous le logo) : **e-mail** + champ **code pilote** (mot de passe simple **`code_pilote`** dans **`Utilisateurs_Acces`**). Si **une seule** ligne existe pour l’e-mail et que **`code_pilote`** est vide dans la feuille, le code n’est pas exigé ; si **`code_pilote`** est renseigné, il faut le saisir. Si **plusieurs** lignes partagent le même e-mail, le **code pilote** est **obligatoire** et doit correspondre **exactement** à la colonne **`code_pilote`** de la ligne voulue (ex. **propriétaire** vs **compagnon serrurerie**). Ce n’est **pas** une authentification forte : mot de passe **en clair** dans Sheets pour le pilote uniquement. **ARTISAN** : menu restreint (dashboard + dispo artisan). **Rôles « équipe »** (propriétaire, compagnon, client inscrit côté compte…) : menu complet Streamlit aligné **§ 2.10**.

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
| `Utilisateurs_Acces` | Profils **pilote** liés à § 2.10 : e-mail, **role**, **`code_pilote`** (choix du profil si un même e-mail sur plusieurs lignes), téléphone, rattachement artisan optionnel (`expert_id_lie`), audit (`enregistre_le`, `maj_le`). |
| `Connexions_Test` | Journaux des tests d’intégration (voir page **Tests connexions**). |

### 3.6.2 Horodatage et dates d’effet (toutes les tables pilote)

Pour **tracer** les enregistrements et **versionner** les référentiels sans tout ressaisir :

- **Données de référence** (`Config`, `Types_Urgence`, `Checklist_SST`, `Regles_Moteur`) : colonnes **`cree_le`**, **`effet_debut`**, **`effet_fin`** (ISO **yyyy-mm-dd** ou **yyyy-mm-ddThh:mm:ssZ** ; **`effet_fin`** vide = ligne toujours valable si `actif` ou équivalent le permet).
- **Données opérationnelles** (`Sessions`, `Experts`, `Disponibilite_Mois`, `Creneau_Astreinte`, `Indisponibilite_Exception`, `Paiements`, `Connexions_Test`) : **`enregistre_le`** (première écriture de la ligne), **`maj_le`** (dernière mise à jour). L’onglet **Sessions** conserve **`created_at`** (métier parcours) en complément ; le code pilote remplit **`maj_le`** à chaque upsert lorsque la colonne existe.

**Mise à jour d’un classeur déjà rempli :** exécuter le script décrit en **§ 3.6.7**. Les nouvelles cellules sont **vides** : alimenter **`effet_*`** ou **`enregistre_le`** selon votre gouvernance (manuellement ou via scripts métier). Les blocs « copier-coller » du **§ 3.6.3** peuvent être **complétés** avec ces colonnes — **source de vérité** du détail des en-têtes : fichier **`sereno_core/sheets_schema.py`**.

### 3.6.3 Prêt à copier-coller — ligne d’en-tête par onglet

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
MESSAGE_FILE	Merci de patienter, notre expert vous rejoint.	Réassurance file d attente
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

**Prototype Streamlit (pilote) :** l’écran d’accueil **« En quoi pouvons-nous vous aider ? »** affiche uniquement les lignes avec **`actif` = oui** (OUI / TRUE / 1…), dans l’**ordre** indiqué, et utilise **`libelle_affichage`** pour le texte du bouton. Si la feuille est vide ou illisible, l’appli retombe sur les **5 codes** intégrés au code (`EAU` … `SERR`). Le secret optionnel **`types_urgence_worksheet_name`** permet de cibler un autre nom d’onglet.

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

**Photo (pilote Streamlit) :** l’application charge l’image depuis **Google Cloud Storage** au chemin **`{prefix}/{expert_id}.jpg`** (compte de service), en essayant aussi **`.JPG` / `.jpeg`** si besoin. Dans la feuille, la colonne **`photo`** peut contenir ce **chemin objet** (ex. `artisan/EXP-001.jpg`), rester **vide**, ou une **URL absolue** en **https://** (ex. lien **storage.googleapis.com** vers l’objet) : cette dernière forme est notamment utilisée pour les **vignettes** de la page **Administration · Artisans (liste)** sans relire GCS côté serveur ; **éviter** les URLs console **storage.cloud.google.com** (souvent inutilisables dans une balise image navigateur).

**Texte court côté client (`essentiel_bio`) :** phrase optionnelle (quelques mots) saisie en fiche **Administration · Artisans** ; affichée sous le nom du prestataire sur l’écran **choix de l’artisan** (file / visio), avec la **priorité d’appel** en dessous (masquable en **libellés minimalistes** via la clé **`file_expert_priority_line`** dans **Config** / paramétrage). La **liste compacte** artisans (**page 22**) affiche aussi une colonne **Bio**. Les classeurs existants peuvent ajouter la colonne **`essentiel_bio`** manuellement ou via **`migrate_google_sheet_schema.py`** / ré-init ciblée.

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

### 3.6.4 Référentiel Google (classeur, compte de service, Vertex, GCS)

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

### 3.6.5 Bilan infrastructure cloud (référence pilote SÉRÉNO)

Synthèse des **piliers** opérationnels côté Google Cloud / Google Workspace. **Aucun mot de passe ni clé secrète** ne figure dans ce document — uniquement des **noms** et **identifiants non secrets** (projet, bucket, email de compte de service, ID de classeur).

| Pilier | État (référence) | Usage pour SÉRÉNO |
|--------|------------------|-------------------|
| **Google Sheet partagé** | Configuré (accès SA) | **Base de données pilote** : configuration, types d’urgence, checklists SST, sessions, experts, paiements simulés, etc. (pas un catalogue « produits » e-commerce — données **métier urgence / artisans**). |
| **Bucket GCS `jopai-sereno`** | Autorisé (droits objets pour la SA) | Stockage **sécurisé** des **médias** liés aux pannes : **photos**, extraits **vidéo**, éventuels **fichiers audio** ; chemins d’objets référencés depuis l’app ou Sheets si besoin. |
| **Vertex AI (famille Gemini)** | Activé (projet `sereno-492614`) | **Intelligence** : analyse d’**images** / contexte, aide à la **guidance** client, **transcription** ou **compte rendu** (selon implémentation) — avec **quota** et **coûts** à surveiller. |
| **Compte de service** | Configuré | **Identité unique** : **`[gcp_service_account]`** dans `.streamlit/secrets.toml` (ou JSON + `service_account_json_path`) ; **non versionné** ; même email SA : `jopai-sereno-streamlit-connect@sereno-492614.iam.gserviceaccount.com`. |

**Complément — OpenAI / Gemini :** clés dans `.streamlit/secrets.toml` ou variables d’environnement ; **jamais** dans un fichier commité. Si la **clé privée** SA est dans le TOML local, traiter ce fichier comme **secret** (même niveau de protection qu’un JSON de clé).

### 3.6.6 Dépannage IAM (erreurs 403 des tests connexions)

| Symptôme | Cause fréquente | Action |
|----------|-----------------|--------|
| **GCS** `storage.buckets.get` refusé | Rôle **objets** seul (ex. admin **objets** du bucket) **sans** lecture des **métadonnées du bucket** | Le test Streamlit utilise désormais **`list_blobs`** (API **Objects**, permission `storage.objects.list`), pas `bucket.exists()`. Si 403 persiste : vérifier que la SA est bien **membre du bucket** `jopai-sereno` avec au minimum **Storage Object Viewer** ou **Storage Object Admin** (niveau **bucket** ou projet). |
| **Vertex** `aiplatform.endpoints.predict` refusé | SA sans droit d’**inférence** Vertex sur le projet / la région | Console **IAM** du projet `sereno-492614` : ajouter à la SA le rôle **Vertex AI User** (`roles/aiplatform.user`). Activer l’**API Vertex AI**. Vérifier que **`vertex_location`** (`europe-west1`, etc.) est une région où le modèle est disponible ; sinon essayer `europe-west4` ou `us-central1` dans `.streamlit/secrets.toml`. |
| **Vertex** « Publisher Model … was not found » (**404**) | **Nom de modèle** non reconnu dans la **région** (souvent un identifiant **sans numéro de version**) | Utiliser un **`vertex_model`** **versionné** listé pour ta région (ex. `gemini-1.5-flash-002`, `gemini-2.0-flash-001`) — voir la documentation Google sur les **versions de modèles** Vertex ; ajuster **`vertex_location`** si le modèle n’y est pas publié. |
| **Vertex indisponible** + clé Gemini renseignée | Repli développeur | La page **Tests connexions** peut enchaîner un appel **API Gemini** via `GEMINI_API_KEY` (hors Vertex) pour valider l’IA sans attendre l’IAM Vertex. |

### 3.6.7 Script de migration du classeur (`migrate_google_sheet_schema.py`)

But : **aligner** un Google Sheet **existant** sur `sereno_core/sheets_schema.py` **sans supprimer** de colonnes ni de lignes.

- **Comportement :** pour chaque onglet défini dans le schéma, le script lit la ligne d’en-tête ; il **ajoute en fin** les intitulés de colonnes **manquants** (dans l’ordre du schéma), puis **complète** chaque ligne de données avec des cellules vides pour ces nouvelles colonnes. Si l’onglet **n’existait pas**, il est **créé** (comme avec `init_google_sheet.py`). Il ne modifie **pas** l’ordre des colonnes déjà présentes.
- **Exécution (depuis la racine du dépôt, avec `.streamlit/secrets.toml` valide) :**
  - `python scripts/migrate_google_sheet_schema.py --dry-run` — affiche les ajouts prévus **sans écrire** ;
  - `python scripts/migrate_google_sheet_schema.py --apply` — **écrit** dans le classeur `gsheet_id`.
- **Quand l’utiliser :** après mise à jour du schéma (ex. horodatage, **`Utilisateurs_Acces`**). Pour un **nouveau** classeur vide, `scripts/init_google_sheet.py` reste suffisant ; pour un classeur **déjà en production pilote**, préférer **`migrate`** puis contrôle visuel de la ligne 1.
- **Contrôles après migration :** relancer **une fois** `--dry-run` (rapport vide attendu) ; ouvrir l’onglet concerné et vérifier les **en-têtes** + une ligne de test ; lancer Streamlit et passer par un parcours qui **lit/écrit** l’onglet (ex. menu pilote / `Utilisateurs_Acces`).
- **Graines :** ce script **n’insère pas** les lignes d’exemple (`seed_rows`) : seul `init_google_sheet.py --seed` le fait pour les onglets encore « presque vides ».

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
| `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM_NUMBER` **ou** table **`[twilio]`** (`account_sid`, `auth_token`, `from_number`, etc.) | Twilio : SMS + appel vocal (réveil artisan). **`TWILIO_FROM_NUMBER`** / **`from_number`** : le numéro **expéditeur attribué par Twilio**, en **E.164** (ex. **+33…** en France, **+1…** si Twilio a provisionné un numéro US — les deux sont valides). **À ne pas** enfermer sous **`[gcp_service_account]`** sans nouveau titre de section : le code **compense** cette erreur TOML courante en relisant aussi ces trois clés dans la table SA. **Numéros des artisans / destinataires (Sheets) :** préférer **+33…** ou **06…** ; éviter la double préfixation **+33336…** (erreur API **21211**). **Erreur 30044** (SMS « Failed ») : **permissions géographiques** (expéditeur **+1** → **+33** : activer la **France** dans **Messaging → Geo permissions**) **ou**, en compte **Trial**, message **trop long** (multi-segments) — le pilote envoie un SMS **compact** ; voir [Twilio 30044](https://www.twilio.com/docs/errors/30044). **Compte d’essai Twilio :** souvent seuls des **numéros vérifiés** reçoivent appels / SMS (erreur **21219** sur les appels) — à régler dans la console Twilio ou passer en compte payant. |
| `DAILY_API_KEY` | Daily : déclenchement enregistrement (optionnel). |

**Streamlit Cloud :** déclarer les mêmes clés dans **Settings → Secrets** (format TOML), y compris la section `[gcp_service_account]`.

## 3.9 Outils Streamlit et initialisation Google Sheets

### 3.9.1 Page « Tests connexions »

- **Fichier :** `pages/1_Tests_connexions.py`.
- **But :** vérifications **manuelles** (boutons) : **Google Sheets**, **GCS** (liste d’objets), **Vertex AI** (credentials passés explicitement depuis `[gcp_service_account]` ; repli **Gemini** si clé définie). Charge **`sereno_core.gcp_credentials`**.
- **Synthèse média (Vertex) :** boutons **vidéo / audio** sur objets **gs://** d’exemple (`gcs_sample_video_object`, `gcs_sample_audio_object`, défauts `video/samplevideo1.mp4` et `audio/sampleaudio1.mp3`) et **upload** d’un court **mp4** → GCS `vertex_uploads/…` puis **`sereno_core/vertex_media_summary.py`** (`summarize_gcs_media_with_vertex`).
- **Lancement :** `streamlit run Home.py` depuis la racine du dépôt ; URL locale type `http://localhost:8501`.
- **Dépendance repli Gemini :** paquet **`google-generativeai`** (optionnel). Sur **Streamlit Cloud**, il n’est **pas** dans `requirements.txt` (évite un *backtracking* pip très long avec Vertex qui peut faire échouer l’installation). **En local**, pour le repli clé **`GEMINI_API_KEY`** : `pip install -r requirements-gemini.txt` dans le **même** Python que Streamlit. Le test appelle **`list_models`** et ne retient que les modèles exposant **`generateContent`**.

### 3.9.2 Script `scripts/init_google_sheet.py`

- **Source des colonnes et graines :** `sereno_core/sheets_schema.py` (aligné sur § 3.6).
- **Configuration :** lit `gsheet_id` et le compte de service via **`get_service_account_info`** (TOML `[gcp_service_account]` ou JSON).
- **Commandes :**
  - `python scripts/init_google_sheet.py` — crée les onglets manquants, écrit les **en-têtes** (ligne 1) si la ligne 1 est vide (sinon conserve).
  - `python scripts/init_google_sheet.py --seed` — ajoute les **lignes d’exemple** si **aucune cellule non vide** sous l’en-tête (des **lignes vides** seules ne bloquent pas l’insertion ; évite d’écraser des données réelles). Les valeurs sont **reclassées** selon les **intitulés** de la ligne 1 (cas où une colonne **`telephone`** a été ajoutée **en fin d’onglet** par migration). Les colonnes **`enregistre_le`** / **`maj_le`** vides dans la graine reçoivent l’**horodatage UTC** au moment du script.
  - `python scripts/init_google_sheet.py --force-headers` — **réécrit** la ligne 1 (à utiliser avec prudence si les titres ont été personnalisés).
- **Quota API (429) :** `init_google_sheet` et `migrate_google_sheet_schema` listent les onglets **une fois** (`sereno_core/gspread_helpers.py`), espacent les appels et **relancent** après pause en cas de « Quota exceeded » — en définitive, attendre **1–2 min** puis **relancer** la commande si besoin.
- **Classeur déjà rempli :** pour **ajouter** des colonnes sans effacer les données, utiliser **`scripts/migrate_google_sheet_schema.py`** (**§ 3.6.7**), pas `--force-headers`.
- **Onglet `Connexions_Test` :** créé avec les mêmes en-têtes que la page de tests Streamlit (y compris colonnes d’audit si migré).

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
- **Reporting indicateurs** : page **`19_Projet_reporting_indicateurs.py`** + module **`sereno_core/reporting_cdc_indicators.py`** — grille **3 colonnes** (indicateurs **§ 1.7**) avec **composants Streamlit variés** : `st.metric`, `st.progress` (simple et par ligne), `st.line_chart`, `st.area_chart`, `st.scatter_chart` (données d’exemple jusqu’au branchement BDD / analytics).
- **Conformité réseau / API Pappers** : page **`18_Proto_Proprietaire_conformite.py`** ; interrogation entreprise par **SIREN** ; secret Streamlit **`PAPPERS_API_KEY`** ; client **`sereno_core/pappers_client.py`**. **Coût API** : chaque consultation est facturée — **cache** session en pilote ; en production, stocker la **réponse JSON complète** en base (table SQL **`papers`**, script **`scripts/sql/create_papers_cache_table.sql`**). **Suite produit** : croiser **certifications** et statut **MAIF** hors Pappers (§ 1.8).
- **Experts du parcours prototype** : chargement depuis l’onglet **`Experts`** du classeur Google Sheets (`gsheet_id` + compte de service) **à chaque chargement de page prototype** (évite une session Streamlit « figée » sur d’anciennes lignes après correction du tableur) ; fusion des lignes partageant le même `expert_id` ; colonne **`types_autorises`** ou **`types_autorisees`** (codes séparés par `;` ou `,`). Normalisation défensive des types si une couche fournit une **chaîne** au lieu d’une liste (`coerce_expert_types`). Repli local minimal **uniquement au premier chargement** si Sheets est indisponible (`sereno_core/proto_state.py`, `sereno_core/sheets_experts.py`).
- **Propriétaire — activité** : **entonnoir** (jalons du parcours démo), avis avec **type d’intervention**, export JSON des événements.
- **Compte-rendu d’intervention (produit cible)** : après session, génération d’un **PDF de synthèse** (parcours, synthèse visio, pièces jointes) — **à concevoir** ; lien placeholder dans le mail de contact pilote.
- **Mise en page Streamlit** : largeur du bloc principal **~70 %** pour **toutes** les sections (`apply_global_styles`) ; logo SÉRÉNO en **haut de barre latérale** si disponible (dossier `logo/` ou GCS).

### 3.9.5 Thème Streamlit, boutons et zoom navigateur

- **Fichiers :** `sereno_core/streamlit_theme.py` (`apply_global_styles`, `inject_sereno_prototype_css`, constante **`_BTN_ZOOM_RESILIENCE_CSS`**, helper **`inject_button_zoom_resilience_css()`**).
- **Objectif :** éviter que le **texte des boutons** « déborde » ou se **coupe** (ex. colonnes **flex** Streamlit trop étroites, zoom navigateur) : `min-height` / **padding en `em`**, **`height: auto`**, **`overflow: visible`**, colonnes contenant un **`.stButton`** avec **`min-width: max-content`**, libellé interne en **`white-space: nowrap`**.
- **Chargement :** le bloc zoom est **fusionné** dans les styles globaux et prototype ; les pages **Projet** qui n’injectent pas ces styles appellent **`inject_button_zoom_resilience_css()`** (drapeau session **`_sereno_btn_zoom_css_v2`** pour éviter les doublons inutiles).
- **Exemple ciblé (liste artisans admin) :** styles locaux sur la page **`22_Admin_artisans_consultation.py`** (colonne **Action** + libellé bouton avec **U+2060** si besoin pour empêcher une coupure au milieu du mot).

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
| **Schéma Sheets** | Onglets + `init_google_sheet.py` + migration **`migrate_google_sheet_schema.py`** | En cours / à valider |
| **Logique Python** | `sereno_core` (credentials, schéma, MD book) | En cours |
| **App client** | Expo : parcours urgence → visio → paiement fake | Non démarré |
| **Visio intégrée** | Salle Daily/Twilio bout en bout | Non démarré |
| **Pilote terrain** | ≥ 5 testeurs, ≥ 3 experts, critères § 1.7 | Non démarré |

*Légende statut :* **Non démarré** · **En cours** · **Fait** · **Bloqué** (préciser la cause).

## 4.4 Environnement Python (`venv`) et `pip`

- **Rôle des paquets** (`requirements.txt`) : faire tourner **Streamlit**, **Google Sheets** (gspread), **GCS**, **Vertex AI** (SDK `google-cloud-aiplatform`), puis le paquet local **`.`** (`sereno_core`). Le **repli Gemini** (`google-generativeai`) est dans **`requirements-gemini.txt`** : à installer **en plus** en local si tu veux tester l’API Gemini hors Vertex ; **non requis** pour le déploiement Cloud.
- **Si tout est déjà « Requirement already satisfied »** : l’environnement est **déjà correct** — **aucune action obligatoire**. Tu peux lancer `streamlit run Home.py` sans relancer `pip install`.
- **Si `pip install -r requirements.txt` reste bloqué longtemps** (messages *backtracking*, *looking at multiple versions*) : arrêter avec **Ctrl+C**. Éviter d’installer **`google-generativeai`** dans le **même** fichier que Vertex si le résolveur *pip* tourne en rond ; préférer d’abord `requirements.txt`, puis éventuellement `requirements-gemini.txt`. Ensuite :  
  `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`  
  (optionnel : `--no-cache-dir` si besoin).
- **Revenir en arrière / repartir propre** :  
  1. Fermer les terminaux qui utilisent le venv.  
  2. Supprimer le dossier **`.venv`** à la racine du dépôt.  
  3. `python -m venv .venv` puis activer le venv (PowerShell : `.\.venv\Scripts\Activate.ps1`).  
  4. `python -m pip install --upgrade pip` puis `pip install -r requirements.txt` (puis `pip install -r requirements-gemini.txt` si besoin du repli Gemini).  
  Aucun paquet n’est « obligatoire » **hors** de ce projet : supprimer `.venv` **ne casse pas** Windows ni les autres projets.

---

## Annexes — révisions

| Version | Date | Auteur | Résumé |
|---------|------|--------|--------|
| 1.35 | 2026-04-16 | JOPAI + assistant | **§ 3.9.5** : thème **zoom** boutons (`_BTN_ZOOM_RESILIENCE_CSS`, colonnes `:has(.stButton)`). **Liste artisans (22)** : colonne **Bio**, colonne **Action** élargie, correctif libellé **Éditer**. **Libellés** : **`file_expert_priority_line`** (priorité d’appel masquable en minimal). **Overlay file** : message **équipe** tant que le choix multi-artisans n’est pas confirmé. **Paiement** : titre **prestation** ; autres libellés **notre expert** / **artisan disponible** (cf. 1.33). |
| 1.34 | 2026-04-16 | JOPAI + assistant | **SST** : option **Config** `SERENO_SST_SINGLE_ACK_BUTTON` (défaut **true**) — un bouton valide toutes les consignes ; sinon un bouton par point. **Paramétrage** : case sous **Affichage global**. **File / visio** : si **un seul** artisan, **`essentiel_bio`** dans le **bandeau vert** (bloc succès) sous la ligne de sélection. |
| 1.33 | 2026-04-16 | JOPAI + assistant | Parcours client : libellés **notre expert** (ton plus personnel) ; file **visio** : pas d’en-tête HTML « Photo / Prestataire / Action », **~1 minute** sans emphase gras, **priorité d’appel** surtout dans la liste, message de succès épuré. **Experts** : colonne **`essentiel_bio`** (schéma graine + fiche admin + lecture liste) ; **satisfaction** : overlay de remerciement **SÉRÉNO** + **étoiles** tenues sur une ligne mobile (CSS). |
| 1.32 | 2026-04-15 | JOPAI + assistant | **Experts prototype** : rechargement Sheets à chaque page (plus de vivier figé sur ``_demo_seeded``) ; **types** via ``coerce_expert_types`` ; page file **visio** : code urgence normalisé. **Photo** : URL **https** dans la colonne **photo** pour liste admin + chargement léger sans GCS en session ; fiche admin conserve GCS + data-URL si besoin. **Règle UX Cursor** : tableaux admin étroits / colonnes alignées. |
| 1.31 | 2026-04-15 | JOPAI + assistant | **Photos artisans** : téléchargement GCS avec variantes **.jpg / .JPG / .jpeg** ; affichage choix prestataire via **``st.image``** (contournement blocage data-URL / bucket privé). **Admin fiche artisan** : **expert_id** auto ``EXP-###`` ; **types_autorises** en multiselect ; page plus compacte. |
| 1.30 | 2026-04-15 | JOPAI + assistant | **Types_Urgence** câblé au prototype client : boutons d’accueil + libellés selon la feuille (`actif`, `ordre`, `libelle_affichage`) ; garde-fou si type désactivé ; **TOUS** (experts) n’étend plus que sur les types **actifs**. |
| 1.29 | 2026-04-15 | JOPAI + assistant | **En-tête prototype (urgence)** : logo **SÉRÉNO** affiché **à côté** du pictogramme du type d’urgence (même taille, bords arrondis). **Overlay traitement** : texte **prénom** uniquement (sinon message générique). **Mise en relation** : message de sélection avec **Prénom Nom** (fallback `nom_affichage`). |
| 1.28 | 2026-04-15 | JOPAI + assistant | **Administration · Pilote** : nouvelle page **Artisans (fiche)** (création / mise à jour dans l’onglet **Experts**, upload **photo JPG** vers **Google Cloud Storage** selon convention `artisan/{expert_id}.jpg`). **Experts** : clarification colonne **`prenom`** (sans accent) + photo par convention. **Satisfaction** : bloc de réassurance en **boîte** sous le titre (évite la duplication question NPS). |
| 1.27 | 2026-04-15 | JOPAI + assistant | **Libellés minimalistes** étendus à tout le parcours client (accueil → paiement → satisfaction) + mode **custom** par libellé. **Satisfaction** : réglage propriétaire `SERENO_SATISFACTION_MODE` (**5 étoiles** par défaut ou **NPS**) + verbatim optionnel dans les deux cas. Page Paramétrage réorganisée en **4 cadrans** + tableau récapitulatif coloré. |
| 1.26 | 2026-04-15 | JOPAI + assistant | **Visio** : mode **libellés minimalistes** (standard/minimal/custom) piloté via l’onglet **Config** (`SERENO_UI_*`) ; bouton unique “démarrer la visio” en minimal. **Sessions** : ajout colonne `user_ip` (capture best-effort via headers) pour distinguer des utilisateurs au-delà du pseudo. |
| 1.25 | 2026-04-13 | JOPAI + assistant | Parcours : persistance **Config** (`sheets_journey_config`, préfixe ``SERENO_JOURNEY_``), menu client **sans** les pages désactivées ; formulaire **Se connecter** : e-mail et code pilote **préremplis** (démo) + reset à la déconnexion. |
| 1.24 | 2026-04-13 | JOPAI + assistant | Page **Paramétrage parcours client** (menu Projet) : parcours **standard**, **simplifié** ou **personnalisé** (étapes optionnelles **SST**, **paiement**, **NPS**) ; clés `journey_*` dans **`proto_state`** conservées au reset parcours ; enchaînements mis à jour sur les pages prototype client. |
| 1.23 | 2026-04-08 | JOPAI + assistant | **Twilio 30044** : piste **Trial / longueur SMS** + SMS **court** (`artisan_notify`) ; **Reporting** : graphiques variés (`reporting_cdc_indicators`) ; filigrane **pastel** ; accueil urgence : **`new_session_id`** systématique + overlay sans nom expert (`busy_overlay_use_assigned_expert`). |
| 1.22 | 2026-04-08 | JOPAI + assistant | **`jopai_brand_html`** : titres **H1** + prototype + footer / filigrane / sidebar ; **Vertex 404** : hints + **`vertex_media_summary`** ; **`streamlit-secrets.EXAMPLE.toml`** : `vertex_model` versionné par défaut ; § **3.6.6** ligne 404. |
| 1.21 | 2026-04-08 | JOPAI + assistant | NPS : **JOP** + *AI* + © turquoise + **SÉRÉNO** pétrole ; `proto_processing_pause` sur urgence, SST (ligne + auto), visio ouvrir/fin, paiement ; accueil projet sans bloc lien/QR verbeux ; Twilio Trial = numéro Sheets **identique** aux **Verified** ; § 1.3.1 + dual-UX (pas de pages app séparées). |
| 1.20 | 2026-04-08 | JOPAI + assistant | Question NPS : HTML **inline** (pétrole `#0b2745`, turquoise `#0d9488`) car filtrage des `class` Streamlit ; Twilio **21608** / **21219** + expander Tests connexions ; **Vertex** : `vertex_iam_hints` + message 403 enrichi (IAM, API, région). |
| 1.19 | 2026-04-08 | JOPAI + assistant | Marque **job** + *Séréno* + © (turquoise `#0d9488`, classes `.brand-job` / `.brand-sereno`) ; overlay **spinner** : **nom de l’expert** (champ **nom** Sheets) + « travaille pour vous… » si `assigned_expert` ; règle **`.cursor/rules/sereno-jopai-brand-jobsereno.mdc`** ; question NPS avec libellé marque. |
| 1.18 | 2026-04-08 | JOPAI + assistant | Calendrier **mois** (décocher jours indispos.) ; **`proto_nav_overlay_once`** visio → paiement ; page **Tests connexions** : synthèse **Vertex** (`vertex_media_summary`, GCS + upload mp4) ; secrets **`gcs_sample_video_object`** / **`gcs_sample_audio_object`** ; note **Twilio 30044** ≠ cache app. |
| 1.17 | 2026-04-08 | JOPAI + assistant | **NPS** seul (plus d’étoiles) sur le prototype client ; **§ 1.7** indicateur satisfaction ; **§ 1.7.1** assistant semaine + graphique **`disponibilite_calendar_ui`** ; **§ 1.8.1** MAIF / réseau sinistres (mandataires, éligibilité, process) ; **§ 3.1.1** enregistrement visio + transcription (Twilio vs GCP) ; règle **`.cursor/rules/sereno-dual-ux-web-mobile.mdc`**. |
| 1.16 | 2026-04-08 | JOPAI + assistant | Twilio **30044** : **§ 3.8.1** + **`streamlit-secrets.EXAMPLE.toml`** + replis page **Tests connexions** ; **`_twilio_error_hint`** dans **`artisan_notify`**. |
| 1.15 | 2026-04-08 | JOPAI + assistant | **`notify_expert`** : SMS / appel avec **motif**, **demandeur** (`client_prenom`), **rassurance**, **lien visio** ; **§ 3.1.1** notification artisan ; rappel **Utilisateurs_Acces** / **`code_pilote`**. |
| 1.14 | 2026-04-08 | JOPAI + assistant | **`gspread_helpers`** : une requête métadonnées / classeur + **429** retry ; **`init_google_sheet`** / **`migrate_google_sheet_schema`** ; **§ 3.8.1** & **EXAMPLE** : **`TWILIO_FROM_NUMBER`** = E.164 **attribué par Twilio** (**+1** ou **+33**, etc.). |
| 1.13 | 2026-04-08 | JOPAI + assistant | **`code_pilote`** dans **`Utilisateurs_Acces`** + login multi-profils **`pilot_auth`** ; **`normalize_phone_e164`** (anti **3336…**) ; erreurs Twilio **sans ANSI** ; **CDC** / **EXAMPLE** (Twilio essai **21219**, **21211**). |
| 1.12 | 2026-04-08 | JOPAI + assistant | **`init_google_sheet --seed`** : alignement graines / en-têtes Sheets ; **6** graines **`Utilisateurs_Acces`** ; **Twilio** depuis **`[gcp_service_account]`** si besoin ; **connexion pilote** en **sidebar** + z-index popover ; fichier **`streamlit-secrets.EXAMPLE.toml`** (ne pas laisser Twilio « coincé » sous la table SA). |
| 1.11 | 2026-04-08 | JOPAI + assistant | **Twilio** : clés racine ou **`[twilio]`** (`artisan_notify`) ; tests / visio passent **`st.secrets`** ; métriques : exclusion **`build/`** + top Py par **lignes** ; **`init_google_sheet --seed`** : lignes vides sous l’en-tête ignorées. |
| 1.10 | 2026-04-08 | JOPAI + assistant | **`pilot_auth`** + menu public / connecté (`Home.py`) ; colonne **`telephone`** et graines **Utilisateurs_Acces** (propriétaire + 2 compagnons) ; **§ 3.3.2** & **§ 3.8.1** (Twilio E.164). |
| 1.9 | 2026-04-08 | JOPAI + assistant | **§ 2.10** profils d’accès & **compagnon** (argumentaire sélection) ; **§ 3.6.2–3.6.7** schéma Sheets horodatage / dates d’effet ; onglet **`Utilisateurs_Acces`** ; script **`migrate_google_sheet_schema.py`** ; `sheets_schema` / écriture **Sessions** & **Paiements** alignées. |
| 1.8 | 2026-04-08 | JOPAI + assistant | Pip / Cloud : `requirements.txt` sans **`google-generativeai`** (fichier **`requirements-gemini.txt`** optionnel) pour éviter échec ou timeout d’installation sur Streamlit Cloud ; **§ 3.9.1** et **§ 4.4** alignés. |
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
