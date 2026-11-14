"""Excel du tableau des surfaces et de l'estimatif de l'option C v5 (villa) et des 2 duplex.

Formules actives : les quantites de l'estimatif renvoient aux cellules du tableau des surfaces, les prix unitaires
renvoient aux ratios de l'onglet PARAMETRES (base Eco-donnees, divisee par le coefficient), les totaux, frais,
imprevus et TVA se recalculent si l'on change une surface, une quantite, un prix ou un parametre.
Sortie : out/06_Surfaces_Estimatif_Option_C_v5_Lot1728.xlsx
"""
import pathlib

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.page import PageMargins

from projet import (DIVISEUR, EXTERIEURS, FRAIS, IMPREVUS, LOCATIF_M, LOYERS, OPTION_C, PLUS_VALUES, RATIOS, TVA)

OUT = pathlib.Path(__file__).resolve().parent.parent / "out" / "06_Surfaces_Estimatif_Option_C_v5_Lot1728.xlsx"
FONT = "Calibri"
INK, HEAD, SUB, TOT = "23262B", "2F4A6D", "EEF1F5", "23262B"
BLEU = "0000FF"          # saisies (convention : bleu = valeur modifiable, noir = formule)
thin = Side(style="thin", color="C9C3B8")
BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)
M2, FCFA, PCT = '#,##0.00', '#,##0;[Red]-#,##0', '0.00%'
NIV = {"RDC": "Rez-de-chaussée", "R+1": "Étage", "TOIT": "Niveau haut (toit-terrasse)"}
ORDRE = ["RDC", "R+1", "TOIT"]


def fnt(bold=False, color=INK, size=10, italic=False):
    return Font(name=FONT, bold=bold, color=color, size=size, italic=italic)


def titre(ws, texte, sous=None):
    ws["A1"] = texte
    ws["A1"].font = fnt(True, HEAD, 13)
    if sous:
        ws["A2"] = sous
        ws["A2"].font = fnt(italic=True, color="6B6F76")


def entete(ws, row, labels, widths):
    for i, lab in enumerate(labels, 1):
        c = ws.cell(row=row, column=i, value=lab)
        c.font = fnt(True, "FFFFFF")
        c.fill = PatternFill("solid", fgColor=HEAD)
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = BORDER
        ws.column_dimensions[get_column_letter(i)].width = widths[i - 1]
    ws.row_dimensions[row].height = 30


def ligne(ws, row, ncol, kind=None, numcols=(), fmt=None):
    for col in range(1, ncol + 1):
        c = ws.cell(row=row, column=col)
        c.border = BORDER
        if kind == "sec":
            c.font = fnt(True, HEAD)
            c.fill = PatternFill("solid", fgColor=SUB)
        elif kind == "sub":
            c.font = fnt(True)
            c.fill = PatternFill("solid", fgColor=SUB)
        elif kind == "tot":
            c.font = fnt(True, "FFFFFF")
            c.fill = PatternFill("solid", fgColor=TOT)
        else:
            c.font = c.font if c.font and c.font.color and c.font.color.rgb == "FF" + BLEU else fnt()
        if col in numcols:
            c.alignment = Alignment(horizontal="right")
            if fmt:
                c.number_format = fmt[col] if isinstance(fmt, dict) else fmt


def saisie(cell):
    cell.font = fnt(color=BLEU)


def mise_en_page(ws, titre_):
    ws.page_setup.orientation = "landscape"
    ws.page_setup.paperSize = ws.PAPERSIZE_A4
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_margins = PageMargins(left=0.4, right=0.4, top=0.5, bottom=0.5)
    ws.oddFooter.left.text = f"Lot 1728 Riviera Palmeraie, option C v5 - {titre_}"
    ws.oddFooter.right.text = "Page &P / &N"
    ws.sheet_view.showGridLines = False


def nom_affiche(r):
    n = r["nom"]
    return n


