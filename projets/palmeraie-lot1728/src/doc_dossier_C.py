"""Dossier de presentation de l'option C (maison a patio), sans rendus IA.

Plans, coupes, elevations et vues 3D sont tires du meme modele (projet.py, facade.py, rendu/scene.py).
Les vues 3D sont des maquettes de volumes (three.js), en perspective a deux points de fuite ou en axonometrie.
"""
import math

import facade as F
import plans
from doc import (DATE, DIVISEUR, EXTERIEURS, FRAIS, IMPREVUS, LEGEND, OUT, RATIOS, TVA, M, a2, html, m, page, pct,
                 svg, tableau_surfaces, to_pdf)
from doc_facade import K, REND, img64, page_elevations, page_reference
from projet import OPTION_C, PLUS_VALUES, budget, pu, pu_ligne, surfaces

D = "Option C · Dossier de présentation"
C = OPTION_C
NIV = {"RDC": (0.45, 3.75), "R+1": (3.75, 6.85)}
POCHE = "#2b2c2e"


# ------------------------------------------------------------------------------------------------ coupes
COUPES = {
    # code : (titre, image, axe de coupe, position, centre u, sens px, legende des cotes u)
    "AA": ("Coupe AA, Nord-Sud à travers la cuisine, la terrasse, le patio et la pergola (vue vers l’Ouest)",
           "coupe_AA.png", "x", 12.6, 9.0, -1),
    "BB": ("Coupe BB, Est-Ouest à travers le bio-bassin, le salon, le patio et l’aile de nounou (vue vers le Nord)",
           "coupe_BB.png", "y", 13.0, 10.0, 1),
}


def _intervals(niveau, axis, at, clos=True, codes=None):
    out = []
    for r in C["pieces"]:
        if r["niveau"] != niveau or (clos and not r["clos"]) or (codes and r["code"] not in codes):
            continue
        for x0, y0, x1, y1 in r["rects"]:
            lo, hi, c0, c1 = (y0, y1, x0, x1) if axis == "x" else (x0, x1, y0, y1)
            if c0 < at < c1:
                out.append((lo, hi, r))
    out.sort(key=lambda t: t[0])
    merged = []
    for lo, hi, r in out:   # une piece en L coupee deux fois : un seul intervalle, pas de mur interieur
        if merged and merged[-1][2] is r and abs(merged[-1][1] - lo) < 0.06:
            merged[-1] = (merged[-1][0], hi, r)
        else:
            merged.append((lo, hi, r))
    return merged


