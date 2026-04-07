"""
Schéma des onglets Google Sheets (en-têtes + lignes de graine).
Source de vérité pour le script scripts/init_google_sheet.py et pour le CDC § 3.6.

**Branchement code (pilote Streamlit)**

| Onglet | Lecture / écriture |
|--------|--------------------|
| **Experts** | Lecture : liste des artisans (`sheets_experts.load_experts_from_sheets`). |
| **Sessions** | Écriture upsert par `session_id` (`sheets_sessions_write`, appels `sync_session_sheet`). |
| **Paiements** | Écriture append à chaque validation paiement (`sheets_paiements_write`, `append_paiement_sheet_row`). |
| **Disponibilite_Mois** | Écriture + lecture pages admin 16/17 (`sheets_disponibilite_write`). |
| **Connexions_Test** | Écriture / lecture page Tests connexions. |
| **Config** | Non lu par l’app (forfait etc. encore en code Python). |
| **Types_Urgence** | Non lu (libellés / ordre dans `proto_checklists`). |
| **Checklist_SST** | Non lu (questions dans `proto_checklists`). |
| **Regles_Moteur** | Non lu (règles encore en code). |
| **Creneau_Astreinte** | Non branché (saisie / moteur à venir). |
| **Indisponibilite_Exception** | Non branché (saisie / moteur à venir). |
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SheetTab:
    title: str
    headers: list[str]
    seed_rows: tuple[tuple[Any, ...], ...] = ()


SHEET_TABS: tuple[SheetTab, ...] = (
    SheetTab(
        title="Config",
        headers=["cle", "valeur", "description"],
        seed_rows=(
            ("FORFAIT_CENTIMES", "5000", "Montant forfait session en centimes (ex: 50 EUR)"),
            ("DEVISE", "EUR", "Code ISO devise"),
            (
                "MESSAGE_FILE",
                "Merci de patienter, un expert vous rejoint.",
                "Reassurance file d attente",
            ),
            ("VERSION_REGLES", "1", "Incrementer si changement majeur checklist"),
            ("PILOTE_PAIEMENT_MODE", "FAKE", "Simulation sans PSP"),
        ),
    ),
    SheetTab(
        title="Types_Urgence",
        headers=[
            "type_code",
            "ordre",
            "libelle_affichage",
            "description_courte",
            "actif",
        ],
        seed_rows=(
            ("EAU", "1", "Eau", "Fuites arret eau inondation locale", "OUI"),
            ("ELEC", "2", "Électricité", "Disjoncteur panne risque", "OUI"),
            ("GAZ", "3", "Gaz", "Odeur coupure consignes", "OUI"),
            ("CHAUFF", "4", "Chauffage", "Chaudiere radiateur ECS", "OUI"),
            ("SERR", "5", "Serrurerie", "Porte bloquee acces", "OUI"),
        ),
    ),
    SheetTab(
        title="Checklist_SST",
        headers=[
            "checklist_id",
            "type_code",
            "ordre",
            "texte_question",
            "type_reponse",
            "obligatoire",
            "bloquant_si",
            "danger_niveau",
            "notes_internes",
        ],
        seed_rows=(
            (
                "CHK-EAU-01",
                "EAU",
                "1",
                "Avez-vous identifie le robinet d arret principal ou l entree d eau",
                "OUI_NON",
                "OUI",
                "",
                "",
                "Ignorer interne",
            ),
            (
                "CHK-EAU-02",
                "EAU",
                "2",
                "L eau est-elle en contact avec des prises ou materiel electrique",
                "OUI_NON",
                "OUI",
                "OUI",
                "2",
                "Fuir vers ELEC urgence si OUI",
            ),
            (
                "CHK-ELEC-01",
                "ELEC",
                "1",
                "Observez-vous etincelles flammes ou odeur de brule",
                "OUI_NON",
                "OUI",
                "OUI",
                "2",
                "Orientation urgence",
            ),
            (
                "CHK-GAZ-01",
                "GAZ",
                "1",
                "Sentez-vous fortement le gaz ou maux de tete nausees",
                "OUI_NON",
                "OUI",
                "OUI",
                "2",
                "Ne pas actionner interrupteurs",
            ),
            (
                "CHK-CHAUFF-01",
                "CHAUFF",
                "1",
                "Le probleme concerne-t-il une installation gaz apparente",
                "OUI_NON",
                "OUI",
                "",
                "",
                "",
            ),
            (
                "CHK-SERR-01",
                "SERR",
                "1",
                "Etes-vous en securite immediate sans violence en cours",
                "OUI_NON",
                "OUI",
                "NON",
                "2",
                "Secours si violence",
            ),
        ),
    ),
    SheetTab(
        title="Regles_Moteur",
        headers=[
            "regle_id",
            "priorite",
            "condition_champ",
            "operateur",
            "valeur_attendue",
            "action",
            "code_message",
        ],
        seed_rows=(
            ("R001", "10", "danger_niveau", "EGAL", "2", "BLOQUER_VISIO", "MSG_URGENCE"),
            ("R002", "20", "checklist_complete", "EGAL", "TRUE", "AUTORISER_VISIO", ""),
        ),
    ),
    SheetTab(
        title="Sessions",
        headers=[
            "session_id",
            "created_at",
            "type_code",
            "statut",
            "user_pseudo",
            "user_contact",
            "expert_id",
            "room_url",
            "notes_cloture",
            "prix_centimes_factures",
            "debut_visio",
            "fin_visio",
        ],
    ),
    SheetTab(
        title="Experts",
        headers=[
            "expert_id",
            "nom",
            "email",
            "telephone",
            "actif",
            "types_autorises",
            "notes_internes",
            "stripe_connect_account_id",
        ],
        seed_rows=(
            (
                "EXP-001",
                "Dupont Jean",
                "jean.dupont@example.com",
                "+33600000000",
                "OUI",
                "EAU;ELEC;GAZ;CHAUFF;SERR",
                "Pilote — couvre les 5 types (ou utiliser TOUS dans la cellule)",
                "",
            ),
        ),
    ),
    SheetTab(
        title="Disponibilite_Mois",
        headers=[
            "id_ligne",
            "expert_id",
            "annee_mois",
            "mode",
            "commentaire_interne",
            "saisi_le",
            "verrouille_le",
        ],
        seed_rows=(
            (
                "DM-001",
                "EXP-001",
                "2026-04",
                "standard",
                "Exemple pilote",
                "",
                "",
            ),
        ),
    ),
    SheetTab(
        title="Creneau_Astreinte",
        headers=[
            "id_ligne",
            "expert_id",
            "annee_mois",
            "jour_semaine",
            "date_specifique",
            "heure_debut",
            "heure_fin",
            "fuseau",
            "priorite_appel",
        ],
    ),
    SheetTab(
        title="Indisponibilite_Exception",
        headers=[
            "id_ligne",
            "expert_id",
            "debut_ts",
            "fin_ts",
            "motif",
        ],
    ),
    SheetTab(
        title="Paiements",
        headers=[
            "paiement_id",
            "session_id",
            "montant_centimes",
            "mode_paiement",
            "statut",
            "stripe_id",
            "created_at",
            "notes",
        ],
    ),
    SheetTab(
        title="Connexions_Test",
        headers=["horodatage_utc", "source", "statut", "note"],
    ),
)
