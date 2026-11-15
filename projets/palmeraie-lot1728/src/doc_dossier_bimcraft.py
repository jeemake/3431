"""Dossier de presentation de l'option C v5 sur la maquette BIMCraft, aux regles Capitude de Supabase.

Regles lues dans `regles_agents` (projet Supabase capitude) le 15-11-2026 : PRESENTATION-PROJETS-ARCHI v4 (mise en page
minimale, grille unique 12 colonnes x 4 rangs, corps 7 / 9 / 14 / 28 pt, noir et gris, un dominant par page, texte <= 40
mots, respiration apres deux pages denses, export PDF A3 + .pptx editable) et GABARIT-VISUEL-PLANS v4 (pieces
numerotees, legende en C10-12, nord et echelle graphique, coupes et facades empilees a la meme echelle). Les dessins
viennent de la maquette BIMCraft par `plans_bimcraft.py` ; les photos du site, les references du client et les vues
d'ambiance Sume sont reprises du dossier 05.

    python3 bimcraft_modele.py && python3 doc_dossier_bimcraft.py
"""
import base64
import csv
import io
import json
import re
import subprocess

from PIL import Image, ImageChops

import bimcraft_modele as BM
import plans_bimcraft as PB
from doc import OUT, to_pdf
from doc_dossier_v5 import (CSS, DIV, IA, LOCATIF_M, PROJET, C, budget, fr, lignes, police_css, surfaces, table_estim)

V = BM.OUT / "vues"
V5 = OUT / "05_Dossier_Option_C_v5_Lot1728.html"
NOM = "07_Dossier_BIMCraft_Lot1728"

CSS_PLUS = """
.hd { top: 13.8mm; }
.vraie { display: flex; flex-direction: column; justify-content: flex-start; }
.vraie .dw svg { display: block; }
.leg { font-size: 7pt; line-height: 9.5pt; }
.leg .lg-t { font-size: 9pt; font-weight: 700; letter-spacing: 1pt; text-transform: uppercase; margin-bottom: 1.5mm; }
.leg .lg b { display: inline-block; width: 5mm; font-weight: 700; }
.leg .lg span { text-transform: uppercase; letter-spacing: 0.4pt; }
.col { display: flex; flex-direction: column; justify-content: space-between; height: 100%; }
.nord { margin-top: 4mm; }
"""


# ------------------------------------------------------------------------------------------------ sources
def dossier_v5():
    """Images incorporees au dossier 05 : {page : [(src, legende), ...]}."""
    h = V5.read_text(encoding="utf-8")
    imgs = {}
    for k, p in enumerate(h.split('<section class="page">')[1:], 1):
        srcs = re.findall(r'<img[^>]*src="(data:[^"]+)"', p)
        caps = re.findall(r'class="cap">([^<]*)', p)
        imgs[k] = list(zip(srcs, caps + [""] * len(srcs)))
    return imgs


def rendu(nom):
    j = V / f"{nom}.jpg"
    return j if j.exists() else V / f"{nom}.png"


def b64(path, maxw=2600, quality=86, rogne=True, marge=30):
    im = Image.open(path).convert("RGB")
    if rogne:
        diff = ImageChops.difference(im, Image.new("RGB", im.size, (255, 255, 255)))
        bb = diff.convert("L").point(lambda v: 255 if v > 12 else 0).getbbox()
        if bb:
            im = im.crop((max(0, bb[0] - marge), max(0, bb[1] - marge), min(im.width, bb[2] + marge),
                          min(im.height, bb[3] + marge)))
    im.thumbnail((maxw, maxw))
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=quality)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


# ------------------------------------------------------------------------------------------------ blocs (grille)
def bloc(c0, c1, r0, r1, html, cls="b"):
    return f'<div class="{cls}" style="grid-column:{c0}/{c1 + 1};grid-row:{r0}/{r1 + 1}">{html}</div>'


def txt(t, cls):
    return f'<div class="{cls}" data-pptx="txt">{t}</div>'


def image(c0, c1, r0, r1, src, cap, fit="cover"):
    return bloc(c0, c1, r0, r1, f'<img class="img" data-pptx="img" src="{src}" style="height:calc(100% - 5mm);object-fit:{fit}"/>'
                                + txt(cap, "cap"))


def dessin(c0, c1, r0, r1, svg, titre, complement=""):
    """Dessin a l'echelle vraie (mm papier), titre dessous cale a gauche sur son emprise."""
    t = f'<div class="titre" data-pptx="txt"><b>{titre}</b> <span>{complement}</span></div>'
    return bloc(c0, c1, r0, r1, f'<div class="dw" data-pptx="img" style="width:fit-content">{svg}</div>{t}', "b vraie")