def coupe_svg(code):
    titre, fichier, axis, at, centre, sens = COUPES[code]
    x0c, y0c, x1c, y1c = 40, 205, 1560, 780
    w, h = x1c - x0c, y1c - y0c
    pu_ = lambda u: 800 + sens * (u - centre) * K - x0c      # noqa: E731
    pz = lambda z: 500 - (z - 3.6) * K - y0c                 # noqa: E731
    g = [f'<image href="{img64(REND / fichier, (x0c, y0c, x1c, y1c))}" x="0" y="0" width="{w}" height="{h}" opacity="0.55"/>']

    def rect(u0, u1, z0, z1, fill=POCHE, extra=""):
        a, b = sorted((pu_(u0), pu_(u1)))
        g.append(f'<rect x="{a:.1f}" y="{pz(z1):.1f}" width="{b - a:.1f}" height="{pz(z0) - pz(z1):.1f}" fill="{fill}" {extra}/>')

    def brick(u0, u1, z0, z1):
        rect(u0, u1, z0, z1, fill="#c98f6c")
        for z in [z0 + 0.15 * i for i in range(1, int((z1 - z0) / 0.15))]:
            a, b = sorted((pu_(u0), pu_(u1)))
            g.append(f'<line x1="{a:.1f}" y1="{pz(z):.1f}" x2="{b:.1f}" y2="{pz(z):.1f}" stroke="#f3e3d6" stroke-width="1"/>')

    perp = "h" if axis == "x" else "v"
    # sol
    g.append(f'<line x1="0" y1="{pz(0):.1f}" x2="{w}" y2="{pz(0):.1f}" stroke="{POCHE}" stroke-width="2.4"/>')
    for niveau, (zf, zc) in NIV.items():
        ivs = _intervals(niveau, axis, at)
        bounds = sorted({round(v, 2) for lo, hi, _ in ivs for v in (lo, hi)})
        for b in bounds:
            gaps = []
            for niv, x, y, s, wd in C["portes"]:
                line, along = (y, x) if s == "h" else (x, y)
                if niv == niveau and s == perp and abs(line - b) < 0.06 and abs(along - at) < wd / 2:
                    gaps.append((0.0, 2.4 if wd < 1.5 else 2.4, "porte"))
            for niv, s, line, a, b2, z0, z1, kind in F.OUVERTURES:
                if niv == niveau and s == perp and abs(line - b) < 0.06 and a <= at <= b2:
                    gaps.append((z0, z1, kind))
            zs = [(0.0, zc - zf - 0.25)]
            for z0, z1, kind in gaps:
                nz = []
                for a, b2 in zs:
                    if z1 <= a or z0 >= b2:
                        nz.append((a, b2))
                        continue
                    if z0 > a:
                        nz.append((a, z0))
                    if z1 < b2:
                        nz.append((z1, b2))
                zs = nz
                if kind != "claustra":
                    rect(b - 0.03, b + 0.03, zf + z0, zf + z1, fill="#7fa7b8")
            for a, b2 in zs:
                rect(b - 0.1, b + 0.1, zf + a, zf + b2)
        # planchers hauts (dalle 25 cm) des pieces closes
        for lo, hi, r in ivs:
            rect(lo - 0.1, hi + 0.1, zc - 0.25, zc)
            g.append(f'<text x="{(pu_(lo) + pu_(hi)) / 2:.1f}" y="{pz(zf + 1.5):.1f}" font-size="15" text-anchor="middle" '
                     f'fill="#23262b" font-weight="600" paint-order="stroke" stroke="#fff" stroke-width="4">{r["nom"]}</text>')
        if niveau == "RDC" and ivs:
            rect(min(lo for lo, _, _ in ivs) - 0.1, max(hi for _, hi, _ in ivs) + 0.1, 0, zf, fill="#8f8a82")
    # dalles des espaces ouverts de l'etage (terrasse / passerelle, balcon, loggia) et casquettes
    for lo, hi, r in _intervals("R+1", axis, at, clos=False, codes=("balcon",)) + \
            _intervals("RDC", axis, at, clos=False, codes=("terrasse",)):
        if r["nom"] in ("Séchoir couvert", "Préau cuisine africaine"):
            rect(lo, hi, 2.8, 2.9)
            continue
        rect(lo, hi, 3.53, 3.75)
        if r["niveau"] == "R+1" or r["nom"].startswith("Terrasse"):
            g.append(f'<text x="{(pu_(lo) + pu_(hi)) / 2:.1f}" y="{pz(5.3 if r["niveau"] == "R+1" else 1.9):.1f}" font-size="13" '
                     f'text-anchor="middle" fill="#45484e" paint-order="stroke" stroke="#fff" stroke-width="4">{r["nom"]}</text>')
    for x0, y0, x1, y1, z in F.CASQUETTES:
        lo, hi, c0, c1 = (y0, y1, x0, x1) if axis == "x" else (x0, x1, y0, y1)
        if c0 < at < c1:
            rect(lo, hi, z - 0.22, z)
    # toiture, vegetalisation, lanterneau
    for x0, y0, x1, y1, d in F.TOIT:
        X0, Y0, X1, Y1 = x0 - d["w"], y0 - d["n"], x1 + d["e"], y1 + d["s"]
        lo, hi, c0, c1 = (Y0, Y1, X0, X1) if axis == "x" else (X0, X1, Y0, Y1)
        if c0 < at < c1:
            rect(lo, hi, F.TOIT_Z - F.TOIT_EP, F.TOIT_Z)
    for x0, y0, x1, y1 in F.TOITURE_VEGETALE:
        lo, hi, c0, c1 = (y0, y1, x0, x1) if axis == "x" else (x0, x1, y0, y1)
        if c0 < at < c1:
            rect(lo, hi, F.TOIT_Z, F.TOIT_Z + 0.15, fill="#8fa577")
    lx0, ly0, lx1, ly1, lz = F.LANTERNEAU
    lo, hi, c0, c1 = (ly0, ly1, lx0, lx1) if axis == "x" else (lx0, lx1, ly0, ly1)
    if c0 < at < c1:
        rect(lo, lo + 0.15, 6.85, lz)
        rect(hi - 0.15, hi, 6.85, lz)
        rect(lo, hi, lz, lz + 0.04, fill="#7fa7b8")
        g.append(f'<text x="{(pu_(lo) + pu_(hi)) / 2:.1f}" y="{pz(lz + 0.35):.1f}" font-size="13" text-anchor="middle" fill="#2f4a6d">lanterneau</text>')
    # double peau, claustra haute du patio, pergola, bio-bassins, clotures
    for x0, y0, x1, y1, z0, z1 in F.DOUBLE_PEAU:
        lo, hi, c0, c1 = (y0, y1, x0, x1) if axis == "x" else (x0, x1, y0, y1)
        if c0 < at < c1:
            brick(lo, hi, z0, z1)
    if axis == "x" and 9.2 < at < 14.9:
        rect(17.85, 18.0, 0.0, 4.0, fill="#b39a7e")
        rect(16.5, 18.0, 3.0, 3.2, fill="#8a6a4f")
        g.append(f'<text x="{pu_(17.2):.1f}" y="{pz(4.4):.1f}" font-size="13" text-anchor="middle" fill="#45484e">claustra 4 m + pergola</text>')
        g.append(f'<text x="{pu_(14.0):.1f}" y="{pz(1.2):.1f}" font-size="15" text-anchor="middle" fill="#4f6b3a" font-weight="600" '
                 f'paint-order="stroke" stroke="#fff" stroke-width="4">Patio planté</text>')
    for x0, y0, x1, y1 in F.BIO_BASSINS:
        lo, hi, c0, c1 = (y0, y1, x0, x1) if axis == "x" else (x0, x1, y0, y1)
        if c0 < at < c1:
            rect(lo - 0.2, hi + 0.2, 0, 0.32, fill="#8f8a82")
            rect(lo, hi, 0.05, 0.36, fill="#9fc2d1")
            g.append(f'<text x="{(pu_(lo) + pu_(hi)) / 2:.1f}" y="{pz(0.75):.1f}" font-size="13" text-anchor="middle" fill="#2f4a6d">bio-bassin</text>')
    if axis == "y":
        for u0, u1 in ((0.0, 0.2), (19.8, 20.0)):
            rect(u0, u1, 0, 2.2, fill="#8f8a82")
    # niveaux
    for z, t in ((0.0, "±0,00"), (0.45, "+0,45"), (3.75, "+3,75"), (6.85, "+6,85"), (F.TOIT_Z, "+7,07")):
        y = pz(z)
        g.append(f'<line x1="{w - 110}" y1="{y:.1f}" x2="{w - 8}" y2="{y:.1f}" stroke="#8a8e94" stroke-width="1" stroke-dasharray="4 3"/>'
                 f'<text x="{w - 8}" y="{y - 4:.1f}" font-size="14" fill="#6b6f76" text-anchor="end">{t}</text>')
    # hauteurs sous plafond
    g.append(f'<text x="14" y="{pz(2.1):.1f}" font-size="13" fill="#6b6f76">HSP RDC 3,05 m</text>'
             f'<text x="14" y="{pz(5.3):.1f}" font-size="13" fill="#6b6f76">HSP étage 2,85 m</text>')
    sx, sy = 14, h + 20
    g.append(f'<rect x="{sx}" y="{sy}" width="{5 * K:.1f}" height="6" fill="#23262b"/>'
             f'<rect x="{sx + K:.1f}" y="{sy}" width="{K:.1f}" height="6" fill="#fff"/><rect x="{sx + 3 * K:.1f}" y="{sy}" width="{K:.1f}" height="6" fill="#fff"/>'
             f'<rect x="{sx}" y="{sy}" width="{5 * K:.1f}" height="6" fill="none" stroke="#23262b"/>'
             f'<text x="{sx + 5 * K + 8:.1f}" y="{sy + 7}" font-size="14" fill="#6b6f76">5 m</text>')
    nord = "Nord →" if sens == -1 else "Est →"
    g.append(f'<text x="{w - 8}" y="{h + 26}" font-size="14" fill="#6b6f76" text-anchor="end">{nord}</text>')
    return (f'<figure style="margin:0"><figcaption style="font-weight:600;font-size:9.5pt;margin-bottom:1mm">{titre}</figcaption>'
            f'<svg viewBox="0 0 {w} {h + 34}" style="width:100%;max-height:73mm;height:auto;display:block" '
            f'font-family="Inter, sans-serif">{"".join(g)}</svg></figure>')


