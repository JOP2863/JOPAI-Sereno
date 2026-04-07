"""Paquet local `sereno_core` — install explicite pour Streamlit Cloud / pip (complément à pyproject.toml)."""

from setuptools import setup

setup(
    name="jopai-sereno",
    version="0.1.0",
    python_requires=">=3.10",
    packages=["sereno_core"],
)