# =============================================================================== PARAMETRES
def parametres(wb):
    ws = wb.create_sheet("PARAMETRES")
    titre(ws, "PARAMÈTRES ET BORDEREAU DE RATIOS", "Cellules en bleu = valeurs modifiables ; tout le reste se recalcule.")
    ws["B4"], ws["B5"], ws["B6"] = "Coefficient diviseur des ratios Éco-données (consigne du client)", "TVA", "Imprévus (stade esquisse)"
    ws["C4"], ws["C5"], ws["C6"] = DIVISEUR, TVA, IMPREVUS
    ws["C5"].number_format = ws["C6"].number_format = '0.0%'
    for c in ("C4", "C5", "C6"):
        saisie(ws[c])
        ws[c].border = BORDER
    ws["B8"] = "Frais, en % du total des travaux HT"
    ws["B8"].font = fnt(True, HEAD)
    for i, (lib, taux) in enumerate(FRAIS):
        r = 9 + i
        ws.cell(row=r, column=2, value=lib)
        c = ws.cell(row=r, column=3, value=taux)
        c.number_format = PCT
        saisie(c)
        c.border = BORDER
    r0 = 9 + len(FRAIS) + 2
    ws.cell(row=r0 - 1, column=1, value="Bordereau de ratios par type de pièce (FCFA HT / m², base Éco-données avant division)").font = fnt(True, HEAD)
    entete(ws, r0, ["Code", "Type de pièce", "Ratio base", "Source", "PU retenu (ratio ÷ diviseur)"], [14, 62, 16, 44, 22])
    ws.column_dimensions["A"].width = 14
    for i, (code, (lab, ratio, src)) in enumerate(RATIOS.items()):
        r = r0 + 1 + i
        ws.cell(row=r, column=1, value=code)
        ws.cell(row=r, column=2, value=lab)
        c = ws.cell(row=r, column=3, value=ratio)
        c.number_format = FCFA
        saisie(c)
        ws.cell(row=r, column=4, value=src)
        e = ws.cell(row=r, column=5, value=f"=C{r}/$C$4")
        e.number_format = FCFA
        for col in range(1, 6):
            ws.cell(row=r, column=col).border = BORDER
            if col not in (3,):
                ws.cell(row=r, column=col).font = fnt()
        saisie(ws.cell(row=r, column=3))
    last = r0 + len(RATIOS)
    mise_en_page(ws, "paramètres")
    return {"div": "PARAMETRES!$C$4", "tva": "PARAMETRES!$C$5", "imp": "PARAMETRES!$C$6",
            "frais_rows": [9 + i for i in range(len(FRAIS))],
            "codes": f"PARAMETRES!$A${r0 + 1}:$A${last}", "ratios": f"PARAMETRES!$C${r0 + 1}:$C${last}",
            "libs": f"PARAMETRES!$B${r0 + 1}:$B${last}"}


