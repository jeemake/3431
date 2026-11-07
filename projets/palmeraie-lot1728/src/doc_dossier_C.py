"""Dossier de presentation de l'option C v4 (markup du client du 07-11-2026) et du locatif en duplex.

Plans aux conventions Capitude avec les blocs Archibooks (plans_capitude.py), coupes et elevations tirees de la
maquette 3D (rendu/scene.py), rendus realistes generes par IA (Higgsfield) a partir des maquettes de volumes.
"""
import math
import pathlib

import facade as F
import plans_capitude as PC
from blocs_archibooks import Bibliotheque
from doc import (DIVISEUR, EXTERIEURS, FRAIS, IMPREVUS, OUT, RATIOS, TVA, M, a2, html, m, page, pct, to_pdf)
from doc_facade import img64
from projet import LOCATIF_M, LOYERS, MX, OPTION_C, PLUS_VALUES, budget, pu, pu_ligne, surfaces

D = "Option C v4 · Dossier de présentation"
C = OPTION_C
REND = OUT / "rendu"
IA = REND / "ia_v2"
K = 1600 / 24.0
ZC = 4.2                                    # hauteur visee des vues orthographiques
CROP = (40, 90, 1560, 850)                  # z de +10,3 a -1,2
POCHE = "#000000"
NIV_C = {"RDC": (0.45, 3.75), "R+1": (3.75, 6.85), "TOIT": (6.85, 9.45)}
NIV_M = {"RDC": (0.15, 3.15), "R+1": (3.15, 6.15), "TOIT": (6.15, 8.75)}


def ia(nom, repli):
    p = IA / nom
    return p if p.exists() else REND / repli


def cartouche(titre, niveau, echelle="Échelle graphique (1:100 en A3)"):
    return (f'<div class="cartouche"><div><b>Lot 1728 · Riviera Palmeraie</b><br>Villa à patio, option C v4</div>'
            f'<div><b>{titre}</b><br>{niveau}</div><div>{echelle}<br>Esquisse · indice B · 07-11-2026</div>'
            f'<div>Blocs et conventions : Capitude<br>Archibooks (bucket privé)</div></div>')


CSS_PLUS = """
.cartouche { position: absolute; right: 15mm; bottom: 12mm; display: grid; grid-template-columns: auto auto auto auto;
  border: 0.8pt solid #000; font-size: 6.8pt; line-height: 1.3; background: #fff; }
.cartouche div { padding: 1.2mm 2.2mm; border-left: 0.5pt solid #000; } .cartouche div:first-child { border-left: none; }
.planpage svg { height: 150mm; width: auto; max-width: 100%; display: block; margin: 0 auto; }
"""


# ------------------------------------------------------------------------------------------------ coupes
def _intervals(opt, niveau, axis, at, clos=True, codes=None):
    out = []
    for r in opt["pieces"]:
        if r["niveau"] != niveau or (clos and not r["clos"]) or (codes and r["code"] not in codes):
            continue
        for x0, y0, x1, y1 in r["rects"]:
            lo, hi, c0, c1 = (y0, y1, x0, x1) if axis == "x" else (x0, x1, y0, y1)
            if c0 < at < c1:
                out.append((lo, hi, r))
    out.sort(key=lambda t: t[0])
    merged = []
    for lo, hi, r in out:
        if merged and merged[-1][2] is r and abs(merged[-1][1] - lo) < 0.06:
            merged[-1] = (merged[-1][0], hi, r)
        else:
            merged.append((lo, hi, r))
    return merged