def donnees(items):
    return '<div class="data">' + "".join(f'<p data-pptx="txt"><span class="k">{k}</span><span class="v">{v}</span></p>'
                                          for k, v in items) + "</div>"


def page(num, titre, sous, corps, folio, plein=False):
    hd = "" if plein else (f'<div class="hd"><div class="n" data-pptx="txt">{num}</div><div class="t" data-pptx="txt">{titre}</div>'
                           f'<div class="s" data-pptx="txt">{sous}</div></div>'
                           f'<div class="ft"><span data-pptx="txt">{PROJET}</span><span data-pptx="txt">{folio:02d}</span></div>')
    return f'<section class="page">{hd}{corps}</section>'


def colonne(haut, bas=""):
    return f'<div class="col"><div>{haut}</div><div class="nord" data-pptx="img" style="width:fit-content">{bas}</div></div>'


# ------------------------------------------------------------------------------------------------ surfaces
def nomenclature():
    lire = lambda f: {(r["Number"], r["Level"]): r for r in csv.DictReader(open(V / f, encoding="utf-8"))}
    axes, utiles = lire("pieces_axes.csv"), lire("pieces_utiles.csv")
    return [{"num": r["Number"], "nom": r["Name"], "niv": r["Level"], "axes": float(r["Area (m²)"]),
             "utile": float(utiles.get(k, {}).get("Area (m²)", 0) or 0)} for k, r in axes.items()]


def tableau_bim(rows, titre):
    lab = {"RDC": "REZ-DE-CHAUSSÉE", "R+1": "ÉTAGE", "Toit-terrasse": "NIVEAU HAUT"}
    out = [f'<table data-pptx="table"><tr><th>PIÈCE ({titre})</th><th class="n">AXES</th><th class="n">UTILE</th></tr>']
    ta = tu = 0
    for niv in ("RDC", "R+1", "Toit-terrasse"):
        rs = sorted((r for r in rows if r["niv"] == niv), key=lambda r: (len(r["num"]), r["num"]))
        if not rs:
            continue
        out.append(f'<tr class="sec"><td colspan="3">{lab[niv]}</td></tr>')
        sa = su = 0
        for r in rs:
            out.append(f'<tr><td>{r["nom"]}</td><td class="n">{fr(r["axes"], 1)}</td><td class="n">{fr(r["utile"], 1)}</td></tr>')
            sa, su = sa + r["axes"], su + r["utile"]
        out.append(f'<tr class="sub"><td>Sous-total</td><td class="n">{fr(sa, 1)}</td><td class="n">{fr(su, 1)}</td></tr>')
        if niv != "Toit-terrasse":
            ta, tu = ta + sa, tu + su
    out.append(f'<tr class="tot"><td>TOTAL CLOS</td><td class="n">{fr(ta, 1)}</td><td class="n">{fr(tu, 1)} m²</td></tr></table>')
    return "".join(out), ta, tu


