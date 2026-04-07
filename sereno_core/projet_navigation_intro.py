"""
Textes d’introduction « Projet / Prototype » — page Accueil Streamlit et couverture PDF du CDC.
"""

from __future__ import annotations

# --- Streamlit (Markdown) -----------------------------------------------------

COVER_INTRO_MARKDOWN = """
**SÉRÉNO**, c’est un service d’**aide immédiate** pour les personnes prises au dépourvu chez elles
(fuite d’eau, problème d’électricité, gaz, chauffage, serrure…) : en quelques gestes sur le téléphone,
elles peuvent **parler à un pro du bâtiment en visio** pour être guidées et rassurées, avec un **forfait clair**
et des **consignes de sécurité** avant d’activer la caméra.

**JOPAI** accompagne les **artisans et le BTP** avec des outils numériques et l’IA ; ce dépôt est le **pilote**
de cette idée : tableau de bord pour les experts, tests techniques (Google Sheets, cloud), et **cahier des charges**
détaillé pour la suite produit.
"""

NAVIGATION_INTRO_MARKDOWN = """
### Comment le menu latéral est organisé

Il y a **deux grands blocs** : l’un pour **l’équipe projet**, l’autre pour **tester le parcours** comme le ferait un utilisateur.

**1. Projet** — réservé à **l’équipe** qui documente et fait vivre le pilote :

- **Accueil** (la page que vous lisez) ;
- **Métriques** (taille du code et du cahier des charges) ;
- **Reporting** (grille d’indicateurs prévus au cahier des charges — à alimenter quand les données seront branchées) ;
- **Cahier des charges** et **Carnet d’échange** ;
- **Tests de connexion** (Sheets, cloud, etc.).

**2. Prototype** — pour **parcourir l’expérience dans le navigateur**, comme un test réaliste :

- fil **Client** : de l’**urgence** jusqu’aux **avis** ;
- espaces **Artisan** et **Propriétaire** pour simuler le réseau et l’administration pilote.

**Application sur téléphone** — la cible « **vraie appli** à installer depuis le store » sera une application **Expo**
(React Native). **En parallèle**, tout ce que vous voyez ici fonctionne **dans le navigateur** (y compris sur mobile) :
pratique pour démontrer et itérer **sans publier une appli** tout de suite.
"""

# --- PDF (texte sans Markdown) ----------------------------------------------

COVER_INTRO_PARAGRAPHS: list[str] = [
    "SÉRÉNO, c’est un service d’aide immédiate pour les personnes prises au dépourvu chez elles "
    "(fuite d’eau, problème d’électricité, gaz, chauffage, serrure…) : en quelques gestes sur le téléphone, "
    "elles peuvent parler à un pro du bâtiment en visio pour être guidées et rassurées, avec un forfait clair "
    "et des consignes de sécurité avant d’activer la caméra.",
    "JOPAI accompagne les artisans et le BTP avec des outils numériques et l’IA ; ce dépôt est le pilote "
    "de cette idée : tableau de bord pour les experts, tests techniques (Google Sheets, cloud), et cahier des charges détaillé.",
]

# Titres + lignes (puces) pour une mise en page PDF lisible et indentée
NAVIGATION_PDF_BLOCKS: list[tuple[str, list[str]]] = [
    (
        "1. Projet — pour l’équipe qui fait avancer le pilote",
        [
            "Accueil ; métriques (volumes code et cahier des charges) ; reporting des indicateurs CDC ; "
            "cahier des charges ; carnet d’échange ; tests de connexion (Sheets, cloud…).",
            "Ce bloc sert à documenter, mesurer et brancher les outils — ce n’est pas l’appli « grand public » finale.",
        ],
    ),
    (
        "2. Prototype — pour tester comme un utilisateur",
        [
            "Parcours Client dans le navigateur : urgence jusqu’aux avis.",
            "Espaces Artisan et Propriétaire : simulation du réseau et du pilotage.",
        ],
    ),
    (
        "Application sur téléphone",
        [
            "La version installable type « store » sera développée avec Expo (React Native).",
            "D’ici là, la démo tourne dans le navigateur — y compris sur mobile — sans passer par les stores.",
        ],
    ),
]