def coupe_svg(code, titre, fichier, opt, niv, explicit, axis, at, centre, sens, extras, decor=()):
    x0c, y0c, x1c, y1c = CROP
    w, h = x1c - x0c, y1c - y0c
    pu_ = lambda u: 800 + sens * (u - centre) * K - x0c      # noqa: E731
    pz = lambda z: 500 - (z - ZC) * K - y0c                  # noqa: E731
    lib = Bibliotheque()
    g = [f'<image href="{img64(REND / fichier, CROP)}" x="0" y="0" width="{w}" height="{h}" opacity="0.5"/>']

    def rect(u0, u1, z0, z1, fill=POCHE, extra=""):
        a, b = sorted((pu_(u0), pu_(u1)))
        g.append(f'<rect x="{a:.1f}" y="{pz(z1):.1f}" width="{b - a:.1f}" height="{pz(z0) - pz(z1):.1f}" fill="{fill}" {extra}/>')

    def brique(u0, u1, z0, z1, col="#c98f6c"):
        rect(u0, u1, z0, z1, fill=col)

    def txt(u, z, t, size=14, col="#000", weight=400):
        g.append(f'<text x="{pu_(u):.1f}" y="{pz(z):.1f}" font-size="{size}" text-anchor="middle" fill="{col}" '
                 f'font-weight="{weight}" paint-order="stroke" stroke="#fff" stroke-width="4">{t}</text>')

    perp = "h" if axis == "x" else "v"
    g.append(f'<line x1="0" y1="{pz(0):.1f}" x2="{w}" y2="{pz(0):.1f}" stroke="#000" stroke-width="2.4"/>')
    for niveau, (zf, zc) in niv.items():
        ivs = _intervals(opt, niveau, axis, at)
        bounds = sorted({round(v, 2) for lo, hi, _ in ivs for v in (lo, hi)})
        for b in bounds:
            gaps = []
            for nv, x, y, s, wd in opt["portes"]:
                line, along = (y, x) if s == "h" else (x, y)
                if nv == niveau and s == perp and abs(line - b) < 0.06 and abs(along - at) < wd / 2:
                    gaps.append((0.0, 2.6 if wd > 1.85 else 2.4, "porte"))
            for nv, s, line, a, b2, z0, z1, kind in explicit:
                if nv == niveau and s == perp and abs(line - b) < 0.06 and a <= at <= b2:
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
                    rect(b - 0.03, b + 0.03, zf + z0, zf + z1, fill="#4f8aa3")
                else:
                    brique(b - 0.32 * sens, b - 0.16 * sens, zf + z0, zf + z1)
            for a, b2 in zs:
                rect(b - 0.1, b + 0.1, zf + a, zf + b2)
        for lo, hi, r in ivs:
            rect(lo - 0.1, hi + 0.1, zc - 0.25, zc)
            nom = r["nom"].split(" ", 1)[1] if "logement" in r else r["nom"]
            if hi - lo > 1.6:
                txt((lo + hi) / 2, zf + 1.55, nom, 14, weight=600)
        if niveau == "RDC" and ivs:
            rect(min(lo for lo, _, _ in ivs) - 0.1, max(hi for _, hi, _ in ivs) + 0.1, 0, zf, fill="#8f8a82")
    for item in extras:
        kind = item[0]
        if kind == "dalle":
            _, lo, hi, z, t = item
            rect(lo, hi, z - t, z)
        elif kind == "brique":
            _, lo, hi, z0, z1 = item
            brique(lo, hi, z0, z1)
        elif kind == "beton":
            _, lo, hi, z0, z1 = item
            rect(lo, hi, z0, z1, fill="#b9b6ae")
        elif kind == "veg":
            _, lo, hi, z0, z1 = item
            rect(lo, hi, z0, z1, fill="#8fa577")
        elif kind == "eau":
            _, lo, hi = item
            rect(lo - 0.2, hi + 0.2, 0, 0.32, fill="#8f8a82")
            rect(lo, hi, 0.05, 0.36, fill="#9fc2d1")
        elif kind == "poteau":
            _, u, z0, z1 = item
            rect(u - 0.06, u + 0.06, z0, z1, fill="#333333")
        elif kind == "poutre":
            _, lo, hi, z = item
            rect(lo, hi, z, z + 0.22, fill="#6b4a2f")
        elif kind == "texte":
            _, u, z, t = item
            txt(u, z, t, 13, "#333333")
        elif kind == "fleurs":
            _, lo, hi, z = item
            for k in range(int(abs(hi - lo) * 5)):
                u = lo + (k + 0.5) * (hi - lo) / int(abs(hi - lo) * 5)
                L = 0.5 + 0.5 * math.sin(k * 1.7) ** 2
                g.append(f'<line x1="{pu_(u):.1f}" y1="{pz(z):.1f}" x2="{pu_(u) + 2:.1f}" y2="{pz(z - L):.1f}" stroke="#5d7a4a" stroke-width="1.2"/>'
                         f'<circle cx="{pu_(u) + 2:.1f}" cy="{pz(z - L):.1f}" r="2.4" fill="#d45a3a"/>')
    # blocs Archibooks de coupe : vegetation et personnages (origine au pied)
    for i, u, z, kk, mir in decor:
        g.append(lib.elevation(i, pu_(u), pz(z), K, k=kk, mirror=mir, opacity=0.75 if i.startswith("veg") else 0.85))
    for z, t in ((0.0, "±0,00"), (0.45 if niv is NIV_C else 0.15, "RDC"), (niv["R+1"][0], "R+1"), (niv["TOIT"][0], "toit"),
                 (niv["TOIT"][0] + 2.7, "pergola")):
        y = pz(z)
        lab = f"+{z:.2f}".replace(".", ",") + f" {t}" if z else f"{t}"
        g.append(f'<line x1="{w - 120}" y1="{y:.1f}" x2="{w - 8}" y2="{y:.1f}" stroke="#555" stroke-width="1" stroke-dasharray="4 3"/>'
                 f'<text x="{w - 8}" y="{y - 4:.1f}" font-size="13" fill="#000" text-anchor="end">{lab}</text>')
    sx, sy = 14, h + 18
    g.append(f'<rect x="{sx}" y="{sy}" width="{5 * K:.1f}" height="6" fill="#000"/>'
             f'<rect x="{sx + K:.1f}" y="{sy}" width="{K:.1f}" height="6" fill="#fff"/><rect x="{sx + 3 * K:.1f}" y="{sy}" width="{K:.1f}" height="6" fill="#fff"/>'
             f'<rect x="{sx}" y="{sy}" width="{5 * K:.1f}" height="6" fill="none" stroke="#000"/>'
             f'<text x="{sx + 5 * K + 8:.1f}" y="{sy + 7}" font-size="13" fill="#000">5 m</text>'
             f'<text x="{w - 8}" y="{sy + 8}" font-size="13" fill="#000" text-anchor="end">{"Nord →" if sens == -1 else "Est →"}</text>')
    return (f'<figure style="margin:0"><figcaption style="font-weight:600;font-size:9.2pt;margin-bottom:1mm">{titre}</figcaption>'
            f'<svg viewBox="0 0 {w} {h + 30}" style="width:100%;max-height:76mm;height:auto;display:block" font-family="Inter, sans-serif">'
            f'<defs>{lib.defs()}</defs>{"".join(g)}</svg></figure>')


def coupe_AA():
    T = 6.85
    ex = [("dalle", 4.5, 5.7, 3.75, 0.25), ("dalle", 4.5, 5.7, T, 0.25), ("brique", 4.36, 4.5, 4.85, 7.45),
          ("brique", 4.36, 4.5, 3.75, 4.85), ("beton", 4.5, 5.3, T, T + 0.6), ("fleurs", 4.4, 4.45, T + 0.6),
          ("dalle", 11.2, 13.6, 3.75, 0.25), ("veg", 11.35, 13.45, 3.75, 3.9), ("poteau", 13.5, 0.45, 3.5),
          ("beton", 11.2, 11.35, T, T + 1.0), ("poteau", 5.7, T, T + 2.7), ("poteau", 11.2, T, T + 2.7),
          ("poutre", 5.7, 11.2, T + 2.7), ("eau", 14.3, 15.6), ("veg", 17.82, 18.0, 0, 3.0),
          ("texte", 15.2, 1.4, "Patio planté"), ("texte", 17.9, 3.4, "mur végétalisé"), ("texte", 8.4, T + 1.6, "toit-terrasse sous pergola"),
          ("texte", 2.4, 1.4, "stationnement")]
    decor = [("arbre_frangipanier" and "veg_coupe_petit_feuillu_dense", 16.2, 0.0, 1.25, False),
             ("veg_coupe_fougeres", 14.6, 0.0, 0.9, False), ("pers_tt_03_robe_motifs_face", 12.2, 0.45, 1.0, False),
             ("pers_pmd_108_assis_profil", 8.0, T, 1.0, True)]
    return coupe_svg("AA", "Coupe AA, Nord-Sud : SAM, chambre 1, terrasse, patio et mur végétalisé (vue vers l’Ouest)",
                     "coupe_AA.png", C, NIV_C, F.OUVERTURES, "x", 12.75, 9.0, -1, ex, decor)


