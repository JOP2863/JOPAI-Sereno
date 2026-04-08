"""
Vues calendrier **pilote** pour les disponibilités (complément du mois AAAA-MM dans Sheets).

L’onglet **Disponibilite_Mois** reste la source de vérité ; l’assistant **semaine** produit un texte
à coller dans **commentaire_interne** (granularité jour non stockée en colonnes dédiées dans le pilote).
"""

from __future__ import annotations

import calendar
from datetime import date, timedelta

import pandas as pd
import streamlit as st

_WD_FR = ("Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim")
_MONTHS_FR = (
    "",
    "janvier",
    "février",
    "mars",
    "avril",
    "mai",
    "juin",
    "juillet",
    "août",
    "septembre",
    "octobre",
    "novembre",
    "décembre",
)


def _week_start(d: date) -> date:
    return d - timedelta(days=d.weekday())


def render_week_unavailability_assistant(*, recap_state_key: str = "sereno_dispo_week_recap") -> None:
    """
    Une semaine : pour chaque jour, cases « indisponible » (matin / après-midi / soir).
    Stocke le récapitulatif dans ``st.session_state[recap_state_key]`` au clic sur **Générer**.
    """
    st.caption(
        "Cochez les **créneaux où vous n’êtes pas disponible** (non coché = disponible sur ce créneau, pilote démo)."
    )
    anchor = st.date_input(
        "Semaine à afficher (recalée au lundi de la semaine ISO)",
        value=date.today(),
        key="sereno_dispo_week_anchor",
    )
    start = _week_start(anchor)

    for i in range(7):
        d = start + timedelta(days=i)
        label = f"{_WD_FR[d.weekday()]} {d.strftime('%d/%m')}"
        st.markdown(f"**{label}**")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.checkbox("Indispo matin", key=f"dispo_w_{d.isoformat()}_m", value=False)
        with c2:
            st.checkbox("Indispo après-midi", key=f"dispo_w_{d.isoformat()}_a", value=False)
        with c3:
            st.checkbox("Indispo soir", key=f"dispo_w_{d.isoformat()}_s", value=False)

    if st.button("Générer le récapitulatif (texte pour commentaire)", type="secondary", key="sereno_dispo_gen"):
        recap_lines: list[str] = []
        for i in range(7):
            d = start + timedelta(days=i)
            label = f"{_WD_FR[d.weekday()]} {d.strftime('%d/%m')}"
            m = bool(st.session_state.get(f"dispo_w_{d.isoformat()}_m", False))
            a = bool(st.session_state.get(f"dispo_w_{d.isoformat()}_a", False))
            s = bool(st.session_state.get(f"dispo_w_{d.isoformat()}_s", False))
            slots = []
            if m:
                slots.append("matin")
            if a:
                slots.append("après-midi")
            if s:
                slots.append("soir")
            if slots:
                recap_lines.append(f"- {label} : indisponible {', '.join(slots)}")
        if not recap_lines:
            text = (
                "Semaine déclarée **entièrement disponible** sur les tranches matin / après-midi / soir (pilote)."
            )
        else:
            text = f"Indisponibilités détaillées (semaine du {start.isoformat()}) :\n" + "\n".join(recap_lines)
        st.session_state[recap_state_key] = text

    if recap_state_key in st.session_state and st.session_state[recap_state_key]:
        st.text_area(
            "Récap à copier (ou utiliser « Ajouter au commentaire » ci-dessous)",
            value=str(st.session_state[recap_state_key]),
            height=120,
            key=f"{recap_state_key}_ta",
        )


def append_recap_to_comment_key(
    *,
    recap_state_key: str,
    comment_session_key: str,
    button_key: str | None = None,
) -> None:
    """Ajoute le récap au champ commentaire géré par Streamlit via une clé d’état."""
    bk = button_key or f"sereno_dispo_append_{recap_state_key}"
    if st.button("Ajouter ce récap au commentaire interne", type="primary", key=bk):
        recap = str(st.session_state.get(recap_state_key) or "").strip()
        if not recap:
            return
        cur = str(st.session_state.get(comment_session_key, "") or "").strip()
        st.session_state[comment_session_key] = (cur + "\n\n" if cur else "") + recap