# ------------------------------------------------------------------------------------------------ parcours
PARCOURS = [   # (libelle, points de passage en m dans le plan, commentaire)
    ("Portillon → porte d’entrée", [(7.5, 0.0), (7.5, 5.0)], "allée sous le porche, à l’écart des voitures"),
    ("Porte d’entrée → salon", [(7.5, 5.0), (7.5, 8.6), (6.8, 9.2), (6.8, 11.0)], "par le hall, WC visiteurs au passage"),
    ("Cuisine → table de la SAM", [(13.2, 7.0), (11.6, 7.0), (9.8, 7.0)], "porte directe, sans passer par le hall"),
    ("Cuisine → cuisine africaine", [(13.2, 7.6), (14.9, 8.0), (16.1, 8.0), (17.0, 6.6)], "par le sas de service à deux portes"),
    ("Portillon de service → cuisine africaine", [(18.25, 0.0), (17.2, 2.6), (17.2, 5.0), (17.0, 6.4)], "livraisons sans traverser la maison"),
    ("Chambre nounou → cuisine", [(16.7, 14.8), (18.5, 14.8), (19.2, 14.8), (19.2, 10.1), (18.5, 10.1), (15.5, 9.4),
                                  (15.5, 8.6), (14.9, 8.0), (13.6, 7.6)], "par le passage Est, la buanderie et le sas"),
    ("Arrivée de l’escalier → salon familial", [(4.4, 8.8), (5.6, 8.8), (7.0, 8.0)], "palier fondu dans le salon familial"),
    ("Chambre parentale → chambre 3", [(6.5, 14.0), (7.7, 12.2), (7.1, 9.2), (9.8, 9.2), (9.8, 9.8), (14.9, 9.8), (16.0, 10.0)],
     "par le dressing, le salon familial et la passerelle"),
    ("Chambre parentale → chambre 2", [(6.5, 14.0), (7.7, 12.2), (7.1, 9.2), (9.5, 8.2), (10.4, 8.2), (11.5, 7.5)],
     "par le dressing et le salon familial"),
]


def longueur(pts):
    return sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))


