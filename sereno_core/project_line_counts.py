"""
Comptage lignes CDC + code source (adapté de JOPAI-BTP `app/components/cdc_viewer.py`).
Racine = dépôt SÉRÉNO ; exclusions adaptées (pas de local_data BTP).
"""

from __future__ import annotations

import os
from pathlib import Path

import streamlit as st

_LOC_INCLUDE_EXTS: frozenset[str] = frozenset(
    {
        ".py",
        ".js",
        ".ts",
        ".tsx",
        ".jsx",
        ".json",
        ".toml",
        ".yaml",
        ".yml",
        ".md",
        ".mdc",
        ".txt",
        ".csv",
        ".css",
        ".html",
        ".sh",
        ".bat",
        ".ps1",
        ".sql",
        ".xml",
        ".rst",
    }
)
_LOC_EXCLUDE_DIRNAMES: frozenset[str] = frozenset(
    {
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        "node_modules",
        ".cursor",
    }
)


@st.cache_data(show_spinner=False, ttl=600)
def top_py_files_by_lines(root_dir: str, limit: int = 10) -> list[dict[str, int | str]]:
    root = Path(root_dir).resolve()
    items: list[dict[str, int | str]] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in _LOC_EXCLUDE_DIRNAMES and not d.startswith(".")]
        for fn in filenames:
            p = Path(dirpath) / fn
            if p.suffix.lower() != ".py":
                continue
            try:
                size_bytes = int(p.stat().st_size)
            except Exception:
                continue
            if size_bytes <= 0:
                continue
            try:
                rel_path = str(p.relative_to(root)).replace("\\", "/")
            except Exception:
                rel_path = str(p)
            items.append({"path": rel_path, "size_bytes": size_bytes})
    items.sort(key=lambda x: int(x.get("size_bytes") or 0), reverse=True)
    out: list[dict[str, int | str]] = []
    for it in items[: max(0, int(limit))]:
        rel_path = str(it.get("path") or "")
        try:
            loc_total = len((root / rel_path).read_text(encoding="utf-8", errors="ignore").splitlines())
        except Exception:
            loc_total = 0
        out.append({**it, "loc_total": loc_total})
    return out


@st.cache_data(show_spinner=False, ttl=600)
def count_project_source_lines(root_dir: str) -> dict[str, int]:
    root = Path(root_dir).resolve()
    total = non_empty = py_total = py_non_empty = 0
    comments_total = comments_py = comments_hors_py = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in _LOC_EXCLUDE_DIRNAMES and not d.startswith(".")]
        for fn in filenames:
            p = Path(dirpath) / fn
            suf = p.suffix.lower()
            if suf not in _LOC_INCLUDE_EXTS:
                continue
            try:
                txt = p.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            lines = txt.splitlines()
            n_total = len(lines)
            if n_total == 0:
                continue
            n_non_empty = sum(1 for ln in lines if ln.strip())
            local_comments = 0
            for ln in lines:
                s = ln.strip()
                if not s:
                    continue
                if suf == ".py" and s.startswith("#"):
                    local_comments += 1
                elif suf in {".js", ".ts", ".tsx", ".jsx", ".css"}:
                    if s.startswith("//") or s.startswith("/*") or s.startswith("*") or s.startswith("*/"):
                        local_comments += 1
                elif suf == ".sql" and s.startswith("--"):
                    local_comments += 1
                elif suf in {".html", ".xml"} and ("<!--" in s or s.startswith("-->")):
                    local_comments += 1
                elif suf in {".sh", ".bat", ".ps1", ".toml", ".yaml", ".yml", ".md", ".mdc", ".txt", ".rst"}:
                    if s.startswith("#"):
                        local_comments += 1
            total += n_total
            non_empty += n_non_empty
            if suf == ".py":
                py_total += n_total
                py_non_empty += n_non_empty
                comments_py += local_comments
            else:
                comments_hors_py += local_comments
            comments_total += local_comments
    hors_py_total = total - py_total
    hors_py_non_empty = non_empty - py_non_empty
    return {
        "total": total,
        "non_empty": non_empty,
        "py_total": py_total,
        "py_non_empty": py_non_empty,
        "hors_py_total": hors_py_total,
        "hors_py_non_empty": hors_py_non_empty,
        "comments_total": comments_total,
        "comments_py": comments_py,
        "comments_hors_py": comments_hors_py,
    }