# ------------------------------------------------------------------------------------------------ dossier
def build():
    v5 = dossier_v5()
    s, b = surfaces(C), budget(C, DIV)
    sm, bm = surfaces(LOCATIF_M), budget(LOCATIF_M, DIV)
    pieces = nomenclature()
    P = []

    def add(num, titre, sous, corps, plein=False):
        P.append(page(num, titre, sous, corps, len(P) + 1, plein))

    def plan_page(num, titre_page, svg_leg, titre, niveau, echelle=100):
        svg, leg = svg_leg
        add(num, titre_page, titre, dessin(1, 9, 1, 4, svg, titre, f"/ 1:{echelle}")
            + bloc(10, 12, 1, 4, colonne(PB.legende_html(leg, niveau), PB.nord_echelle(echelle))))

    # couverture : une image, le titre en L 28 pt en bas a gauche, une ligne LIEU · MISSION · DATE
    add("", "", "", bloc(1, 12, 1, 3, f'<img class="img" data-pptx="img" src="{b64(rendu("cam_angle"), rogne=False)}"/>')
        + bloc(1, 6, 4, 4, '<div class="cover"><h1 data-pptx="txt">Villa à patio et deux maisons duplex</h1>'
                           '<div class="l" data-pptx="txt">Riviera Palmeraie, Abidjan · Esquisse, maquette BIMCraft · 15.11.2026</div></div>'),
        plein=True)
    # 01 site
    site = v5.get(2, [])
    corps = image(1, 6, 1, 3, site[0][0], site[0][1]) if site else ""
    for k, (src, cap) in enumerate(site[1:4]):
        corps += image(7 + 2 * k, 8 + 2 * k, 1, 2, src, cap)
    corps += bloc(7, 12, 3, 4, donnees([("Parcelle", "20 × 33 m, 660 m²"), ("Rues", "Nord : villa · Ouest : duplex · latérite"),
                                        ("Contexte", "maisons R+1 et R+2 en béton")]))
    add("01", "Site", "État des lieux", corps)
    # 02 references (une ligne chacune)
    refs = v5.get(3, [])
    corps = "".join(image(1 + 4 * k, 4 + 4 * k, 1, 3, src, cap) for k, (src, cap) in enumerate(refs[:2]))
    corps += bloc(9, 12, 1, 2, donnees([("Référence 1", "lames de bois en damier, toiture mince"),
                                        ("Référence 2", "bardage, grands débords, claustra béton")]))
    add("02", "Références", "Images du client", corps)
    # 03 intention (respiration)
    add("03", "Intention", "Vue d'ambiance", image(1, 12, 1, 4, b64(IA / "arrivee_V1.jpg", rogne=False),
                                                     "Vue d’ambiance · rue Nord, variante V1 (dossier 05)"))
    # 04 plan masse
    corps = (dessin(1, 9, 1, 4, PB.plan_masse(), "Plan masse", "/ 1:200")
             + bloc(10, 12, 1, 4, colonne(donnees([("Parcelle", "660 m²"), ("Villa", f"{fr(s['clos'], 1)} m² clos"),
                                                   ("Duplex", f"2 × {fr(sm['clos'] / 2, 1)} m² clos")]),
                                          PB.nord_echelle(200))))
    add("04", "Plan masse", "Villa au Nord, duplex au Sud", corps)
    # 05-09 villa
    plan_page("05", "Villa", PB.villa("RDC"), "Plan du rez-de-chaussée", "Rez-de-chaussée")
    add("06", "Villa", "Axonométrie", image(1, 12, 1, 4, b64(V / "axo_NO.png"),
                                            "Axonométrie depuis le Nord-Ouest · maquette BIMCraft, aplats par matériau", "contain"))
    plan_page("07", "Villa", PB.villa("R+1"), "Plan de l’étage", "Étage")
    plan_page("08", "Villa", PB.villa("TOIT"), "Plan du niveau haut", "Niveau haut")
    add("09", "Villa", "Les niveaux en 3D", image(1, 6, 1, 4, b64(V / "axo_RDC.png"), "Rez-de-chaussée, coupé à +2,90", "contain")
        + image(7, 12, 1, 4, b64(V / "axo_R1.png"), "Étage, coupé à +6,20", "contain"))
    # 10 coupes
    add("10", "Villa", "Coupes", dessin(1, 9, 1, 2, PB.coupe("Coupe_AA"), "Coupe AA", "/ 1:100, Nord-Sud sur l’axe 10,75")
        + dessin(1, 9, 3, 4, PB.coupe("Coupe_BB"), "Coupe BB", "/ 1:100, Est-Ouest sur le patio")
        + bloc(10, 12, 1, 2, donnees([("Niveaux", "±0,00 · +3,30 · +6,60 · +9,00")])))
    # 11-13 facades
    add("11", "Façades", "Rues Nord et Ouest", dessin(1, 9, 1, 2, PB.elevation("Elevation_Nord"), "Élévation nord", "/ 1:100, sur la rue")
        + dessin(1, 12, 3, 4, PB.elevation("Elevation_Ouest"), "Élévation ouest", "/ 1:100, villa à gauche, duplex à droite"))
    add("12", "Vues", "Vue d'ambiance", image(1, 12, 1, 4, b64(rendu("cam_rue_nord"), rogne=False),
                                               "Vue d’ambiance · depuis la rue Nord, maquette BIMCraft"))
    add("13", "Façades", "Sud et Est", dessin(1, 9, 1, 2, PB.elevation("Elevation_Sud"), "Élévation sud", "/ 1:100, duplex sur les cours")
        + dessin(1, 12, 3, 4, PB.elevation("Elevation_Est"), "Élévation est", "/ 1:100, passage de service"))
    # 14-19 duplex
    plan_page("14", "Duplex", PB.duplex("RDC"), "Plan du rez-de-chaussée", "Rez-de-chaussée")
    plan_page("15", "Duplex", PB.duplex("R+1"), "Plan de l’étage", "Étage")
    add("16", "Vues", "Vue d'ambiance", image(1, 12, 1, 4, b64(rendu("cam_rue_ouest"), rogne=False),
                                               "Vue d’ambiance · les duplex depuis la rue Ouest, maquette BIMCraft"))
    plan_page("17", "Duplex", PB.duplex("TOIT"), "Plan du niveau haut", "Niveau haut")
    add("18", "Duplex", "Coupe", dessin(1, 9, 1, 2, PB.coupe("Coupe_CC"), "Coupe CC", "/ 1:100, Nord-Sud sur la maison 1")
        + image(1, 12, 3, 4, b64(V / "axo_SE.png"), "Axonométrie depuis le Sud-Est · les duplex devant la villa", "contain"))
    add("19", "Vues", "Vue d'ambiance", image(1, 6, 1, 4, b64(IA / "patio.jpg", rogne=False), "Vue d’ambiance · le patio (dossier 05)")
        + image(7, 12, 1, 4, b64(IA / "toit_V2.jpg", rogne=False), "Vue d’ambiance · le toit-terrasse couvert, variante V2 (dossier 05)"))
    # 20 surfaces (comparatif)
    villa = [r for r in pieces if not r["num"].startswith("M")]
    m1 = [r for r in pieces if r["num"].startswith("M1.")]
    tv, va, vu = tableau_bim(villa, "VILLA")
    t1, ma, mu = tableau_bim(m1, "MAISON 1")
    add("20", "Surfaces", "Nomenclature de la maquette", bloc(1, 4, 1, 4, tv) + bloc(5, 8, 1, 4, t1)
        + bloc(9, 12, 1, 2, donnees([("Villa", f"{fr(va, 1)} m² aux axes, {fr(vu, 1)} m² utiles"),
                                     ("Duplex", f"2 × {fr(ma, 1)} m² aux axes, 2 × {fr(mu, 1)} m² utiles"),
                                     ("Axes", "comme l’estimatif ; utile : au nu des murs")])))
    # 21-23 estimatif
    for num, opt, titre in (("21", C, "Villa"), ("23", LOCATIF_M, "Duplex")):
        rows = lignes(opt)
        half = (len(rows) + 1) // 2
        add(num, "Estimatif", f"{titre} · Éco-données ÷ {fr(DIV, 1)}, FCFA",
            bloc(1, 6, 1, 4, table_estim(rows[:half]).replace("<table", '<table data-pptx="table"'))
            + bloc(7, 12, 1, 4, table_estim(rows[half:]).replace("<table", '<table data-pptx="table"')))
        if num == "21":
            add("22", "Vues", "Vue d'ambiance", image(1, 12, 1, 4, b64(IA / "angle_V1.jpg", rogne=False),
                                                       "Vue d’ambiance · angle des rues, variante V1 (dossier 05)"))
    # 24 suite
    add("24", "Suite", "Points à arbitrer", bloc(1, 3, 1, 2, donnees([
        ("Villa", f"{fr(b['travaux'] / 1e6, 1)} M HT · {fr(b['total_ttc'] / 1e6, 1)} M TTC"),
        ("Duplex", f"{fr(bm['travaux'] / 1e6, 1)} M HT · {fr(bm['total_ttc'] / 1e6, 1)} M TTC"),
        ("À arbitrer", "façade V1 ou V2 ; loyer des duplex"),
        ("À vérifier", "niveau couvert à +9,00 et R+1 maximum")])))
    html = (f'<!doctype html><html><head><meta charset="utf-8"><style>{police_css()}{CSS}{CSS_PLUS}</style></head><body>'
            + "".join(P) + "</body></html>")
    out_html = OUT / f"{NOM}.html"
    out_html.write_text(html, encoding="utf-8")
    to_pdf(out_html, OUT / f"{NOM}.pdf")
    pptx(out_html, OUT / f"{NOM}.pptx")
    print("pages", len(P))


