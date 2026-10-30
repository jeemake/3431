"""Generation des trois documents PDF (HTML -> PDF via Chromium/Playwright)."""
import json
import pathlib
import subprocess

from projet import (DIVISEUR, EXTERIEURS, FRAIS, IMPREVUS, LOCATIF, LOYERS, OPTION_A, OPTION_B,
                    PLUS_VALUES, RATIOS, TVA, budget, pu, pu_ligne, surfaces)
import plans
import bp

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
SRC = ROOT / "src"
DATE = "Octobre 2026"


def m(x, d=0):
    """Montant FCFA avec espace insecable comme separateur de milliers."""
    s = f"{x:,.{d}f}".replace(",", " ").replace(".", ",")
    return s


def M(x):
    """Millions FCFA."""
    return f"{x / 1e6:,.1f}".replace(",", " ").replace(".", ",") + " M"


def pct(x, d=1):
    return f"{100 * x:.{d}f}".replace(".", ",") + " %"


def a2(x):
    return f"{x:.2f}".replace(".", ",")


CSS = """
@page { size: A4 landscape; margin: 0; }
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body { font-family: Inter, 'Liberation Sans', sans-serif; color: #23262b; font-size: 9.6pt; line-height: 1.45;
       -webkit-print-color-adjust: exact; print-color-adjust: exact; background: #fff; }
.page { width: 297mm; height: 210mm; padding: 13mm 15mm 12mm; position: relative; overflow: hidden;
        page-break-after: always; background: #fff; }
.portrait .page { width: 210mm; height: auto; padding: 0 15mm; overflow: visible; }
.portrait .folio { display: none; }
thead { display: table-header-group; } tr { break-inside: avoid; }
.page:last-child { page-break-after: auto; }
.folio { position: absolute; bottom: 6mm; left: 15mm; right: 15mm; display: flex; justify-content: space-between;
         font-size: 7.2pt; color: #8a8e94; border-top: 0.4pt solid #d9d4ca; padding-top: 2mm; }
h1 { font-size: 21pt; font-weight: 600; margin: 0 0 3mm; letter-spacing: -0.2pt; }
h2 { font-size: 15pt; font-weight: 600; margin: 0 0 1.5mm; letter-spacing: -0.1pt; }
h3 { font-size: 10.5pt; font-weight: 600; margin: 4mm 0 1.5mm; color: #2f4a6d; }
.kicker { font-size: 7.6pt; letter-spacing: 1.2pt; text-transform: uppercase; color: #b5653a; font-weight: 600;
          margin-bottom: 1.5mm; }
.lead { font-size: 10.4pt; color: #45484e; max-width: 230mm; margin: 0 0 4mm; }
p { margin: 0 0 2mm; }
.muted { color: #6b6f76; }
.small { font-size: 8pt; }
.grid { display: grid; gap: 7mm; }
.g2 { grid-template-columns: 1fr 1fr; }
.g3 { grid-template-columns: 1fr 1fr 1fr; }
.g21 { grid-template-columns: 1.35fr 1fr; }
.g12 { grid-template-columns: 1fr 1.35fr; }
.plan svg { width: 100%; height: auto; display: block; }
.plan-cap { font-size: 8pt; color: #6b6f76; margin-top: 1mm; display: flex; justify-content: space-between; }
table { border-collapse: collapse; width: 100%; font-size: 8.4pt; }
th { text-align: left; font-weight: 600; color: #fff; background: #2f4a6d; padding: 1.4mm 2mm; font-size: 7.8pt; }
td { padding: 1.1mm 2mm; border-bottom: 0.4pt solid #e3ded4; vertical-align: top; }
td.n, th.n { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
tr.sub td { background: #f1efe9; font-weight: 600; }
tr.tot td { background: #23262b; color: #fff; font-weight: 600; }
tr.sec td { color: #2f4a6d; font-weight: 600; border-bottom: 0.6pt solid #2f4a6d; padding-top: 2.2mm; }
ul { margin: 0 0 2mm; padding-left: 4.5mm; }
li { margin-bottom: 1mm; }
.kpis { display: grid; grid-template-columns: repeat(4, 1fr); gap: 4mm; margin: 2mm 0 5mm; }
.kpi { border-top: 1.4pt solid #23262b; padding-top: 2mm; }
.kpi .v { font-size: 17pt; font-weight: 600; letter-spacing: -0.3pt; }
.kpi .l { font-size: 7.8pt; color: #6b6f76; }
.card { border: 0.5pt solid #d9d4ca; border-radius: 2mm; padding: 4mm 4.5mm; background: #fbfaf7; }
.card h3 { margin-top: 0; }
.tag { display: inline-block; font-size: 7pt; padding: 0.5mm 2mm; border-radius: 3mm; background: #eef1f5;
       color: #2f4a6d; font-weight: 600; margin-right: 1.5mm; }
.tag.t { background: #f6e9df; color: #9a4f25; }
.tag.g { background: #e7eedf; color: #4f6b3a; }
.legend { display: flex; gap: 4mm; flex-wrap: wrap; font-size: 7.4pt; color: #6b6f76; margin-top: 1.5mm; }
.legend span::before { content: ''; display: inline-block; width: 3mm; height: 3mm; border-radius: 0.6mm;
                       margin-right: 1.2mm; vertical-align: -0.5mm; background: var(--c); border: 0.3pt solid #bbb; }
.cover { display: flex; flex-direction: column; justify-content: space-between; height: 100%; }
.cover h1 { font-size: 34pt; line-height: 1.08; margin-bottom: 4mm; }
.cover .sub { font-size: 13pt; color: #2f4a6d; }
.rule { height: 1.4pt; background: #23262b; width: 40mm; margin: 6mm 0; }
.callout { border-left: 2pt solid #b5653a; padding: 1mm 0 1mm 4mm; margin: 2mm 0 3mm; color: #3b3e44; }
.rev h3 { margin-top: 3mm; }
.rev p, .rev li { font-size: 8.5pt; }
.two-col { column-count: 2; column-gap: 8mm; }
.two-col h3 { break-after: avoid; }
.two-col li, .two-col p { break-inside: avoid; }
table.tight { font-size: 7.5pt; } table.tight td { padding: 0.55mm 1.6mm; } table.tight th { padding: 1mm 1.6mm; }
"""

LEGEND = ('<div class="legend"><span style="--c:#efe4d2">jour</span><span style="--c:#dfe4ee">nuit</span>'
          '<span style="--c:#d6e8ec">eau</span><span style="--c:#e6e3de">service</span>'
          '<span style="--c:#faf8f4">circulation</span><span style="--c:#e9d3b5">engawa / bois</span>'
          '<span style="--c:#cfe0bf">patio / jardin</span></div>')


def page(body, n, doc, cls=""):
    return (f'<section class="page {cls}">{body}<div class="folio"><span>Lot 1728 · Riviera Palmeraie · {doc}</span>'
            f'<span>{n}</span></div></section>')


def html(pages, title, portrait=False):
    return (f'<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>{title}</title>'
            f'<style>{CSS}{"@page { size: A4 portrait; margin: 14mm 0 16mm 0; }" if portrait else ""}</style></head><body class="{"portrait" if portrait else ""}">{"".join(pages)}</body></html>')


def to_pdf(html_path, pdf_path, portrait=False):
    js = f"""
const {{ chromium }} = require('playwright');
(async () => {{
  const b = await chromium.launch(); const p = await b.newPage();
  await p.goto('file://{html_path}', {{waitUntil: 'networkidle'}});
  await p.pdf({{path: '{pdf_path}', format: 'A4', landscape: {str(not portrait).lower()}, printBackground: true,
               margin: {{top: '{"14mm" if portrait else "0"}', right: '0', bottom: '{"16mm" if portrait else "0"}', left: '0'}},
               preferCSSPageSize: {str(not portrait).lower()}, displayHeaderFooter: {str(portrait).lower()},
               headerTemplate: '<span></span>',
               footerTemplate: '<div style="font-family:Inter,sans-serif;font-size:7px;color:#8a8e94;width:100%;padding:0 15mm;display:flex;justify-content:space-between"><span>Lot 1728 · Riviera Palmeraie · Estimatif sommaire</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>'}});
  await b.close();
}})();"""
    tmp = OUT / "_render.js"
    tmp.write_text(js)
    subprocess.run(["node", str(tmp)], check=True, cwd="/tmp")
    tmp.unlink()


