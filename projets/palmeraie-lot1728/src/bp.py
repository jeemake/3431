"""Business plan de l'investissement locatif (calcul Python + classeur XLSX a formules)."""
import pathlib
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.workbook.defined_name import DefinedName

from projet import LOCATIF, LOYERS, OPTION_B, budget, surfaces

OUT = pathlib.Path(__file__).resolve().parent.parent / "out"
HORIZON = 15

BL = budget(LOCATIF)
BV = budget(OPTION_B)

H = {  # hypotheses (nom: (valeur, libelle, format))
    "cout_loc_ttc": (BL["total_ttc"], "Cout du batiment locatif TTC (estimatif, prix / 2)", "num"),
    "frais_annexes": (3_500_000, "Permis, frais administratifs, raccordement, mise en location", "num"),
    "foncier_m2": (150_000, "Valeur du foncier (hypothese a confirmer), FCFA / m2", "num"),
    "foncier_surf": (300, "Surface de la parcelle locative (m2)", "num"),
    "nb_2p": (4, "Nombre de 2 pieces (48,6 m2)", "int"),
    "nb_t1": (2, "Nombre de T1 bis (32,4 m2)", "int"),
    "l2p_nu": (LOYERS["2P"]["nu"], "Loyer mensuel 2 pieces nu", "num"),
    "lt1_nu": (LOYERS["T1bis"]["nu"], "Loyer mensuel T1 bis nu", "num"),
    "l2p_mb": (LOYERS["2P"]["meuble"], "Loyer mensuel 2 pieces meuble (moyenne duree)", "num"),
    "lt1_mb": (LOYERS["T1bis"]["meuble"], "Loyer mensuel T1 bis meuble (moyenne duree)", "num"),
    "nuit_2p": (LOYERS["2P"]["nuit"], "Nuitee 2 pieces (courte duree)", "num"),
    "nuit_t1": (LOYERS["T1bis"]["nuit"], "Nuitee T1 bis (courte duree)", "num"),
    "mob_2p": (4_500_000, "Mobilier + equipement par 2 pieces", "num"),
    "mob_t1": (3_000_000, "Mobilier + equipement par T1 bis", "num"),
    "index_loyer": (0.02, "Indexation annuelle des loyers", "pct"),
    "index_charges": (0.03, "Indexation annuelle des charges fixes", "pct"),
    "assurance": (0.0015, "Assurance proprietaire (% du cout de construction / an)", "pct"),
    "gardien": (1_200_000, "Gardiennage + entretien des parties communes (FCFA / an)", "num"),
    "cap_rate": (0.10, "Taux de capitalisation pour la valeur de sortie (annee 15)", "pct"),
    "actualisation": (0.10, "Taux d'actualisation (VAN)", "pct"),
    "ltv": (0.60, "Part financee par credit (du cout de construction TTC)", "pct"),
    "taux": (0.085, "Taux du credit immobilier", "pct"),
    "duree": (15, "Duree du credit (ans)", "int"),
}

# Scenarios : occupation stabilisee, occupation an 1, % de charges variables, provision mobilier
SCEN = {
    "S1": {"nom": "Location nue longue duree", "occ": 0.92, "occ1": 0.70, "gestion": 0.10,
           "charges": 0.00, "plateforme": 0.00, "entretien": 0.05, "fisc": 0.07, "prov_mob": 0.0,
           "meuble": False},
    "S2": {"nom": "Meuble moyenne duree (1 a 6 mois)", "occ": 0.85, "occ1": 0.65, "gestion": 0.10,
           "charges": 0.12, "plateforme": 0.00, "entretien": 0.05, "fisc": 0.07, "prov_mob": 0.10,
           "meuble": True},
    "S4": {"nom": "Location nue, montage optimise", "occ": 0.92, "occ1": 0.70, "gestion": 0.00,
           "charges": 0.00, "plateforme": 0.00, "entretien": 0.05, "fisc": 0.07, "prov_mob": 0.0,
           "meuble": False, "cout": round(BL["total_ht"] - 0.08 * BL["travaux"]), "part_gardien": 0.5},
    "S3": {"nom": "Courte duree (plateformes)", "occ": 0.55, "occ1": 0.40, "gestion": 0.20,
           "charges": 0.18, "plateforme": 0.15, "entretien": 0.05, "fisc": 0.10, "prov_mob": 0.15,
           "meuble": True},
}


