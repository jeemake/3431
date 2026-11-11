"""Estimatif XLSX (formules actives) a partir de projet.py."""
import pathlib
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.page import PageMargins

from projet import (DIVISEUR, EXTERIEURS, FRAIS, IMPREVUS, LOCATIF, OPTION_A, OPTION_B, OPTION_C,
                    PLUS_VALUES, RATIOS, TVA, budget, surfaces)

OUT = pathlib.Path(__file__).resolve().parent.parent / "out"
FONT = "Calibri"
INK = "23262B"
HEAD = "2F4A6D"
SUB = "EEF1F5"
TOT = "23262B"
NUM = '#,##0;[Red]-#,##0'
NUM2 = '#,##0.00'
thin = Side(style="thin", color="C9C3B8")
BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)


def f(bold=False, color=INK, size=10, italic=False):
    return Font(name=FONT, bold=bold, color=color, size=size, italic=italic)


def header(ws, row, labels, widths=None):
    for i, lab in enumerate(labels, 1):
        c = ws.cell(row=row, column=i, value=lab)
        c.font = f(True, "FFFFFF")
        c.fill = PatternFill("solid", fgColor=HEAD)
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = BORDER
    ws.row_dimensions[row].height = 30
    if widths:
        for i, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(i)].width = w


def style_row(ws, row, ncol, kind=None):
    for col in range(1, ncol + 1):
        c = ws.cell(row=row, column=col)
        c.border = BORDER
        if kind == "sub":
            c.fill = PatternFill("solid", fgColor=SUB)
            c.font = f(True)
        elif kind == "tot":
            c.fill = PatternFill("solid", fgColor=TOT)
            c.font = f(True, "FFFFFF")
        elif kind == "sec":
            c.font = f(True, HEAD)
        else:
            c.font = f()
        if col >= 4:
            c.alignment = Alignment(horizontal="right")


def page_setup(ws, title):
    ws.page_setup.orientation = "landscape"
    ws.page_setup.paperSize = ws.PAPERSIZE_A4
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_margins = PageMargins(left=0.4, right=0.4, top=0.5, bottom=0.5)
    ws.oddFooter.left.text = f"Lot 1728 Riviera Palmeraie - {title}"
    ws.oddFooter.right.text = "Page &P / &N"
    ws.print_title_rows = "1:4"