def coupe_BB():
    T = 6.85
    ex = [("eau", 0.9, 2.9), ("dalle", 2.7, 3.5, 3.75, 0.22), ("veg", 2.85, 3.45, 4.2, 4.5),
          ("beton", 3.5, 3.65, T, T + 1.0), ("beton", 9.85, 10.0, T, T + 1.0), ("poteau", 3.6, T, T + 2.7),
          ("poteau", 10.0, T, T + 2.7), ("poutre", 3.5, 10.0, T + 2.7), ("eau", 10.6, 12.8),
          ("veg", 15.65, 18.85, 3.75, 3.9), ("texte", 12.9, 1.4, "Patio"), ("texte", 1.9, 1.0, "bio-bassin")]
    decor = [("veg_coupe_palmier_retombant", 1.5, 0.0, 0.7, False), ("veg_coupe_grandes_feuilles", 14.4, 0.0, 0.9, False),
             ("veg_coupe_petit_feuillu_dense", 13.6, 0.0, 1.3, True), ("pers_pmd_042_debout_face", 6.0, 0.45, 1.0, False)]
    return coupe_svg("BB", "Coupe BB, Est-Ouest : bio-bassin, salon, chambre principale, patio, chambre nounou (vue vers le Nord)",
                     "coupe_BB.png", C, NIV_C, F.OUVERTURES, "y", 15.0, 10.0, 1, ex, decor)


def coupe_CC():
    T = 6.15
    expl = [o for k, x0 in enumerate(MX[:3]) for o in F.ouvertures_maison(x0, k == 0)]
    ex = [("beton", 21.0, 21.15, T, T + 1.0), ("beton", 29.85, 30.0, T, T + 1.0), ("beton", 20.85, 21.45, T, T + 0.6),
          ("fleurs", 20.9, 20.95, T + 0.6), ("poteau", 21.15, T, T + 2.5), ("poteau", 26.35, T, T + 2.5),
          ("poutre", 21.1, 26.4, T + 2.5), ("veg", 17.82, 18.0, 0, 3.0), ("texte", 19.5, 1.2, "jardin"),
          ("texte", 31.5, 1.2, "stationnement")]
    decor = [("veg_coupe_bosquet_etage", 19.6, 0.0, 0.42, False), ("pers_tt_02_marche_profil_sac", 31.2, 0.0, 1.0, True)]
    return coupe_svg("CC", "Coupe CC, Nord-Sud sur la maison 2 : jardin, séjour, cuisine, chambre, SE, toit-terrasse",
                     "coupe_CC.png", LOCATIF_M, NIV_M, expl, "x", 12.0, 25.5, -1, ex, decor)


# ------------------------------------------------------------------------------------------------ elevations
ELEV = {   # code : (titre, image, sens, centre)
    "N1": ("Façade Nord, variante 1 : brique semi-perforée", "elev_N_V1.png", -1, 10.5),
    "N2": ("Façade Nord, variante 2 : résille de béton triangulée", "elev_N_V2.png", -1, 10.5),
    "O": ("Façade Ouest, sur la rue latérale", "elev_O.png", 1, 10.5),
    "S": ("Façade Sud, sur le mur végétalisé", "elev_S.png", 1, 10.5),
    "E": ("Façade Est, en limite à 1 m", "elev_E.png", -1, 10.5),
}
NOTES = {
    "N": [(11.2, 8.9, "Pergola bois sur poteaux acier, toit-terrasse", 0), (5.0, 7.3, "Jardinière : firecracker plants", 1),
          (9.0, 5.5, "Double peau semi-perforée devant la loggia-rangement de 1,2 m", 0),
          (17.8, 2.0, "Préau de la cuisine africaine", 2), (7.5, 1.4, "Entrée (axe 7,5)", 2), (11.75, 1.7, "SAM", 2),
          (14.5, 1.7, "Cuisine", 2), (3.0, 4.5, "Lanterne d’escalier", 1)],
    "O": [(7.8, 8.0, "Édicule et lanterne d’escalier en brique ajourée", 0), (12.5, 5.6, "SdB", 1),
          (15.4, 5.0, "Chambre principale, jardinière", 0), (15.4, 1.4, "Salon : coulissant sur le bio-bassin", 2),
          (12.5, 1.7, "Salon", 2)],
    "S": [(6.2, 5.6, "Chambre principale (jour haut)", 0), (12.75, 5.6, "Galerie vitrée, écrans bois", 1),
          (6.2, 1.7, "Salon, vue sur le mur végétalisé", 2), (17.25, 1.7, "Chambre nounou", 2)],
    "E": [(7.25, 5.6, "Chambre 2 : jour haut", 0), (14.0, 2.0, "Bureau, SE et chambre nounou : jours hauts", 2),
          (4.0, 2.0, "Cuisine africaine, préau", 2)],
}


def elevation_svg(code):
    titre, fichier, sens, centre = ELEV[code]
    notes = NOTES[code[0]]
    x0c, y0c, x1c, y1c = CROP
    w, h = x1c - x0c, y1c - y0c
    px = lambda u: 800 + sens * (u - centre) * K - x0c      # noqa: E731
    pz = lambda z: 500 - (z - ZC) * K - y0c                 # noqa: E731
    g = [f'<image href="{img64(REND / fichier, CROP)}" x="0" y="0" width="{w}" height="{h}"/>']
    for z, t in ((0.0, "±0,00"), (0.45, "+0,45 RDC"), (3.75, "+3,75 R+1"), (6.85, "+6,85 toit"), (9.55, "+9,55 pergola")):
        y = pz(z)
        g.append(f'<line x1="{w - 128}" y1="{y:.1f}" x2="{w - 8}" y2="{y:.1f}" stroke="#555" stroke-width="1" stroke-dasharray="4 3"/>'
                 f'<text x="{w - 8}" y="{y - 4:.1f}" font-size="14" fill="#000" text-anchor="end">{t}</text>')
    rows_up, rows_dn = [22, 48, 74], [h - 46, h - 18]
    used = {}
    for u, z, t, rang in sorted(notes, key=lambda n: px(n[0])):
        x, y = px(u), pz(z)
        half = len(t) * 4.6
        cand = rows_up if rang < 2 else rows_dn
        ty = cand[-1]
        for r in cand:
            if used.get(r, -1e9) < x - half - 10:
                ty = r
                break
        used[ty] = x + half
        g.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="#000"/>'
                 f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{x:.1f}" y2="{ty + (6 if rang < 2 else -18):.1f}" stroke="#000" stroke-width="1"/>'
                 f'<text x="{x:.1f}" y="{ty:.1f}" font-size="16" fill="#000" text-anchor="middle" font-weight="500" '
                 f'paint-order="stroke" stroke="#fff" stroke-width="4">{t}</text>')
    sx, sy = 14, h + 18
    g.append(f'<rect x="{sx}" y="{sy}" width="{5 * K:.1f}" height="6" fill="#000"/>'
             f'<rect x="{sx + K:.1f}" y="{sy}" width="{K:.1f}" height="6" fill="#fff"/><rect x="{sx + 3 * K:.1f}" y="{sy}" width="{K:.1f}" height="6" fill="#fff"/>'
             f'<rect x="{sx}" y="{sy}" width="{5 * K:.1f}" height="6" fill="none" stroke="#000"/>'
             f'<text x="{sx + 5 * K + 8:.1f}" y="{sy + 7}" font-size="13" fill="#000">5 m</text>')
    return (f'<figure style="margin:0"><figcaption style="font-weight:600;font-size:9.2pt;margin-bottom:1mm">{titre}</figcaption>'
            f'<svg viewBox="0 0 {w} {h + 30}" style="width:100%;max-height:74mm;height:auto;display:block" font-family="Inter, sans-serif">'
            f'{"".join(g)}</svg></figure>')