def tableau_surfaces(opt, niveaux=("RDC", "R+1"), total=True):
    rows = []
    for niv in niveaux:
        ps = [p for p in opt["pieces"] if p["niveau"] == niv]
        if not ps:
            continue
        rows.append(f'<tr class="sec"><td colspan="2">{"Rez-de-chaussée" if niv == "RDC" else "Étage"}</td></tr>')
        for p in ps:
            ext = "" if p["clos"] else ' <span class="muted">(hors clos)</span>'
            rows.append(f'<tr><td>{p["nom"]}{ext}</td><td class="n">{a2(p["surface"])}</td></tr>')
        tot = sum(p["surface"] for p in ps if p["clos"])
        rows.append(f'<tr class="sub"><td>Surface close {niv}</td><td class="n">{a2(tot)}</td></tr>')
    s = surfaces(opt)
    if total:
        rows.append(f'<tr class="tot"><td>Total surface close</td><td class="n">{a2(s["clos"])} m²</td></tr>')
    return f'<table class="tight"><tr><th>Pièce</th><th class="n">m²</th></tr>{"".join(rows)}</table>'


def tableau_locatif():
    rows = []
    for typ, code, lab, n in (("2P", "2P-a-RDC", "2 pièces (× 4)", 4), ("T1bis", "T1-a-RDC", "T1 bis (× 2)", 2)):
        ps = [p for p in LOCATIF["pieces"] if p.get("logement") == code]
        rows.append(f'<tr class="sec"><td colspan="2">{lab}</td></tr>')
        for p in ps:
            rows.append(f'<tr><td>{p["nom"].split(" ", 1)[1]}</td><td class="n">{a2(p["surface"])}</td></tr>')
        rows.append(f'<tr class="sub"><td>Surface d’un logement</td><td class="n">{a2(sum(p["surface"] for p in ps))}</td></tr>')
    rows.append('<tr class="sec"><td colspan="2">Parties communes et extérieurs</td></tr>')
    for p in LOCATIF["pieces"]:
        if "logement" not in p:
            ext = "" if p["clos"] else ' <span class="muted">(hors clos)</span>'
            rows.append(f'<tr><td>{p["nom"]}{ext}</td><td class="n">{a2(p["surface"])}</td></tr>')
    s = surfaces(LOCATIF)
    hab = sum(p["surface"] for p in LOCATIF["pieces"] if "logement" in p)
    rows.append(f'<tr class="sub"><td>Surface habitable des 6 logements</td><td class="n">{a2(hab)}</td></tr>')
    rows.append(f'<tr class="tot"><td>Total surface close (RDC {a2(s["RDC"])} + R+1 {a2(s["R+1"])})</td><td class="n">{a2(s["clos"])} m²</td></tr>')
    return f'<table class="tight"><tr><th>Pièce</th><th class="n">m²</th></tr>{"".join(rows)}</table>'


def svg(name, fn):
    s = fn()
    (OUT / "svg" / name).write_text(s)
    return s