def page_etude(n):
    rows = "".join(f"<tr><td>{a}</td><td class='n'>{a2(longueur(p))} m</td><td class='muted'>{c}</td></tr>" for a, p, c in PARCOURS)
    s = surfaces(C)
    circ = sum(r["surface"] for r in C["pieces"] if r["clos"] and r["code"] in ("circ", "escalier"))
    se = [("SE ch.2", "1,50 × 2,80", 4.20, "lanière : douche au fond, vasque, WC près de la porte coulissante de 90"),
          ("SE ch.3", "3,60 × 1,40", 5.04, "au-dessus de la SE nounou (gaines superposées), jour haut à l’Est"),
          ("SdB parentale", "3,00 × 2,70", 8.10, "par le dressing : douche à l’italienne, double vasque, WC isolé"),
          ("SE nounou", "3,60 × 1,60", 5.76, "privée, porte depuis la chambre, jour haut sur le passage Est"),
          ("WC visiteurs", "1,40 × 2,00", 2.80, "dans le hall, jour haut sur la façade Nord")]
    se_rows = "".join(f"<tr><td>{a}</td><td class='n'>{b}</td><td class='n'>{a2(c)}</td><td class='muted'>{d}</td></tr>" for a, b, c, d in se)
    regles = [
        ("Couloirs de 1,10 à 1,40 m, de service 1,20 à 1,80 m (Anthurium, JIK, EMIIKA)", "passerelle 1,20 m, sas de service 1,20 m, hall 2,40 m"),
        ("Part des circulations de 13 % (ABYA 2) à 27 % (Anthurium MV)", f"{pct(circ / s['clos'], 0)} : le palier est un salon familial, la passerelle est dehors"),
        ("SE de chambre en lanière 1,40-1,54 × 2,55-2,80 m, 3,8 à 4,9 m²", "SE ch.2 1,50 × 2,80 m (4,2 m²) ; SE ch.3 5,0 m²"),
        ("SdB parentale 6,7 à 8,8 m² par le dressing (Anthurium, ABYA 2)", "8,1 m², dressing traversant de 9,0 m²"),
        ("Chambre de personnel 8 à 12 m² + SE 4 à 5,5 m² sur une cour de service (EMIIKA, Casa Lineal)", "11,9 m² + SE 5,8 m², porte sur le passage Est"),
        ("Cuisine africaine séparée, ventilée sur une cour, reliée par le service (EMIIKA)", "11,5 m² + préau 6,2 m², sas vers la cuisine"),
        ("Séquence jardin d’entrée → bassin → séjour → SAM → patio (Casa Lineal)", "porche → hall → salon sur le bio-bassin Ouest et sur le patio"),
        ("Étage : escalier → salon TV → passerelles → chambres (Casa Lineal)", "escalier → salon familial → passerelle → chambre 3"),
    ]
    reg_rows = "".join(f"<tr><td>{a}</td><td>{b}</td></tr>" for a, b in regles)
    body = f"""
<div class="kicker">2 · Étude des pièces</div>
<h2>Comment les pièces s’enchaînent, se desservent et se ventilent</h2>
<div class="grid g2" style="gap:7mm;margin-top:2mm">
<div><h3 style="margin-top:0">Règles tirées de Capitude et application</h3>
<table class="tight"><tr><th style="width:55%">Règle (projets de la base)</th><th>Option C</th></tr>{reg_rows}</table>
<h3>Salles d’eau</h3>
<table class="tight"><tr><th>Pièce</th><th class="n">Dimensions</th><th class="n">m²</th><th>Disposition</th></tr>{se_rows}</table></div>
<div><h3 style="margin-top:0">Distances de parcours (mesurées sur le plan, de porte à porte)</h3>
<table class="tight"><tr><th>Parcours</th><th class="n">Distance</th><th>Passage</th></tr>{rows}</table>
<div class="callout small" style="margin-top:3mm">Les trois mondes ne se croisent pas : les invités vont de la rue au salon
en moins de 12 m sans voir le service ; le personnel rejoint la cuisine africaine par le portillon de service et la
cuisine par le sas ; la famille monte au salon familial, qui distribue la suite à l’Ouest et les chambres à l’Est par la
passerelle. Le patio est vu depuis le salon, la SAM, la cuisine, la terrasse, la passerelle et la chambre 3.</div></div>
</div>"""
    return page(body, n, D)