# =============================================================================== SURFACES
def surfaces_sheet(wb, nom, opt, titre_, par_maison=False):
    ws = wb.create_sheet(nom)
    titre(ws, titre_, "Surfaces calculées sur le modèle (rectangles de pièces), au m² près à deux décimales.")
    labels = (["Maison"] if par_maison else []) + ["Niveau", "Pièce", "Code ratio", "Nature", "Surface (m²)", "Dans l'emprise"]
    widths = ([12] if par_maison else []) + [16, 44, 14, 14, 14, 16]
    off = 1 if par_maison else 0
    head_row = 14
    entete(ws, head_row, labels, widths)
    pieces = [p for niv in ORDRE for p in opt["pieces"] if p["niveau"] == niv]
    rows = {}
    r = head_row + 1
    for p in pieces:
        emprise = (p["niveau"] == "RDC" and p["clos"] and p["nom"] != "Guérite + WC gardien")
        vals = ([p.get("logement", "")] if par_maison else []) + [p["niveau"], nom_affiche(p), p["code"],
                                                                  "Clos" if p["clos"] else "Hors clos", p["surface"],
                                                                  "Oui" if emprise else "Non"]
        for i, v in enumerate(vals, 1):
            ws.cell(row=r, column=i, value=v)
        ligne(ws, r, len(vals), numcols=(5 + off,), fmt=M2)
        saisie(ws.cell(row=r, column=5 + off))
        rows[id(p)] = r
        r += 1
    last = r - 1
    cn, cs, cc, ce = (get_column_letter(1 + off), get_column_letter(5 + off), get_column_letter(3 + off), get_column_letter(6 + off))
    code = f"${cc}${head_row + 1}:${cc}${last}"
    surf = f"${cs}${head_row + 1}:${cs}${last}"
    niv = f"${cn}${head_row + 1}:${cn}${last}"
    nat = f"${get_column_letter(5 + off - 1 + 0)}${head_row + 1}:${get_column_letter(5 + off - 1)}${last}"
    nat = f"${get_column_letter(4 + off + 0)}${head_row + 1}:${get_column_letter(4 + off)}${last}"
    # colonne "Nature" = colonne (4 + off) ; "Code ratio" = (3 + off)
    cnat = get_column_letter(4 + off)
    nat = f"${cnat}${head_row + 1}:${cnat}${last}"
    emp = f"${ce}${head_row + 1}:${ce}${last}"
    lab_col = 2 if not par_maison else 3
    # synthese en tete
    ws.cell(row=4, column=lab_col, value="SYNTHÈSE").font = fnt(True, HEAD)
    items = [("Surface close du rez-de-chaussée (m²)", f'=SUMIFS({surf},{niv},"RDC",{nat},"Clos")'),
             ("Surface close de l'étage (m²)", f'=SUMIFS({surf},{niv},"R+1",{nat},"Clos")'),
             ("SURFACE CLOSE TOTALE (m²)", None),
             ("Emprise au sol bâtie (m²)", f'=SUMIFS({surf},{emp},"Oui")'),
             ("Terrasses, loggia, balcon et préau, hors clos (m²)",
              "=" + "+".join(f'SUMIFS({surf},{code},"{c_}",{nat},"Hors clos")' for c_ in ("terrasse", "balcon", "l_coursive")))]
    refs = {}
    for k, (lab, fm) in enumerate(items):
        rr = 5 + k
        ws.cell(row=rr, column=lab_col, value=lab).font = fnt(k == 2)
        c = ws.cell(row=rr, column=lab_col + 3, value=fm if fm else f"={get_column_letter(lab_col + 3)}5+{get_column_letter(lab_col + 3)}6")
        c.number_format = M2
        c.font = fnt(k == 2)
        c.alignment = Alignment(horizontal="right")
        for cc_ in range(lab_col, lab_col + 4):
            ws.cell(row=rr, column=cc_).border = BORDER
        refs[k] = f"'{nom}'!${get_column_letter(lab_col + 3)}${rr}"
    if par_maison:
        ws.cell(row=11, column=lab_col, value="Détail par maison (surface close, m²)").font = fnt(True, HEAD)
        for k, mn in enumerate(("M1", "M2")):
            rr = 12 + k
            ws.cell(row=rr, column=lab_col, value=f"Maison {k + 1}").font = fnt()
            c = ws.cell(row=rr, column=lab_col + 3,
                        value=f'=SUMIFS({surf},$A${head_row + 1}:$A${last},"{mn}",{niv},"RDC",{nat},"Clos")+'
                              f'SUMIFS({surf},$A${head_row + 1}:$A${last},"{mn}",{niv},"R+1",{nat},"Clos")')
            c.number_format = M2
            c.alignment = Alignment(horizontal="right")
            for cc_ in range(lab_col, lab_col + 4):
                ws.cell(row=rr, column=cc_).border = BORDER
        head_hint = 10
    ws.freeze_panes = ws.cell(row=head_row + 1, column=1)
    ws.auto_filter.ref = f"A{head_row}:{get_column_letter(len(labels))}{last}"
    mise_en_page(ws, titre_)
    ws.print_title_rows = f"{head_row}:{head_row}"
    return {"rows": rows, "refs": refs, "off": off, "name": nom}


