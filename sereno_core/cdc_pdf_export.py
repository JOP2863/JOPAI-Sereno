"""

Export PDF du cahier des charges — UTF-8 (police DejaVu), mise en page épurée et lisible.



Les fichiers `assets/fonts/DejaVuSans*.ttf` doivent être présents (fournis dans le dépôt).

"""



from __future__ import annotations



import re

from io import BytesIO

from pathlib import Path

from typing import Iterable



from fpdf import FPDF

from fpdf.enums import XPos, YPos

from sereno_core.projet_navigation_intro import COVER_INTRO_PARAGRAPHS, NAVIGATION_PDF_BLOCKS


COLOR_PRIMARY = (0, 51, 102)

COLOR_SECTION_BG = (236, 242, 249)

COLOR_TEXT = (30, 30, 30)

COLOR_MUTED = (90, 90, 95)



_REPO_ROOT = Path(__file__).resolve().parent.parent

_FONT_REG = _REPO_ROOT / "assets" / "fonts" / "DejaVuSans.ttf"

_FONT_BOLD = _REPO_ROOT / "assets" / "fonts" / "DejaVuSans-Bold.ttf"





def _render_navigation_intro_pdf(pdf: FPDF) -> None:
    """Bloc « menu » plus lisible : titre fort, fond léger, puces indentées."""
    pdf.ln(2.5)
    pdf.set_font("DejaVu", "B", 13)
    pdf.set_text_color(*COLOR_PRIMARY)
    pdf.set_fill_color(*COLOR_SECTION_BG)
    pdf.multi_cell(
        0,
        7.5,
        "  Comment lire le menu latéral ? (rappel pour débuter)",
        fill=True,
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )
    pdf.set_text_color(*COLOR_TEXT)
    pdf.ln(2)
    pdf.set_font("DejaVu", "", 9.5)
    pdf.multi_cell(
        0,
        5,
        "Deux familles d’écrans : outils « projet » d’un côté, parcours « utilisateur » de l’autre.",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )
    pdf.ln(2)
    indent_mm = 10.0
    body_w = pdf.w - pdf.l_margin - pdf.r_margin - indent_mm
    for title, bullets in NAVIGATION_PDF_BLOCKS:
        pdf.set_font("DejaVu", "B", 10)
        pdf.set_text_color(*COLOR_PRIMARY)
        pdf.set_x(pdf.l_margin + indent_mm)
        pdf.multi_cell(body_w, 5.5, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_text_color(*COLOR_TEXT)
        pdf.set_font("DejaVu", "", 9.5)
        for line in bullets:
            pdf.set_x(pdf.l_margin + indent_mm + 5)
            pdf.multi_cell(body_w - 5, 5, "\u2022 " + line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(1.8)



def _fonts_ok() -> bool:

    return _FONT_REG.is_file() and _FONT_BOLD.is_file()





def _strip_md_noise(line: str) -> str:

    s = line.strip()

    s = re.sub(r"^#{1,6}\s+", "", s)

    s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)

    s = re.sub(r"`([^`]+)`", r"\1", s)

    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)

    return s.strip()





def _body_to_plain(body: str) -> list[str]:

    lines_out: list[str] = []

    for raw in body.splitlines():

        line = raw.rstrip()

        if not line.strip():

            lines_out.append("")

            continue

        if line.strip().startswith("|"):

            cells = [c.strip() for c in line.split("|") if c.strip() and not re.match(r"^-+$", c.strip())]

            if cells:

                lines_out.append("• " + " — ".join(cells))

            continue

        if line.startswith("### "):

            lines_out.append(_strip_md_noise(line))

            continue

        lines_out.append(_strip_md_noise(line))

    return lines_out





def _qr_png_bytes(url: str) -> bytes | None:

    try:

        import qrcode

    except ImportError:

        return None

    try:

        qr = qrcode.QRCode(version=1, box_size=4, border=2)

        qr.add_data(url)

        qr.make(fit=True)

        img = qr.make_image(fill_color="#003366", back_color="white")

        buf = BytesIO()

        img.save(buf, format="PNG")

        return buf.getvalue()

    except Exception:

        return None





class _CdcPdf(FPDF):

    def __init__(self) -> None:

        super().__init__(unit="mm", format="A4")

        self.set_auto_page_break(auto=True, margin=18)

        self.set_margins(18, 18, 18)