# =============================================================================== 01 ESQUISSE
def doc_esquisse(revue_html):
    D = "Esquisse"
    sa, sb, sl = surfaces(OPTION_A), surfaces(OPTION_B), surfaces(LOCATIF)
    ba, bb, bl = budget(OPTION_A), budget(OPTION_B), budget(LOCATIF)
    P = []
    n = 0

    def add(body):
        nonlocal n
        n += 1
        P.append(page(body, n, D))

    # --- couverture
    add(f'''<div class="cover"><div><div class="kicker">Étude de faisabilité · Esquisse</div>
<h1>Villa « engawa » et petit<br>immeuble locatif<br>à la Riviera Palmeraie</h1>
<div class="sub">Lot 1728, îlot 174, Djorogobité 1, Cocody (Abidjan). Parcelle de 660 m²</div>
<div class="rule"></div>
<p class="lead">Analyse du site, deux options d'aménagement pour une villa duplex de 4 chambres sur 360 m², un
bâtiment locatif R+1 sur les 300 m² restants. Une architecture d'inspiration japonaise adaptée au climat
d'Abidjan et à ses matériaux : béton, terre et bois.</p></div>
<div class="grid g3 small muted"><div><b>Document 1 / 3</b><br>Analyse et esquisse</div>
<div><b>Document 2 / 3</b><br>Estimatif sommaire (PDF + Excel)</div><div><b>Document 3 / 3</b><br>Business plan (PDF + Excel)</div></div>
<div class="small muted">{DATE} · Projet personnel · Phase esquisse. Les hypothèses réglementaires sont à confirmer avant l'APS.</div></div>''')

    # --- synthese
    add(f'''<div class="kicker">Synthèse</div><h1>L'essentiel en une page</h1>
<p class="lead">La parcelle d'angle est coupée en deux bandes. La villa occupe la bande Nord (20 × 18 m) avec
son entrée sur la rue Nord. Le locatif occupe la bande Sud (20 × 15 m) avec son accès sur la rue Ouest. Les deux
sont séparés par un mur doublé de bambous. Les deux options de villa partagent la même trame de 3,60 m et la même partie jour.
Elles diffèrent par l'emprise au sol et la place de la suite parentale.</p>
<div class="kpis"><div class="kpi"><div class="v">{a2(sa["clos"])} m²</div><div class="l">Option A, maison en L : surface close, emprise {pct(sa["emprise"] / 360, 0)}</div></div>
<div class="kpi"><div class="v">{a2(sb["clos"])} m²</div><div class="l">Option B, duplex compact : surface close, emprise {pct(sb["emprise"] / 360, 0)}</div></div>
<div class="kpi"><div class="v">6 logements</div><div class="l">Locatif R+1 : 4 × 2 pièces + 2 × T1 bis, {a2(sl["clos"])} m² clos</div></div>
<div class="kpi"><div class="v">{M(bb["total_ht"] + bl["total_ht"])}</div><div class="l">Opération B + locatif, FCFA HT (prix base ÷ {DIVISEUR}, honoraires et aléas compris)</div></div></div>
<table><tr><th>Ouvrage</th><th class="n">Emprise</th><th class="n">Surface close</th><th class="n">Engawa / balcons</th>
<th class="n">Travaux HT</th><th class="n">Total HT</th><th class="n">Total TTC</th></tr>
<tr><td>Villa, option A : maison en L sur cour-jardin</td><td class="n">{a2(sa["emprise"])}</td><td class="n">{a2(sa["clos"])}</td><td class="n">{a2(sa["ext_couvert"])}</td><td class="n">{M(ba["travaux"])}</td><td class="n">{M(ba["total_ht"])}</td><td class="n">{M(ba["total_ttc"])}</td></tr>
<tr><td>Villa, option B : duplex compact sur grand jardin</td><td class="n">{a2(sb["emprise"])}</td><td class="n">{a2(sb["clos"])}</td><td class="n">{a2(sb["ext_couvert"])}</td><td class="n">{M(bb["travaux"])}</td><td class="n">{M(bb["total_ht"])}</td><td class="n">{M(bb["total_ttc"])}</td></tr>
<tr><td>Bâtiment locatif R+1 (6 logements)</td><td class="n">{a2(sl["emprise"])}</td><td class="n">{a2(sl["clos"])}</td><td class="n">{a2(sl["ext_couvert"])}</td><td class="n">{M(bl["travaux"])}</td><td class="n">{M(bl["total_ht"])}</td><td class="n">{M(bl["total_ttc"])}</td></tr>
</table>
<div class="grid g2" style="margin-top:5mm"><div class="callout"><b>Recommandation : option B</b>, confirmée par la
revue de l'architecte senior. Pour {M(bb["travaux"] - ba["travaux"])} de travaux en plus (+{pct(bb["travaux"] / ba["travaux"] - 1, 0)}),
elle offre {a2(sb["clos"] - sa["clos"])} m² de plus et un jardin d'un seul tenant (environ 109 m² contre 78 m²). Sa toiture
parasol ventilée est bien plus sûre que des toitures-terrasses sous 1 800 mm de pluie. Les chambres sont à l'étage, loin du locatif,
et le washitsu avec sa salle d'eau sert de chambre de plain-pied.</div>
<div class="callout"><b>Locatif : rentable seulement en montage optimisé.</b> Au coût TTC confié à des entreprises, le TRI sur
15 ans n'est que de {pct(bp.calc("S1")["tri"])} et le crédit n'est pas couvert. En marchés par lots HT, avec la conception assurée
par le maître d'ouvrage, une gestion en direct et un gardien partagé avec la villa (scénario S4), il atteint
{pct(bp.calc("S4")["tri"])} et la couverture de dette passe à {a2(bp.calc("S4", levier=True)["dscr"])}. Voir le document 3.</div></div>''')

    # --- analyse de site
    add(f'''<div class="grid g12" style="height:100%"><div class="plan">{svg("site.svg", plans.plan_site)}</div>
<div><div class="kicker">1 · Analyse du site</div><h2>Une parcelle d'angle, régulière et bien orientée</h2>
<h3>Données foncières (plan cadastral du 04-11-2025)</h3>
<ul><li>Lot 1728, îlot 174, centre de Djorogobité 1, Cocody, morcellement du TF 358, cédant État de CI.</li>
<li>Rectangle de 20,00 × 33,00 m, soit 6 a 60 ca (660 m²). Angles de 100 gr aux bornes B1 à B4.</li>
<li>Deux voies en terre : la rue Nord (20 m de façade) et la rue Ouest (33 m). À l'Est, le lot 1730. Au Sud, une parcelle voisine.</li>
<li>L'axe long est tourné de {plans.NORD_DEG:.1f}° vers l'Est par rapport au Nord géographique. En pratique, le terrain est orienté Nord-Sud.</li></ul>
<h3>Constat sur photo</h3>
<ul><li>Une clôture maçonnée et deux portails métalliques existent. On les réutilise et on les reprend.</li>
<li>Végétation spontanée à défricher. La voie n'est pas revêtue : prévoir un seuil surélevé et la gestion des eaux pluviales.</li>
<li>Voisins en R+1 en cours de construction : les vues vers l'Est et le Sud sont à filtrer.</li>
<li>Terrain apparemment plat. Un relevé topographique est nécessaire, car la revue signale un risque d'inondation dans le secteur
de Djorogobité, à vérifier.</li></ul>
<h3>Climat (Abidjan, 5° N)</h3>
<ul><li>Soleil presque au zénith à midi. Les façades Nord et Sud se protègent avec des débords de 1,2 à 1,8 m.
Les façades Est et Ouest sont les plus exposées : peu d'ouvertures et des brise-soleil.</li>
<li>Vents dominants de Sud-Ouest. Les pièces de vie sont orientées pour la ventilation traversante Nord-Sud.</li>
<li>Environ 1 800 mm de pluie par an, avec des averses violentes en mai-juin : grands débords, socle à +0,45 m, sols perméables.</li></ul>
<h3>Hypothèses réglementaires (à confirmer)</h3>
<ul><li>Recul de 5 m sur la rue Nord, d'environ 3 m sur la rue Ouest. Pan coupé éventuel à l'angle. Implantation en
limite Est avec un mur aveugle, sans débord de toiture sur le voisin. Vues droites à 1,90 m minimum des limites (art. 678 du
Code civil). Locatif limité à R+1.</li>
<li>Découpage proposé : villa de 360 m² au Nord, locatif de 300 m² au Sud. <b>On garde un seul titre foncier</b>
(SCI ou indivision) : pas de reculs sur la limite intérieure, une seule procédure.</li></ul></div></div>''')

    # --- capitude
    add('''<div class="kicker">2 · Enseignements de la base Capitude</div><h2>Ce que nos projets de référence nous apprennent</h2>
<p class="lead">La base Capitude compte 12 projets, 1 277 espaces et 162 motifs de conception. Pour le programme, on
en a extrait les surfaces médianes par type de pièce (villas et logements) et les motifs qui marchent sous climat
tropical humide.</p>
<div class="grid g2"><div><h3>Surfaces de référence (médianes des villas et logements)</h3>
<table><tr><th>Type de pièce</th><th class="n">n</th><th class="n">Médiane</th><th class="n">Retenu ici</th></tr>
<tr><td>Séjour-SAM</td><td class="n">12</td><td class="n">57,6</td><td class="n">38,9 + engawa 26–30</td></tr>
<tr><td>Chambre</td><td class="n">32</td><td class="n">13,1</td><td class="n">13,0</td></tr>
<tr><td>Chambre parentale</td><td class="n">13</td><td class="n">21,8</td><td class="n">20,4 / 21,6</td></tr>
<tr><td>Salle d'eau</td><td class="n">48</td><td class="n">4,1</td><td class="n">4,3 / 4,8</td></tr>
<tr><td>Dressing</td><td class="n">11</td><td class="n">5,8</td><td class="n">3,8 / 13,0</td></tr>
<tr><td>Cuisine</td><td class="n">17</td><td class="n">10,4</td><td class="n">13,0</td></tr>
<tr><td>Chambre de personnel</td><td class="n">11</td><td class="n">8,2</td><td class="n">8,6</td></tr>
<tr><td>WC visiteurs</td><td class="n">14</td><td class="n">2,8</td><td class="n">2,2</td></tr>
<tr><td>Escalier</td><td class="n">19</td><td class="n">12,2</td><td class="n">8,6 + palier 4,3</td></tr>
<tr><td>Buanderie</td><td class="n">10</td><td class="n">6,7</td><td class="n">4,3 / 8,6</td></tr></table>
<p class="small muted" style="margin-top:2mm">Le séjour fermé reste sous la médiane : l'engawa couvert de 1,80 m
le prolonge de 26 à 30 m². Sur 360 m², c'est le moyen le plus économique d'agrandir la pièce de vie.</p></div>
<div><h3>Motifs repris</h3>
<table><tr><th>Motif</th><th>Projet source</th><th>Application</th></tr>
<tr><td>Séjour traversant entre deux terrasses</td><td>ABYA (Assinie)</td><td>Séjour-SAM ouvert au Nord et au Sud</td></tr>
<tr><td>Galerie-rotule jour / nuit / service</td><td>Villa JIK</td><td>Rōka qui distribue cuisine, service et nuit</td></tr>
<tr><td>Salon familial comme rotule d'étage</td><td>Anthurium, EMIIKA</td><td>Salon familial entre les suites</td></tr>
<tr><td>Vestibule à placard devant la salle d'eau</td><td>EMIIKA</td><td>Vestibule-placard de 3,8 m² par suite</td></tr>
<tr><td>Salles d'eau dos à dos</td><td>ABYA, Anthurium</td><td>Gaine commune aux SE des chambres 2 et 3</td></tr>
<tr><td>Dressing traversant comme sas</td><td>Anthurium, JIK</td><td>Accès à la suite parentale</td></tr>
<tr><td>Bande de services le long d'une limite</td><td>EMIIKA</td><td>Bloc service en limite Est</td></tr>
<tr><td>Chambre de personnel à porte extérieure</td><td>EMIIKA</td><td>Accès direct depuis la cour</td></tr>
<tr><td>Patios pour éclairer un plan épais</td><td>EMIIKA, JIK</td><td>Tsubo-niwa, patios du locatif</td></tr>
<tr><td>Logements traversants de 9 à 11 m</td><td>SANKOFA</td><td>Barre locative de 9,0 m</td></tr>
<tr><td>Pièces humides en bande centrale</td><td>Modules R+12</td><td>Bande humide de 1,8 m</td></tr>
<tr><td>Double peau claustra sur les pignons</td><td>Typologie urbaine 8</td><td>Claustras terre cuite à l'Ouest</td></tr></table></div></div>''')

    # --- principes japonais
    add('''<div class="kicker">3 · Parti architectural</div><h2>Penser japonais, construire ivoirien</h2>
<p class="lead">La maison japonaise traditionnelle répond à un climat chaud et humide, comme celui d'Abidjan : grands
débords de toit, plancher surélevé, parois coulissantes, ventilation traversante, jardins proches des pièces. On en reprend
la logique, sans pastiche, avec les matériaux et les savoir-faire locaux.</p>
<div class="grid g2"><div><table><tr><th style="width:28%">Principe</th><th>Traduction dans le projet</th></tr>
<tr><td><b>Ken</b> (trame)</td><td>Module de 0,90 / 1,80 m, trame porteuse de 3,60 m. Petites portées en béton armé
(poutres de 30 cm), coffrages répétitifs, placards et lits qui tombent juste.</td></tr>
<tr><td><b>Engawa</b></td><td>Galerie de 1,80 m en bois sur le jardin, sous le débord de toiture. C'est un espace
entre dedans et dehors, à l'ombre, qui protège les baies de la pluie.</td></tr>
<tr><td><b>Genkan</b></td><td>Entrée de 8,6 m² avec une marche et un getabako (meuble à chaussures). On s'y déchausse,
ce qui garde la maison propre malgré la latérite de la rue.</td></tr>
<tr><td><b>Rōka</b></td><td>Couloir-galerie éclairé qui sépare les flux : les invités ne voient jamais le service.</td></tr>
<tr><td><b>Fusuma / shoji</b></td><td>Panneaux coulissants en bois massif et lames : le washitsu s'ouvre sur l'engawa ou
s'isole en chambre. Au-dessus des portes, des ranma ajourés laissent passer l'air la nuit. Le washitsu a un parquet bois, pas de
tatamis (humidité, termites).</td></tr>
<tr><td><b>Amado</b></td><td>Volets coulissants en bois qui se rangent dans un caisson (tobukuro). Ils ferment les grandes baies
la nuit : sécurité, pluie battante. Des moustiquaires sont intégrées.</td></tr>
<tr><td><b>Tsubo-niwa</b></td><td>Petits patios plantés pour éclairer et ventiler le cœur du plan et les salles d'eau.</td></tr>
<tr><td><b>Shakkei</b></td><td>Cadrer les vues sur le jardin et le grand arbre, filtrer celles sur les voisins avec bambous et claustras.</td></tr>
<tr><td><b>Nagaya</b></td><td>Le locatif reprend la maison en bande japonaise : logements traversants alignés, coursive-engawa, patios privés.</td></tr></table></div>
<div><table><tr><th style="width:28%">Matériau</th><th>Usage et précautions</th></tr>
<tr><td><b>Béton armé</b></td><td>Ossature poteaux-poutres, dalles, socle de +0,45 m. Fondations à définir après l'étude de sol (sols sableux de la Palmeraie).</td></tr>
<tr><td><b>BTC</b> (brique de terre comprimée)</td><td>Remplissage des murs extérieurs, apparents à l'intérieur. Meilleure inertie que l'agglo.
Stabilisées à 6–8 % de ciment, résistance d'au moins 4 MPa testée, soubassement en béton de 50 cm, enduit hydrofuge sur les façades
Sud-Ouest. Les débords de toit sont indispensables.</td></tr>
<tr><td><b>Pisé</b> (terre crue stabilisée)</td><td>Un mur d'accent par maison (genkan, séjour), protégé de la pluie. On le traite comme une pièce d'artisanat.</td></tr>
<tr><td><b>Bois local</b></td><td>Iroko, teck ou doussié pour les coulissants, le platelage de l'engawa et les brise-soleil.
Jamais d'ayous ou de samba en extérieur. Bois séchés et traités, pieds de poteaux sur sabots à +30 cm. Traitement anti-termites
du sol obligatoire.</td></tr>
<tr><td><b>Terre cuite</b></td><td>Claustras sur les façades Ouest, la buanderie et la cage d'escalier du locatif : de l'ombre et de l'air, sans regard.</td></tr>
<tr><td><b>Toiture</b></td><td>Option B : bac acier aluzinc de 0,50 mm, isolé et traité contre le bruit de la pluie, sur charpente
bois traitée, ancré contre le vent, avec lame d'air ventilée. Côté Est, mur pignon et chéneau encaissé. Option A : dalles avec
étanchéité bicouche anti-racines, environ 200 kg/m², plus exigeantes en entretien.</td></tr></table>
<div class="callout small" style="margin-top:3mm">L'engawa et les débords sont le cœur du confort. Ils remplacent une
partie de la climatisation : murs à l'ombre toute la journée, baies ouvertes pendant les averses, nuits ventilées
grâce aux ranma.</div></div></div>''')

    # --- options
    for opt, s, b, other in ((OPTION_A, sa, ba, "A"), (OPTION_B, sb, bb, "B")):
        k = opt["code"]
        add(f'''<div class="kicker">4 · Option {k}</div><h2>{opt["nom"].split("— ")[1]}</h2>
<p class="lead" style="margin-bottom:2mm">{opt["parti"]}</p>
<div class="grid g2"><div class="plan">{svg(f"{k}_RDC.svg", lambda: plans.plan_villa(opt, "RDC"))}
<div class="plan-cap"><span>Rez-de-chaussée · {a2(s["RDC"])} m² clos</span><span>Échelle graphique : trame 3,60 m</span></div></div>
<div class="plan">{svg(f"{k}_R1.svg", lambda: plans.plan_villa(opt, "R+1"))}
<div class="plan-cap"><span>Étage · {a2(s["R+1"])} m² clos</span><span>Plans d'esquisse, cotes en m</span></div></div></div>{LEGEND}''')
        if k == "A":
            atouts = ["Suite parentale de plain-pied (47,8 m²) : confortable à long terme, indépendante de l'étage des enfants.",
                      "Jardin-cour abrité au Nord et à l'Est, ouvert au Sud-Ouest d'où vient la brise. L'engawa en L le borde.",
                      "Toit-jardin de 17,8 m² accessible depuis le salon familial. Le garde-corps est reculé à 1,90 m de la limite Est.",
                      f"L'emprise la plus forte ({pct(s['emprise'] / 360, 0)}) : la consigne « maximiser l'emprise au sol » est respectée."]
            limites = ["Jardin plus petit (environ 78 m² en L) et coupé par l'aile parentale.",
                       "L'aile parentale est en limite Sud, à 4 m de la façade locative. La chambre ne prend le jour qu'à l'Ouest et par le patio.",
                       "On accède à la suite par le rōka de service, près de la buanderie. Le dressing traversant n'a pas de jour (ventilation mécanique).",
                       "Toitures-terrasses et toit végétalisé : étanchéité coûteuse, surchauffe des pièces dessous sans isolation."]
        else:
            atouts = ["Volume simple sous une grande toiture parasol : moins de façades et pas d'étanchéité de terrasse.",
                      "Jardin d'un seul tenant en L (environ 109 m²) sur lequel s'ouvrent toutes les pièces de jour par l'engawa.",
                      "Les 3 chambres sont à l'étage, loin de la rue et du locatif (environ 10 m). Le balcon-engawa protège les baies Sud.",
                      "Washitsu de 13 m² avec sa salle d'eau : bureau, chambre d'amis ou chambre de plain-pied pour un parent âgé."]
            limites = ["Le jardin Sud ne fait que 4 m de profondeur derrière l'engawa : c'est un jardin long plutôt qu'un grand jardin.",
                       "Étage en limite Est sur le bloc service : mur pignon aveugle et chéneau encaissé, à valider au règlement.",
                       f"Emprise plus faible ({pct(s['emprise'] / 360, 0)}) : on « maximise » le jardin plutôt que le bâti au sol.",
                       "Les salles d'eau des chambres 2 et 3 sont aveugles : lanterneau sous toiture et extraction mécanique."]
        coupe = (f'<div class="plan" style="margin-top:3mm">{svg("coupe_B.svg", plans.coupe_B)}<div class="plan-cap">'
                 f'<span>Coupe de principe Nord-Sud : socle, débords, ventilation traversante</span></div></div>' if k == "B" else "")
        add(f'''<div class="grid" style="grid-template-columns:1.5fr 1.5fr;gap:6mm"><div><div class="kicker">4 · Option {k}, programme</div><h2>Surfaces et lecture critique</h2>
<div class="grid g2" style="gap:5mm"><div><h3>Atouts</h3><ul>{"".join(f"<li>{x}</li>" for x in atouts)}</ul></div>
<div><h3>Limites</h3><ul>{"".join(f"<li>{x}</li>" for x in limites)}</ul></div></div>
<h3>Structure et coût</h3>
<p>Ossature béton armé sur trame de 3,60 m, remplissage en BTC, {opt["toiture"].lower()}.
Travaux estimés à <b>{M(b["travaux"])} FCFA HT</b>, soit {m(b["travaux"] / s["clos"])} FCFA/m² clos. Total avec
honoraires et aléas : {M(b["total_ht"])} HT / {M(b["total_ttc"])} TTC.</p>
</div><div><div class="grid g2" style="gap:5mm"><div>{tableau_surfaces(opt, ("RDC",), total=False)}</div>
<div>{tableau_surfaces(opt, ("R+1",))}</div></div>{coupe}</div></div>''')

    # --- comparatif
    rows = [("Surface close (m²)", a2(sa["clos"]), a2(sb["clos"])),
            ("Emprise au sol (m², % de 360)", f'{a2(sa["emprise"])} · {pct(sa["emprise"] / 360, 0)}',
             f'{a2(sb["emprise"])} · {pct(sb["emprise"] / 360, 0)}'),
            ("Jardin principal (env.)", "78 m² en L + toit-jardin 17,8 m²", "109 m² d'un seul tenant en L"),
            ("Engawa / balcons couverts (m²)", a2(sa["ext_couvert"]), a2(sb["ext_couvert"])),
            ("Suite parentale", "Plain-pied, 47,8 m²", "Étage, 38,9 m²"),
            ("Pièce en plus", "Toit-jardin", "Washitsu + SE invités"),
            ("Toiture", "Terrasses + végétalisée", "Parasol bac acier ventilé"),
            ("Travaux HT", M(ba["travaux"]), M(bb["travaux"])),
            ("Travaux HT / m² clos", m(ba["travaux"] / sa["clos"]), m(bb["travaux"] / sb["clos"])),
            ("Total TTC (honoraires + aléas)", M(ba["total_ttc"]), M(bb["total_ttc"]))]
    add(f'''<div class="grid" style="grid-template-columns:0.55fr 0.55fr 1.6fr;gap:5mm">
<div class="plan">{svg("masse_A.svg", lambda: plans.plan_masse(OPTION_A))}<div class="plan-cap"><span>Plan masse A + locatif</span></div></div>
<div class="plan">{svg("masse_B.svg", lambda: plans.plan_masse(OPTION_B))}<div class="plan-cap"><span>Plan masse B + locatif</span></div></div>
<div><div class="kicker">5 · Comparaison</div><h2>Option A ou option B ?</h2>
<table><tr><th>Critère</th><th>A · Maison en L</th><th>B · Duplex compact</th></tr>
{"".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>" for a, b, c in rows)}</table>
<div class="callout" style="margin-top:4mm"><b>Option B recommandée</b>, avec l'accord de la revue senior. Elle coûte environ
{pct(bb["travaux"] / ba["travaux"] - 1, 0)} de plus, mais elle donne plus de surface, un jardin d'un seul tenant et une toiture
bien plus fiable sous ce climat. Toutes les chambres sont à l'étage, à distance du locatif et de la rue. Le washitsu avec sa SE
garde une chambre de plain-pied pour plus tard. L'option A ne se justifie que si la suite parentale de plain-pied est impérative.
Il faudrait alors la retourner vers le jardin, avec un accès distinct du service.</div></div></div>''')

    # --- locatif
    add(f'''<div class="kicker">6 · Parcelle arrière : programme locatif</div><h2>Un « nagaya » de 6 logements traversants</h2>
<div class="grid g2"><div class="plan">{svg("L_RDC.svg", lambda: plans.plan_locatif("RDC"))}
<div class="plan-cap"><span>Rez-de-chaussée · {a2(sl["RDC"])} m² (escalier compris)</span><span>Accès par la rue Ouest</span></div></div>
<div class="plan">{svg("L_R1.svg", lambda: plans.plan_locatif("R+1"))}
<div class="plan-cap"><span>R+1 · {a2(sl["R+1"])} m² + coursive {a2(17.28)} m²</span><span>Logements identiques au RDC</span></div></div></div>{LEGEND}''')
    add(f'''<div class="grid g21"><div><div class="kicker">6 · Locatif, parti</div><h2>Maximiser la surface louable en R+1</h2>
<ul><li><b>Une barre de 14,40 × 9,00 m</b> le long de la limite Sud. C'est la profondeur la plus grande qui garde des
logements traversants Nord-Sud sans couloir (motif SANKOFA). On obtient {a2(sl["clos"])} m² clos pour {a2(sl["emprise"])} m² d'emprise, soit
{pct(sl["emprise"] / 300, 0)} de la parcelle.</li>
<li><b>Six logements</b> : 4 × 2 pièces de 48,6 m² (séjour de 13,0 m², cuisine fermée de 6,5 m² côté coursive avec allège
à 1,40 m, chambre de 13,0 m², bureau-dressing, cellier, SE) et 2 × T1 bis de 32,4 m² (séjour avec cuisine linéaire de 2,40 m,
dégagement qui dessert la SE, alcôve nuit séparée). Ce sont les typologies les plus demandées à la Palmeraie par les jeunes actifs
et les couples.</li>
<li><b>Cour commune de 4 m</b> côté villa. Elle sert d'allée plantée (roji), de terrasses privées sous la coursive pour le RDC
et de recul visuel : avec l'option B, on compte environ 10 m entre la villa et la façade locative. Le mur séparatif de 2,5 m est doublé de bambous.</li>
<li><b>Patios privés de 2 m</b> au Sud (tsubo-niwa) : lumière et ventilation des chambres, un atout pour la location.</li>
<li><b>Escalier droit extérieur</b> le long de la façade Nord, garde-corps plein côté villa, et <b>coursive-engawa</b> de 1,20 m
bordée de claustras de 1,80 m : intimité de la villa, pas de parties communes closes. La coursive fait aussi casquette pour le RDC.</li>
<li><b>Ce que le marché exige</b> : guérite et gardien, bâche à eau et surpresseur (déficit SODECI), compteurs individuels, attentes de
climatisation, cuisine fermée. C'est ce qui justifie un 2 pièces à 230 k plutôt qu'à 180–200 k.</li>
<li><b>5 places de stationnement</b> en pavés drainants, dans l'enceinte, derrière un portail coulissant sur la rue Ouest.</li></ul>
<h3>Variantes pour densifier</h3>
<p>Avec 8 T1 bis (4 par niveau), la surface est la même mais le revenu est quasi identique et il faut deux cuisines et deux SE de plus :
<b>pas rentable</b>. Avec 4 × 3 pièces de 64,8 m² (environ 300–330 k chacun), le revenu est équivalent avec moins de vacance et
moins de pièces humides : c'est une variante à chiffrer à l'APS. Un toit-terrasse partagé (buanderie, panneaux solaires) peut être
ajouté sans créer de niveau.</p></div>
<div>{tableau_locatif()}</div></div>''')

    # --- revue
    add(revue_html)

    # --- etapes
    add('''<div class="kicker">8 · Suite à donner</div><h2>Points à valider et prochaines étapes</h2>
<div class="grid g3"><div class="card"><h3>Réglementaire et foncier</h3><ul>
<li>Cahier des charges du lotissement : reculs, COS / CES, hauteur, implantation en limite Est.</li>
<li>Choix du montage : un TF en SCI ou en indivision, ou morcellement (plus long, impose des reculs).</li>
<li>Certificat d'urbanisme puis permis de construire (ministère de la Construction, guichet unique).</li>
<li>Bornage contradictoire : les 4 bornes sont à vérifier sur place.</li></ul></div>
<div class="card"><h3>Technique</h3><ul>
<li>Étude géotechnique G2 : nature du sol, nappe, type de fondations.</li>
<li>Assainissement : réseau public ou fosse et puisard, avec une étude de perméabilité.</li>
<li>Pression SODECI et puissance CIE : bâche à eau et surpresseur prévus, compteurs individuels pour le locatif.</li>
<li>Filière BTC et bois : artisans, prototype de mur et de coulissant avant le marché.</li></ul></div>
<div class="card"><h3>Économie et calendrier</h3><ul>
<li>Phasage conseillé : locatif d'abord (environ 10 mois), villa ensuite. Les loyers aident à financer la villa
(voir le business plan).</li>
<li>Consultation par lots séparés : gros œuvre, menuiseries bois, électricité-plomberie, finitions.</li>
<li>APS : plans cotés, façades, perspectives, descriptif sommaire, estimation affinée par corps d'état.</li>
<li>Valider les loyers cibles avec deux agences de la Riviera Palmeraie.</li></ul></div></div>''')
    path = OUT / "01_Esquisse_Lot1728_Palmeraie.html"
    path.write_text(html(P, "Esquisse – Lot 1728 Riviera Palmeraie"))
    to_pdf(path, OUT / "01_Esquisse_Lot1728_Palmeraie.pdf")
    return path


