"""Generation des trois documents PDF (HTML -> PDF via Chromium/Playwright)."""
import json
import pathlib
import subprocess

from projet import (DIVISEUR, EXTERIEURS, FRAIS, IMPREVUS, LOCATIF, LOYERS, OPTION_A, OPTION_B, OPTION_C,
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
          '<span style="--c:#faf8f4">circulation</span><span style="--c:#e9d3b5">terrasse / balcon</span>'
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
RECO = {"opt": "B", "texte": ""}  # texte calcule dans doc_esquisse


def doc_esquisse(revue_html):
    D = "Esquisse"
    sa, sb, sc, sl = surfaces(OPTION_A), surfaces(OPTION_B), surfaces(OPTION_C), surfaces(LOCATIF)
    ba, bb, bc, bl = budget(OPTION_A), budget(OPTION_B), budget(OPTION_C), budget(LOCATIF)
    br = {"A": ba, "B": bb, "C": bc}[RECO["opt"]]
    RECO["texte"] = (f"<b>Recommandation : option B</b>, retenue par les deux revues senior. C'est la plus robuste : "
                     f"cuisine africaine vraiment détachée avec préau et livraisons, studio de nounou autonome relié par "
                     f"une galerie couverte, grande cuisine moderne avec îlot, {a2(sb['ext_couvert'])} m² d'extérieurs couverts. "
                     f"<b>L'option C</b> offre la plus belle qualité d'espace autour du patio pour un coût proche "
                     f"({M(bc['total_ttc'])} contre {M(bb['total_ttc'])} TTC). Corrigée selon sa revue, elle reste un bon choix "
                     f"si le patio est votre priorité. L'option A est à écarter : cuisine trop petite, nounou à l'étage.")
    P = []
    n = 0

    def add(body):
        nonlocal n
        n += 1
        P.append(page(body, n, D))

    # --- couverture
    add(f'''<div class="cover"><div><div class="kicker">Étude de faisabilité · Esquisse · version 2</div>
<h1>Villa familiale et petit<br>immeuble locatif<br>à la Riviera Palmeraie</h1>
<div class="sub">Lot 1728, îlot 174, Djorogobité 1, Cocody (Abidjan). Parcelle de 660 m²</div>
<div class="rule"></div>
<p class="lead">Analyse du site, étude des plans de la base Capitude, trois options pour une villa duplex de 4 chambres
dont une chambre de nounou, avec cuisine africaine, sur 360 m², et un bâtiment locatif R+1 sur les 300 m² restants.
Une architecture pensée pour le climat d'Abidjan et la vie familiale ivoirienne.</p></div>
<div class="grid g3 small muted"><div><b>Document 1 / 3</b><br>Analyse et esquisse</div>
<div><b>Document 2 / 3</b><br>Estimatif sommaire (PDF + Excel)</div><div><b>Document 3 / 3</b><br>Business plan (PDF + Excel)</div></div>
<div class="small muted">{DATE} · Projet personnel · Phase esquisse. Les hypothèses réglementaires sont à confirmer avant l'APS.</div></div>''')

    # --- synthese
    add(f'''<div class="kicker">Synthèse</div><h1>L'essentiel en une page</h1>
<p class="lead">La parcelle d'angle est coupée en deux bandes. La villa occupe la bande Nord (20 × 18 m), avec son entrée,
sa guérite et son parking sur la rue Nord. Le locatif occupe la bande Sud (20 × 15 m), avec son accès sur la rue Ouest.
Les trois options de villa reprennent l'organisation des villas de la base Capitude : salon ouvert sur une
terrasse ou un patio, salle à manger entre salon et cuisine, salon familial à l'étage. Chaque option a une cuisine africaine
hors du volume habité, avec préau ou cour, et une chambre de nounou avec sa salle d'eau.</p>
<div class="kpis" style="grid-template-columns:repeat(5,1fr)"><div class="kpi"><div class="v">{a2(sa["clos"])} m²</div><div class="l">A · villa compacte, nounou à l'étage · emprise {pct(sa["emprise"] / 360, 0)}</div></div>
<div class="kpi"><div class="v">{a2(sb["clos"])} m²</div><div class="l">B · villa avec aile de service · emprise {pct(sb["emprise"] / 360, 0)}</div></div>
<div class="kpi"><div class="v">{a2(sc["clos"])} m²</div><div class="l">C · maison à patio central · emprise {pct(sc["emprise"] / 360, 0)}</div></div>
<div class="kpi"><div class="v">6 logements</div><div class="l">Locatif R+1 : 4 × 2 pièces + 2 × T1 bis, {a2(sl["clos"])} m² clos</div></div>
<div class="kpi"><div class="v">{M(br["total_ht"] + bl["total_ht"])}</div><div class="l">Opération {RECO["opt"]} + locatif, FCFA HT (base ÷ {DIVISEUR}, honoraires et aléas compris)</div></div></div>
<table><tr><th>Ouvrage</th><th class="n">Emprise</th><th class="n">Surface close</th><th class="n">Terrasses / balcons</th>
<th class="n">Travaux HT</th><th class="n">Total HT</th><th class="n">Total TTC</th></tr>
<tr><td>Villa, option A : villa compacte, nounou à l'étage</td><td class="n">{a2(sa["emprise"])}</td><td class="n">{a2(sa["clos"])}</td><td class="n">{a2(sa["ext_couvert"])}</td><td class="n">{M(ba["travaux"])}</td><td class="n">{M(ba["total_ht"])}</td><td class="n">{M(ba["total_ttc"])}</td></tr>
<tr><td>Villa, option B : villa avec aile de service</td><td class="n">{a2(sb["emprise"])}</td><td class="n">{a2(sb["clos"])}</td><td class="n">{a2(sb["ext_couvert"])}</td><td class="n">{M(bb["travaux"])}</td><td class="n">{M(bb["total_ht"])}</td><td class="n">{M(bb["total_ttc"])}</td></tr>
<tr><td>Villa, option C : maison à patio central</td><td class="n">{a2(sc["emprise"])}</td><td class="n">{a2(sc["clos"])}</td><td class="n">{a2(sc["ext_couvert"])}</td><td class="n">{M(bc["travaux"])}</td><td class="n">{M(bc["total_ht"])}</td><td class="n">{M(bc["total_ttc"])}</td></tr>
<tr><td>Bâtiment locatif R+1 (6 logements)</td><td class="n">{a2(sl["emprise"])}</td><td class="n">{a2(sl["clos"])}</td><td class="n">{a2(sl["ext_couvert"])}</td><td class="n">{M(bl["travaux"])}</td><td class="n">{M(bl["total_ht"])}</td><td class="n">{M(bl["total_ttc"])}</td></tr>
</table>
<div class="grid g2" style="margin-top:5mm"><div class="callout">{RECO["texte"]}</div>
<div class="callout"><b>Locatif : rentable seulement en montage optimisé.</b> Au coût TTC confié à des entreprises, le TRI sur
15 ans n'est que de {pct(bp.calc("S1")["tri"])} et le crédit n'est pas couvert. En marchés par lots HT, avec la conception assurée
par le maître d'ouvrage, une gestion en direct et un gardien partagé avec la villa (scénario S4), il atteint
{pct(bp.calc("S4")["tri"])}. Voir le document 3.</div></div>''')

    # --- analyse de site
    add(f'''<div class="grid g12" style="height:100%"><div class="plan">{svg("site.svg", plans.plan_site)}</div>
<div><div class="kicker">1 · Analyse du site</div><h2>Une parcelle d'angle, régulière et bien orientée</h2>
<h3>Données foncières (plan cadastral du 04-11-2025)</h3>
<ul><li>Lot 1728, îlot 174, centre de Djorogobité 1, Cocody, morcellement du TF 358, cédant État de CI.</li>
<li>Rectangle de 20,00 × 33,00 m, soit 6 a 60 ca (660 m²). Angles de 100 gr aux bornes B1 à B4.</li>
<li>Deux voies en terre : la rue Nord (20 m de façade) et la rue Ouest (33 m). À l'Est, le lot 1730. Au Sud, une parcelle voisine.</li>
<li>L'axe long est tourné de {plans.NORD_DEG:.1f}° vers l'Est par rapport au Nord géographique : le terrain est orienté Nord-Sud.</li></ul>
<h3>Constat sur photo</h3>
<ul><li>Une clôture maçonnée et deux portails métalliques existent. On les réutilise et on les reprend.</li>
<li>Végétation spontanée à défricher. La voie n'est pas revêtue : prévoir un seuil surélevé et la gestion des eaux pluviales.</li>
<li>Voisins en R+1 en cours de construction : les vues vers l'Est et le Sud sont à filtrer.</li>
<li>Terrain apparemment plat. Un relevé topographique est nécessaire (risque d'inondation signalé dans le secteur, à vérifier).</li></ul>
<h3>Climat (Abidjan, 5° N)</h3>
<ul><li>Soleil presque au zénith à midi. Les façades Nord et Sud se protègent avec des débords et des balcons.
Les façades Est et Ouest sont les plus exposées : peu d'ouvertures, claustras et brise-soleil.</li>
<li>Vents dominants de Sud-Ouest : pièces de vie traversantes Nord-Sud.</li>
<li>Environ 1 800 mm de pluie par an, averses violentes en mai-juin : débords, socle à +0,45 m, sols perméables.</li></ul>
<h3>Hypothèses réglementaires (à confirmer)</h3>
<ul><li>Recul de 5 m sur la rue Nord, d'environ 3 m sur la rue Ouest. Pan coupé éventuel à l'angle. Vues droites à 1,90 m
minimum des limites (art. 678 du Code civil), aucun débord de toiture sur le voisin. Locatif limité à R+1.</li>
<li>Découpage : villa de 360 m² au Nord, locatif de 300 m² au Sud. <b>On garde un seul titre foncier</b>
(SCI ou indivision) : une seule procédure, pas de recul sur la limite intérieure.</li></ul></div></div>''')

    # --- etude Capitude
    add('''<div class="kicker">2 · Étude des plans de la base Capitude</div><h2>Comment nos villas de référence sont organisées</h2>
<p class="lead" style="margin-bottom:2mm">On a relu pièce par pièce les plans vectorisés de quatre projets résidentiels d'Abidjan et
d'Assinie (surfaces, dimensions, portes, liaisons entre pièces). Ce sont eux qui fixent l'organisation des deux options.</p>
<table class="tight"><tr><th style="width:17%">Projet</th><th style="width:30%">Organisation</th><th>Ce qu'on en retient pour le lot 1728</th></tr>
<tr><td><b>Maison de ville Anthurium</b><br>R+1, 4 ch., lot de 12 × 30 m, Riviera Golf</td><td>Hall et escalier le long d'un mur, noyau de service côté
rue (cuisine 15,2 m², buanderie 8,5 m², chambre de service 8 m²), SAM 14,4 m², salon 7,0 × 6,5 m sur terrasse couverte de 42 m².</td>
<td>Séquence hall, SAM, salon, terrasse, jardin. À l'étage, l'escalier débouche sur un salon familial de 11,8 m² qui
distribue la suite parentale (31,2 m²) et les chambres. C'est le cas le plus proche de notre programme.</td></tr>
<tr><td><b>Villa ABYA 2</b><br>R+1, 4 pièces, Assinie</td><td>Séjour de 11 × 7 m vitré au Nord et au Sud, cuisine ouverte et cuisine
fermée en bande (1,9 × 7,0 m), pavillon de service (chambre 6,8 m² + SE 5,5 m²), préau cuisine de 7,1 m², cour de service en claustra.</td>
<td>Séjour traversant, cuisine fermée en bande, cour de service fermée de claustras. Balcon filant au Sud sous le débord de toiture,
dressing traversant de 12,7 m² en sas de la suite.</td></tr>
<tr><td><b>Résidence EMIIKA</b><br>Cocody Danga</td><td>Lanière de services le long d'une limite : cuisine africaine de 16,2 m² face à la
cuisine moderne, de part et d'autre d'un patio. Buanderie de 12,5 m², séchoir à ciel ouvert de 25 m², deux studios de personnel de 12,1 m²
avec SE en lanière de 4,7 m² dos à dos, guérite et WC du gardien.</td>
<td>La cuisine africaine est une vraie pièce, séparée, ventilée sur une cour, reliée à la cuisine moderne par la circulation de
service. Les chambres de personnel ont une porte extérieure et leur propre salle d'eau.</td></tr>
<tr><td><b>Villa JIK</b><br>plain-pied, Cocody Ambassade</td><td>Galerie qui distribue jour, nuit et service ; cuisine de réception de
29,5 m² et cuisine technique de 9 m² ouverte sur une cour de service ; chambre de personnel de 8,9 m², séchoir de 10,8 m², guérite de 7,8 m².</td>
<td>Les invités ne traversent jamais le service, le personnel rejoint la cuisine sans passer par le séjour. Guérite au portillon.</td></tr></table>
<div class="grid g2" style="gap:6mm;margin-top:2mm"><div><h3>Liaisons les plus fréquentes (portes et baies relevées)</h3>
<table class="tight"><tr><th>Liaison</th><th class="n">Cas</th><th>Projets</th></tr>
<tr><td>Chambre de personnel ↔ salle d'eau</td><td class="n">5</td><td>ABYA, EMIIKA</td></tr>
<tr><td>Séjour ↔ terrasse (baie)</td><td class="n">5</td><td>ABYA, EMIIKA</td></tr>
<tr><td>Cuisine ↔ séjour / SAM</td><td class="n">6</td><td>ABYA, Anthurium, JIK</td></tr>
<tr><td>Chambre parentale ↔ dressing</td><td class="n">4</td><td>ABYA, Anthurium, EMIIKA</td></tr>
<tr><td>Escalier ↔ hall d'entrée</td><td class="n">4</td><td>ABYA, Anthurium</td></tr>
<tr><td>Cuisine ↔ couloir de service</td><td class="n">3</td><td>ABYA, EMIIKA, JIK</td></tr>
<tr><td>Buanderie ↔ séchoir / couloir</td><td class="n">5</td><td>EMIIKA, JIK, ABYA</td></tr></table></div>
<div><h3>Règles retenues pour les deux options</h3><ul class="small">
<li>Salon traversant Nord-Sud d'environ 45 m² + SAM de 14 m² (médiane séjour-SAM de la base : 57,6 m²).</li>
<li>Hall, WC visiteurs (2,8 m²) et escalier groupés côté rue. La SAM fait le lien entre salon et cuisine.</li>
<li>Deux cuisines : une cuisine moderne et une cuisine africaine sur cour de service, avec buanderie et séchoir.</li>
<li>Chambre de nounou d'environ 9 m² (médiane de la base : 8,2 m²) avec sa propre salle d'eau.</li>
<li>Étage : salon familial à l'arrivée de l'escalier, suite parentale avec dressing traversant.</li>
<li>Guérite et WC du gardien au portillon, 3 places de parking.</li></ul></div></div>''')

    # --- parti climat / culture
    add('''<div class="kicker">3 · Parti architectural</div><h2>Une villa pour le climat d'Abidjan et la vie ivoirienne</h2>
<div class="grid g2"><div><table><tr><th style="width:30%">Usage</th><th>Réponse dans le projet</th></tr>
<tr><td><b>Recevoir</b></td><td>Salon de 43 à 45 m² ouvert sur une terrasse couverte (A, B) ou sur le patio (C), à l'ombre. La SAM
se ferme ou s'ouvre sur le salon. Le WC visiteurs est dans le hall : les invités ne montent pas à l'étage.</td></tr>
<tr><td><b>Cuisine africaine</b></td><td>Pièce carrelée sol et murs, évier double bac, plan bas pour le mortier et le pilon, hotte et
conduit remonté au-dessus des toitures, cage à bouteilles de gaz accessible depuis l'aire de livraison. Toujours hors du volume habité
(pas de chambre au-dessus), reliée à la cuisine moderne, prolongée par un préau ou une cour pour cuisiner dehors.</td></tr>
<tr><td><b>Cuisine moderne</b></td><td>Cuisine fermée avec plan de travail, ou cuisine avec îlot (option B), reliée à la SAM. C'est la cuisine
« de tous les jours » et de réception.</td></tr>
<tr><td><b>Nounou</b></td><td>Chambre de 9 à 12 m² avec salle d'eau privée. A : à l'étage, près des chambres d'enfants.
B et C : studio indépendant dans l'aile de service, avec porte extérieure.</td></tr>
<tr><td><b>Gardien et sécurité</b></td><td>Guérite avec WC au portillon, à l'angle des deux rues. Portail coulissant, porte d'entrée blindée,
grilles de défense sur les baies du RDC.</td></tr>
<tr><td><b>Linge et provisions</b></td><td>Buanderie et séchoir à ciel ouvert hors de la vue des invités. Magasin pour les provisions (sacs de riz,
huile, ignames).</td></tr></table></div>
<div><table><tr><th style="width:30%">Climat</th><th>Réponse dans le projet</th></tr>
<tr><td><b>Soleil</b></td><td>Longues façades au Nord et au Sud. Au Sud, la terrasse et le balcon filant font une casquette de 2,4 m.
Les pignons Est et Ouest sont peu percés, avec claustras en terre cuite et brise-soleil.</td></tr>
<tr><td><b>Ventilation</b></td><td>Salon et chambres traversants Nord-Sud dans l'axe de la brise de Sud-Ouest. Impostes à persiennes
au-dessus des portes. Menuiseries bois à jalousies, qui ventilent même fermées.</td></tr>
<tr><td><b>Pluie</b></td><td>Socle à +0,45 m, débords de toiture de 1,2 m, terrasses couvertes, cours de service drainées (siphons, pavés drainants).</td></tr>
<tr><td><b>Chaleur</b></td><td>Toiture en bac acier isolé avec lame d'air ventilée, cachée par un acrotère. Murs en BTC (brique de terre comprimée),
plus d'inertie qu'un agglo. Arbres d'ombrage côté Ouest.</td></tr>
<tr><td><b>Matériaux</b></td><td>Ossature béton armé sur trame de 3,6 m, remplissage BTC stabilisée (6 à 8 % de ciment) sur soubassement béton
de 50 cm. Bois durs locaux (iroko, doussié) traités pour les menuiseries et les brise-soleil. Traitement anti-termites du sol.</td></tr></table></div></div>''')

    # --- options
    for opt, s, b in ((OPTION_A, sa, ba), (OPTION_B, sb, bb), (OPTION_C, sc, bc)):
        k = opt["code"]
        add(f'''<div class="kicker">4 · Option {k} · références : {opt["ref"]}</div><h2>{opt["nom"].split("— ")[1]}</h2>
<p class="lead" style="margin-bottom:2mm">{opt["parti"]}</p>
<div class="grid g2"><div class="plan">{svg(f"{k}_RDC.svg", lambda: plans.plan_villa(opt, "RDC"))}
<div class="plan-cap"><span>Rez-de-chaussée · {a2(s["RDC"])} m² clos (guérite comprise)</span><span>Trame 3,60 m</span></div></div>
<div class="plan">{svg(f"{k}_R1.svg", lambda: plans.plan_villa(opt, "R+1"))}
<div class="plan-cap"><span>Étage · {a2(s["R+1"])} m² clos</span><span>Plans d'esquisse, cotes en m</span></div></div></div>{LEGEND}''')
        if k == "A":
            atouts = ["Un seul volume, simple à construire, avec la plus petite emprise.",
                      "La nounou dort à côté des chambres d'enfants : pratique avec un nourrisson.",
                      "Toutes les chambres ont leur salle d'eau, celles des enfants dos à dos.",
                      "Grande terrasse couverte de 34,6 m² et jardin d'environ 95 m²."]
            limites = ["Cuisine moderne réduite à 9,4 m² par l'escalier allongé.",
                       "La cuisine africaine, en pavillon de 8,6 m² dans la cour, reste petite.",
                       "La nounou partage l'étage de la famille et traverse la maison pour rejoindre le service.",
                       "SE des enfants compactes (3,6 m²), dont une enclavée : conduit de ventilation naturelle."]
        elif k == "B":
            atouts = ["Cuisine africaine dans l'aile de service, avec préau et porte de livraison (modèle EMIIKA, ABYA 2).",
                      "Studio de la nounou indépendant, relié à la maison par la galerie couverte.",
                      "Cuisine moderne avec îlot (18 m²) et office : la cuisine de réception attendue dans une villa.",
                      "La galerie de service relie les deux cuisines sans traverser la maison."]
            limites = ["Emprise la plus forte et jardin plus petit (environ 80 m²).",
                       "La nounou est loin des enfants la nuit : babyphone à prévoir.",
                       "Les chambres 2 et 3 partagent une salle d'eau (comme dans la maison de ville Anthurium).",
                       "Aile en limite Est (toiture vers l'Ouest, acrotère) : à valider au cahier des charges."]
        else:
            atouts = ["Environ 50 m² d'espace central : patio planté à ciel ouvert (28 m²), terrasse couverte (13,7 m²) et pergola (8,6 m²).",
                      "Salon, salle à manger et cuisine s'ouvrent sur le patio ; arbre (frangipanier) et bassin à recirculation.",
                      "Patio fermé au Sud par une claustra de 4 m et une pergola plantée : à l'abri des vues du locatif.",
                      "Passage de 1,50 m autour de la maison ; nounou, service et cuisine africaine à l'Est, portillon de service."]
            limites = ["Patio réduit par rapport à la première esquisse : la revue a imposé une vraie terrasse couverte et la fermeture Sud.",
                       "Patio bordé de R+1 sur trois côtés : une cour fraîche plus qu'un jardin ; la brise vient surtout de l'Ouest.",
                       "Coursive ouverte vers les chambres 2 et 3 : grilles et éclairage de nuit nécessaires.",
                       "Façade Est à 1,50 m de la limite : seulement des jours hauts (vues droites à 1,90 m)."]
        add(f'''<div class="grid" style="grid-template-columns:1.5fr 1.5fr;gap:6mm"><div><div class="kicker">4 · Option {k}, programme</div><h2>Surfaces et lecture critique</h2>
<div class="grid g2" style="gap:5mm"><div><h3>Atouts</h3><ul>{"".join(f"<li>{x}</li>" for x in atouts)}</ul></div>
<div><h3>Limites</h3><ul>{"".join(f"<li>{x}</li>" for x in limites)}</ul></div></div>
<h3>Structure et coût</h3>
<p>Ossature béton armé sur trame de 3,60 m, remplissage en BTC. {opt["toiture"]}.
Travaux estimés à <b>{M(b["travaux"])} FCFA HT</b>, soit {m(b["travaux"] / s["clos"])} FCFA/m² clos. Total avec
honoraires et aléas : {M(b["total_ht"])} HT / {M(b["total_ttc"])} TTC.</p>
{f'<div class="plan" style="margin-top:3mm;max-width:150mm">{svg("coupe_B.svg", plans.coupe_B)}<div class="plan-cap"><span>Coupe de principe Nord-Sud (options A et B) : socle, débords, ventilation traversante</span></div></div>' if k == "A" else ""}
</div><div><div class="grid g2" style="gap:5mm"><div>{tableau_surfaces(opt, ("RDC",), total=False)}</div>
<div>{tableau_surfaces(opt, ("R+1",))}</div></div></div></div>''')

    # --- comparatif
    rows = [("Surface close (m²)", a2(sa["clos"]), a2(sb["clos"]), a2(sc["clos"])),
            ("Emprise au sol (% de 360)", pct(sa["emprise"] / 360, 0), pct(sb["emprise"] / 360, 0), pct(sc["emprise"] / 360, 0)),
            ("Espace vert principal", "jardin ≈ 95 m²", "jardin ≈ 80 m²", "patio 28 m² + terrasse 14 + pergola 9"),
            ("Salon + SAM", "45,4 + 14,4 m²", "45,4 + 14,4 m²", "43,1 + 15,1 m²"),
            ("Cuisine moderne", "9,4 m²", "18,0 m² + office", "13,9 m²"),
            ("Cuisine africaine", "pavillon 8,6 m²", "aile 12,0 m² + préau", "aile 13,0 m² + préau, sas buanderie"),
            ("Nounou", "étage, 8,6 + SE 4,3", "studio RDC 9,0 + SE 4,2", "studio RDC 11,9 + SE 5,8"),
            ("SE des enfants", "une par chambre", "une partagée", "une par chambre"),
            ("Extérieurs couverts", f'{a2(sa["ext_couvert"])} m²', f'{a2(sb["ext_couvert"])} m²', f'{a2(sc["ext_couvert"])} m²'),
            ("Total TTC", M(ba["total_ttc"]), M(bb["total_ttc"]), M(bc["total_ttc"]))]
    add(f'''<div class="grid" style="grid-template-columns:0.42fr 0.42fr 0.42fr 1.6fr;gap:4mm">
<div class="plan">{svg("masse_A.svg", lambda: plans.plan_masse(OPTION_A))}<div class="plan-cap"><span>Masse A</span></div></div>
<div class="plan">{svg("masse_B.svg", lambda: plans.plan_masse(OPTION_B))}<div class="plan-cap"><span>Masse B</span></div></div>
<div class="plan">{svg("masse_C.svg", lambda: plans.plan_masse(OPTION_C))}<div class="plan-cap"><span>Masse C</span></div></div>
<div><div class="kicker">5 · Comparaison</div><h2>Quelle option retenir ?</h2>
<table class="tight"><tr><th>Critère</th><th>A · Compacte</th><th>B · Aile de service</th><th>C · Patio central</th></tr>
{"".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td><td>{d}</td></tr>" for a, b, c, d in rows)}</table>
<div class="callout" style="margin-top:4mm">{RECO["texte"]}</div></div></div>''')

    # --- locatif
    add(f'''<div class="kicker">6 · Parcelle arrière : programme locatif</div><h2>Une barrette de 6 logements traversants</h2>
<div class="grid g2"><div class="plan">{svg("L_RDC.svg", lambda: plans.plan_locatif("RDC"))}
<div class="plan-cap"><span>Rez-de-chaussée · {a2(sl["RDC"])} m² (escalier et guérite compris)</span><span>Accès par la rue Ouest</span></div></div>
<div class="plan">{svg("L_R1.svg", lambda: plans.plan_locatif("R+1"))}
<div class="plan-cap"><span>R+1 · {a2(sl["R+1"])} m² + coursive {a2(17.28)} m²</span><span>Logements identiques au RDC</span></div></div></div>{LEGEND}''')
    add(f'''<div class="grid g21"><div><div class="kicker">6 · Locatif, parti</div><h2>Maximiser la surface louable en R+1</h2>
<ul><li><b>Une barre de 14,40 × 9,00 m</b> le long de la limite Sud. C'est la profondeur la plus grande qui garde des
logements traversants Nord-Sud sans couloir (immeuble SANKOFA de la base : barre de 11 m, logements traversants). On obtient
{a2(sl["clos"])} m² clos pour {a2(sl["emprise"])} m² d'emprise, soit {pct(sl["emprise"] / 300, 0)} de la parcelle.</li>
<li><b>Six logements</b> : 4 × 2 pièces de 48,6 m² (séjour de 13,0 m², cuisine fermée de 6,5 m² côté coursive avec allège
à 1,40 m, chambre de 13,0 m², bureau-dressing, cellier, SE) et 2 × T1 bis de 32,4 m² (séjour avec cuisine linéaire, dégagement
qui dessert la SE, alcôve nuit séparée). Ce sont les typologies les plus demandées à la Palmeraie.</li>
<li><b>Pièces humides en bande centrale</b> (immeuble Modules R+12 de la base), <b>cuisine fermée</b> et cour de service comme dans la
typologie urbaine 8 : les patios Sud du RDC servent de séchoir, le R+1 a un étendoir derrière les claustras de la coursive.</li>
<li><b>Cour commune de 4 m</b> côté villa : allée plantée, terrasses privées sous la coursive pour le RDC, et recul visuel vis-à-vis
de la villa. Mur séparatif de 2,5 m doublé d'une haie.</li>
<li><b>Escalier droit extérieur</b> le long de la façade Nord, garde-corps plein côté villa, et <b>coursive</b> de 1,20 m bordée de
claustras de 1,80 m : intimité de la villa, pas de parties communes closes.</li>
<li><b>Ce que le marché exige</b> : guérite et gardien, bâche à eau et surpresseur (déficit SODECI), compteurs individuels, attentes de
climatisation, cuisine fermée. C'est ce qui justifie un 2 pièces à 230 k plutôt qu'à 180–200 k.</li>
<li><b>5 places de stationnement</b> en pavés drainants, dans l'enceinte, derrière un portail coulissant sur la rue Ouest.</li></ul>
<h3>Variantes pour densifier</h3>
<p>Avec 8 T1 bis, la surface est la même, le revenu quasi identique, et il faut deux cuisines et deux SE de plus : <b>pas rentable</b>.
Avec 4 × 3 pièces de 64,8 m² (environ 300–330 k chacun), le revenu est équivalent avec moins de vacance : variante à chiffrer à l'APS.</p></div>
<div>{tableau_locatif()}</div></div>''')

    # --- revue
    add(revue_html)

    # --- etapes
    add('''<div class="kicker">8 · Suite à donner</div><h2>Points à valider et prochaines étapes</h2>
<div class="grid g3"><div class="card"><h3>Réglementaire et foncier</h3><ul>
<li>Cahier des charges du lotissement : reculs, COS / CES, hauteur, implantation en limite Est, guérite en recul.</li>
<li>Choix du montage : un TF en SCI ou en indivision, ou morcellement (plus long, impose des reculs).</li>
<li>Certificat d'urbanisme puis permis de construire.</li>
<li>Bornage contradictoire : les 4 bornes sont à vérifier sur place.</li></ul></div>
<div class="card"><h3>Technique</h3><ul>
<li>Étude géotechnique G2 et relevé topographique.</li>
<li>Assainissement : réseau public ou fosse et puisard, avec une étude de perméabilité.</li>
<li>Pression SODECI et puissance CIE : bâche à eau et surpresseur, compteurs individuels pour le locatif.</li>
<li>Cuisine africaine : conduit d'extraction en toiture, cage à gaz ventilée, sol et murs lavables.</li></ul></div>
<div class="card"><h3>Économie et calendrier</h3><ul>
<li>Phasage conseillé : locatif d'abord (environ 10 mois), villa ensuite. Les loyers aident à financer la villa.</li>
<li>Consultation par lots séparés : gros œuvre, menuiseries, électricité-plomberie, finitions.</li>
<li>APS : plans cotés, façades, perspectives, descriptif sommaire, estimation par corps d'état.</li>
<li>Valider les loyers cibles avec deux agences de la Riviera Palmeraie.</li></ul></div></div>''')
    path = OUT / "01_Esquisse_Lot1728_Palmeraie.html"
    path.write_text(html(P, "Esquisse – Lot 1728 Riviera Palmeraie"))
    to_pdf(path, OUT / "01_Esquisse_Lot1728_Palmeraie.pdf")
    return path


REVUE = """<div class="kicker">7 · Contrôle qualité</div><h2>Revues par un architecte senior</h2>
<p class="lead" style="margin-bottom:2mm">Chaque version a été relue par un architecte senior (25 ans de villas à Abidjan). Les points
bloquants ont été corrigés dans les plans et le chiffrage de ce dossier.</p>
<div class="grid g3 rev" style="gap:5mm"><div><h3>Revue V2 · options A et B</h3><ul>
<li><b>Escalier trop court</b> pour 3,30 m d'étage : cage portée à 2,40 × 4,50 m, portes sur les paliers.</li>
<li><b>Cuisine africaine dans le volume habité (A)</b> : sortie en pavillon de claustra dans la cour. En B, préau de 7,2 m² et cage à gaz
côté livraisons. Conduits remontés au-dessus des toitures.</li>
<li><b>Livraisons bloquées</b> par la 3e voiture : aire de livraison libre ; 3e place par le 2e portail existant.</li>
<li><b>Porte SAM-cuisine</b> au milieu de la table : déplacée côté hall ; en B, office relié à l'escalier.</li>
<li>Galerie couverte jusqu'au studio de la nounou (B), séchoirs couverts, grilles à l'étage, guérite à côté du portillon,
aile B en monopente vers l'Ouest avec acrotère sur la limite.</li></ul></div>
<div><h3>Revue de l'option C · patio</h3><ul>
<li><b>Patio exposé au locatif</b> et abrité du vent par lui : fermé au Sud par une claustra de 4 m et une pergola plantée.</li>
<li><b>Pas de vraie terrasse</b> : galerie Nord élargie à 2,40 m (13,7 m²). Branche Ouest de la coursive supprimée, patio à ciel ouvert,
balcon privé à l'Ouest pour la suite.</li>
<li><b>Chambre 2 de 1,80 m de large</b> : recomposée (12,6 m² + SE 6,3 m²), palier fusionné avec le salon familial.</li>
<li><b>Eaux pluviales</b> : toitures vers l'extérieur, caniveau grillé et exutoire autour du patio.</li>
<li>Cuisine africaine sans porte directe sur la maison (sas par la buanderie), SE ch.3 au-dessus de la SE nounou, portillon de service,
bassin à recirculation, imposte haute au Sud du salon.</li></ul></div>
<div><h3>Avis et points à valider</h3><ul>
<li><b>Les deux revues recommandent l'option B</b> : la plus robuste pour les usages (cuisines, nounou, livraisons, réception).
C est la plus belle spatialement, A est à écarter.</li>
<li>Le ratio ÷ 2 est jugé « plausible mais au bas de la fourchette » : estimation par lots dès l'APS.</li>
<li>À vérifier : cahier des charges (emprise, implantation en limite Est, préaux et guérite en recul), cote d'inondation,
dimensionnement de l'assainissement, besoin d'un ou deux gardiens (villa et locatif).</li>
<li>Non retenu à ce stade : chambre d'amis au RDC pour les parents de passage (à arbitrer avec vous).</li></ul></div></div>"""


# =============================================================================== 02 ESTIMATIF
def doc_estimatif():
    D = "Estimatif sommaire"
    P = []
    ops = [(OPTION_A, "Villa, option A"), (OPTION_B, "Villa, option B"), (OPTION_C, "Villa, option C"),
           (LOCATIF, "Bâtiment locatif R+1")]

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
        for o, k in ((OPTION_A, "A"), (OPTION_B, "B"), (OPTION_C, "C")))
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
    bl, bb = budget(LOCATIF), budget({"A": OPTION_A, "B": OPTION_B, "C": OPTION_C}[RECO["opt"]])
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
<div class="grid g2" style="gap:6mm"><div><h3>Budget global (option {RECO["opt"]} + locatif)</h3>
<table><tr><th>Poste</th><th class="n">FCFA</th></tr>
<tr><td>Villa option {RECO["opt"]} : travaux, honoraires, aléas (TTC)</td><td class="n">{m(bb["total_ttc"])}</td></tr>
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