# ------------------------------------------------------------------------------------------------ parcours
PARCOURS = [
    ("Portillon → porte d’entrée", [(7.7, 0.0), (7.7, 4.5), (7.5, 5.7)], "sous le passage couvert, à l’écart des voitures"),
    ("Porte d’entrée → salon", [(7.5, 5.7), (7.5, 10.6), (7.6, 11.2), (7.0, 13.0)], "par le hall ; WC visiteurs au passage"),
    ("Cuisine → table de la SAM", [(15.0, 8.4), (13.5, 7.6), (11.0, 8.4)], "porte directe"),
    ("Cuisine → cuisine africaine", [(15.0, 9.5), (16.5, 10.4), (17.75, 10.2), (17.75, 9.6), (17.75, 7.6)], "par la buanderie-sas"),
    ("Portillon de service → cuisine africaine", [(18.25, 0.0), (17.25, 2.6), (17.25, 5.7), (17.5, 7.0)], "livraisons sans traverser la maison"),
    ("Chambre nounou → cuisine", [(17.25, 15.8), (19.0, 15.8), (19.5, 15.8), (19.5, 10.4), (19.0, 10.4), (16.5, 10.4), (15.0, 9.5)],
     "par le passage Est et la buanderie"),
    ("Bureau → hall", [(17.2, 12.2), (15.5, 12.2), (11.75, 12.0), (11.75, 11.2), (9.5, 9.0), (8.5, 7.6)], "par la terrasse et la SAM"),
    ("Escalier → salon familial", [(5.0, 8.6), (6.5, 8.6), (8.2, 8.4)], "arrivée directe dans le salon familial"),
    ("Chambre principale → chambre 1", [(6.7, 15.4), (8.3, 13.8), (8.3, 11.2), (9.5, 10.6), (11.75, 10.6), (11.75, 8.0)],
     "par le dressing, le salon familial et la galerie"),
    ("Chambre principale → chambre 2", [(6.7, 15.4), (8.3, 13.8), (8.3, 11.2), (9.5, 10.6), (15.5, 10.6), (17.0, 9.5)],
     "galerie de 1,20 m vitrée sur le patio"),
]


def L(pts):
    return sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))


def tableau_surf(opt, niveaux):
    rows = []
    tot = 0
    for niv in niveaux:
        ps = [p for p in opt["pieces"] if p["niveau"] == niv]
        if not ps:
            continue
        lab = {"RDC": "Rez-de-chaussée", "R+1": "Étage", "TOIT": "Niveau pergola (toit-terrasse)"}[niv]
        rows.append(f'<tr class="sec"><td colspan="3">{lab}</td></tr>')
        st = 0
        for p in ps:
            nom = p["nom"]
            rows.append(f'<tr><td>{nom}{"" if p["clos"] else " <span class=muted>(hors clos)</span>"}</td><td>{PC.usage(p) or "ext."}</td>'
                        f'<td class="n">{a2(p["surface"])}</td></tr>')
            if p["clos"] and niv != "TOIT":
                st += p["surface"]
        if niv != "TOIT":
            rows.append(f'<tr class="sub"><td colspan="2">Surface close {lab.lower()}</td><td class="n">{a2(st)}</td></tr>')
            tot += st
    return f'<table class="tight"><tr><th>Pièce</th><th>Usage</th><th class="n">m²</th></tr>{"".join(rows)}</table>', tot


# ------------------------------------------------------------------------------------------------ estimatif
def lignes(opt):
    k = opt["code"]
    rows = []
    for niv, lab in (("RDC", "Rez-de-chaussée"), ("R+1", "Étage"), ("TOIT", "Niveau pergola")):
        ps = [p for p in opt["pieces"] if p["niveau"] == niv]
        if not ps:
            continue
        rows.append(("sec", lab))
        agg = {}
        for p in ps:
            key = p["nom"].split(" ", 1)[1] if "logement" in p else p["nom"]
            a = agg.setdefault(key, [0, p["code"]])
            a[0] += p["surface"]
        st = 0
        for key, (sf, code) in agg.items():
            t = sf * pu(code)
            st += t
            rows.append(("l", key + (" (× 3)" if k == "M" and "Allée" not in key else ""), RATIOS[code][0], f"{a2(sf)} m²", m(pu(code)), m(t)))
        rows.append(("sub", f"Sous-total {lab.lower()}", m(st)))
    for titre, liste in (("Aménagements extérieurs et VRD", EXTERIEURS), ("Plus-values du parti (matières, patio, toiture)", PLUS_VALUES)):
        ls = [lg for lg in liste if lg[4].get(k, 0)]
        if not ls:
            continue
        rows.append(("sec", titre))
        st = 0
        for lg in ls:
            q = lg[4][k]
            t = q * pu_ligne(lg)
            st += t
            rows.append(("l", lg[0], f"base ÷ {DIVISEUR}" if lg[5] else "prix de marché", f"{a2(q)} {lg[1]}", m(pu_ligne(lg)), m(t)))
        rows.append(("sub", "Sous-total", m(st)))
    b = budget(opt)
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


def pages_estimatif(opt, titre, n0, npages):
    rows = lignes(opt)
    per = math.ceil(len(rows) / npages)
    head = '<thead><tr><th>Désignation</th><th>Ratio ou source</th><th class="n">Qté</th><th class="n">PU HT</th><th class="n">Total HT</th></tr></thead>'
    out = []
    for i in range(npages):
        ch = rows[i * per:(i + 1) * per]
        intro = ("" if i else f'<p class="small muted" style="max-width:250mm;margin-bottom:2mm">Ratios par type de pièce de la base '
                 f'Éco-données (Pavillon Akpo 2022, Résidences Anthurium 2021, Les Flamboyants, Villa Cacao 6), <b>divisés par {DIVISEUR}</b> '
                 f'sur votre consigne ; postes hors base au prix du marché, sans division. Montants en FCFA HT.</p>')
        out.append(page(f'<div class="kicker">9 · Estimatif sommaire{" (suite)" if i else ""}</div><h2>{titre}</h2>{intro}'
                        f'<table class="tight">{head}<tbody>{"".join(tr(r) for r in ch)}</tbody></table>', n0 + i, D))
    return out