# ------------------------------------------------------------------------------------------------ estimatif
def lignes_estimatif():
    k = "C"
    rows = []
    for niv, lab in (("RDC", "Rez-de-chaussée"), ("R+1", "Étage")):
        rows.append(("sec", lab))
        st = 0
        for p in [p for p in C["pieces"] if p["niveau"] == niv]:
            t = p["surface"] * pu(p["code"])
            st += t
            rows.append(("l", p["nom"], RATIOS[p["code"]][0], f'{a2(p["surface"])} m²', m(pu(p["code"])), m(t)))
        rows.append(("sub", f"Sous-total {lab.lower()}", m(st)))
    for titre, liste in (("Aménagements extérieurs et VRD", EXTERIEURS), ("Plus-values du parti (matières, patio, toiture)", PLUS_VALUES)):
        rows.append(("sec", titre))
        st = 0
        for lg in [lg for lg in liste if lg[4].get(k, 0)]:
            q = lg[4][k]
            t = q * pu_ligne(lg)
            st += t
            rows.append(("l", lg[0], f"base ÷ {DIVISEUR}" if lg[5] else "prix de marché", f"{a2(q)} {lg[1]}", m(pu_ligne(lg)), m(t)))
        rows.append(("sub", "Sous-total", m(st)))
    b = budget(C)
    rows.append(("tot", "TOTAL TRAVAUX HT", m(b["travaux"])))
    for lib, taux in FRAIS + [("Imprévus (stade esquisse)", IMPREVUS)]:
        rows.append(("l", lib, "", pct(taux, 2), "", m(taux * b["travaux"])))
    rows.append(("tot", "TOTAL GÉNÉRAL HT", m(b["total_ht"])))
    rows.append(("l", "TVA", "", pct(TVA, 0), "", m(b["tva"])))
    rows.append(("tot", "TOTAL GÉNÉRAL TTC", m(b["total_ttc"])))
    return rows


def tr(r):
    if r[0] == "sec":
        return f'<tr class="sec"><td colspan="5">{r[1]}</td></tr>'
    if r[0] in ("sub", "tot"):
        return f'<tr class="{r[0]}"><td colspan="4">{r[1]}</td><td class="n">{r[2]}</td></tr>'
    return f'<tr><td>{r[1]}</td><td class="small muted">{r[2]}</td><td class="n">{r[3]}</td><td class="n">{r[4]}</td><td class="n">{r[5]}</td></tr>'


def pages_estimatif(n):
    rows = lignes_estimatif()
    per = math.ceil(len(rows) / 3)
    chunks = [rows[i:i + per] for i in range(0, len(rows), per)]
    out = []
    head = '<thead><tr><th>Désignation</th><th>Ratio ou source</th><th class="n">Qté</th><th class="n">PU HT</th><th class="n">Total HT</th></tr></thead>'
    for i, ch in enumerate(chunks):
        intro = ("" if i else f'<p class="small muted" style="max-width:250mm;margin-bottom:2mm">Ratios par type de pièce de la base Éco-données '
                 f'(Pavillon Akpo 2022, Résidences Anthurium 2021, Les Flamboyants, Villa Cacao 6), <b>divisés par {DIVISEUR}</b> sur votre '
                 f'consigne ; postes hors base au prix du marché, sans division. Montants en FCFA HT.</p>')
        out.append(page(f'<div class="kicker">7 · Estimatif sommaire{" (suite)" if i else ""}</div><h2>Option C : estimation par pièce et par poste</h2>'
                        f'{intro}<table class="tight">{head}<tbody>{"".join(tr(r) for r in ch)}</tbody></table>', n + i, D))
    return out


