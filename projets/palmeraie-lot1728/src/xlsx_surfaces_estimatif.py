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

from projet import (DIVISEUR_V5 as DIVISEUR, EXTERIEURS, FRAIS, IMPREVUS, LOCATIF_M, LOYERS, OPTION_C, PLUS_VALUES, RATIOS, TVA)

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
    ws["B4"], ws["B5"], ws["B6"] = "Coefficient diviseur des ratios Éco-données (recalage sur 450 000 FCFA / m² clos)", "TVA", "Imprévus (stade esquisse)"
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
    cles = {}
    pu = lambda row: f'=IF(H{row}="Oui",G{row}/{P["div"]},G{row})'      # noqa: E731

    def section(texte):
        nonlocal r
        ws.cell(row=r, column=1, value=texte)
        ligne(ws, r, 10, "sec")
        r += 1

    def sous_total(texte, a, b, cle_=None):
        nonlocal r
        ws.cell(row=r, column=2, value=texte)
        c = ws.cell(row=r, column=10, value=f"=SUM(J{a}:J{b})")
        ligne(ws, r, 10, "sub", numcols=(10,), fmt=FCFA)
        subs.append(r)
        if cle_:
            cles[cle_] = r
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
        sous_total(f"Sous-total {NIV[niv].lower()}", a, r - 1, niv)
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
        sous_total("Sous-total", a, r - 1, "ext" if liste is EXTERIEURS else "pv")
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
            "f0": f0, "name": nom, "imp_row": f0 + len(P["frais_rows"]), "sub": cles}


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
        f"· Ratios par type de pièce : base Éco-données (Pavillon Akpo 2022, Résidences Anthurium 2021, Les Flamboyants, Villa Cacao 6), divisés par {str(DIVISEUR).replace('.', ',')} (recalage sur l'objectif de 450 000 FCFA / m² clos, demande du client).",
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