REVUE = """<div class="kicker">7 · Contrôle qualité</div><h2>Revue par un architecte senior</h2>
<p class="lead" style="margin-bottom:2mm">Une première version de l'esquisse a été relue par un architecte senior (pratique en
Côte d'Ivoire, connaissance de l'architecture japonaise). Sa revue a relevé 6 points bloquants. <b>Tous ont été corrigés dans
les plans et le chiffrage de ce dossier.</b></p>
<div class="grid g3 rev" style="gap:5mm"><div><h3>Points bloquants corrigés</h3><ul>
<li><b>Rōka accessible seulement par la cuisine, palier coupé de l'escalier.</b> Le noyau est élargi : une bande de distribution de
1,20 m relie genkan, rōka, escalier et palier. L'escalier en U (2 volées de 1,10 m, 19 marches de 17,4 cm) est décalé.</li>
<li><b>SE de la chambre 3 accessible par la SE de la chambre 2.</b> La porte est déplacée sur le vestibule de la chambre 3.</li>
<li><b>Débord de toiture de l'option B sur le lot 1730</b> (art. 681 du Code civil). Côté Est : mur pignon, acrotère et chéneau encaissé.</li>
<li><b>T1 bis</b> : kitchenette et alcôve ne communiquaient pas avec le séjour. Un dégagement dessert maintenant SE et alcôve, la cuisine est linéaire dans le séjour.</li>
<li><b>Vues droites</b> (art. 678) : escalier locatif remplacé par un escalier droit avec garde-corps plein. Toit-jardin A reculé à 1,90 m de la limite.</li></ul></div>
<div><h3>Améliorations intégrées</h3><ul>
<li>Cour de service fermée de claustras au Nord-Est, avec arrière-cuisine (fumées loin de la réception) et séchoir hors du jardin.</li>
<li>SE invités pour le washitsu de l'option B, qui devient une vraie chambre de plain-pied.</li>
<li>3 places de stationnement pour la villa, portail coulissant. Chemin d'entrée dégagé des voitures.</li>
<li>Amado (volets coulissants à caisson), moustiquaires, porte d'entrée blindée. Pas de tatamis.</li>
<li>Locatif : cuisine fermée dans les 2 pièces, claustras en rive de coursive, guérite et gardien, parking dans l'enceinte.</li>
<li>Estimation : aléas portés à 10 %, anti-termites, équipements (chauffe-eau, attentes de climatisation), surcoût de la grande toiture.
Le ÷ 2 ne s'applique plus qu'aux ratios de la base.</li></ul></div>
<div><h3>Avis et points à valider</h3><ul>
<li><b>Recommandation de la revue : option B</b>. Toiture parasol mieux adaptée au climat, chambres à l'étage, structure simple.
L'option A seulement si la suite de plain-pied est impérative.</li>
<li>Le ratio ÷ 2 est jugé « plausible mais au bas de la fourchette » (villa 450–600 k, locatif 300–380 k FCFA/m² de travaux).
Il faut une estimation par lots à l'APS.</li>
<li>À vérifier : CES et COS du lotissement (A ≈ 45 %, B ≈ 40 % sur le TF unique), pan coupé, mitoyenneté Est, risque d'inondation,
dimensionnement des fosses et puisards (environ 30 équivalents-habitants, pluies de 150 mm/h).</li>
<li>Points de la revue non retenus à ce stade : retourner la suite de l'option A vers le jardin (option non recommandée),
variante 4 × 3 pièces (à chiffrer à l'APS).</li></ul></div></div>"""