def build():
    wb = Workbook()

    # ------------------------------------------------------------------ BASE PRIX
    bp = wb.active
    bp.title = "BASE PRIX"
    bp["A1"] = "BORDEREAU DE RATIOS - base Eco-donnees (estimations sommaires ESQ, FCFA HT / m2)"
    bp["A1"].font = f(True, HEAD, 12)
    bp["A2"] = "Coefficient diviseur (consigne : prix de construction divises par 2)"
    bp["A2"].font = f(italic=True)
    bp["E2"] = DIVISEUR
    bp["E2"].font = f(True, "C0504D", 12)
    bp["E2"].fill = PatternFill("solid", fgColor="FFF4D6")
    wb.defined_names.add(__import__("openpyxl").workbook.defined_name.DefinedName(
        "DIVISEUR", attr_text="'BASE PRIX'!$E$2"))
    header(bp, 4, ["CODE", "DESIGNATION", "SOURCE (projet de reference)", "PU BASE HT", "PU RETENU HT"],
           [12, 38, 52, 16, 16])
    ref = {}
    r = 5
    for code, (lib, base, src) in RATIOS.items():
        bp.cell(row=r, column=1, value=code)
        bp.cell(row=r, column=2, value=lib)
        bp.cell(row=r, column=3, value=src)
        bp.cell(row=r, column=4, value=base).number_format = NUM
        bp.cell(row=r, column=5, value=f"=D{r}/DIVISEUR").number_format = NUM
        style_row(bp, r, 5)
        ref[code] = f"'BASE PRIX'!$E${r}"
        r += 1
    r += 1
    bp.cell(row=r, column=1, value="Les ratios sont issus des tableaux d'estimation sommaire de la base Eco-donnees "
            "(Pavillon Akpo 2022, Résidences Anthurium 2021, Résidence Les Flamboyants, Villa Cacao 6 2023). "
            "Ils incluent tous corps d'etat (gros oeuvre a finitions) au prorata de la surface de chaque piece.").font = f(italic=True, size=9)
    page_setup(bp, "Base prix")

    sheets = {}

    def detail(opt, title):
        ws = wb.create_sheet(title)
        ws["A1"] = opt["nom"].upper()
        ws["A1"].font = f(True, HEAD, 12)
        ws["A2"] = "Estimation sommaire par piece - ratios base Eco-donnees / coefficient diviseur"
        ws["A2"].font = f(italic=True)
        header(ws, 4, ["N°", "DESIGNATION", "NIVEAU", "SURFACE / QTE", "PU HT (FCFA)", "TOTAL HT (FCFA)", "SOURCE PRIX"],
               [7, 50, 10, 14, 16, 18, 40])
        row = 5
        subtot_cells = []
        n = 0
        for niv, lab in (("RDC", "REZ-DE-CHAUSSEE"), ("R+1", "ETAGE (R+1)")):
            ps = [p for p in opt["pieces"] if p["niveau"] == niv]
            if not ps:
                continue
            ws.cell(row=row, column=2, value=lab)
            style_row(ws, row, 6, "sec")
            row += 1
            first = row
            for p in ps:
                n += 1
                ws.cell(row=row, column=1, value=n)
                nom = p["nom"] + ("" if p["clos"] else " (hors clos)")
                ws.cell(row=row, column=2, value=nom)
                ws.cell(row=row, column=3, value=niv if p["clos"] else niv + " ext")
                ws.cell(row=row, column=4, value=p["surface"]).number_format = NUM2
                ws.cell(row=row, column=5, value=f"={ref[p['code']]}").number_format = NUM
                ws.cell(row=row, column=6, value=f"=D{row}*E{row}").number_format = NUM
                style_row(ws, row, 6)
                row += 1
            ws.cell(row=row, column=2, value=f"Sous-total {lab.lower()}")
            ws.cell(row=row, column=4, value=f"=SUM(D{first}:D{row - 1})").number_format = NUM2
            ws.cell(row=row, column=6, value=f"=SUM(F{first}:F{row - 1})").number_format = NUM
            style_row(ws, row, 6, "sub")
            subtot_cells.append(f"F{row}")
            row += 2

        k = opt["code"]
        for titre, liste in (("AMENAGEMENTS EXTERIEURS ET VRD", EXTERIEURS),
                             ("PLUS-VALUES DU PARTI ARCHITECTURAL (terre, bois, claustras)", PLUS_VALUES)):
            lignes = [lg for lg in liste if lg[4].get(k, 0)]
            if not lignes:
                continue
            ws.cell(row=row, column=2, value=titre)
            style_row(ws, row, 6, "sec")
            row += 1
            first = row
            for lg in lignes:
                n += 1
                lib, unit, base = lg[0], lg[1], lg[2]
                ws.cell(row=row, column=1, value=n)
                ws.cell(row=row, column=2, value=lib)
                ws.cell(row=row, column=3, value=unit)
                ws.cell(row=row, column=4, value=lg[4][k]).number_format = NUM2
                ws.cell(row=row, column=5, value=f"={base}/DIVISEUR" if lg[5] else base).number_format = NUM
                ws.cell(row=row, column=7, value=lg[3] + ("" if lg[5] else " - non divise")).font = f(italic=True, size=9)
                ws.cell(row=row, column=6, value=f"=D{row}*E{row}").number_format = NUM
                style_row(ws, row, 6)
                row += 1
            ws.cell(row=row, column=2, value="Sous-total")
            ws.cell(row=row, column=6, value=f"=SUM(F{first}:F{row - 1})").number_format = NUM
            style_row(ws, row, 6, "sub")
            subtot_cells.append(f"F{row}")
            row += 2

        ws.cell(row=row, column=2, value="TOTAL TRAVAUX HT")
        ws.cell(row=row, column=6, value="=" + "+".join(subtot_cells)).number_format = NUM
        style_row(ws, row, 6, "tot")
        trav = row
        row += 2
        ws.cell(row=row, column=2, value="HONORAIRES, ETUDES ET ALEAS (% des travaux)")
        style_row(ws, row, 6, "sec")
        row += 1
        first = row
        for lib, taux in FRAIS + [("Imprévus", IMPREVUS)]:
            ws.cell(row=row, column=2, value=lib)
            ws.cell(row=row, column=3, value="%")
            ws.cell(row=row, column=4, value=taux).number_format = "0.00%"
            ws.cell(row=row, column=6, value=f"=D{row}*F{trav}").number_format = NUM
            style_row(ws, row, 6)
            row += 1
        ws.cell(row=row, column=2, value="Sous-total honoraires et aleas")
        ws.cell(row=row, column=6, value=f"=SUM(F{first}:F{row - 1})").number_format = NUM
        style_row(ws, row, 6, "sub")
        frais = row
        row += 2
        ws.cell(row=row, column=2, value="TOTAL GENERAL HT")
        ws.cell(row=row, column=6, value=f"=F{trav}+F{frais}").number_format = NUM
        style_row(ws, row, 6, "tot")
        ht = row
        row += 1
        ws.cell(row=row, column=2, value="TVA")
        ws.cell(row=row, column=4, value=TVA).number_format = "0%"
        ws.cell(row=row, column=6, value=f"=D{row}*F{ht}").number_format = NUM
        style_row(ws, row, 6)
        row += 1
        ws.cell(row=row, column=2, value="TOTAL GENERAL TTC")
        ws.cell(row=row, column=6, value=f"=F{ht}+F{row - 1}").number_format = NUM
        style_row(ws, row, 6, "tot")
        ttc = row
        row += 2
        ws.cell(row=row, column=2, value="Surface close (SHOB) m2")
        ws.cell(row=row, column=4, value=f"=SUMIFS(D5:D{trav},C5:C{trav},\"RDC\")+SUMIFS(D5:D{trav},C5:C{trav},\"R+1\")").number_format = NUM2
        style_row(ws, row, 6)
        shob = row
        row += 1
        ws.cell(row=row, column=2, value="Ratio travaux HT / m2 clos")
        ws.cell(row=row, column=6, value=f"=F{trav}/D{shob}").number_format = NUM
        style_row(ws, row, 6)
        row += 2
        ws.cell(row=row, column=2, value="NB : mobilier, electromenager, groupe electrogene, piscine et foncier non compris. "
                "Montant sommaire susceptible d'evoluer aux phases APS / APD.").font = f(italic=True, size=9)
        page_setup(ws, title)
        ws.freeze_panes = "A5"
        sheets[k] = {"name": title, "trav": f"F{trav}", "frais": f"F{frais}", "ht": f"F{ht}",
                     "ttc": f"F{ttc}", "shob": f"D{shob}"}

    detail(OPTION_A, "VILLA OPTION A")
    detail(OPTION_B, "VILLA OPTION B")
    detail(OPTION_C, "VILLA OPTION C")
    detail(LOCATIF, "LOCATIF R+1")

    # ------------------------------------------------------------------ RECAP
    rc = wb.create_sheet("RECAP", 0)
    rc["A1"] = "LOT 1728 - RIVIERA PALMERAIE - RECAPITULATIF DE L'ESTIMATION SOMMAIRE"
    rc["A1"].font = f(True, HEAD, 13)
    rc["A2"] = ("Prix de construction = ratios base Eco-donnees divises par le coefficient de l'onglet BASE PRIX "
                "(actuellement 2). FCFA.")
    rc["A2"].font = f(italic=True)
    header(rc, 4, ["N°", "OUVRAGE", "SURFACE CLOSE (m2)", "TRAVAUX HT", "HONORAIRES + ALEAS",
                   "TOTAL HT", "TOTAL TTC", "TRAVAUX HT / m2"], [6, 40, 16, 18, 18, 18, 18, 16])
    row = 5
    lines = {}
    for i, (k, lab) in enumerate((("A", "Villa - Option A (villa compacte, nounou a l'etage)"),
                                  ("B", "Villa - Option B (aile de service)"),
                                  ("C", "Villa - Option C (maison a patio central)"),
                                  ("L", "Batiment locatif R+1 (6 logements)")), 1):
        s = sheets[k]
        q = f"'{s['name']}'!"
        rc.cell(row=row, column=1, value=i)
        rc.cell(row=row, column=2, value=lab)
        rc.cell(row=row, column=3, value=f"={q}{s['shob']}").number_format = NUM2
        rc.cell(row=row, column=4, value=f"={q}{s['trav']}").number_format = NUM
        rc.cell(row=row, column=5, value=f"={q}{s['frais']}").number_format = NUM
        rc.cell(row=row, column=6, value=f"={q}{s['ht']}").number_format = NUM
        rc.cell(row=row, column=7, value=f"={q}{s['ttc']}").number_format = NUM
        rc.cell(row=row, column=8, value=f"=D{row}/C{row}").number_format = NUM
        style_row(rc, row, 8)
        lines[k] = row
        row += 1
    row += 1
    for lab, k in (("OPERATION COMPLETE - Option A + locatif", "A"), ("OPERATION COMPLETE - Option B + locatif", "B"),
                   ("OPERATION COMPLETE - Option C + locatif", "C")):
        rc.cell(row=row, column=2, value=lab)
        for col in range(3, 8):
            L = get_column_letter(col)
            rc.cell(row=row, column=col, value=f"={L}{lines[k]}+{L}{lines['L']}").number_format = (
                NUM2 if col == 3 else NUM)
        rc.cell(row=row, column=8, value=f"=D{row}/C{row}").number_format = NUM
        style_row(rc, row, 8, "tot")
        row += 1
    row += 1
    notes = [
        "Base : ratios par type de piece des estimations sommaires (phase ESQ) de la base Eco-donnees, projets residentiels "
        "d'Abidjan 2015-2023, appliques aux surfaces des plans d'esquisse.",
        "Honoraires et aleas : architecte 8 %, BET 2 %, geotechnique 1,5 %, bureau de controle 1,35 %, assurances 1,2 % "
        "(taux du recapitulatif Pavillon Akpo), imprevus 10 % (stade esquisse).",
        "Le coefficient diviseur ne s'applique qu'aux ratios de la base Eco-donnees ; les prix de marche directs "
        "(cloture, assainissement, menuiseries bois, claustras, equipements) ne sont pas divises.",
        "TVA 18 % applicable si les travaux sont confies a des entreprises assujetties.",
        "Non compris : foncier, mobilier et electromenager, climatiseurs, groupe electrogene ou solaire, forage, piscine, "
        "fondations speciales (selon etude de sol), frais de permis, geometre et notaire (integres au business plan).",
    ]
    for t in notes:
        rc.cell(row=row, column=2, value="- " + t).font = f(size=9, italic=True)
        rc.merge_cells(start_row=row, start_column=2, end_row=row, end_column=8)
        rc.cell(row=row, column=2).alignment = Alignment(wrap_text=True, vertical="top")
        rc.row_dimensions[row].height = 28
        row += 1
    page_setup(rc, "Recapitulatif")
    path = OUT / "02_Estimatif_Lot1728_Palmeraie.xlsx"
    wb.save(path)
    return path


if __name__ == "__main__":
    p = build()
    print(p)
    for o in (OPTION_A, OPTION_B, OPTION_C, LOCATIF):
        print(o["code"], budget(o), surfaces(o)["clos"])