# =============================================================================== COUT AU M2
def cout_m2(wb, SV, SD, EV, ED):
    ws = wb.create_sheet("COUT AU M2")
    titre(ws, "COÛT DE CONSTRUCTION AU M² · OPTION C v5",
          "Même estimatif que les onglets détaillés, exprimé au m² de surface close : surface × coût au m² = coût total.")
    for col, w in zip("ABCDEFG", (62, 18, 20, 20, 20, 20, 20)):
        ws.column_dimensions[col].width = w
    # ---- bloc 1 : coût au m² clos
    entete(ws, 4, ["COÛT AU M² DE SURFACE CLOSE", "Surface close (m²)", "Coût au m² (FCFA / m²)", "Total (FCFA)",
                   "Ordre de grandeur (FCFA / m², arrondi à 10 000)", "Écart avec l'estimatif détaillé (FCFA)"],
           [62, 18, 20, 20, 20, 20])
    ws.row_dimensions[4].height = 44
    lots = [("VILLA À PATIO", SV, EV), ("2 MAISONS DUPLEX", SD, ED)]
    r = 5
    cles_hl = {}
    for nom_lot, S, E in lots:
        ws.cell(row=r, column=1, value=nom_lot)
        ligne(ws, r, 6, "sec")
        r += 1
        for lab, src in (("Travaux HT, construction seule (pièces, extérieurs, plus-values)", E["trav"]),
                         ("Total HT, avec honoraires, BET, contrôle, assurances et imprévus", E["ht"]),
                         ("TOTAL TTC", E["ttc"])):
            kind = "tot" if lab.startswith("TOTAL") else None
            ws.cell(row=r, column=1, value=lab)
            ws.cell(row=r, column=2, value=f"={S['refs'][2]}")
            ws.cell(row=r, column=3, value=f"={src}/B{r}")
            ws.cell(row=r, column=4, value=f"=B{r}*C{r}")
            ws.cell(row=r, column=5, value=f"=ROUND(C{r},-4)")
            ws.cell(row=r, column=6, value=f"=ROUND(D{r}-{src},0)")
            ligne(ws, r, 6, kind, numcols=(2, 3, 4, 5, 6), fmt={2: M2, 3: FCFA, 4: FCFA, 5: FCFA, 6: FCFA})
            cles_hl[(nom_lot, lab[:5])] = r
            r += 1
    r += 1
    # ---- bloc 2 : decomposition
    ws.cell(row=r, column=1, value="DÉCOMPOSITION DU COÛT AU M² CLOS (la somme des lignes redonne le total)").font = fnt(True, HEAD)
    r += 1
    labels = ["Poste", "Villa : total (FCFA)", "Villa : FCFA / m² clos", "Villa : % du TTC",
              "Duplex : total (FCFA)", "Duplex : FCFA / m² clos", "Duplex : % du TTC"]
    for i, lab in enumerate(labels, 1):
        c = ws.cell(row=r, column=i, value=lab)
        c.font = fnt(True, "FFFFFF")
        c.fill = PatternFill("solid", fgColor=HEAD)
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = BORDER
    ws.row_dimensions[r].height = 32
    r += 1
    surf_v, surf_d = SV["refs"][2], SD["refs"][2]
    postes = [("Pièces du rez-de-chaussée", "RDC"), ("Pièces de l'étage", "R+1"), ("Niveau haut (toit-terrasse, édicule, jardinière)", "TOIT"),
              ("Aménagements extérieurs et VRD", "ext"), ("Plus-values du parti (façade bois, couverture, mur végétalisé…)", "pv")]
    first = r
    for lab, cle in postes:
        ws.cell(row=r, column=1, value=lab)
        for col0, E in ((2, EV), (5, ED)):
            ref = f"='{E['name']}'!J{E['sub'][cle]}"
            ws.cell(row=r, column=col0, value=ref)
        r += 1
    last_post = r - 1
    rows_after = [("Total travaux HT", "sub", lambda L: f"=SUM({L}{first}:{L}{last_post})"),
                  ("Honoraires, BET, géotechnique, contrôle, assurances", None,
                   lambda L, E=None: None),
                  ("Imprévus (stade esquisse)", None, None),
                  ("Total HT", "sub", None), ("TVA", None, None), ("TOTAL TTC", "tot", None)]
    # lignes finales construites explicitement
    r_trav = r
    ws.cell(row=r, column=1, value="Total travaux HT")
    ws.cell(row=r, column=2, value=f"=SUM(B{first}:B{last_post})")
    ws.cell(row=r, column=5, value=f"=SUM(E{first}:E{last_post})")
    r += 1
    ws.cell(row=r, column=1, value="Honoraires, BET, géotechnique, contrôle, assurances")
    ws.cell(row=r, column=2, value=f"=SUM('{EV['name']}'!J{EV['f0']}:J{EV['imp_row'] - 1})")
    ws.cell(row=r, column=5, value=f"=SUM('{ED['name']}'!J{ED['f0']}:J{ED['imp_row'] - 1})")
    r += 1
    ws.cell(row=r, column=1, value="Imprévus (stade esquisse)")
    ws.cell(row=r, column=2, value=f"='{EV['name']}'!J{EV['imp_row']}")
    ws.cell(row=r, column=5, value=f"='{ED['name']}'!J{ED['imp_row']}")
    r += 1
    r_ht = r
    ws.cell(row=r, column=1, value="Total HT")
    ws.cell(row=r, column=2, value=f"=SUM(B{r_trav}:B{r - 1})")
    ws.cell(row=r, column=5, value=f"=SUM(E{r_trav}:E{r - 1})")
    r += 1
    ws.cell(row=r, column=1, value="TVA")
    ws.cell(row=r, column=2, value=f"={EV['tva']}")
    ws.cell(row=r, column=5, value=f"={ED['tva']}")
    r += 1
    r_ttc = r
    ws.cell(row=r, column=1, value="TOTAL TTC")
    ws.cell(row=r, column=2, value=f"=B{r_ht}+B{r - 1}")
    ws.cell(row=r, column=5, value=f"=E{r_ht}+E{r - 1}")
    for rr in range(first, r_ttc + 1):
        ws.cell(row=rr, column=3, value=f"=B{rr}/{surf_v}")
        ws.cell(row=rr, column=6, value=f"=E{rr}/{surf_d}")
        ws.cell(row=rr, column=4, value=f"=B{rr}/B${r_ttc}")
        ws.cell(row=rr, column=7, value=f"=E{rr}/E${r_ttc}")
        kind = "tot" if rr == r_ttc else ("sub" if rr in (r_trav, r_ht) else None)
        ligne(ws, rr, 7, kind, numcols=(2, 3, 4, 5, 6, 7), fmt={2: FCFA, 3: FCFA, 4: '0.0%', 5: FCFA, 6: FCFA, 7: '0.0%'})
    r = r_ttc + 2
    ws.cell(row=r, column=1, value="Contrôle : total TTC de la décomposition moins total TTC de l'estimatif détaillé (doit être 0)")
    ws.cell(row=r, column=2, value=f"=ROUND(B{r_ttc}-{EV['ttc']},0)")
    ws.cell(row=r, column=5, value=f"=ROUND(E{r_ttc}-{ED['ttc']},0)")
    for col in (1, 2, 5):
        ws.cell(row=r, column=col).font = fnt(italic=True)
        ws.cell(row=r, column=col).number_format = FCFA
    r += 2
    notes = [
        "Lecture et limites",
        "· Le coût au m² est rapporté à la surface close (rez-de-chaussée et étage fermés). Les terrasses, la loggia, le toit-terrasse couvert, le patio, "
        "les jardins, la clôture et les plus-values de façade sont dans le coût mais pas dans la surface : le coût au m² est donc un coût tout compris, "
        "plutôt haut si on le compare à un ratio de bâti seul.",
        "· Pour réutiliser ces ratios sur un autre projet, prendre la ligne « Travaux HT » (construction seule) et y ajouter les frais et imprévus "
        "(24,05 % des travaux : 14,05 % de frais et 10 % d'imprévus) puis la TVA (18 %).",
        "· Les ratios Éco-données sont divisés par le coefficient de l'onglet PARAMETRES (voir RECALAGE 450K) ; les postes hors base sont des prix de marché non divisés, à confirmer.",
        "· Esquisse : les quantités viennent du modèle et restent à reprendre par le BET structure et l'économiste de la construction avant tout engagement.",
    ]
    for k, t in enumerate(notes):
        c = ws.cell(row=r + k, column=1, value=t)
        c.font = fnt(k == 0, HEAD if k == 0 else INK)
        c.alignment = Alignment(wrap_text=True, vertical="top")
        ws.merge_cells(start_row=r + k, start_column=1, end_row=r + k, end_column=7)
        ws.row_dimensions[r + k].height = 18 if k == 0 else 32
    ws.freeze_panes = "A5"
    mise_en_page(ws, "coût au m²")
    return ws


