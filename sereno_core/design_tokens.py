"""
Jetons d’identité SÉRÉNO — palette institutionnelle BTP (confiance, lisibilité, accessibilité).
"""

from __future__ import annotations

# --- Palette SÉRÉNO (institutionnel BTP) ---
COLOR_BLEU_SOUVERAIN = "#003366"  # primaire, confiance / ordre / protection
COLOR_BLEU_ACIER = "#2C5282"  # actions, liens importants, survol
COLOR_GRIS_BETON = "#F4F7F9"  # fonds, neutre chantier
COLOR_VERT_SECURITE = "#28A745"  # succès, voyants conformité
COLOR_OR_DISCRET = "#D4AF37"  # premium, patrimoine — parcimonie
# Aligné charte JOPAI-BTP (`--jopai-turquoise` dans app/ui/themes.py)
COLOR_JOPAI_TURQUOISE = "#0d9488"
COLOR_DASHED_ZONE = "#CBD5E0"  # zones upload / dépôt (pointillés)

# Alias sémantiques (code UI)
COLOR_PRIMARY = COLOR_BLEU_SOUVERAIN
COLOR_PRIMARY_HOVER = COLOR_BLEU_ACIER
COLOR_BG = COLOR_GRIS_BETON
COLOR_SURFACE = "#FFFFFF"
COLOR_TEXT = "#1a202c"  # lisible sur gris béton / blanc
COLOR_TEXT_MUTED = "#4a5568"
COLOR_BORDER = "#E2E8F0"

# Réassurance : institutionnel (barre latérale bleu souverain)
COLOR_REASSURE_BG = COLOR_GRIS_BETON
COLOR_REASSURE_BORDER = COLOR_BLEU_SOUVERAIN
COLOR_REASSURE_ACCENT = COLOR_BLEU_ACIER

# Succès utilisateur (doc : fond vert pâle + bordure verte marquée)
COLOR_SUCCESS_BG = "#e8f5e9"
COLOR_SUCCESS_BORDER = COLOR_VERT_SECURITE

# Typo (doc : Inter ou Roboto, titres bold, letter-spacing léger)
FONT_UI = "'Inter', 'Roboto', 'Segoe UI', system-ui, sans-serif"
FONT_LETTER_SPACING_TITLES = "-0.02em"

# Rayons (doc : boutons ~6px, pas « gadget » rond)
RADIUS_BTN = "6px"
RADIUS_CARD = "8px"
RADIUS_LG = RADIUS_CARD  # cartes / blocs

# Zones de clic « stress » (seniors) : hauteur mini conservée ; rayon doc sur les boutons
BTN_MIN_HEIGHT_PX = 56