# ------------------------------------------------------------------------------------------------ export .pptx
JS_RELEVE = r"""
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({deviceScaleFactor: 2, viewport: {width: 1588, height: 1123}});
  await p.goto('file://%HTML%', {waitUntil: 'networkidle'});
  const pages = await p.$$('section.page'); const out = [];
  for (let i = 0; i < pages.length; i++) {
    const pg = pages[i]; await pg.scrollIntoViewIfNeeded(); const pb = await pg.boundingBox(); const items = [];
    for (const el of await pg.$$('[data-pptx]')) {
      const kind = await el.getAttribute('data-pptx'); const bb = await el.boundingBox();
      if (!bb || bb.width < 1 || bb.height < 1) continue;
      const it = {kind, x: bb.x - pb.x, y: bb.y - pb.y, w: bb.width, h: bb.height};
      if (kind === 'img') { const photo = (await el.evaluate(e => e.tagName)) === 'IMG';
        it.png = '%DIR%/p' + i + '_' + items.length + (photo ? '.jpg' : '.png');
        await el.screenshot(photo ? {path: it.png, type: 'jpeg', quality: 85} : {path: it.png}); }
      else if (kind === 'table') { it.rows = await el.$$eval('tr', trs => trs.map(tr => [...tr.children].map(td =>
          ({t: td.innerText, n: td.classList.contains('n'), bold: parseInt(getComputedStyle(td).fontWeight) >= 600, span: td.colSpan})))); }
      else { it.runs = await el.evaluate(e => { const st = getComputedStyle(e);
          return {t: e.innerText, size: parseFloat(st.fontSize), bold: parseInt(st.fontWeight) >= 600,
                  color: st.color, caps: st.textTransform === 'uppercase'}; }); }
      items.push(it);
    }
    out.push({w: pb.width, h: pb.height, items});
  }
  require('fs').writeFileSync('%DIR%/releve.json', JSON.stringify(out));
  await b.close();
})();
"""