def _register_fonts(pdf: FPDF) -> None:

    if not _fonts_ok():

        raise FileNotFoundError(

            f"Polices DejaVu introuvables sous {_REPO_ROOT / 'assets' / 'fonts'}. "

            "Ajoutez DejaVuSans.ttf et DejaVuSans-Bold.ttf (voir dossier assets/fonts)."

        )

    pdf.add_font("DejaVu", "", str(_FONT_REG))

    pdf.add_font("DejaVu", "B", str(_FONT_BOLD))





def build_cdc_pdf_bytes(

    parties: list[tuple[str, list[tuple[str, str]]]],

    selected_titles: Iterable[str],

    *,

    qr_target_url: str | None = None,

) -> bytes:

    if qr_target_url is None:

        from sereno_core.app_urls import client_urgency_entry_url



        qr_target_url = client_urgency_entry_url()



    sel = set(selected_titles)

    pdf = _CdcPdf()

    _register_fonts(pdf)

    pdf.add_page()



    pdf.set_font("DejaVu", "B", 18)

    pdf.set_text_color(*COLOR_TEXT)

    pdf.multi_cell(

        0,

        8,

        "SÉRÉNO — Cahier des charges (extrait)",

        new_x=XPos.LMARGIN,

        new_y=YPos.NEXT,

    )



    pdf.set_font("DejaVu", "", 10)

    pdf.set_text_color(*COLOR_MUTED)

    pdf.multi_cell(

        0,

        5,

        "Document à lire tranquillement : gros titres, texte aéré. Une partie = un bloc bleu. "

        "Ci-dessous : rappel de la page d’accueil projet et accès direct au parcours client.",

        new_x=XPos.LMARGIN,

        new_y=YPos.NEXT,

    )

    pdf.ln(3)



    pdf.set_font("DejaVu", "", 10)

    pdf.set_text_color(*COLOR_TEXT)

    for para in COVER_INTRO_PARAGRAPHS:

        pdf.multi_cell(0, 5.2, para, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        pdf.ln(1.5)

    _render_navigation_intro_pdf(pdf)

    pdf.ln(2)

    pdf.set_font("DejaVu", "B", 11)

    pdf.set_text_color(*COLOR_PRIMARY)

    pdf.multi_cell(

        0,

        6,

        "Parcours client — QR code (écran « En quoi pouvons-nous vous aider ? »)",

        new_x=XPos.LMARGIN,

        new_y=YPos.NEXT,

    )

    pdf.set_font("DejaVu", "", 9)

    pdf.set_text_color(*COLOR_MUTED)

    pdf.multi_cell(0, 4.5, qr_target_url, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.ln(1)



    png = _qr_png_bytes(qr_target_url)

    if png:

        y_img = pdf.get_y()

        x_img = pdf.get_x()

        pdf.image(BytesIO(png), x=x_img, y=y_img, w=46)

        pdf.set_y(y_img + 50)

    else:

        pdf.set_font("DejaVu", "", 9)

        pdf.set_text_color(*COLOR_MUTED)

        pdf.multi_cell(

            0,

            4,

            "(Installez qrcode[pil] pour générer le QR dans le PDF ; le lien ci-dessus reste valide.)",

            new_x=XPos.LMARGIN,

            new_y=YPos.NEXT,

        )



    for ptitle, sections in parties:

        if ptitle not in sel:

            continue

        pdf.add_page()

        pdf.set_font("DejaVu", "B", 12)

        pdf.set_fill_color(*COLOR_PRIMARY)

        pdf.set_text_color(255, 255, 255)

        safe_pt = _strip_md_noise(ptitle)[:200]

        pdf.multi_cell(0, 8, safe_pt, fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        pdf.set_text_color(*COLOR_TEXT)

        pdf.ln(2)



        for sec_title, sec_body in sections:

            if sec_title:

                pdf.set_font("DejaVu", "B", 11)

                pdf.set_fill_color(*COLOR_SECTION_BG)

                pdf.set_text_color(*COLOR_PRIMARY)

                st = _strip_md_noise(sec_title)[:180]

                pdf.multi_cell(0, 6, st, fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

                pdf.set_text_color(*COLOR_TEXT)

                pdf.ln(1)

            pdf.set_font("DejaVu", "", 10)

            for pl in _body_to_plain(sec_body):

                if pl == "":

                    pdf.ln(3)

                    continue

                pdf.multi_cell(0, 5.2, pl[:3500], new_x=XPos.LMARGIN, new_y=YPos.NEXT)

            pdf.ln(3)



    buf = BytesIO()

    pdf.output(buf)

    return buf.getvalue()