def render_disponibilite_mois_chart(df: pd.DataFrame, *, title: str = "Vue par mois (volume par mode)") -> None:
    if df is None or len(df) == 0:
        st.caption("Aucune ligne à afficher.")
        return
    if "annee_mois" not in df.columns or "mode" not in df.columns:
        st.caption("Colonnes **annee_mois** / **mode** absentes.")
        return
    try:
        sub = df[["annee_mois", "mode"]].copy()
        sub["annee_mois"] = sub["annee_mois"].astype(str)
        pivot = sub.groupby(["annee_mois", "mode"]).size().unstack(fill_value=0)
        if pivot.empty:
            return
        st.markdown(f"**{title}**")
        st.bar_chart(pivot)
    except Exception:
        st.caption("Impossible de construire le graphique — voir le tableau.")


def filter_disponibilite_df(df: pd.DataFrame, expert_id: str | None) -> pd.DataFrame:
    if expert_id is None or "expert_id" not in df.columns:
        return df
    return df[df["expert_id"].astype(str) == str(expert_id)]


def render_month_unavailability_assistant(*, recap_state_key: str, key_prefix: str) -> None:
    """
    Calendrier **mensuel** (navigation ◀ ▶) : cases **cochées** = jour **disponible** ;
    **décochée** = **indisponible** (logique proche d’un calendrier type location courte).
    """
    st.caption(
        "Naviguez par **mois**. Une case **décochée** = **indisponible** ce jour-là (journée entière, pilote démo)."
    )
    yk, mk = f"{key_prefix}_cal_y", f"{key_prefix}_cal_m"
    if yk not in st.session_state:
        t = date.today()
        st.session_state[yk] = t.year
        st.session_state[mk] = t.month

    year = int(st.session_state[yk])
    month = int(st.session_state[mk])

    n1, n2, n3 = st.columns([0.12, 0.76, 0.12])
    with n1:
        if st.button("◀", key=f"{key_prefix}_prev_m", help="Mois précédent"):
            if month <= 1:
                st.session_state[mk] = 12
                st.session_state[yk] = year - 1
            else:
                st.session_state[mk] = month - 1
            st.rerun()
    with n2:
        st.markdown(
            f"<div style='text-align:center;font-weight:650;font-size:1.1rem;'>"
            f"{_MONTHS_FR[month].capitalize()} {year}</div>",
            unsafe_allow_html=True,
        )
    with n3:
        if st.button("▶", key=f"{key_prefix}_next_m", help="Mois suivant"):
            if month >= 12:
                st.session_state[mk] = 1
                st.session_state[yk] = year + 1
            else:
                st.session_state[mk] = month + 1
            st.rerun()

    cal = calendar.Calendar(firstweekday=0)
    weeks = cal.monthdatescalendar(year, month)
    hdr = " · ".join(_WD_FR)
    st.caption(hdr)

    for week in weeks:
        cols = st.columns(7)
        for i, d in enumerate(week):
            with cols[i]:
                if d.month != month:
                    st.markdown("<div style='min-height:2.5rem'></div>", unsafe_allow_html=True)
                else:
                    st.checkbox(
                        str(d.day),
                        value=True,
                        key=f"{key_prefix}_day_{d.isoformat()}_avail",
                        help=f"{d.strftime('%d/%m/%Y')} — décocher si indisponible",
                    )

    gen_key = f"{key_prefix}_month_gen"
    if st.button("Générer le récapitulatif (mois affiché)", type="secondary", key=gen_key):
        bad: list[date] = []
        for week in weeks:
            for d in week:
                if d.month != month:
                    continue
                ck = f"{key_prefix}_day_{d.isoformat()}_avail"
                if not bool(st.session_state.get(ck, True)):
                    bad.append(d)
        if not bad:
            text = (
                f"Mois **{year:04d}-{month:02d}** : aucun jour marqué indisponible sur le calendrier (pilote)."
            )
        else:
            bad.sort()
            labels = ", ".join(x.strftime("%d/%m/%Y") for x in bad)
            text = f"Indisponibilités **journées entières** ({year:04d}-{month:02d}) : {labels}"
        st.session_state[recap_state_key] = text

    if recap_state_key in st.session_state and st.session_state[recap_state_key]:
        st.text_area(
            "Récap mois (copier ou « Ajouter au commentaire »)",
            value=str(st.session_state[recap_state_key]),
            height=100,
            key=f"{recap_state_key}_ta",
        )