# =============================================================================== 02 ESTIMATIF
def doc_estimatif():
    D = "Estimatif sommaire"
    P = []
    ops = [(OPTION_A, "Villa, option A"), (OPTION_B, "Villa, option B"), (LOCATIF, "Bâtiment locatif R+1")]

    def detail_rows(opt):
        k = opt["code"]
        rows = []
        for niv, lab in (("RDC", "Rez-de-chaussée"), ("R+1", "Étage")):
            ps = [p for p in opt["pieces"] if p["niveau"] == niv]
            if not ps:
                continue
            rows.append(f'<tr class="sec"><td colspan="5">{lab}</td></tr>')
            agg = {}
            for p in ps:
                key = p["nom"].split(" ", 1)[1] if "logement" in p else p["nom"]
                if "logement" in p:
                    key = f'{"2 pièces" if p["type_log"] == "2P" else "T1 bis"} · {key}'
                a = agg.setdefault(key, [0, p["code"]])
                a[0] += p["surface"]
            st = 0
            for key, (sf, code) in agg.items():
                t = sf * pu(code)
                st += t
                rows.append(f'<tr><td>{key}</td><td>{RATIOS[code][0]}</td><td class="n">{a2(sf)}</td>'
                            f'<td class="n">{m(pu(code))}</td><td class="n">{m(t)}</td></tr>')
            rows.append(f'<tr class="sub"><td colspan="4">Sous-total {lab.lower()}</td><td class="n">{m(st)}</td></tr>')
        for titre, liste in (("Aménagements extérieurs et VRD", EXTERIEURS), ("Plus-values du parti (terre, bois, claustras)", PLUS_VALUES)):
            ls = [lg for lg in liste if lg[4].get(k, 0)]
            rows.append(f'<tr class="sec"><td colspan="5">{titre}</td></tr>')
            st = 0
            for lg in ls:
                q = lg[4][k]
                t = q * pu_ligne(lg)
                st += t
                src = "base ÷ " + str(DIVISEUR) if lg[5] else "prix de marché"
                rows.append(f'<tr><td>{lg[0]}</td><td class="small muted">{src}</td><td class="n">{a2(q)} {lg[1]}</td>'
                            f'<td class="n">{m(pu_ligne(lg))}</td><td class="n">{m(t)}</td></tr>')
            rows.append(f'<tr class="sub"><td colspan="4">Sous-total</td><td class="n">{m(st)}</td></tr>')
        b = budget(opt)
        rows.append(f'<tr class="tot"><td colspan="4">TOTAL TRAVAUX HT</td><td class="n">{m(b["travaux"])}</td></tr>')
        for lib, taux in FRAIS + [("Imprévus", IMPREVUS)]:
            rows.append(f'<tr><td colspan="3">{lib}</td><td class="n">{pct(taux, 2)}</td><td class="n">{m(taux * b["travaux"])}</td></tr>')
        rows.append(f'<tr class="tot"><td colspan="4">TOTAL GÉNÉRAL HT</td><td class="n">{m(b["total_ht"])}</td></tr>')
        rows.append(f'<tr><td colspan="3">TVA</td><td class="n">{pct(TVA, 0)}</td><td class="n">{m(b["tva"])}</td></tr>')
        rows.append(f'<tr class="tot"><td colspan="4">TOTAL GÉNÉRAL TTC</td><td class="n">{m(b["total_ttc"])}</td></tr>')
        return "".join(rows)

    n = 1
    recap = "".join(
        f'<tr><td>{lab}</td><td class="n">{a2(surfaces(o)["clos"])}</td><td class="n">{m(budget(o)["travaux"])}</td>'
        f'<td class="n">{m(budget(o)["frais"] + budget(o)["imprevus"])}</td><td class="n">{m(budget(o)["total_ht"])}</td>'
        f'<td class="n">{m(budget(o)["total_ttc"])}</td><td class="n">{m(budget(o)["travaux"] / surfaces(o)["clos"])}</td></tr>'
        for o, lab in ops)
    tot = "".join(
        f'<tr class="tot"><td>Opération {k} + locatif</td><td class="n">{a2(surfaces(o)["clos"] + surfaces(LOCATIF)["clos"])}</td>'
        f'<td class="n">{m(budget(o)["travaux"] + budget(LOCATIF)["travaux"])}</td>'
        f'<td class="n">{m(budget(o)["frais"] + budget(o)["imprevus"] + budget(LOCATIF)["frais"] + budget(LOCATIF)["imprevus"])}</td>'
        f'<td class="n">{m(budget(o)["total_ht"] + budget(LOCATIF)["total_ht"])}</td>'
        f'<td class="n">{m(budget(o)["total_ttc"] + budget(LOCATIF)["total_ttc"])}</td>'
        f'<td class="n">{m((budget(o)["travaux"] + budget(LOCATIF)["travaux"]) / (surfaces(o)["clos"] + surfaces(LOCATIF)["clos"]))}</td></tr>'
        for o, k in ((OPTION_A, "A"), (OPTION_B, "B")))
    base_rows = "".join(f'<tr><td>{lib}</td><td class="small">{src}</td><td class="n">{m(b)}</td><td class="n">{m(b / DIVISEUR)}</td></tr>'
                        for c, (lib, b, src) in RATIOS.items())
    P.append(page(f'''<div class="kicker">Document 2 / 3</div><h1>Estimatif sommaire</h1>
<p class="lead">Méthode des estimations sommaires de la base Éco-données : un ratio de coût par type de pièce
(tous corps d'état, phase ESQ) est appliqué aux surfaces des plans d'esquisse. Sur votre consigne, <b>les prix de
construction de la base sont divisés par {DIVISEUR}</b>. Les postes absents de la base (clôture, assainissement, menuiseries bois,
claustras, équipements) sont chiffrés au prix du marché, sans division. Les honoraires et les aléas (10 % au stade esquisse) sont
ajoutés en pourcentage. Montants en FCFA.</p>
<table class="tight"><tr><th>Ouvrage</th><th class="n">m² clos</th><th class="n">Travaux HT</th><th class="n">Honoraires + aléas</th>
<th class="n">Total HT</th><th class="n">Total TTC</th><th class="n">Travaux / m²</th></tr>{recap}{tot}</table>
<h3>Bordereau de ratios (FCFA HT / m²)</h3>
<table class="tight"><tr><th>Poste</th><th>Source (base Éco-données)</th><th class="n">Ratio base</th><th class="n">Retenu (÷ {DIVISEUR})</th></tr>{base_rows}</table>
<p class="small muted" style="margin-top:2mm">Non compris : foncier, mobilier et électroménager, climatiseurs, groupe électrogène
ou solaire, forage, piscine, fondations spéciales selon l'étude de sol, frais de permis, de géomètre et de notaire (repris au business plan).
La revue senior juge le ratio ÷ 2 ambitieux : il faut le confirmer par une consultation par lots dès l'APS. Le classeur Excel joint contient toutes les formules. Le coefficient
diviseur se modifie dans l'onglet BASE PRIX.</p>''', n, D, ""))
    for o, lab in ops:
        n += 1
        P.append(page(f'''<div class="kicker">Détail</div><h2>{lab}</h2>
<table class="tight"><thead><tr><th>Désignation</th><th>Ratio appliqué</th><th class="n">Qté</th><th class="n">PU HT</th><th class="n">Total HT</th></tr></thead>
<tbody>{detail_rows(o)}</tbody></table>''', n, D))
    path = OUT / "02_Estimatif_Lot1728_Palmeraie.html"
    path.write_text(html(P, "Estimatif – Lot 1728 Riviera Palmeraie", portrait=True))
    to_pdf(path, OUT / "02_Estimatif_Lot1728_Palmeraie.pdf", portrait=True)


