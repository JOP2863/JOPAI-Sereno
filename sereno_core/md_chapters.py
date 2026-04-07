"""Parse Markdown en chapitres ## / sous-sections ### (CDC / carnet)."""

from __future__ import annotations

import re


def strip_front_matter(text: str) -> str:
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[end + 4 :].lstrip("\n")
    return text


def split_into_h2_sections(text: str) -> list[tuple[str, str]]:
    """
    Découpe un bloc Markdown sur les titres ## (pas ###).
    Sans aucun ## : une seule entrée (« », corps entier).
    Un préambule avant le premier ## est conservé avec le titre vide.
    """
    text = text.strip()
    if not text:
        return []
    lines = text.split("\n")
    first_h2 = None
    for i, line in enumerate(lines):
        if line.startswith("## ") and not line.startswith("###"):
            first_h2 = i
            break
    if first_h2 is None:
        return [("", text)]

    sections: list[tuple[str, str]] = []
    pre = "\n".join(lines[:first_h2]).strip()
    if pre:
        sections.append(("", pre))

    current_title: str | None = None
    current_lines: list[str] = []
    for line in lines[first_h2:]:
        if line.startswith("## ") and not line.startswith("###"):
            if current_title is not None:
                sections.append((current_title, "\n".join(current_lines).strip()))
            current_title = line[3:].strip()
            current_lines = []
        else:
            current_lines.append(line)
    if current_title is not None:
        sections.append((current_title, "\n".join(current_lines).strip()))
    return sections


_PARTIE1_RE = re.compile(r"^# Partie 1\b", re.MULTILINE)
_PARTIE_HEADER_RE = re.compile(r"^# (Partie \d+ — .+)$", re.MULTILINE)


def parse_cdc_by_parties(md: str) -> list[tuple[str, list[tuple[str, str]]]] | None:
    """
    Structure cahier des charges : tout avant « # Partie 1 » → chapitre « 0 — Introduction »,
    puis une entrée par « # Partie N — … », chacune découpée en sections ##.

    Retourne None si le document ne suit pas ce schéma (ex. carnet d’échange).
    """
    md = strip_front_matter(md.strip())
    m = _PARTIE1_RE.search(md)
    if not m:
        return None
    intro = md[: m.start()].strip()
    rest = md[m.start() :]
    headers = list(_PARTIE_HEADER_RE.finditer(rest))
    if not headers:
        return None

    out: list[tuple[str, list[tuple[str, str]]]] = [
        ("0 — Introduction", split_into_h2_sections(intro)),
    ]
    for i, h in enumerate(headers):
        title = h.group(1)
        start = h.end()
        end = headers[i + 1].start() if i + 1 < len(headers) else len(rest)
        body = rest[start:end].lstrip("\n")
        out.append((title, split_into_h2_sections(body)))
    return out


def parse_chapters(md: str) -> list[tuple[str, str]]:
    md = strip_front_matter(md.strip())
    lines = md.split("\n")
    first_h2 = None
    for i, line in enumerate(lines):
        if line.startswith("## ") and not line.startswith("###"):
            first_h2 = i
            break
    if first_h2 is None:
        return [("Document", md)] if md.strip() else []
    intro = "\n".join(lines[:first_h2]).strip()
    tail = "\n".join(lines[first_h2:])
    sections = split_into_h2_sections(tail)
    chapters: list[tuple[str, str]] = []
    if intro:
        chapters.append(("En-tête", intro))
    chapters.extend(sections)
    return chapters


def parse_subsections(body: str) -> list[tuple[str, str]]:
    pattern = re.compile(r"^### (.+)$", re.MULTILINE)
    matches = list(pattern.finditer(body))
    if not matches:
        return []

    out: list[tuple[str, str]] = []
    pre = body[: matches[0].start()].strip()
    if pre:
        out.append(("", pre))

    for i, m in enumerate(matches):
        title = m.group(1).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        content = body[start:end].strip()
        out.append((title, content))
    return out


def highlight_snippet(text: str, query: str) -> str:
    if not query.strip():
        return ""
    low = text.lower()
    q = query.lower().strip()
    idx = low.find(q)
    if idx == -1:
        return ""
    a = max(0, idx - 60)
    b = min(len(text), idx + len(q) + 80)
    frag = text[a:b]
    if a > 0:
        frag = "…" + frag
    if b < len(text):
        frag = frag + "…"
    matched = text[idx : idx + len(q)]
    return frag.replace(matched, f"**{matched}**", 1)