# =============================================================================== ESTIMATIF
def estimatif_sheet(wb, nom, opt, cle, titre_, S, P):
    ws = wb.create_sheet(nom)
    titre(ws, titre_, "Quantités liées au tableau des surfaces ; ratios Éco-données ÷ coefficient (PARAMETRES) ; "
                      "postes hors base au prix de marché (hypothèses, non divisés). Montants en FCFA HT.")
    labels = ["Niveau / section", "Désignation", "Code", "Ratio ou source", "Unité", "Quantité", "Prix de base (FCFA)", "Divisé ?",
              "PU HT retenu", "Total HT (FCFA)"]
    entete(ws, 4, labels, [24, 62, 12, 40, 8, 14, 18, 10, 16, 20])
    r = 5
    subs = []
    pu = lambda row: f'=IF(H{row}="Oui",G{row}/{P["div"]},G{row})'      # noqa: E731

    def section(texte):
        nonlocal r
        ws.cell(row=r, column=1, value=texte)
        ligne(ws, r, 10, "sec")
        r += 1

    def sous_total(texte, a, b):
        nonlocal r
        ws.cell(row=r, column=2, value=texte)
        c = ws.cell(row=r, column=10, value=f"=SUM(J{a}:J{b})")
        ligne(ws, r, 10, "sub", numcols=(10,), fmt=FCFA)
        subs.append(r)
        r += 1

    pieces_par_niv = {niv: [p for p in opt["pieces"] if p["niveau"] == niv] for niv in ORDRE}
    scol = get_column_letter(5 + S["off"])
    for niv in ORDRE:
        ps = pieces_par_niv[niv]
        if not ps:
            continue
        section(NIV[niv].upper())
        a = r
        for p in ps:
            ws.cell(row=r, column=1, value=niv)
            ws.cell(row=r, column=2, value=nom_affiche(p))
            ws.cell(row=r, column=3, value=p["code"])
            ws.cell(row=r, column=4, value=f'=INDEX({P["libs"]},MATCH(C{r},{P["codes"]},0))')
            ws.cell(row=r, column=5, value="m²")
            ws.cell(row=r, column=6, value=f"='{S['name']}'!{scol}{S['rows'][id(p)]}")
            ws.cell(row=r, column=7, value=f'=INDEX({P["ratios"]},MATCH(C{r},{P["codes"]},0))')
            ws.cell(row=r, column=8, value="Oui")
            ws.cell(row=r, column=9, value=pu(r))
            ws.cell(row=r, column=10, value=f"=F{r}*I{r}")
            ligne(ws, r, 10, numcols=(6, 7, 9, 10), fmt={6: M2, 7: FCFA, 9: FCFA, 10: FCFA})
            ws.cell(row=r, column=8).alignment = Alignment(horizontal="center")
            saisie(ws.cell(row=r, column=8))
            r += 1
        sous_total(f"Sous-total {NIV[niv].lower()}", a, r - 1)
    for titre_s, liste in (("AMÉNAGEMENTS EXTÉRIEURS ET VRD", EXTERIEURS), ("PLUS-VALUES DU PARTI (matières, façade, toiture, végétal)", PLUS_VALUES)):
        ls = [lg for lg in liste if lg[4].get(cle, 0)]
        if not ls:
            continue
        section(titre_s)
        a = r
        for lg in ls:
            lib, unit, pu_, src, qtes, divise = lg
            ws.cell(row=r, column=1, value="Extérieurs / VRD" if liste is EXTERIEURS else "Plus-value")
            ws.cell(row=r, column=2, value=lib)
            ws.cell(row=r, column=4, value=src if not divise else f"{src} (base ÷ diviseur)")
            ws.cell(row=r, column=5, value=unit)
            ws.cell(row=r, column=6, value=qtes[cle])
            ws.cell(row=r, column=7, value=pu_)
            ws.cell(row=r, column=8, value="Oui" if divise else "Non")
            ws.cell(row=r, column=9, value=pu(r))
            ws.cell(row=r, column=10, value=f"=F{r}*I{r}")
            ligne(ws, r, 10, numcols=(6, 7, 9, 10), fmt={6: M2, 7: FCFA, 9: FCFA, 10: FCFA})
            ws.cell(row=r, column=2).alignment = Alignment(wrap_text=True, vertical="top")
            ws.cell(row=r, column=4).alignment = Alignment(wrap_text=True, vertical="top")
            ws.cell(row=r, column=8).alignment = Alignment(horizontal="center")
            for col in (6, 7, 8):
                saisie(ws.cell(row=r, column=col))
            r += 1
        sous_total("Sous-total", a, r - 1)
    # totaux
    ws.cell(row=r, column=2, value="TOTAL TRAVAUX HT")
    ws.cell(row=r, column=10, value="=" + "+".join(f"J{x}" for x in subs))
    ligne(ws, r, 10, "tot", numcols=(10,), fmt=FCFA)
    trav = r
    r += 1
    f0 = r
    for k, row_p in enumerate(P["frais_rows"]):
        ws.cell(row=r, column=2, value=f"=PARAMETRES!B{row_p}")
        ws.cell(row=r, column=8, value=f"=PARAMETRES!C{row_p}")
        ws.cell(row=r, column=8).number_format = PCT
        ws.cell(row=r, column=10, value=f"=H{r}*$J${trav}")
        ligne(ws, r, 10, numcols=(8, 10), fmt={8: PCT, 10: FCFA})
        r += 1
    ws.cell(row=r, column=2, value="Imprévus (stade esquisse)")
    ws.cell(row=r, column=8, value=f"={P['imp']}")
    ws.cell(row=r, column=10, value=f"=H{r}*$J${trav}")
    ligne(ws, r, 10, numcols=(8, 10), fmt={8: '0.0%', 10: FCFA})
    r += 1
    ws.cell(row=r, column=2, value="TOTAL GÉNÉRAL HT")
    ws.cell(row=r, column=10, value=f"=J{trav}+SUM(J{f0}:J{r - 1})")
    ligne(ws, r, 10, "tot", numcols=(10,), fmt=FCFA)
    ht = r
    r += 1
    ws.cell(row=r, column=2, value="TVA")
    ws.cell(row=r, column=8, value=f"={P['tva']}")
    ws.cell(row=r, column=10, value=f"=J{ht}*H{r}")
    ligne(ws, r, 10, numcols=(8, 10), fmt={8: '0%', 10: FCFA})
    tva = r
    r += 1
    ws.cell(row=r, column=2, value="TOTAL GÉNÉRAL TTC")
    ws.cell(row=r, column=10, value=f"=J{ht}+J{tva}")
    ligne(ws, r, 10, "tot", numcols=(10,), fmt=FCFA)
    ttc = r
    ws.freeze_panes = "A5"
    mise_en_page(ws, titre_)
    ws.print_title_rows = "4:4"
    return {"trav": f"'{nom}'!$J${trav}", "ht": f"'{nom}'!$J${ht}", "tva": f"'{nom}'!$J${tva}", "ttc": f"'{nom}'!$J${ttc}",
            "f0": f0, "name": nom, "imp_row": f0 + len(P["frais_rows"])}