SCEN = {k: SCEN[k] for k in ("S1", "S4", "S2", "S3")}


def cout(s):
    return SCEN[s].get("cout", v("cout_loc_ttc"))


def v(k):
    return H[k][0]


def potentiel(s):
    if s in ("S1", "S4"):
        return 12 * (v("nb_2p") * v("l2p_nu") + v("nb_t1") * v("lt1_nu"))
    if s == "S2":
        return 12 * (v("nb_2p") * v("l2p_mb") + v("nb_t1") * v("lt1_mb"))
    return 365 * (v("nb_2p") * v("nuit_2p") + v("nb_t1") * v("nuit_t1"))


def mobilier(s):
    return (v("nb_2p") * v("mob_2p") + v("nb_t1") * v("mob_t1")) if SCEN[s]["meuble"] else 0


def irr(cfs, lo=-0.99, hi=1.0):
    def npv(r):
        return sum(c / (1 + r) ** t for t, c in enumerate(cfs))
    for _ in range(200):
        mid = (lo + hi) / 2
        if npv(mid) > 0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def pmt(rate, n, pv):
    return pv * rate / (1 - (1 + rate) ** -n)


def calc(s, foncier=False, levier=False):
    p = SCEN[s]
    invest = cout(s) + v("frais_annexes") + mobilier(s)
    var = p["gestion"] + p["charges"] + p["plateforme"] + p["entretien"] + p["fisc"]
    rows = []
    loan = v("ltv") * cout(s) if levier else 0
    ann = pmt(v("taux"), v("duree"), loan) if levier else 0
    cf = [-(invest - loan) - (v("foncier_m2") * v("foncier_surf") if foncier else 0)]
    for t in range(1, HORIZON + 1):
        occ = p["occ1"] if t == 1 else p["occ"]
        rev = potentiel(s) * (1 + v("index_loyer")) ** (t - 1) * occ
        fixe = (v("assurance") * cout(s) + p.get("part_gardien", 1.0) * v("gardien")
                + p["prov_mob"] * mobilier(s)) * (1 + v("index_charges")) ** (t - 1)
        noi = rev * (1 - var) - fixe
        debt = ann if (levier and t <= v("duree")) else 0
        flux = noi - debt
        if t == HORIZON and levier and v("duree") > HORIZON:
            k = v("duree") - HORIZON
            flux -= ann * (1 - (1 + v("taux")) ** -k) / v("taux")  # capital restant du
        if t == HORIZON:
            noi_next = potentiel(s) * (1 + v("index_loyer")) ** t * p["occ"] * (1 - var) - fixe * (1 + v("index_charges"))
            flux += noi_next / v("cap_rate")
        rows.append({"t": t, "rev": rev, "noi": noi, "debt": debt, "flux": flux})
        cf.append(flux)
    noi2 = rows[1]["noi"]
    cum, payback = cf[0], None
    for t in range(1, HORIZON + 1):
        prev = cum
        cum += rows[t - 1]["noi"] - rows[t - 1]["debt"]
        if payback is None and cum >= 0:
            payback = t - 1 + (-prev) / (rows[t - 1]["noi"] - rows[t - 1]["debt"])
    return {
        "invest": invest, "potentiel": potentiel(s), "noi_stab": noi2,
        "rdt_brut": potentiel(s) * p["occ"] / invest, "rdt_net": noi2 / invest,
        "tri": irr(cf), "van": sum(c / (1 + v("actualisation")) ** t for t, c in enumerate(cf)),
        "payback": payback, "rows": rows, "loan": loan, "annuite": ann,
        "dscr": (noi2 / ann) if ann else None, "cf": cf,
    }


def sensibilite():
    """TRI S1 selon la base de cout, le niveau de loyer et la duree du credit."""
    base = dict((k, H[k]) for k in H)
    archi = 0.08 * BL["travaux"]
    couts = {
        "Prix base non divisés (TTC)": budget(LOCATIF, div=1)["total_ttc"],
        "TTC, entreprises assujetties": BL["total_ttc"],
        "HT (lots, artisans non assujettis)": BL["total_ht"],
        "HT sans honoraires architecte": BL["total_ht"] - archi,
    }
    out = {"couts": couts, "grille": {}, "credit": {}}
    for lab, cout in couts.items():
        for dl in (-0.10, 0.0, 0.10):
            H["cout_loc_ttc"] = (cout,) + base["cout_loc_ttc"][1:]
            H["l2p_nu"] = (base["l2p_nu"][0] * (1 + dl),) + base["l2p_nu"][1:]
            H["lt1_nu"] = (base["lt1_nu"][0] * (1 + dl),) + base["lt1_nu"][1:]
            r = calc("S1")
            out["grille"][(lab, dl)] = (r["tri"], r["rdt_net"])
        H.update(base)
    for d in (10, 15, 20):
        H["duree"] = (d,) + base["duree"][1:]
        r = calc("S4", levier=True)
        out["credit"][d] = (r["annuite"], r["dscr"], r["tri"])
    H.update(base)
    return out


