"""Formatage d’affichage UI (séparateurs de milliers, etc.)."""


def format_thousands_int(value: int | float | str | None) -> str:
    """
    Entier affiché avec séparateur de milliers (espace insécable fine U+202F).
    Aligné sur JOPAI-BTP `app/ui/themes.py` — `format_thousands_int`.
    """
    if value is None:
        return "0"
    try:
        n = int(value)
    except Exception:
        return str(value)
    return f"{n:,}".replace(",", "\u202F")
