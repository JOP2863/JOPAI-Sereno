"""Checklists SST par type d’urgence (prototype — aligné CDC § 2.3)."""

from __future__ import annotations

CHECKLISTS: dict[str, list[str]] = {
    "EAU": [
        "Couper l’arrivée d’eau si un robinet d’arrêt est accessible et sans risque.",
        "Éloigner prises et appareils électriques de la zone mouillée.",
        "Ne pas toucher à l’électricité si l’eau est proche : privilégier la coupure générale si indiqué.",
    ],
    "ELEC": [
        "Ne pas toucher un fil ou un appareil humide ou dénudé.",
        "Identifier le tableau : noter si un disjoncteur est tombé (sans forcer).",
        "Éloigner enfants et animaux de la zone à risque.",
    ],
    "GAZ": [
        "Aérer sans créer d’étincelle : ouvrir fenêtres, ne pas utiliser interrupteurs.",
        "Ne pas utiliser téléphone / sonnette à proximité immédiate du point suspect.",
        "Si odeur forte ou malaise : quitter les lieux et suivre les consignes urgence gaz.",
    ],
    "CHAUFF": [
        "Vérifier si le problème concerne gaz, électricité ou eau (sans manipulation dangereuse).",
        "Ne pas démonter chaudière ou radiateur sous pression.",
        "Aérer la pièce si odeur ou fumée anormale.",
    ],
    "SERR": [
        "Ne pas forcer une serrure si quelqu’un est en danger à l’intérieur : composer les secours.",
        "Vérifier qu’aucune issue de secours n’est disponible avant toute dégradation.",
        "Restez joignable : l’expert pourra vous guider pas à pas.",
    ],
}

URGENCE_LABELS: dict[str, str] = {
    "EAU": "Eau",
    "ELEC": "Électricité",
    "GAZ": "Gaz",
    "CHAUFF": "Chauffage",
    "SERR": "Serrurerie / accès",
}