def cibles(tri=0.10):
    """Cout de construction maximal et loyers minimaux pour atteindre un TRI cible (S1, sans credit)."""
    base = dict(H)
    lo, hi = 10e6, 400e6
    for _ in range(80):
        mid = (lo + hi) / 2
        H["cout_loc_ttc"] = (mid,) + base["cout_loc_ttc"][1:]
        lo, hi = (mid, hi) if calc("S1")["tri"] > tri else (lo, mid)
    cout = lo
    H.update(base)
    lo, hi = 0.5, 3.0
    for _ in range(80):
        mid = (lo + hi) / 2
        H["l2p_nu"] = (base["l2p_nu"][0] * mid,) + base["l2p_nu"][1:]
        H["lt1_nu"] = (base["lt1_nu"][0] * mid,) + base["lt1_nu"][1:]
        lo, hi = (lo, mid) if calc("S1")["tri"] > tri else (mid, hi)
    mult = hi
    H.update(base)
    return {"cout": cout, "cout_m2": cout / surfaces(LOCATIF)["clos"], "mult_loyer": mult,
            "l2p": base["l2p_nu"][0] * mult, "lt1": base["lt1_nu"][0] * mult}


# ---------------------------------------------------------------------------- XLSX
INK, HEAD, SUB = "23262B", "2F4A6D", "EEF1F5"
thin = Side(style="thin", color="C9C3B8")
BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)
NUM = '#,##0;[Red]-#,##0'


def fnt(b=False, c=INK, s=10, i=False):
    return Font(name="Calibri", bold=b, color=c, size=s, italic=i)


def hdr(ws, row, labels, widths):
    for i, lab in enumerate(labels, 1):
        c = ws.cell(row=row, column=i, value=lab)
        c.font = fnt(True, "FFFFFF")
        c.fill = PatternFill("solid", fgColor=HEAD)
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = BORDER
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w


def cell(ws, r, c, val, fmt=None, bold=False, fill=None, color=INK):
    x = ws.cell(row=r, column=c, value=val)
    x.font = fnt(bold, color)
    x.border = BORDER
    if fmt == "num":
        x.number_format = NUM
    elif fmt == "pct":
        x.number_format = "0.0%"
    elif fmt == "int":
        x.number_format = "0"
    elif fmt == "dec":
        x.number_format = "0.00"
    if fill:
        x.fill = PatternFill("solid", fgColor=fill)
    return x