# ------------------------------------------------------------------------------------------------ dossier
def build():
    s, b = surfaces(C), budget(C)
    P = []
    n = 0

    def add(body):
        nonlocal n
        n += 1
        P.append(page(body, n, D))

    add(f'''<div class="cover"><div><div class="kicker">Lot 1728 · Riviera Palmeraie · Cocody, Abidjan</div>
<h1>Maison à patio<br>Option C</h1>
<div class="sub">Dossier de présentation · esquisse</div>
<div class="rule"></div></div>
<img src="{img64(REND / 'clay_arrivee.png', quality=84)}" style="width:100%;height:105mm;object-fit:cover;display:block;border:0.4pt solid #e3ded5"/>
<div class="grid g3 small muted"><div><b>Villa duplex, 4 chambres</b><br>dont une chambre de nounou, cuisine africaine</div>
<div><b>{a2(s["clos"])} m² clos</b><br>{a2(s["ext_couvert"])} m² de terrasses, loggia et balcons</div>
<div><b>{M(b["total_ttc"])} FCFA TTC</b><br>ratios Éco-données ÷ {DIVISEUR}, aléas compris</div></div>
<div class="small muted">Novembre 2026 · Projet personnel · Vues 3D : maquette de volumes, sans matières ni rendu.</div></div>''')

    kpis = [(f'{a2(s["clos"])} m²', "surface close (RDC " + a2(s["RDC"]) + ", étage " + a2(s["R+1"]) + ")"),
            (f'{a2(s["emprise"])} m²', f"emprise, soit {pct(s['emprise'] / 360, 0)} de la parcelle de 360 m²"),
            ("50 m²", "au cœur : patio planté 28 m², terrasse couverte 13,7 m², pergola 8,6 m²"),
            (M(b["travaux"]), "travaux HT, FCFA"), (M(b["total_ttc"]), "total TTC avec honoraires et aléas, FCFA")]
    add(f'''<div class="kicker">Synthèse</div><h1>Une maison tournée vers son patio</h1>
<p class="lead">La maison occupe la bande Nord du lot (20 × 18 m). Elle s’organise autour d’un patio planté à ciel ouvert, au
cœur de la parcelle : salon à l’Ouest, salle à manger et cuisine au Nord, service et nounou à l’Est, fermeture au Sud par une
pergola et une claustra haute qui le protègent des vues du locatif. À l’étage, le salon familial distribue la suite parentale
et, par une passerelle bois sous lanterneau, les chambres. Un passage de 1,50 m fait le tour de la maison.</p>
<div class="kpis" style="grid-template-columns:repeat(5,1fr)">{"".join(f'<div class="kpi"><div class="v">{v}</div><div class="l">{l}</div></div>' for v, l in kpis)}</div>
<div class="grid g3" style="gap:6mm">
<div class="card"><h3>Programme</h3><ul class="small">
<li>Salon 43 m² sur le patio et le bio-bassin, SAM 15 m², cuisine 14 m², WC visiteurs</li>
<li>Cuisine africaine 11,5 m² + préau, sas de service, buanderie-magasin, séchoir couvert</li>
<li>Chambre de nounou 11,9 m² + SE, porte indépendante</li>
<li>Suite parentale (chambre 25,8 m², dressing 9, SdB 8,1, balcon), chambres 2 et 3 avec SE</li>
<li>Guérite + WC gardien, 3 places de parking, aire de livraison</li></ul></div>
<div class="card"><h3>Références Capitude</h3><ul class="small">
<li><b>Palinda Kannangara</b> : Casa Lineal (patio, passerelle, lanterneau, moellons, bois) et Casa Estudio (double peau de brique ajourée)</li>
<li><b>Anthurium MV</b> : séquence hall, SAM, salon, salon familial à l’étage</li>
<li><b>EMIIKA, JIK, ABYA 2</b> : cuisine africaine, sas, chambre de personnel, guérite</li></ul></div>
<div class="card"><h3>Climat</h3><ul class="small">
<li>Brique ajourée au Nord et à l’Ouest : intimité, air, ombre</li>
<li>Débords de 0,6 à 1,6 m, toiture végétalisée, socle +0,45</li>
<li>Patio, bassins et arbre : air plus frais, ventilation traversante</li>
<li>Jours hauts seulement à l’Est (limite à 1,50 m)</li></ul></div></div>''')

    add(f'''<div class="grid g12" style="height:100%"><div class="plan">{svg("masse_C.svg", lambda: plans.plan_masse(C))}
<div class="plan-cap"><span>Plan de masse, villa au Nord et locatif au Sud</span><span>Parcelle 20 × 33 m</span></div></div>
<div><div class="kicker">1 · Site et implantation</div><h2>Une parcelle d’angle coupée en deux bandes</h2>
<ul><li>Lot 1728, îlot 174, Djorogobité 1 : rectangle de 20 × 33 m (660 m²) à l’angle de deux voies en terre, au Nord et à l’Ouest.</li>
<li>Villa sur la bande Nord de 20 × 18 m (360 m²), accès, guérite et parking sur la rue Nord. Locatif R+1 sur la bande Sud,
accès par la rue Ouest.</li>
<li>Reculs supposés : 5 m sur la rue Nord, 3,2 m sur la rue Ouest ; passage de 1,50 m sur les autres côtés, mur séparatif de 2,5 m
avec le locatif.</li>
<li>Climat lagunaire (5° N) : soleil presque au zénith, pignons Est et Ouest exposés, vents de Sud-Ouest, averses violentes
en mai-juin.</li>
<li>Hypothèses réglementaires à confirmer : reculs, emprise, vues droites à 1,90 m (art. 678 du Code civil), débords sur l’espace public.</li></ul>
<h3>Ce que l’implantation donne</h3>
<ul><li>Le patio est au centre géométrique de la villa et au cœur du lot : aucun voisin n’y voit, le locatif est masqué par la
claustra haute.</li><li>Le salon traverse d’Ouest en Est : bio-bassin et jardin d’un côté, patio de l’autre.</li>
<li>L’aile de service longe la limite Est, de plain-pied : elle n’ombre pas le patio le matin.</li></ul></div></div>''')

    n += 1
    P.append(page_etude(n))

    for niveau, lab in (("RDC", "Rez-de-chaussée"), ("R+1", "Étage")):
        k = "RDC" if niveau == "RDC" else "R1"
        add(f'''<div class="grid" style="grid-template-columns:1fr 62mm;gap:6mm;height:100%">
<div class="plan">{svg(f"C_{k}.svg", lambda: plans.plan_villa(C, niveau))}</div>
<div><div class="kicker">3 · Plans</div><h2>{lab}</h2>
<p class="small">{a2(s[niveau])} m² clos{" (guérite comprise)" if niveau == "RDC" else ""}.</p>
{tableau_surfaces(C, (niveau,), total=niveau == "R+1")}
<div style="margin-top:3mm">{LEGEND}</div>
<p class="small muted" style="margin-top:2mm">Fenêtres en bleu (tirets : jours hauts à 1,80 m), brique ajourée en terre cuite,
portes et baies en blanc. Traits de coupe AA et BB au rez-de-chaussée. Mobilier et appareils sanitaires indicatifs.</p></div></div>''')

    add(f'''<div class="grid g2" style="gap:7mm">
<div><div class="kicker">3 · Toiture</div><h2>Plan de toiture</h2>
<img src="{img64(REND / 'toiture.png', (100, 0, 1500, 1000), quality=84)}" style="width:100%;display:block;border:0.4pt solid #e3ded5"/>
<p class="small muted" style="margin-top:1.5mm">Vue de dessus de la maquette, Nord en haut. Toitures-terrasses en béton brut,
végétalisées (substrat 15 cm, jardinières engazonnées en rive) ; lanterneau vitré ventilé sur la passerelle ; patio à ciel ouvert ;
aile de service de plain-pied à l’Est.</p></div>
<div><div class="kicker">3 · Volumes</div><h2>Axonométrie</h2>
<img src="{img64(REND / 'clay_aerien.png', quality=84)}" style="width:100%;display:block;border:0.4pt solid #e3ded5"/>
<p class="small muted" style="margin-top:1.5mm">Depuis le Nord-Ouest : l’étage en béton brut sur un rez-de-chaussée en moellons
côté rues, la double peau de brique ajourée de la loggia Nord, la lanterne d’escalier à l’angle, le bio-bassin devant le salon.</p>
<h3>Eaux pluviales</h3><p class="small">Les toitures se vident vers l’extérieur par des descentes en façade : aucune eau de toiture
dans le patio, sauf celle du lanterneau, recueillie par le bio-bassin. Caniveau grillé et exutoire autour du patio ; pavés drainants
au parking.</p></div></div>''')

    add(f'''<div class="kicker">4 · Coupes</div><h2>Coupes AA et BB</h2>
<div class="grid" style="grid-template-columns:1fr 52mm;gap:6mm;margin-top:2mm">
<div style="display:grid;gap:3mm">{coupe_svg("AA")}{coupe_svg("BB")}</div>
<div class="small muted" style="padding-top:6mm">
<p>Socle à +0,45 m au-dessus du terrain (pluies, voie non revêtue). Hauteur d’étage 3,30 m : 3,05 m sous plafond au
rez-de-chaussée, 2,85 m à l’étage ; dalles de 25 cm.</p>
<p><b>AA</b> : la cuisine et la chambre 2 au Nord derrière la loggia en brique ajourée ; la terrasse couverte et la passerelle
sous le lanterneau ; le patio à ciel ouvert, fermé au Sud par la claustra de 4 m et la pergola.</p>
<p><b>BB</b> : le bio-bassin devant le coulissant du salon, la suite et son balcon derrière la brique ajourée, le patio et son
bassin, l’aile de nounou de plain-pied et la SE de la chambre 3 au-dessus.</p>
<p>Coupe tirée du modèle : en noir les murs et dalles coupés, en bleu les vitrages, en fond la maquette au-delà du plan de coupe.</p></div></div>''')

    for pg in (page_reference, ):
        n += 1
        P.append(pg(n, D).replace("Option C · Façades et patio", "5 · Façades et patio"))
    n += 1
    P.append(page_elevations(n, D, ("N", "O")).replace("Option C · Façades", "5 · Façades"))
    n += 1
    P.append(page_elevations(n, D, ("S", "E")).replace("Option C · Façades", "5 · Façades"))

    add(f'''<div class="kicker">6 · Le patio</div><h2>Le cœur de la maison : ombre, eau, bois et lumière zénithale</h2>
<div class="grid g2" style="gap:6mm;margin-top:2mm">
<figure style="margin:0"><img src="{img64(REND / 'clay_patio.png', quality=82)}" style="width:100%;height:78mm;object-fit:cover;display:block;border:0.4pt solid #e3ded5"/>
<figcaption class="small muted" style="margin-top:1.2mm">Le patio, 8 h 30 en novembre : terrasse couverte sur poteaux bois,
passerelle avec écrans en lattes sous le lanterneau, arbre et bassin.</figcaption></figure>
<figure style="margin:0"><img src="{img64(REND / 'clay_patio_terrasse.png', quality=82)}" style="width:100%;height:78mm;object-fit:cover;display:block;border:0.4pt solid #e3ded5"/>
<figcaption class="small muted" style="margin-top:1.2mm">Depuis la terrasse vers le Sud-Ouest : l’arbre, la pergola et la claustra
haute qui ferme le patio côté locatif, la baie du salon.</figcaption></figure></div>
<div class="grid g3" style="gap:6mm;margin-top:3mm">
<div><h3>Ce qui est conservé</h3><p class="small">Patio planté à ciel ouvert de 28 m², terrasse couverte de 13,7 m² au Nord, pergola
et claustra haute au Sud, passerelle bois de 1,20 m à l’étage, baies du salon (4,0 m) et de la SAM sur le patio.</p></div>
<div><h3>Ce que Casa Lineal apporte</h3><p class="small">Un lanterneau vitré et ventilé au-dessus de la passerelle, des écrans en lattes
de bois, un bio-bassin plus grand au pied de l’arbre (eaux du lanterneau), des sols en ciment poli et des marches en bois sans contremarche.</p></div>
<div><h3>Entretien et usage</h3><p class="small">Bassin à recirculation et plantes épuratrices (pas d’eau stagnante : moustiques),
caniveau grillé périphérique, arbre à racines peu traçantes (frangipanier), éclairage bas pour les soirées.</p></div></div>''')

    add(f'''<div class="kicker">6 · Vues 3D</div><h2>Depuis les deux rues</h2>
<p class="small muted" style="margin:0 0 2mm">Maquette de volumes, perspectives à deux points de fuite (axe de visée horizontal, cadrage par
décentrement) : les verticales restent verticales.</p>
<div class="grid g2" style="gap:6mm">
<figure style="margin:0"><img src="{img64(REND / 'clay_rue.png', quality=82)}" style="width:100%;height:96mm;object-fit:cover;display:block;border:0.4pt solid #e3ded5"/>
<figcaption class="small muted" style="margin-top:1.2mm">Depuis le carrefour au Nord-Ouest, 16 h 30. La clôture (socle en moellons de 1,0 m,
brique ajourée jusqu’à 2,2 m) laisse passer l’air ; au-dessus, la double peau de l’étage et la lanterne d’escalier sous la corniche
de béton brut.</figcaption></figure>
<figure style="margin:0"><img src="{img64(REND / 'clay_arrivee.png', quality=82)}" style="width:100%;height:96mm;object-fit:cover;display:block;border:0.4pt solid #e3ded5"/>
<figcaption class="small muted" style="margin-top:1.2mm">L’arrivée par le portail de la rue Nord, 8 h 30 : porche d’entrée, SAM et cuisine
en moellons sous la loggia ; brique plus percée dans l’axe des baies ; guérite à droite.</figcaption></figure></div>''')

    add(f'''<div class="kicker">7 · Surfaces</div><h2>Tableau des surfaces</h2>
<div class="grid g2" style="gap:7mm;margin-top:2mm"><div>{tableau_surfaces(C, ("RDC",), total=False)}</div>
<div>{tableau_surfaces(C, ("R+1",))}
<table class="tight" style="margin-top:4mm"><tr><th>Récapitulatif</th><th class="n">m²</th></tr>
<tr><td>Surface close, rez-de-chaussée (guérite comprise)</td><td class="n">{a2(s["RDC"])}</td></tr>
<tr><td>Surface close, étage</td><td class="n">{a2(s["R+1"])}</td></tr>
<tr class="sub"><td>Surface close totale</td><td class="n">{a2(s["clos"])}</td></tr>
<tr><td>Terrasses, loggia, balcons, passerelle (couverts)</td><td class="n">{a2(s["ext_couvert"])}</td></tr>
<tr><td>Emprise au sol (hors guérite)</td><td class="n">{a2(s["emprise"])}</td></tr>
<tr><td>Part de la bande villa de 360 m²</td><td class="n">{pct(s["emprise"] / 360, 0)}</td></tr></table></div></div>''')

    for pg in pages_estimatif(n + 1):
        n += 1
        P.append(pg)

    add(f'''<div class="kicker">8 · Suite à donner</div><h2>Points à valider pour passer à l’APS</h2>
<div class="grid g3" style="gap:6mm"><div class="card"><h3>À arbitrer avec vous</h3><ul class="small">
<li>Double peau de brique sur toute la loggia Nord, ou seulement devant les chambres ?</li>
<li>Toiture végétalisée (entretien, étanchéité) ou toiture-terrasse simple avec jardinières de rive ?</li>
<li>Bio-bassin Ouest : bassin planté ou simple jardin de pluie (moins d’entretien) ?</li>
<li>Lanterneau vitré ou passerelle couverte en dalle pleine ?</li></ul></div>
<div class="card"><h3>Technique</h3><ul class="small">
<li>Étude de sol G2 et relevé topographique ; cote d’inondation du secteur.</li>
<li>Brique ajourée : choix du fabricant, résistance du garde-corps de la loggia (1,00 m plein au minimum).</li>
<li>Étanchéité anti-racines et descentes EP en façade ; trop-plein du bio-bassin vers le puisard.</li>
<li>Conduit de la cuisine africaine, cage à gaz, extraction de la buanderie.</li></ul></div>
<div class="card"><h3>Coût</h3><ul class="small">
<li>Le ratio ÷ {DIVISEUR} est au bas de la fourchette : consultation par lots dès l’APS.</li>
<li>Les postes propres à l’écriture Kannangara (brique, moellons, béton brut, toiture, lanterneau, bassins, écrans)
représentent {M(sum(lg[4].get("C", 0) * pu_ligne(lg) for lg in PLUS_VALUES[-7:]))} FCFA HT, chiffrés au prix du marché : à confirmer par devis.</li>
<li>Non compris : foncier, mobilier, climatisation, forage, groupe électrogène, permis et notaire.</li></ul></div></div>''')

    path = OUT / "04_Dossier_Option_C_Lot1728.html"
    path.write_text(html(P, "Option C – Dossier de présentation"))
    to_pdf(path, OUT / "04_Dossier_Option_C_Lot1728.pdf")
    print("ok", len(P), "pages")


if __name__ == "__main__":
    build()