def fig(src, cap, hmm=62, q=82):
    return (f'<figure style="margin:0"><img src="{img64(src, quality=q)}" style="width:100%;height:{hmm}mm;object-fit:cover;display:block;'
            f'border:0.4pt solid #e3ded5"/><figcaption class="small muted" style="margin-top:1.2mm">{cap}</figcaption></figure>')


# ------------------------------------------------------------------------------------------------ dossier
def build():
    s, b = surfaces(C), budget(C)
    sm, bm = surfaces(LOCATIF_M), budget(LOCATIF_M)
    P = []
    n = 0

    def add(body, cls=""):
        nonlocal n
        n += 1
        P.append(page(body, n, D, cls))

    svgs = {}
    for nv in ("RDC", "R+1", "TOIT"):
        svgs["C" + nv] = PC.villa(nv)
        svgs["M" + nv] = PC.maisons(nv)
        (OUT / "svg" / f"C4_{nv.replace('+', '')}.svg").write_text(svgs["C" + nv])
        (OUT / "svg" / f"M_{nv.replace('+', '')}.svg").write_text(svgs["M" + nv])

    # 1 couverture
    add(f'''<div class="cover"><div><div class="kicker">Lot 1728 · Riviera Palmeraie · Cocody, Abidjan</div>
<h1>Maison à patio<br>et trois maisons en duplex</h1>
<div class="sub">Option C v4 · dossier de présentation · esquisse</div><div class="rule"></div></div>
<img src="{img64(ia('arrivee_V1_a.jpg', 'clay_arrivee_V1.png'), quality=84)}" style="width:100%;height:108mm;object-fit:cover;display:block"/>
<div class="grid g3 small muted"><div><b>Villa : {a2(s["clos"])} m² clos</b><br>4 chambres dont nounou, bureau, cuisine africaine, toit-terrasse sous pergola</div>
<div><b>Locatif : 3 maisons de {a2(sm["clos"] / 3)} m²</b><br>duplex 2 chambres, jardin, toit-terrasse sous pergola</div>
<div><b>{M(b["total_ttc"] + bm["total_ttc"])} FCFA TTC</b><br>villa et locatif, ratios Éco-données ÷ {DIVISEUR}</div></div>
<div class="small muted">7 novembre 2026 · Projet personnel · Image : rendu d’ambiance généré par IA (Higgsfield) à partir de la maquette.</div></div>''')

    # 2 synthese
    kp = [(f'{a2(s["clos"])} m²', f'villa close (RDC {a2(s["RDC"])}, étage {a2(s["R+1"])})'),
          ("110 m²", "toit-terrasse sous pergola de la villa"),
          (f'{a2(sm["clos"])} m²', "locatif : 3 duplex de 108 m², jardins et pergolas"),
          (M(b["total_ttc"]), "villa, total TTC, FCFA"), (M(bm["total_ttc"]), "locatif, total TTC, FCFA")]
    add(f'''<div class="kicker">Synthèse</div><h1>Votre markup, appliqué à la trame</h1>
<p class="lead">Les trames de votre markup du 7 novembre sont reprises telles quelles, avec deux ajustements pour tenir dans la bande
de 18 m : stationnement de 4,50 m au Nord et passages de 1,00 m à l’Est et au fond. La villa garde son patio au cœur ; l’étage se
dessine en L (salon familial et deux chambres sur la rue, chambre principale au fond) ; l’escalier monte à un toit-terrasse sous
pergola, bordé d’une jardinière de firecracker plants qui retombe sur la double peau Nord. Au fond, un mur végétalisé. Au Sud,
trois maisons en duplex, chacune avec son jardin, son stationnement et sa pergola.</p>
<div class="kpis" style="grid-template-columns:repeat(5,1fr)">{"".join(f'<div class="kpi"><div class="v">{v}</div><div class="l">{lb}</div></div>' for v, lb in kp)}</div>
<div class="grid g3" style="gap:6mm">
<div class="card"><h3>Trame retenue (m)</h3><p class="small"><b>Villa, en X</b> : recul Ouest 3,5 · 3 · 3,5 · 3,5 · 2 · 3,5 · passage 1.<br>
<b>Villa, en Y</b> : stationnement 4,5 · bande avant 1,2 · 5,5 · 5,8 · passage 1 · mur végétalisé.<br>
<b>Étage, en Y</b> : 1,2 (loggia-rangement) · 5,5 · 2,6 (SdB, dressing) · 3,2 (chambre principale).<br>
<b>Locatif</b> : allée 2 · 6 · 6 · 6 en X ; jardins 3 · 5,5 · 3,5 · stationnement 3 en Y.</p></div>
<div class="card"><h3>Ce qui change</h3><ul class="small">
<li>Bureau au RDC, chambre 3 supprimée : 4 chambres dont la nounou</li>
<li>Étage en L, galerie vitrée sur le patio au lieu de la passerelle</li>
<li>Niveau pergola, jardinière continue, mur végétalisé</li>
<li>Double peau Nord en deux variantes</li>
<li>Locatif : 3 maisons duplex au lieu de 6 logements</li></ul></div>
<div class="card"><h3>Représentation</h3><ul class="small">
<li>Plans aux conventions Capitude : aplats à 45 % par usage, légende, trame d’axes, murs noirs</li>
<li>Blocs Archibooks de la base : portes, arbres, sols, eau, végétation et personnages de coupe</li>
<li>Rendus réalistes générés par IA à partir des maquettes, en dernière partie</li></ul></div></div>''')

    # 3 site / masse
    add(f'''<div class="grid g12" style="height:100%"><div><img src="{img64(REND / 'toiture.png', (240, 0, 1360, 1000), quality=84)}" style="width:100%;display:block;border:0.4pt solid #e3ded5"/>
<p class="small muted">Vue de dessus de la maquette, Nord en haut : villa, patio et pergola au Nord, trois maisons au Sud, mur végétalisé entre les deux.</p></div>
<div><div class="kicker">1 · Site et implantation</div><h2>Une parcelle d’angle de 20 × 33 m, deux bandes</h2>
<ul><li>Lot 1728, îlot 174, Djorogobité 1 : 660 m² à l’angle de deux voies en terre, au Nord et à l’Ouest.</li>
<li>Villa sur la bande Nord de 20 × 18 m : stationnement de 3 places sur la rue Nord (4,50 m), guérite, local GE et niche à compteurs
à l’angle Nord-Ouest, portillon de service et séchoir au Nord-Est.</li>
<li>Locatif sur la bande Sud de 20 × 15 m : allée piétonne de 2 m le long de la rue Ouest, trois maisons de 6 × 9 m, jardins
privés au Nord contre le mur végétalisé, stationnement au Sud.</li>
<li>Climat lagunaire (5° N) : soleil presque au zénith, pignons Est et Ouest exposés, vents de Sud-Ouest, averses violentes.</li>
<li>À confirmer : reculs, emprise, hauteur (le niveau pergola n’est pas un étage clos), vues droites à 1,90 m vers l’Est, accès
du stationnement locatif.</li></ul></div></div>''')

    # 4 references et regles Capitude
    R = F.REFERENCE
    rep = "".join(f"<tr><td style='font-weight:600;width:38mm'>{a}</td><td>{bb}</td></tr>" for a, bb in R["repris"])
    add(f'''<div class="kicker">2 · Références et règles Capitude</div><h2>Matière de Palinda Kannangara, représentation Capitude</h2>
<div class="grid g2" style="gap:7mm"><div><h3 style="margin-top:0">{R["nom"]}</h3><p class="small">{R["pourquoi"]}</p>
<table class="tight">{rep}</table>
<p class="small muted" style="margin-top:2mm">Variante 2 de la double peau : Typologie urbaine 8 (Capitude), « claustra en résille
triangulée en nu extérieur, devant une loggia filante ». Les images des planches ne sont pas consultées : la lecture repose sur les
données et les légendes de la base.</p></div>
<div><h3 style="margin-top:0">Règles graphiques appliquées (table regles_agents)</h3><table class="tight">
<tr><td><b>GRAPHISME-APLATS-LEGENDE-TRAME</b></td><td>Aplats pastel à 45 % par usage, légende sur chaque plan, trame d’axes 1-6 / A-E en périphérie</td></tr>
<tr><td><b>GRAPHISME-OPACITES</b></td><td>Murs, cotes, textes noirs opaques ; végétation 45-65 %, sols 55-70 %, mobilier 80 %, eau 30 %</td></tr>
<tr><td><b>GRAPHISME-ELCROQUIS-EXTERIEURS</b></td><td>Sols différenciés et recadrés au contour, strates végétales, bassins</td></tr>
<tr><td><b>BLOCS-ARCHIBOOKS</b></td><td>Portes, arbres, textures et eau issus du bucket privé, maîtres inchangés, SHA-256 contrôlés</td></tr>
<tr><td><b>PAYSAGE-TROPICAL-COMPOSITION</b></td><td>Arbres variés selon leur rôle : repère du patio, ombre Ouest, angle des rues, fond de parcelle</td></tr>
<tr><td><b>VEGETATION / PERSONNAGES-COUPES</b></td><td>Blocs veg_coupe_* et personnages pers_tt / pers_pmd dans les coupes</td></tr></table>
<h3>Blocs Archibooks utilisés</h3><p class="small">porte_battante_90, porte_double · arbre_frangipanier, arbre_feuilles_ovales,
arbre_touffes_frisees, arbre_feuillage_dense · texture_paves, texture_pierre_bandes, texture_granulat_fin, texture_couvre_sol,
texture_massif_tropical, texture_pas_irreguliers, texture_eau · veg_coupe_petit_feuillu_dense, veg_coupe_palmier_retombant,
veg_coupe_fougeres, veg_coupe_grandes_feuilles, veg_coupe_bosquet_etage · pers_tt_02, pers_tt_03, pers_pmd_042, pers_pmd_108.</p>
<p class="small"><b>Absents du catalogue (signalés)</b> : appareils sanitaires, lits, canapés, tables, plans de cuisine, voitures,
cadre et cartouche. Ils sont dessinés ici en symboles neutres provisoires, à remplacer quand la bibliothèque les aura.</p></div></div>''')

    # 5 etude
    circ = sum(r["surface"] for r in C["pieces"] if r["clos"] and r["code"] in ("circ", "escalier") and r["niveau"] != "TOIT")
    rows = "".join(f"<tr><td>{a}</td><td class='n'>{a2(L(p))} m</td><td class='muted'>{c}</td></tr>" for a, p, c in PARCOURS)
    se = [("SE ch.1", "2,00 × 2,15", 4.30, "lanière, porte depuis la chambre, jour haut sur la loggia"),
          ("SE ch.2", "2,00 × 2,15", 4.30, "dos à dos avec la SE ch.1 (une gaine)"),
          ("SdB parentale", "3,00 × 2,60", 7.80, "par le dressing : douche à l’italienne, double vasque, WC"),
          ("SE nounou", "3,50 × 1,40", 4.90, "lanière, jours hauts sur le patio et le passage Est"),
          ("WC visiteurs", "3,00 × 1,30", 3.90, "depuis le hall, sous l’escalier, jour haut à l’Ouest")]
    se_rows = "".join(f"<tr><td>{a}</td><td class='n'>{bb}</td><td class='n'>{a2(c)}</td><td class='muted'>{d}</td></tr>" for a, bb, c, d in se)
    add(f'''<div class="kicker">3 · Étude des pièces</div><h2>Enchaînements, distances et salles d’eau</h2>
<div class="grid g2" style="gap:7mm"><div><h3 style="margin-top:0">Distances de parcours, de porte à porte</h3>
<table class="tight"><tr><th>Parcours</th><th class="n">Distance</th><th>Passage</th></tr>{rows}</table>
<p class="small" style="margin-top:2mm">Circulations closes (hall, escaliers, galerie) : {a2(circ)} m², soit {pct(circ / s["clos"], 0)} de la
surface close, dans la fourchette des villas de la base (13 % ABYA 2 à 27 % Anthurium).</p></div>
<div><h3 style="margin-top:0">Salles d’eau</h3><table class="tight"><tr><th>Pièce</th><th class="n">Dimensions</th><th class="n">m²</th><th>Disposition</th></tr>{se_rows}</table>
<div class="callout small" style="margin-top:3mm">Invités, famille et service ne se croisent pas : la rue mène au salon par le hall
sans voir le service ; le personnel entre par le portillon de service et rejoint la cuisine par la buanderie-sas ; la nounou a sa
porte sur le passage Est. À l’étage, le salon familial distribue la suite au fond du L et, par la galerie vitrée sur le patio, les
chambres 1 et 2.</div></div></div>''')

    # 6-8 plans villa
    for key, nv, lab in (("CRDC", "RDC", "Rez-de-chaussée"), ("CR+1", "R+1", "Étage"), ("CTOIT", "TOIT", "Niveau pergola")):
        sf = s.get(nv)
        add(f'''<div class="kicker">4 · Plans de la villa</div><h2 style="margin-bottom:1mm">{lab}{f" · {a2(sf)} m² clos" if sf else " · toit-terrasse de 110 m² sous pergola"}</h2>
<div class="planpage">{svgs[key]}</div>{cartouche("Plan " + lab.lower(), "Villa, option C v4")}''')

    # 9 coupes
    add(f'''<div class="kicker">5 · Coupes</div><h2>Coupes AA et BB</h2>
<div class="grid" style="grid-template-columns:1fr 50mm;gap:6mm;margin-top:1mm"><div style="display:grid;gap:3mm">{coupe_AA()}{coupe_BB()}</div>
<div class="small muted" style="padding-top:5mm"><p>Socle à +0,45 m. Étage à 3,30 m : 3,05 m sous plafond au RDC, 2,85 m à l’étage.
Toit-terrasse à +6,85 m, acrotère de 1,00 m, pergola à +9,55 m.</p><p>En noir les murs et dalles coupés, en bleu les vitrages,
en terre cuite la double peau ; au-delà, la maquette. Végétation et personnages : blocs Archibooks de coupe.</p></div></div>''')

    # 10 double peau : deux variantes
    add(f'''<div class="kicker">6 · Façade Nord</div><h2>La double peau semi-perforée : deux propositions</h2>
<div class="grid g2" style="gap:6mm;margin-top:1mm">
<div>{elevation_svg("N1")}<p class="small" style="margin-top:1mm"><b>V1 · {F.VARIANTES["V1"][0]}</b> (Casa Estudio, Capitude). {F.VARIANTES["V1"][2]}</p></div>
<div>{elevation_svg("N2")}<p class="small" style="margin-top:1mm"><b>V2 · {F.VARIANTES["V2"][0]}</b> (Typologie urbaine 8, Capitude). {F.VARIANTES["V2"][2]}</p></div>
{fig(ia("arrivee_V1_a.jpg", "clay_arrivee_V1.png"), "V1 : arrivée depuis la rue Nord, rendu d’ambiance IA.", 58)}
{fig(ia("arrivee_V2.jpg", "clay_arrivee_V2.png"), "V2 : même vue, résille de béton, rendu d’ambiance IA.", 58)}</div>''')

    # 11 elevations
    add(f'''<div class="kicker">7 · Élévations</div><h2>Façades Ouest, Sud et Est</h2>
<div class="grid g2" style="gap:5mm;margin-top:1mm">{elevation_svg("O")}{elevation_svg("S")}{elevation_svg("E")}
<div class="small muted" style="padding-top:6mm"><p><b>Alignements.</b> Axes verticaux communs aux niveaux (Nord 7,5 / 11,75 /
14,5 / 17,25 ; Ouest 7,8 / 12,5 / 15,4) ; linteaux à 2,40 m ; allèges à 1,00 m (fenêtres) et 1,80 m (jours hauts).</p>
<p><b>Est</b> à 1 m de la limite : jours hauts seulement. <b>Sud</b> sur le mur végétalisé : la chambre principale garde un jour
haut au-dessus du lit. <b>Ouest</b> : la lanterne d’escalier en brique monte jusqu’à l’édicule du toit.</p>
<p>Élévations tirées de la maquette 3D, clôtures et arbres masqués, lumière conventionnelle à 45°.</p></div></div>''')

    # 12 patio et verdure
    add(f'''<div class="kicker">8 · Patio, toit et limites végétales</div><h2>La maison plongée dans la verdure</h2>
<div class="grid g2" style="gap:6mm;margin-top:2mm">
{fig(ia("patio.jpg", "clay_patio.png"), "Le patio à 8 h 30 : terrasse couverte, frangipanier, bio-bassin, galerie vitrée à écrans bois, mur végétalisé au fond.", 70)}
{fig(ia("toit.jpg", "clay_toit.png"), "Le toit-terrasse sous la pergola, jardinière de firecracker plants sur la façade Nord.", 70)}</div>
<div class="grid g3" style="gap:6mm;margin-top:3mm">
<div><h3>Mur végétalisé</h3><p class="small">En limite villa / locatif sur 20 m, 3 m de haut : treillis inox, jardinières et
goutte-à-goutte, plantes grimpantes et retombantes ; il ferme le patio au Sud et donne aux jardins des maisons une vue verte.</p></div>
<div><h3>Firecracker plants</h3><p class="small">Russelia equisetiformis : tiges fines retombantes, fleurs tubulaires rouge orangé
presque toute l’année, plein soleil, peu d’eau. Jardinière continue de 15,5 m en tête de la façade Nord, et sur chaque maison.</p></div>
<div><h3>Patio et bassins</h3><p class="small">Frangipanier repère, sous-strate tropicale, pas japonais vers le fond, bio-bassin
à recirculation ; bio-bassin Ouest devant le coulissant du salon. Pas d’eau stagnante (moustiques) : pompe et plantes épuratrices.</p></div></div>''')

    # 13 vues
    add(f'''<div class="kicker">8 · Vues</div><h2>Depuis la rue et l’angle des deux voies</h2>
<div class="grid g2" style="gap:6mm;margin-top:2mm">
{fig(ia("rue.jpg", "clay_rue.png"), "Depuis le carrefour Nord-Ouest, 16 h 30 : clôture en moellons et brique ajourée, lanterne d’escalier, pergola.", 78)}
{fig(ia("arrivee_V1_b.jpg", "clay_arrivee_V1.png"), "Arrivée par temps gris d’août, variante 1 de la double peau.", 78)}</div>
<p class="small muted" style="margin-top:2mm">Rendus d’ambiance générés par IA (Higgsfield, Nano Banana Pro) à partir des maquettes de
volumes : la géométrie est imposée, les matières, la végétation et les personnages sont interprétés. Images indicatives.</p>''')

    # 14 axonometrie
    add(f'''<div class="kicker">8 · Volumes</div><h2>Axonométries</h2>
<div class="grid g2" style="gap:6mm;margin-top:2mm">
{fig(REND / "clay_aerien.png", "Ensemble depuis le Nord-Ouest : villa, patio, pergolas et trois maisons au fond.", 92)}
{fig(REND / "clay_locatif.png", "Les trois maisons depuis le Sud-Ouest : stationnement, édicules et pergolas.", 92)}</div>''')

    # 15-17 locatif
    add(f'''<div class="kicker">10 · Locatif</div><h2 style="margin-bottom:1mm">Trois maisons duplex · rez-de-chaussée</h2>
<div class="planpage">{svgs["MRDC"]}</div>{cartouche("Plan du rez-de-chaussée", "Locatif, 3 maisons")}''')
    for key, lab in (("MR+1", "étage"), ("MTOIT", "niveau pergola")):
        add(f'''<div class="kicker">10 · Locatif</div><h2 style="margin-bottom:1mm">Trois maisons duplex · {lab}</h2>
<div class="planpage">{svgs[key]}</div>{cartouche("Plan " + lab, "Locatif, 3 maisons")}''')
    loyer = LOYERS["MD"]["nu"]
    add(f'''<div class="kicker">10 · Locatif</div><h2>Coupe et programme des maisons</h2>
<div class="grid" style="grid-template-columns:1.3fr 1fr;gap:6mm">{coupe_CC()}
<div><h3 style="margin-top:0">Une maison de 6 × 9 m sur deux niveaux</h3><ul class="small">
<li>RDC : séjour-SAM de 33 m² ouvert sur le jardin privé de 18 m², cuisine de 11,9 m² avec porte de service, entrée, escalier et WC.</li>
<li>Étage : deux chambres de 16,5 m², SE de 7,7 m², placard, dégagement.</li>
<li>Toit-terrasse de 45 m² sous pergola, jardinière de firecracker plants sur la façade Nord.</li>
<li>Stationnement : une place par maison dans la bande de 3 m au Sud, accès par la rue Ouest.</li></ul>
<div class="callout small"><b>À arbitrer</b> : en 3 m de large, les trois places sont en enfilade et se bloquent. Variantes : places
sur la rue Ouest, ou bande portée à 5,5 m au détriment des cuisines.</div>
<p class="small">Loyer de marché retenu pour un duplex 2 chambres avec jardin et toit-terrasse : <b>{m(loyer)} FCFA/mois</b> nu
(hypothèse à valider avec deux agences). Le business plan (document 3) sera mis à jour sur cette base.</p></div></div>''')

    # 18 surfaces
    tc1, tot1 = tableau_surf(C, ("RDC",))
    tc2, tot2 = tableau_surf(C, ("R+1", "TOIT"))
    tm, totm = tableau_surf({"pieces": [p for p in LOCATIF_M["pieces"] if p.get("logement") in ("M1", None)]}, ("RDC", "R+1", "TOIT"))
    add(f'''<div class="kicker">11 · Surfaces</div><h2>Tableau des surfaces de la villa · {a2(tot1 + tot2)} m² clos</h2>
<div class="grid g2" style="gap:7mm"><div>{tc1}</div><div>{tc2}</div></div>''')
    add(f'''<div class="kicker">11 · Surfaces</div><h2>Locatif et récapitulatif</h2>
<div class="grid g2" style="gap:7mm"><div><h3 style="margin-top:0">Une maison (× 3) · {a2(totm)} m² clos</h3>{tm}</div>
<div><table class="tight"><tr><th>Récapitulatif</th><th class="n">m²</th></tr>
<tr><td>Villa, surface close</td><td class="n">{a2(s["clos"])}</td></tr><tr><td>Villa, emprise (hors guérite et local GE)</td><td class="n">{a2(s["emprise"])}</td></tr>
<tr><td>Villa, extérieurs couverts (passage, loggia, terrasse, préau, jardinière)</td><td class="n">{a2(s["ext_couvert"])}</td></tr>
<tr><td>Villa, toit-terrasse sous pergola</td><td class="n">110,35</td></tr>
<tr><td>Locatif, surface close (3 maisons)</td><td class="n">{a2(sm["clos"])}</td></tr><tr><td>Locatif, emprise</td><td class="n">{a2(sm["emprise"])}</td></tr>
<tr><td>Locatif, toits-terrasses (3 × 44,9)</td><td class="n">134,70</td></tr>
<tr class="sub"><td>Total clos de l’opération</td><td class="n">{a2(s["clos"] + sm["clos"])}</td></tr></table></div></div>''')

    # 19-22 estimatif
    for pg in pages_estimatif(C, "Villa, option C v4 : estimation par pièce et par poste", n + 1, 3):
        n += 1
        P.append(pg)
    for pg in pages_estimatif(LOCATIF_M, "Locatif, 3 maisons duplex : estimation", n + 1, 2):
        n += 1
        P.append(pg)

    # 23 suite
    pv = sum(lg[4].get("C", 0) * pu_ligne(lg) for lg in PLUS_VALUES if lg[3].startswith("Prix") and lg[4].get("C"))
    add(f'''<div class="kicker">12 · Suite à donner</div><h2>Points à valider</h2>
<div class="grid g3" style="gap:6mm"><div class="card"><h3>À arbitrer avec vous</h3><ul class="small">
<li>Double peau : V1 brique semi-perforée ou V2 résille de béton</li>
<li>Stationnement du locatif : places en enfilade ou sur la rue Ouest</li>
<li>Ajustements de trame : stationnement 4,50 m, passages de 1 m</li>
<li>Escalier ouvert vers le toit ou édicule fermé (pluie)</li></ul></div>
<div class="card"><h3>Technique et règlement</h3><ul class="small">
<li>Le niveau pergola n’est pas un étage clos : à confirmer au cahier des charges (hauteur, R+1)</li>
<li>Étanchéité du toit-terrasse et des jardinières, arrosage goutte-à-goutte, trop-pleins</li>
<li>Mur végétalisé mitoyen : convention avec le locatif, accès d’entretien</li>
<li>Étude de sol G2, assainissement, cote d’inondation</li></ul></div>
<div class="card"><h3>Coût et bibliothèque</h3><ul class="small">
<li>Ratio ÷ {DIVISEUR} au bas de la fourchette : consultation par lots dès l’APS</li>
<li>Postes au prix du marché de la villa : {M(pv)} FCFA HT, à confirmer par devis</li>
<li>Blocs à ajouter à Archibooks : sanitaires, lits, canapés, cuisines, voitures, cartouche</li></ul></div></div>''')

    path = OUT / "04_Dossier_Option_C_Lot1728.html"
    doc_html = html(P, "Option C v4 – Dossier de présentation").replace("</style>", CSS_PLUS + "</style>", 1)
    path.write_text(doc_html)
    to_pdf(path, OUT / "04_Dossier_Option_C_Lot1728.pdf")
    print("ok", len(P), "pages")


if __name__ == "__main__":
    build()