# =============================================================================== RECALAGE
# Valeurs figees, calculees le 14-11-2026 en appliquant les etapes dans l'ordre sur l'estimatif precedent (ratios / 2).
RECALAGE = {
    "C": [("Estimatif précédent (ratios Éco-données ÷ 2)", 193663038, 704332),
          ("1 · Toit-terrasse chiffré en finition seule (la dalle est déjà comptée sous l'étage)", 185386788, 674232),
          ("2 · Plus-values re-spécifiées (bois local, couverture légère, mur galvanisé, patio) et doublons retirés", 173131788, 629662),
          ("3 · Finition standard des pièces secondaires de la villa (SE, WC, lingerie, rangement)", 167229288, 608195),
          ("4 · Coefficient diviseur des ratios de ÷ 2 à ÷ 3", 125832859, 457641)],
    "M": [("Estimatif précédent (ratios Éco-données ÷ 2)", 171769038, 561337),
          ("1 · Toit-terrasse chiffré en finition seule (la dalle est déjà comptée sous l'étage)", 161644038, 528248),
          ("2 · Plus-values re-spécifiées (bois local, couverture légère, mur galvanisé, patio) et doublons retirés", 152904038, 499686),
          ("3 · Finition standard des pièces secondaires de la villa (SE, WC, lingerie, rangement)", 152904038, 499686),
          ("4 · Coefficient diviseur des ratios de ÷ 2 à ÷ 3", 112227692, 366757)],
}