# =============================================================================== SYNTHESE
def synthese(wb, SV, SD, EV, ED):
    ws = wb["SYNTHESE"]
    titre(ws, "LOT 1728 · RIVIERA PALMERAIE · OPTION C v5 : SURFACES ET ESTIMATIF",
          "Villa à patio (parcelle Nord) et 2 maisons duplex (parcelle Sud) · esquisse du 10.11.2026 · ratios Éco-données divisés par le coefficient.")
    entete(ws, 4, ["", "Villa à patio", "2 duplex (total)"], [56, 22, 22])
    lignes = [
        ("Surface close (m²)", f"={SV['refs'][2]}", f"={SD['refs'][2]}", M2),
        ("Emprise au sol bâtie (m²)", f"={SV['refs'][3]}", f"={SD['refs'][3]}", M2),
        ("Terrasses, loggia, balcon et préau hors clos (m²)", f"={SV['refs'][4]}", f"={SD['refs'][4]}", M2),
        ("Total travaux HT (FCFA)", f"={EV['trav']}", f"={ED['trav']}", FCFA),
        ("Honoraires, BET, géotechnique, contrôle, assurances (FCFA)",
         f"=SUM('{EV['name']}'!J{EV['f0']}:J{EV['imp_row'] - 1})", f"=SUM('{ED['name']}'!J{ED['f0']}:J{ED['imp_row'] - 1})", FCFA),
        ("Imprévus (FCFA)", f"='{EV['name']}'!J{EV['imp_row']}", f"='{ED['name']}'!J{ED['imp_row']}", FCFA),
        ("Total général HT (FCFA)", f"={EV['ht']}", f"={ED['ht']}", FCFA),
        ("TVA (FCFA)", f"={EV['tva']}", f"={ED['tva']}", FCFA),
        ("TOTAL GÉNÉRAL TTC (FCFA)", f"={EV['ttc']}", f"={ED['ttc']}", FCFA),
        ("Travaux HT par m² clos (FCFA)", "=B8/B5", "=C8/C5", FCFA),
        ("Total TTC en millions de FCFA", "=B13/1000000", "=C13/1000000", '#,##0.0'),
    ]
    for k, (lab, a, b, fm) in enumerate(lignes):
        r = 5 + k
        ws.cell(row=r, column=1, value=lab)
        ws.cell(row=r, column=2, value=a)
        ws.cell(row=r, column=3, value=b)
        kind = "tot" if lab.startswith("TOTAL") else ("sub" if lab.startswith("Total") else None)
        ligne(ws, r, 3, kind, numcols=(2, 3), fmt=fm)
    r = 5 + len(lignes) + 1
    notes = [
        "Hypothèses et limites",
        f"· Ratios par type de pièce : base Éco-données (Pavillon Akpo 2022, Résidences Anthurium 2021, Les Flamboyants, Villa Cacao 6), divisés par {DIVISEUR} sur consigne du client.",
        "· Postes hors base (clôture, façade bois, couverture à +9,00, mur végétalisé 3,50 m, pergola…) : prix de marché, hypothèses non divisées, à confirmer.",
        f"· Loyer d'un duplex retenu au business plan : {LOYERS['MD']['nu']:,} FCFA / mois (hypothèse à valider avec deux agences).".replace(",", " "),
        "· Le niveau couvert à +9,00 est un toit-terrasse ouvert : à faire valider au regard de la règle R+1 maximum.",
        "· Esquisse : quantités issues du modèle, à reprendre par le BET et l'économiste de la construction aux phases suivantes.",
        "· Cellules en bleu : saisies modifiables (surfaces, quantités, prix de base, indicateur « Divisé ? », paramètres).",
    ]
    for k, t in enumerate(notes):
        c = ws.cell(row=r + k, column=1, value=t)
        c.font = fnt(k == 0, HEAD if k == 0 else INK)
        c.alignment = Alignment(wrap_text=True, vertical="top")
        ws.merge_cells(start_row=r + k, start_column=1, end_row=r + k, end_column=3)
        ws.row_dimensions[r + k].height = 30 if k else 18
    mise_en_page(ws, "synthèse")


def build():
    wb = Workbook()
    wb.active.title = "SYNTHESE"
    P = parametres(wb)
    SV = surfaces_sheet(wb, "SURFACES VILLA", OPTION_C, "TABLEAU DES SURFACES · VILLA À PATIO")
    SD = surfaces_sheet(wb, "SURFACES DUPLEX", LOCATIF_M, "TABLEAU DES SURFACES · 2 MAISONS DUPLEX", par_maison=True)
    EV = estimatif_sheet(wb, "ESTIMATIF VILLA", OPTION_C, "C", "ESTIMATIF SOMMAIRE · VILLA À PATIO", SV, P)
    ED = estimatif_sheet(wb, "ESTIMATIF DUPLEX", LOCATIF_M, "M", "ESTIMATIF SOMMAIRE · 2 MAISONS DUPLEX", SD, P)
    synthese(wb, SV, SD, EV, ED)
    wb.move_sheet("PARAMETRES", offset=4)
    OUT.parent.mkdir(exist_ok=True)
    wb.save(OUT)
    print(OUT)


if __name__ == "__main__":
    build()