# =============================================================================== 03 BUSINESS PLAN
def chart_cumul(res):
    """Tresorerie cumulee sans credit, 3 scenarios (PDF statique : legende + etiquettes directes)."""
    W, Hh, pl, pr, pt, pb = 640, 270, 64, 120, 16, 34
    cols = {"S1": "#2a78d6", "S4": "#eb6834", "S2": "#1baf7a", "S3": "#eda100"}
    series = {}
    for s, r in res.items():
        cum, pts = 0, []
        for t, c in enumerate(r["cf"]):
            if t == bp.HORIZON:
                c -= r["rows"][-1]["flux"] - r["rows"][-1]["noi"]  # sans la valeur de sortie
            cum += c
            pts.append(cum)
        series[s] = pts
    lo = min(min(v) for v in series.values())
    hi = max(max(v) for v in series.values())
    lo, hi = min(lo, 0) * 1.08, max(hi, 0) * 1.15 + 1
    X = lambda t: pl + t * (W - pl - pr) / bp.HORIZON  # noqa: E731
    Y = lambda v: pt + (hi - v) * (Hh - pt - pb) / (hi - lo)  # noqa: E731
    g = []
    step = 50e6
    v = (int(lo / step) - 1) * step
    while v <= hi:
        if v >= lo:
            g.append(f'<line x1="{pl}" x2="{W - pr}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" stroke="{"#9a9a96" if v == 0 else "#e6e4df"}" stroke-width="{1 if v == 0 else 0.6}"/>'
                     f'<text x="{pl - 6}" y="{Y(v) + 3:.1f}" font-size="9" fill="#52514e" text-anchor="end">{v / 1e6:.0f} M</text>')
        v += step
    for t in range(0, bp.HORIZON + 1, 3):
        g.append(f'<text x="{X(t):.1f}" y="{Hh - pb + 14}" font-size="9" fill="#52514e" text-anchor="middle">an {t}</text>')
    ends = sorted(((Y(pts[-1]), s) for s, pts in series.items()))
    placed, last = {}, -99
    for y, s in ends:
        y = max(y, last + 12)
        placed[s], last = y, y
    for s, pts in series.items():
        d = " ".join(f"{'M' if i == 0 else 'L'}{X(i):.1f},{Y(p):.1f}" for i, p in enumerate(pts))
        g.append(f'<path d="{d}" fill="none" stroke="{cols[s]}" stroke-width="2" stroke-linejoin="round"/>')
        g.append(f'<circle cx="{X(len(pts) - 1):.1f}" cy="{Y(pts[-1]):.1f}" r="4" fill="{cols[s]}" stroke="#fff" stroke-width="2"/>')
        g.append(f'<text x="{X(len(pts) - 1) + 8:.1f}" y="{placed[s] + 3:.1f}" font-size="9" fill="#0b0b0b">{s} · {pts[-1] / 1e6:.0f} M</text>')
    leg = "".join(f'<span style="--c:{cols[s]}">{s} · {bp.SCEN[s]["nom"]}</span>' for s in series)
    return (f'<svg viewBox="0 0 {W} {Hh}" style="width:100%;height:auto" font-family="Inter, sans-serif">{"".join(g)}</svg>'
            f'<div class="legend">{leg}</div>')