def recalage(wb):
    ws = wb.create_sheet("RECALAGE 450K")
    titre(ws, "RECALAGE DU COÛT SUR L'OBJECTIF DE 450 000 FCFA / M² CLOS",
          "Travaux HT (construction seule), par étape, à partir de l'estimatif précédent. Valeurs figées au 14-11-2026 ; "
          "les onglets d'estimatif et le coût au m² sont, eux, recalculés en direct.")
    entete(ws, 4, ["Étape", "Villa : travaux HT (FCFA)", "Villa : FCFA / m² clos", "Duplex : travaux HT (FCFA)", "Duplex : FCFA / m² clos",
                   "Villa : gain de l'étape (FCFA / m²)", "Duplex : gain de l'étape (FCFA / m²)"], [88, 22, 20, 22, 20, 22, 22])
    ws.row_dimensions[4].height = 44
    for k, ((lab, tc, pc), (_, tm, pm)) in enumerate(zip(RECALAGE["C"], RECALAGE["M"])):
        r = 5 + k
        ws.cell(row=r, column=1, value=lab)
        ws.cell(row=r, column=2, value=tc)
        ws.cell(row=r, column=3, value=pc)
        ws.cell(row=r, column=4, value=tm)
        ws.cell(row=r, column=5, value=pm)
        if k:
            ws.cell(row=r, column=6, value=f"=C{r - 1}-C{r}")
            ws.cell(row=r, column=7, value=f"=E{r - 1}-E{r}")
        ligne(ws, r, 7, "sub" if k in (0, 4) else None, numcols=(2, 3, 4, 5, 6, 7), fmt=FCFA)
        ws.cell(row=r, column=1).alignment = Alignment(wrap_text=True, vertical="top")
    r = 11
    ws.cell(row=r, column=1, value="Objectif du client : environ 450 000 FCFA / m² de surface close (travaux HT)")
    ws.cell(row=r, column=3, value=450000)
    ws.cell(row=r, column=5, value=450000)
    ligne(ws, r, 7, "tot", numcols=(3, 5), fmt=FCFA)
    r += 2
    notes = [
        "Ce qu'il faut retenir",
        "· Les étapes 1 à 3 sont des corrections de méthode et des choix de spécification : elles font passer la villa de 704 000 à 608 000 FCFA / m² et les duplex de 561 000 à 500 000. "
        "Elles ne suffisent pas à atteindre l'objectif.",
        "· L'étape 4 est un recalage : les ratios de la base Éco-données sont divisés par 3 au lieu de 2. C'est le levier principal (environ 60 % de la baisse sur la villa). "
        "Il fixe un niveau de prix, il ne le mesure pas : une consultation de deux ou trois entreprises ivoiriennes sur le même descriptif est nécessaire pour le confirmer.",
        "· Conséquences sur le niveau de finition : pièces d'eau et circulations de la villa en finition standard, peau de façade en bois local, couverture à +9,00 en structure légère "
        "(la dalle mince en béton de la variante V1 est à chiffrer en plus), mur végétalisé en treillis galvanisé, moellons limités au socle de clôture.",
        "· Les duplex tombent plus bas que la villa (367 000 contre 458 000) : bâtiment compact, répété, en finition locative. Pour les ramener vers 450 000, on peut y remonter les finitions.",
        "· Les honoraires, le contrôle et les imprévus (24,05 % des travaux) et la TVA (18 %) viennent en plus : voir l'onglet COUT AU M2.",
    ]
    for k, t in enumerate(notes):
        c = ws.cell(row=r + k, column=1, value=t)
        c.font = fnt(k == 0, HEAD if k == 0 else INK)
        c.alignment = Alignment(wrap_text=True, vertical="top")
        ws.merge_cells(start_row=r + k, start_column=1, end_row=r + k, end_column=7)
        ws.row_dimensions[r + k].height = 18 if k == 0 else 46
    mise_en_page(ws, "recalage")
    return ws


def build():
    wb = Workbook()
    wb.active.title = "SYNTHESE"
    P = parametres(wb)
    SV = surfaces_sheet(wb, "SURFACES VILLA", OPTION_C, "TABLEAU DES SURFACES · VILLA À PATIO")
    SD = surfaces_sheet(wb, "SURFACES DUPLEX", LOCATIF_M, "TABLEAU DES SURFACES · 2 MAISONS DUPLEX", par_maison=True)
    EV = estimatif_sheet(wb, "ESTIMATIF VILLA", OPTION_C, "C", "ESTIMATIF SOMMAIRE · VILLA À PATIO", SV, P)
    ED = estimatif_sheet(wb, "ESTIMATIF DUPLEX", LOCATIF_M, "M", "ESTIMATIF SOMMAIRE · 2 MAISONS DUPLEX", SD, P)
    synthese(wb, SV, SD, EV, ED)
    cout_m2(wb, SV, SD, EV, ED)
    recalage(wb)
    ordre = ["SYNTHESE", "COUT AU M2", "RECALAGE 450K", "SURFACES VILLA", "SURFACES DUPLEX", "ESTIMATIF VILLA", "ESTIMATIF DUPLEX"]
    wb._sheets = [wb[n] for n in ordre] + [wb["PARAMETRES"]]
    wb.move_sheet("PARAMETRES", offset=len(wb.sheetnames))
    OUT.parent.mkdir(exist_ok=True)
    wb.save(OUT)
    print(OUT)


if __name__ == "__main__":
    build()