def build_xlsx():
    wb = Workbook()
    hy = wb.active
    hy.title = "HYPOTHESES"
    hy["A1"] = "BUSINESS PLAN - BATIMENT LOCATIF R+1 (6 logements) - LOT 1728 RIVIERA PALMERAIE"
    hy["A1"].font = fnt(True, HEAD, 12)
    hy["A2"] = "Cellules jaunes = hypotheses modifiables. Montants en FCFA."
    hy["A2"].font = fnt(i=True)
    hdr(hy, 4, ["CLE", "HYPOTHESE", "VALEUR"], [16, 62, 18])
    r = 5
    for k, (val, lib, fmt) in H.items():
        cell(hy, r, 1, k)
        cell(hy, r, 2, lib)
        cell(hy, r, 3, val, fmt, fill="FFF4D6")
        wb.defined_names.add(DefinedName(k, attr_text=f"HYPOTHESES!$C${r}"))
        r += 1
    r += 1
    hy.cell(row=r, column=2, value="SCENARIOS D'EXPLOITATION").font = fnt(True, HEAD)
    r += 1
    hdr_row = r
    labels = ["", "PARAMETRE"] + [SCEN[s]["nom"] for s in SCEN]
    hy.column_dimensions["F"].width = 18
    for i, lab in enumerate(labels, 1):
        c = hy.cell(row=r, column=i, value=lab)
        c.font = fnt(True, "FFFFFF")
        c.fill = PatternFill("solid", fgColor=HEAD)
        c.alignment = Alignment(wrap_text=True, horizontal="center")
        c.border = BORDER
    hy.column_dimensions["D"].width = 18
    hy.column_dimensions["E"].width = 18
    hy.row_dimensions[r].height = 32
    r += 1
    params = [("occ", "Taux d'occupation stabilise"), ("occ1", "Taux d'occupation annee 1"),
              ("gestion", "Gestion / conciergerie (% revenus)"), ("charges", "Charges incluses (energie, eau, internet, menage)"),
              ("plateforme", "Commission plateforme"), ("entretien", "Entretien courant"),
              ("fisc", "Fiscalite fonciere (hyp. a valider)"), ("prov_mob", "Provision renouvellement mobilier (% mobilier / an)")]
    prow = {}
    for key, lib in params:
        cell(hy, r, 2, lib)
        for j, s in enumerate(SCEN):
            cell(hy, r, 3 + j, SCEN[s][key], "pct", fill="FFF4D6")
        prow[key] = r
        r += 1
    cell(hy, r, 2, "Part du gardiennage supportee par le locatif")
    for j, s in enumerate(SCEN):
        cell(hy, r, 3 + j, SCEN[s].get("part_gardien", 1.0), "pct", fill="FFF4D6")
    prow["part_gardien"] = r
    r += 1
    cell(hy, r, 2, "Cout de construction retenu (TTC ou HT selon montage)", bold=True)
    for j, s in enumerate(SCEN):
        cell(hy, r, 3 + j, SCEN[s]["cout"] if "cout" in SCEN[s] else "=cout_loc_ttc", "num", True, fill="FFF4D6")
    prow["cout"] = r
    r += 1
    # potentiel et mobilier par scenario
    pot = {"S1": "=12*(nb_2p*l2p_nu+nb_t1*lt1_nu)", "S4": "=12*(nb_2p*l2p_nu+nb_t1*lt1_nu)",
           "S2": "=12*(nb_2p*l2p_mb+nb_t1*lt1_mb)", "S3": "=365*(nb_2p*nuit_2p+nb_t1*nuit_t1)"}
    cell(hy, r, 2, "Revenu locatif potentiel annuel (100 % occupation)", bold=True)
    for j, s in enumerate(SCEN):
        cell(hy, r, 3 + j, pot[s], "num", True)
    prow["pot"] = r
    r += 1
    cell(hy, r, 2, "Mobilier et equipement (investissement initial)", bold=True)
    for j, s in enumerate(SCEN):
        cell(hy, r, 3 + j, "=nb_2p*mob_2p+nb_t1*mob_t1" if SCEN[s]["meuble"] else 0, "num", True)
    prow["mob"] = r
    r += 1
    cell(hy, r, 2, "Total charges variables (% revenus)", bold=True)
    for j in range(len(SCEN)):
        L = get_column_letter(3 + j)
        cell(hy, r, 3 + j, f"={L}{prow['gestion']}+{L}{prow['charges']}+{L}{prow['plateforme']}"
             f"+{L}{prow['entretien']}+{L}{prow['fisc']}", "pct", True)
    prow["var"] = r

    # ---------------------------------------------------------------- CF par scenario
    synth = {}
    for j, s in enumerate(SCEN):
        col = get_column_letter(3 + j)
        ref = lambda key: f"HYPOTHESES!${col}${prow[key]}"  # noqa: E731
        ws = wb.create_sheet(f"CF {s}")
        ws["A1"] = f"FLUX DE TRESORERIE - {s} : {SCEN[s]['nom']}"
        ws["A1"].font = fnt(True, HEAD, 12)
        hdr(ws, 3, ["POSTE"] + [f"An {t}" for t in range(0, HORIZON + 1)], [40] + [13] * (HORIZON + 1))
        lines = ["Investissement (construction + frais + mobilier)", "Revenus locatifs encaisses",
                 "Charges variables", "Charges fixes (assurance, gardien, provision mobilier)", "Resultat d'exploitation (NOI)",
                 "Valeur de sortie (NOI an 16 / taux de capitalisation)", "FLUX NET - sans credit",
                 "Credit : versement initial", "Credit : annuites (+ solde a l'an 15)", "FLUX NET - avec credit",
                 "Foncier (apport valorise)", "FLUX NET - foncier valorise (sans credit)"]
        R0 = 4
        for i, lab in enumerate(lines):
            cell(ws, R0 + i, 1, lab, bold=lab.startswith("FLUX") or lab.startswith("Resultat"))
        rI, rRev, rVar, rFix, rNoi, rVs, rF1, rLoan, rAnn, rF2, rLand, rF3 = range(R0, R0 + 12)
        for t in range(0, HORIZON + 1):
            c = 2 + t
            L = get_column_letter(c)
            if t == 0:
                cell(ws, rI, c, f"=-({ref('cout')}+frais_annexes+{ref('mob')})", "num")
                for rr in (rRev, rVar, rFix, rNoi, rVs, rAnn):
                    cell(ws, rr, c, 0, "num")
                cell(ws, rLoan, c, f"=ltv*{ref('cout')}", "num")
                cell(ws, rLand, c, "=-foncier_m2*foncier_surf", "num")
            else:
                cell(ws, rI, c, 0, "num")
                occ = ref("occ1") if t == 1 else ref("occ")
                cell(ws, rRev, c, f"={ref('pot')}*(1+index_loyer)^({t}-1)*{occ}", "num")
                cell(ws, rVar, c, f"=-{L}{rRev}*{ref('var')}", "num")
                cell(ws, rFix, c, f"=-(assurance*{ref('cout')}+{ref('part_gardien')}*gardien+{ref('prov_mob')}*{ref('mob')})"
                     f"*(1+index_charges)^({t}-1)", "num")
                cell(ws, rNoi, c, f"={L}{rRev}+{L}{rVar}+{L}{rFix}", "num", True)
                if t == HORIZON:
                    cell(ws, rVs, c, f"=({ref('pot')}*(1+index_loyer)^{t}*{ref('occ')}*(1-{ref('var')})"
                         f"+{L}{rFix}*(1+index_charges))/cap_rate", "num")
                else:
                    cell(ws, rVs, c, 0, "num")
                cell(ws, rLoan, c, 0, "num")
                solde = (f"-IF(duree>{HORIZON},PV(taux,duree-{HORIZON},-PMT(taux,duree,-ltv*{ref('cout')})),0)"
                         if t == HORIZON else "")
                cell(ws, rAnn, c, f"=IF({t}<=duree,PMT(taux,duree,-ltv*{ref('cout')}),0)*-1{solde}", "num")
                cell(ws, rLand, c, 0, "num")
            cell(ws, rF1, c, f"={L}{rI}+{L}{rNoi}+{L}{rVs}", "num", True, SUB)
            cell(ws, rF2, c, f"={L}{rF1}+{L}{rLoan}+{L}{rAnn}", "num", True, SUB)
            cell(ws, rF3, c, f"={L}{rF1}+{L}{rLand}", "num", True, SUB)
        last = get_column_letter(2 + HORIZON)
        k = R0 + 13
        ind = [("TRI sans credit (15 ans)", f"=IRR(B{rF1}:{last}{rF1})", "pct"),
               ("TRI avec credit", f"=IRR(B{rF2}:{last}{rF2})", "pct"),
               ("TRI foncier valorise", f"=IRR(B{rF3}:{last}{rF3})", "pct"),
               ("VAN sans credit", f"=B{rF1}+NPV(actualisation,C{rF1}:{last}{rF1})", "num"),
               ("Rendement brut (revenu a occupation stabilisee / investissement)",
                f"={ref('pot')}*{ref('occ')}/-B{rI}", "pct"),
               ("Rendement net (NOI an 2 / investissement)", f"=D{rNoi}/-B{rI}", "pct"),
               ("Couverture de la dette (NOI an 2 / annuite)", f"=D{rNoi}/-D{rAnn}", "dec")]
        for i, (lab, frm, fm) in enumerate(ind):
            cell(ws, k + i, 1, lab, bold=True)
            cell(ws, k + i, 2, frm, fm, True, "FFF4D6")
        synth[s] = {"sheet": ws.title, "rows": {lab: k + i for i, (lab, _, _) in enumerate(ind)},
                    "inv": f"B{rI}", "noi": f"D{rNoi}"}
        ws.freeze_panes = "B4"
        ws.page_setup.orientation = "landscape"
        ws.sheet_properties.pageSetUpPr.fitToPage = True

    # ---------------------------------------------------------------- SYNTHESE
    sy = wb.create_sheet("SYNTHESE", 0)
    sy["A1"] = "SYNTHESE - INVESTISSEMENT LOCATIF LOT 1728 (Riviera Palmeraie)"
    sy["A1"].font = fnt(True, HEAD, 12)
    hdr(sy, 3, ["INDICATEUR"] + [SCEN[s]["nom"] for s in SCEN], [52, 22, 22, 22, 22])
    sy.row_dimensions[3].height = 32
    r = 4
    cell(sy, r, 1, "Investissement total (hors foncier)", bold=True)
    for j, s in enumerate(SCEN):
        cell(sy, r, 2 + j, f"=-'{synth[s]['sheet']}'!{synth[s]['inv']}", "num")
    r += 1
    cell(sy, r, 1, "Resultat d'exploitation stabilise (NOI an 2)", bold=True)
    for j, s in enumerate(SCEN):
        cell(sy, r, 2 + j, f"='{synth[s]['sheet']}'!{synth[s]['noi']}", "num")
    r += 1
    for lab in synth["S1"]["rows"]:
        cell(sy, r, 1, lab, bold=True)
        for j, s in enumerate(SCEN):
            fm = "dec" if "Couverture" in lab else ("num" if "VAN" in lab else "pct")
            cell(sy, r, 2 + j, f"='{synth[s]['sheet']}'!B{synth[s]['rows'][lab]}", fm)
        r += 1
    r += 1
    cell(sy, r, 1, "Annuite de credit (60 % du cout retenu, 8,5 %, 15 ans)", bold=True)
    for j, s in enumerate(SCEN):
        cell(sy, r, 2 + j, f"=PMT(taux,duree,-ltv*HYPOTHESES!{get_column_letter(3 + j)}{prow['cout']})", "num")
    r += 2
    notes = ["Loyers de reference Riviera Palmeraie (jan.-fev. 2026) : studio 90-160 k, 2 pieces 160-280 k FCFA / mois "
             "(non meuble) ; meuble +30 a 50 %. Courte duree : ~30 000 FCFA / nuit pour un studio meuble.",
             "Le foncier est un apport en nature : TRI 'foncier valorise' = rentabilite en integrant sa valeur "
             "d'opportunite (hypothese 150 000 FCFA / m2, a confirmer).",
             "Fiscalite fonciere, conditions de credit et taux d'occupation sont des hypotheses a valider "
             "(fiscaliste, banque, gestionnaire).",
             "S4 : marches par lots HT avec artisans non assujettis, conception par le maitre d'ouvrage (sans "
             "honoraires d'architecte), gestion en direct, gardien partage a 50 % avec la villa.",
             "Base de cout : modifier 'cout_loc_ttc' (HYPOTHESES) - TTC entreprises = %s ; HT = %s ; "
             "HT sans honoraires architecte = %s FCFA." % tuple(f"{x:,.0f}".replace(",", " ") for x in (
                 BL["total_ttc"], BL["total_ht"], BL["total_ht"] - 0.08 * BL["travaux"]))]
    for t in notes:
        c = sy.cell(row=r, column=1, value="- " + t)
        c.font = fnt(i=True, s=9)
        c.alignment = Alignment(wrap_text=True, vertical="top")
        sy.merge_cells(start_row=r, start_column=1, end_row=r, end_column=5)
        sy.row_dimensions[r].height = 30
        r += 1
    path = OUT / "03_Business_Plan_Lot1728_Palmeraie.xlsx"
    wb.save(path)
    return path


if __name__ == "__main__":
    print(build_xlsx())
    for s in SCEN:
        a = calc(s)
        b = calc(s, levier=True)
        c = calc(s, foncier=True)
        print(s, SCEN[s]["nom"], "invest", round(a["invest"]), "pot", round(a["potentiel"]),
              "NOI2", round(a["noi_stab"]), "brut %.1f%% net %.1f%%" % (100 * a["rdt_brut"], 100 * a["rdt_net"]),
              "TRI %.1f%% lev %.1f%% fonc %.1f%%" % (100 * a["tri"], 100 * b["tri"], 100 * c["tri"]),
              "VAN", round(a["van"]), "payback", a["payback"] and round(a["payback"], 1),
              "DSCR", b["dscr"] and round(b["dscr"], 2), "annuite", round(b["annuite"]))
    import pprint
    pprint.pprint(sensibilite())