def doc_bp():
    D = "Business plan"
    P = []
    res = {s: bp.calc(s) for s in bp.SCEN}
    lev = {s: bp.calc(s, levier=True) for s in bp.SCEN}
    fon = {s: bp.calc(s, foncier=True) for s in bp.SCEN}
    sens = bp.sensibilite()
    bl, bb = budget(LOCATIF), budget(OPTION_B)
    r1 = res["S1"]
    r4 = res["S4"]
    cib = bp.cibles(0.10)
    v = bp.v
    loyers_mois = v("nb_2p") * v("l2p_nu") + v("nb_t1") * v("lt1_nu")
    n = 1
    P.append(page(f'''<div class="kicker">Document 3 / 3</div><h1>Business plan de l'investissement</h1>
<p class="lead">L'investissement analysé est le bâtiment locatif de 6 logements. La villa, occupée par le propriétaire,
entre dans le plan de financement global mais ne produit pas de revenu. Tous les calculs sont repris dans le classeur Excel
joint, avec des hypothèses modifiables.</p>
<div class="kpis"><div class="kpi"><div class="v">{M(r4["invest"])}</div><div class="l">Investissement locatif en montage optimisé (S4, HT, frais compris, hors foncier)</div></div>
<div class="kpi"><div class="v">{m(loyers_mois)}</div><div class="l">Loyers mensuels potentiels en location nue (FCFA)</div></div>
<div class="kpi"><div class="v">{pct(r4["rdt_net"])}</div><div class="l">Rendement net stabilisé (S4) · {pct(r1["rdt_net"])} en S1</div></div>
<div class="kpi"><div class="v">{pct(r4["tri"])}</div><div class="l">TRI sur 15 ans sans crédit (S4) · {pct(r1["tri"])} en S1</div></div></div>
<h3>Ce qu'il faut retenir</h3>
<ul style="font-size:8.6pt"><li><b>Confié à des entreprises au coût TTC (S1), le locatif ne rapporte pas assez</b> : TRI de {pct(r1["tri"])}, rendement
net de {pct(r1["rdt_net"])}, et les loyers ne couvrent pas une annuité de crédit (couverture de {a2(lev["S1"]["dscr"])}).
C'est la conclusion honnête après intégration de la revue senior (aléas à 10 %, équipements, gardien).</li>
<li><b>En montage optimisé (S4), l'opération atteint {pct(r4["tri"])}</b> avec le même loyer. Les leviers : marchés par lots
avec des artisans non assujettis à la TVA, conception assurée par le maître d'ouvrage (architecte), gestion en direct, gardien
partagé avec la villa. Le capital est récupéré en environ {r4["payback"]:.0f} ans, la couverture de dette est de {a2(lev["S4"]["dscr"])}.</li>
<li><b>Repères pour décider</b> : pour un TRI de 10 % en location nue gérée par agence, il faut un coût de construction
d'au plus {M(cib["cout"])} ({m(cib["cout_m2"])} FCFA/m² tout compris), ou des loyers de {m(cib["l2p"])} / {m(cib["lt1"])} FCFA,
au-dessus du marché.</li>
<li><b>Le meublé (S2) et la courte durée (S3) ne sont pas intéressants ici</b> : la prime de loyer est absorbée par les charges
incluses, les commissions et 24 M de mobilier. La courte durée peut se tester sur 1 ou 2 T1 bis seulement.</li>
<li><b>Ne pas lancer le locatif tant que les devis par lots ne confirment pas un coût proche de celui de S4</b>
({M(bp.cout("S4"))} HT hors frais annexes).</li></ul>
<h3>Résultats par scénario</h3>
<table class="tight"><tr><th>Indicateur</th>{"".join(f'<th class="n">{s} · {bp.SCEN[s]["nom"]}</th>' for s in bp.SCEN)}</tr>
<tr><td>Coût de construction retenu</td>{"".join(f'<td class="n">{M(bp.cout(s))}</td>' for s in bp.SCEN)}</tr>
<tr><td>Investissement (hors foncier)</td>{"".join(f'<td class="n">{M(res[s]["invest"])}</td>' for s in bp.SCEN)}</tr>
<tr><td>Revenu annuel stabilisé</td>{"".join(f'<td class="n">{M(res[s]["rows"][1]["rev"])}</td>' for s in bp.SCEN)}</tr>
<tr><td>Résultat d'exploitation stabilisé (an 2)</td>{"".join(f'<td class="n">{M(res[s]["noi_stab"])}</td>' for s in bp.SCEN)}</tr>
<tr><td>Rendement brut / net</td>{"".join(f'<td class="n">{pct(res[s]["rdt_brut"])} / {pct(res[s]["rdt_net"])}</td>' for s in bp.SCEN)}</tr>
<tr class="sub"><td>TRI 15 ans sans crédit</td>{"".join(f'<td class="n">{pct(res[s]["tri"])}</td>' for s in bp.SCEN)}</tr>
<tr><td>TRI avec crédit (60 % du coût, 8,5 %, 15 ans)</td>{"".join(f'<td class="n">{pct(lev[s]["tri"])}</td>' for s in bp.SCEN)}</tr>
<tr><td>TRI avec le foncier valorisé à 45 M</td>{"".join(f'<td class="n">{pct(fon[s]["tri"])}</td>' for s in bp.SCEN)}</tr>
<tr><td>VAN à 10 % (sans crédit)</td>{"".join(f'<td class="n">{M(res[s]["van"])}</td>' for s in bp.SCEN)}</tr>
<tr><td>Couverture de la dette (an 2)</td>{"".join(f'<td class="n">{a2(lev[s]["dscr"])}</td>' for s in bp.SCEN)}</tr></table>''', n, D))

    n += 1
    hyp = "".join(f'<tr><td>{lib}</td><td class="n">{pct(val) if fmt == "pct" else m(val)}</td></tr>'
                  for k, (val, lib, fmt) in bp.H.items())
    scen = "".join(f'<tr><td>{lab}</td>{"".join(f"<td class=n>{pct(bp.SCEN[s][key], 0)}</td>" for s in bp.SCEN)}</tr>'
                   for key, lab in (("occ", "Occupation stabilisée"), ("occ1", "Occupation an 1"), ("gestion", "Gestion / conciergerie"),
                                    ("charges", "Charges incluses"), ("plateforme", "Commission plateforme"), ("entretien", "Entretien"),
                                    ("fisc", "Fiscalité foncière (hyp.)"), ("prov_mob", "Provision mobilier (% / an)")))
    P.append(page(f'''<div class="kicker">Hypothèses</div><h2>Marché, coûts et exploitation</h2>
<div class="grid g2" style="gap:6mm"><div><h3>Marché locatif (Riviera Palmeraie, janv.-févr. 2026)</h3>
<table><tr><th>Typologie</th><th class="n">Fourchette marché</th><th class="n">Retenu (neuf, design)</th></tr>
<tr><td>Studio / T1 bis, nu</td><td class="n">90–160 k</td><td class="n">{m(LOYERS["T1bis"]["nu"])}</td></tr>
<tr><td>2 pièces, nu</td><td class="n">160–280 k</td><td class="n">{m(LOYERS["2P"]["nu"])}</td></tr>
<tr><td>Meublé (prime)</td><td class="n">+30 à 50 %</td><td class="n">+40 %</td></tr>
<tr><td>Studio meublé, courte durée</td><td class="n">≈ 30 k / nuit</td><td class="n">{m(LOYERS["T1bis"]["nuit"])} / nuit</td></tr>
<tr><td>2 pièces meublé, courte durée</td><td class="n">—</td><td class="n">{m(LOYERS["2P"]["nuit"])} / nuit</td></tr></table>
<p class="small muted" style="margin-top:1.5mm">Sources : moyenne des annonces et agences d'Abidjan publiée début 2026
(blog.iambeezy.app, « prix des loyers à Abidjan par quartier ») et annonces de studios meublés à la Palmeraie (expat.com).
Les loyers sont pris dans le haut de la fourchette pour un produit neuf, traversant, avec patio ou terrasse. Ils sont à confirmer auprès d'agences.</p>
<h3>Paramètres des scénarios</h3>
<table><tr><th>Paramètre</th>{"".join(f'<th class="n">{s}</th>' for s in bp.SCEN)}</tr>{scen}</table></div>
<div><h3>Hypothèses générales (modifiables dans l'Excel)</h3><table><tr><th>Hypothèse</th><th class="n">Valeur</th></tr>{hyp}</table></div></div>''', n, D, ""))

    n += 1
    g = sens["grille"]
    grille = "".join(
        f'<tr><td>{lab}<br><span class="muted small">{M(c)}</span></td>' +
        "".join(f'<td class="n">{pct(g[(lab, dl)][0])}<br><span class="muted small">net {pct(g[(lab, dl)][1])}</span></td>'
                for dl in (-0.10, 0.0, 0.10)) + "</tr>"
        for lab, c in sens["couts"].items())
    cred = "".join(f'<tr><td>{d} ans</td><td class="n">{M(a)}</td><td class="n">{a2(ds)}</td><td class="n">{pct(t)}</td></tr>'
                   for d, (a, ds, t) in sens["credit"].items())
    P.append(page(f'''<div class="kicker">Trajectoire et sensibilité</div><h2>Quand l'investissement est-il remboursé ?</h2>
<p class="muted small">Trésorerie cumulée sans crédit, en FCFA, valeur de revente exclue. Seul S4 rembourse l'investissement dans l'horizon. Investissement en année 0, mise en location en année 1
(montée en charge), loyers indexés de 2 % par an.</p>
<div style="width:70%">{chart_cumul(res)}</div>
<div class="grid g2" style="gap:6mm;margin-top:2mm"><div><h3>TRI en location nue gérée par agence selon le coût et les loyers</h3>
<table class="tight"><tr><th>Base de coût</th><th class="n">Loyers −10 %</th><th class="n">Loyers cibles</th><th class="n">Loyers +10 %</th></tr>{grille}</table></div>
<div><h3>Crédit : durée et couverture (S4, 60 % à 8,5 %)</h3>
<table class="tight"><tr><th>Durée</th><th class="n">Annuité</th><th class="n">Couverture</th><th class="n">TRI avec crédit</th></tr>{cred}</table>
<p class="small muted" style="margin-top:1.5mm">Une banque demande en général une couverture d'au moins 1,2. En S4, elle est
atteinte dès 15 ans. Le capital restant dû à l'année 15 est déduit de la valeur de sortie.</p></div></div>''', n, D, ""))

    n += 1
    ops_tot = bb["total_ttc"] + bl["total_ttc"] + v("frais_annexes") * 2
    P.append(page(f'''<div class="kicker">Financement global et risques</div><h2>Plan de financement de l'opération complète</h2>
<div class="grid g2" style="gap:6mm"><div><h3>Budget global (option B + locatif)</h3>
<table><tr><th>Poste</th><th class="n">FCFA</th></tr>
<tr><td>Villa option B : travaux, honoraires, aléas (TTC)</td><td class="n">{m(bb["total_ttc"])}</td></tr>
<tr><td>Bâtiment locatif (TTC)</td><td class="n">{m(bl["total_ttc"])}</td></tr>
<tr><td>Frais annexes villa et locatif (permis, raccordements, divers)</td><td class="n">{m(v("frais_annexes") * 2)}</td></tr>
<tr class="tot"><td>Total à financer, entreprises TTC (hors foncier)</td><td class="n">{m(ops_tot)}</td></tr>
<tr><td>Montage optimisé : lots HT, sans honoraires d'architecte</td><td class="n">{m(bb["total_ht"] - 0.08 * bb["travaux"] + bp.cout("S4") + v("frais_annexes") * 2)}</td></tr></table>
<h3>Phasage conseillé</h3>
<table><tr><th>Phase</th><th>Contenu</th><th class="n">Durée</th></tr>
<tr><td>0</td><td>Bornage, étude de sol, permis, clôture et mur séparatif</td><td class="n">3–4 mois</td></tr>
<tr><td>1</td><td>Bâtiment locatif, mise en location</td><td class="n">9–10 mois</td></tr>
<tr><td>2</td><td>Villa (les loyers, environ {M(r1["rows"][1]["rev"] / 12)} par mois, couvrent une partie des appels de fonds)</td><td class="n">12–14 mois</td></tr></table>
<p class="small muted" style="margin-top:1.5mm">Une installation de chantier commune aux deux ouvrages ferait gagner environ 2 à 3 % sur
les travaux, mais elle repousse les premiers loyers d'un an.</p></div>
<div><h3>Risques principaux et parades</h3>
<table><tr><th>Risque</th><th>Parade</th></tr>
<tr><td>Dérive des coûts (le ratio ÷ 2 est ambitieux)</td><td>Aux prix de base non divisés, le TRI devient négatif ({pct(g[("Prix base non divisés (TTC)", 0.0)][0])}). Marchés par lots à prix fermes, aléas de 10 %, consultation dès l'APS.</td></tr>
<tr><td>Loyers inférieurs aux cibles</td><td>À −10 % de loyers et au coût HT, le TRI tombe à {pct(g[("HT (lots, artisans non assujettis)", -0.1)][0])}. Le gardien, l'eau continue et la cuisine fermée soutiennent le loyer.</td></tr>
<tr><td>Vacance, impayés</td><td>Gestion par une agence (10 %), caution de 2 mois et avance de 2 mois, bail écrit.</td></tr>
<tr><td>Réglementaire (reculs, limite Est)</td><td>Certificat d'urbanisme avant l'APS. Si des reculs de 3 m sont imposés au Sud et à l'Est, la barre passe à 11,4 × 9,0 m (environ −20 %, 5 logements).</td></tr>
<tr><td>Termites, humidité (bois, terre)</td><td>Bois traités et certifiés, soubassements béton, débords. Les prototypes sont testés avant le marché.</td></tr>
<tr><td>Fiscalité foncière</td><td>Taux hypothétique de 7 %. À valider avec un fiscaliste, ainsi que les exonérations éventuelles pour construction neuve.</td></tr></table></div></div>''', n, D, ""))
    path = OUT / "03_Business_Plan_Lot1728_Palmeraie.html"
    path.write_text(html(P, "Business plan – Lot 1728 Riviera Palmeraie"))
    to_pdf(path, OUT / "03_Business_Plan_Lot1728_Palmeraie.pdf")


if __name__ == "__main__":
    import sys
    doc_esquisse(REVUE)
    doc_estimatif()
    doc_bp()
    print("ok")