def pptx(html, dest):
    """Meme mise en page en .pptx (PRESENTATION-PROJETS-ARCHI, section 8) : dessins et images en images, textes,
    legendes et tableaux editables, police URW Gothic (Century Gothic sur un poste qui l'a)."""
    from pptx import Presentation
    from pptx.dml.color import RGBColor
    from pptx.util import Emu, Pt
    d = OUT / "_pptx"
    d.mkdir(exist_ok=True)
    (d / "releve.js").write_text(JS_RELEVE.replace("%HTML%", str(html)).replace("%DIR%", str(d)))
    subprocess.run(["node", str(d / "releve.js")], check=True, cwd="/tmp")
    pages = json.loads((d / "releve.json").read_text())
    prs = Presentation()
    prs.slide_width, prs.slide_height = Emu(420 * 36000), Emu(297 * 36000)
    k = 420 / pages[0]["w"] * 36000                 # px CSS -> EMU
    for pg in pages:
        sl = prs.slides.add_slide(prs.slide_layouts[6])
        for it in pg["items"]:
            x, y, w, h = (Emu(int(v * k)) for v in (it["x"], it["y"], it["w"], it["h"]))
            if it["kind"] == "img":
                sl.shapes.add_picture(it["png"], x, y, w, h)
            elif it["kind"] == "table":
                rows = it["rows"]
                ncol = max(sum(c["span"] for c in r) for r in rows)
                tb = sl.shapes.add_table(len(rows), ncol, x, y, w, h).table
                for i, r in enumerate(rows):
                    j = 0
                    for c in r:
                        cell = tb.cell(i, j)
                        if c["span"] > 1:
                            cell.merge(tb.cell(i, j + c["span"] - 1))
                        cell.text = c["t"]
                        cell.margin_top = cell.margin_bottom = Emu(0)
                        for para in cell.text_frame.paragraphs:
                            for run in para.runs:
                                run.font.size, run.font.bold, run.font.name = Pt(7), c["bold"], "URW Gothic"
                                run.font.color.rgb = RGBColor(0x3A, 0x33, 0x2E)
                        cell.fill.background()
                        j += c["span"]
            else:
                r = it["runs"]
                tx = sl.shapes.add_textbox(x, y, w, h).text_frame
                tx.word_wrap = True
                tx.margin_left = tx.margin_right = tx.margin_top = tx.margin_bottom = 0
                tx.text = r["t"].upper() if r["caps"] else r["t"]
                rgb = [int(v) for v in re.findall(r"\d+", r["color"])[:3]]
                for para in tx.paragraphs:
                    for run in para.runs:
                        run.font.size = Pt(round(r["size"] * 0.75, 1))
                        run.font.bold, run.font.name = r["bold"], "URW Gothic"
                        run.font.color.rgb = RGBColor(*rgb)
    prs.save(dest)
    for f in d.iterdir():
        f.unlink()
    d.rmdir()


if __name__ == "__main__":
    build()
