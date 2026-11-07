"""Export de la maquette 3D (clay) de l'option C vers JSON pour three.js.

Repere three.js : x = Est, z = Sud (= y du plan), y = hauteur.
Murs exterieurs deduits d'une grille d'occupation 0,1 m ; ouvertures = portes du modele ;
fenetres selon des regles explicites (documentees dans le dossier) pour que les rendus
n'inventent rien.
"""
import json
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from projet import LOCATIF_M, MX, OPTION_C  # noqa: E402
import facade as F  # noqa: E402

G = 0.05
NIV = {"RDC": (0.45, 3.75), "R+1": (3.75, 6.85), "TOIT": (6.85, 9.45)}
NIV_M = {"RDC": (0.15, 3.15), "R+1": (3.15, 6.15), "TOIT": (6.15, 8.75)}
OUT = pathlib.Path(__file__).resolve().parent.parent.parent / "out" / "rendu"


def occ(pieces, niveau):
    cells = {}
    for r in pieces:
        if r["niveau"] != niveau or not r["clos"]:
            continue
        for x0, y0, x1, y1 in r["rects"]:
            for i in range(round(x0 / G), round(x1 / G)):
                for j in range(round(y0 / G), round(y1 / G)):
                    cells[(i, j)] = r
    return cells


def walls(cells):
    """Segments de murs exterieurs : aretes de cellules occupees bordees de vide."""
    hseg, vseg = {}, {}
    for (i, j) in cells:
        if (i, j - 1) not in cells:
            hseg.setdefault(j, []).append(i)
        if (i, j + 1) not in cells:
            hseg.setdefault(j + 1, []).append(i)
        if (i - 1, j) not in cells:
            vseg.setdefault(i, []).append(j)
        if (i + 1, j) not in cells:
            vseg.setdefault(i + 1, []).append(j)
    out = []
    for j, xs in hseg.items():
        xs = sorted(set(xs))
        start = prev = xs[0]
        for x in xs[1:] + [None]:
            if x is None or x != prev + 1:
                out.append(("h", start * G, (prev + 1) * G, j * G))
                if x is not None:
                    start = x
            if x is not None:
                prev = x
    for i, ys in vseg.items():
        ys = sorted(set(ys))
        start = prev = ys[0]
        for y in ys[1:] + [None]:
            if y is None or y != prev + 1:
                out.append(("v", start * G, (prev + 1) * G, i * G))
                if y is not None:
                    start = y
            if y is not None:
                prev = y
    return out


def openings(opt, niveau, segs, cells):
    """Ouvertures sur murs exterieurs : portes du modele + fenetres par regle."""
    ops = []
    for niv, x, y, sens, w in opt["portes"]:
        if niv != niveau:
            continue
        for s in segs:
            if s[0] == sens and abs(s[3] - (y if sens == "h" else x)) < 0.06 and s[1] - 0.05 <= (x if sens == "h" else y) <= s[2] + 0.05:
                c = x if sens == "h" else y
                big = w >= 1.5
                ops.append({"sens": sens, "line": s[3], "a": c - w / 2, "b": c + w / 2,
                            "z0": 0.0, "z1": 2.6 if big else 2.2, "kind": "baie" if big else "porte"})
    # fenetres : une par piece habitable et par facade exterieure de plus de 2,0 m sans porte
    for s in segs:
        sens, a, b, line = s
        L = b - a
        if L < 2.0:
            continue
        mid = (a + b) / 2
        probe = (mid, line + 0.05) if sens == "h" else (line + 0.05, mid)
        probe2 = (mid, line - 0.05) if sens == "h" else (line - 0.05, mid)
        r = cells.get((int(probe[0] / G), int(probe[1] / G))) or cells.get((int(probe2[0] / G), int(probe2[1] / G)))
        if not r or r["code"] in ("escalier", "circ", "dressing"):
            continue
        if any(o["sens"] == sens and abs(o["line"] - line) < 0.06 and o["a"] < b and o["b"] > a for o in ops):
            continue
        east = sens == "v" and line >= 18.4          # facade Est a 1,50 m : jours hauts seulement
        wet = r["code"] in ("eau", "cuis_afr", "service")
        w = min(1.6 if not wet else 1.0, L - 0.8)
        z0, z1 = (1.8, 2.4) if (east or wet) else (0.9, 2.3)
        ops.append({"sens": sens, "line": line, "a": mid - w / 2, "b": mid + w / 2, "z0": z0, "z1": z1,
                    "kind": "jour" if (east or wet) else "fenetre"})
    return ops


def explicit(niveau, segs, ops):
    """Remplace les ouvertures des facades composees (facade.py) par la liste explicite."""
    ex = [o for o in F.OUVERTURES if o[0] == niveau]
    out = []
    for o in ops:
        covered = any(e[1] == o["sens"] and abs(e[2] - o["line"]) < 0.06 for e in ex
                      for s in segs if s[0] == o["sens"] and abs(s[3] - o["line"]) < 0.06
                      and s[1] <= e[3] < s[2] and s[1] <= o["a"] < s[2])
        if not covered:
            out.append(o)
    for _, sens, line, a, b, z0, z1, kind in ex:
        out.append({"sens": sens, "line": line, "a": a, "b": b, "z0": z0, "z1": z1, "kind": kind})
    return out


def outside(cells, sens, line, mid):
    """+1 si l'exterieur est du cote des x (ou y) croissants."""
    p = (mid, line + 0.05) if sens == "h" else (line + 0.05, mid)
    return -1 if (int(p[0] / G), int(p[1] / G)) in cells else 1


def ouvertures(opt, niveau, segs, explicites):
    """Portes du modele sur les murs exterieurs + ouvertures explicites de facade.py (sans fenetres inventees)."""
    ops = []
    ex = [o for o in explicites if o[0] == niveau]
    for niv, x, y, sens, w in opt["portes"]:
        if niv != niveau:
            continue
        line, c = (y, x) if sens == "h" else (x, y)
        if not any(s[0] == sens and abs(s[3] - line) < 0.06 and s[1] - 0.05 <= c <= s[2] + 0.05 for s in segs):
            continue
        if any(e[1] == sens and abs(e[2] - line) < 0.06 and e[3] - 0.05 <= c <= e[4] + 0.05 for e in ex):
            continue
        big = w >= 1.85
        ops.append({"sens": sens, "line": line, "a": c - w / 2, "b": c + w / 2, "z0": 0.0, "z1": 2.6 if big else 2.4,
                    "kind": "baie" if big else "porte"})
    for _, sens, line, a, b, z0, z1, kind in ex:
        ops.append({"sens": sens, "line": line, "a": a, "b": b, "z0": z0, "z1": z1, "kind": kind})
    return ops


def plants_cascade(data, x0, x1, y, ztop, seed=7, dens=6.0, drop=(0.4, 1.1), grp="maison"):
    """Firecracker plants : tiges retombantes vertes a fleurs rouge orange, devant une facade (plan y)."""
    import random
    rnd = random.Random(seed)
    n = int((x1 - x0) * dens)
    for k in range(n):
        x = x0 + (k + rnd.random()) * (x1 - x0) / n
        L = rnd.uniform(*drop)
        dy = rnd.uniform(-0.12, 0.0)
        data["boxes"].append({"x0": x - 0.018, "y0": y + dy - 0.02, "x1": x + 0.018, "y1": y + dy + 0.02,
                              "z0": ztop - L, "z1": ztop + 0.1, "m": "vegetal_fonce", "grp": grp})
        for t in range(3):
            zz = ztop - L * rnd.uniform(0.15, 1.0)
            data["boxes"].append({"x0": x - 0.035, "y0": y + dy - 0.05, "x1": x + 0.035, "y1": y + dy + 0.01,
                                  "z0": zz - 0.07, "z1": zz, "m": "fleur", "grp": grp})
    # touffe au sommet
    for k in range(int((x1 - x0) * 3)):
        x = x0 + (k + rnd.random()) * (x1 - x0) / int((x1 - x0) * 3)
        data["boxes"].append({"x0": x - 0.09, "y0": y + 0.05, "x1": x + 0.09, "y1": y + 0.45,
                              "z0": ztop, "z1": ztop + rnd.uniform(0.12, 0.3), "m": "vegetal_fonce", "grp": grp})


def mur_vegetal(data, x0, x1, y0, y1, h, seed=3):
    import random
    rnd = random.Random(seed)
    data["boxes"].append({"x0": x0, "y0": y0, "x1": x1, "y1": y1, "z0": 0, "z1": h, "m": "vegetal", "grp": "cloture"})
    for face in (y0 - 0.12, y1):
        for k in range(int((x1 - x0) * h * 2.2)):
            x, z = rnd.uniform(x0, x1), rnd.uniform(0.1, h)
            r = rnd.uniform(0.12, 0.3)
            data["boxes"].append({"x0": x - r, "y0": face, "x1": x + r, "y1": face + 0.12, "z0": z - r * 0.7,
                                  "z1": z + r * 0.7, "m": rnd.choice(["vegetal", "vegetal_fonce"]), "grp": "cloture"})


def double_peau(data, variante):
    x0, y0, x1, y1, z0, z1 = F.DOUBLE_PEAU
    za = z0 + F.DP_ALLEGE
    if variante == "V1":   # brique semi-perforee (Casa Estudio)
        data["boxes"].append({"x0": x0, "y0": y0, "x1": x1, "y1": y1, "z0": z0, "z1": za, "m": "brique"})
        dense = [(a - 0.8 - x0, a + 0.8 - x0) for a in F.DP_AXES]
        data["claustras"].append({"x0": x0, "y0": y0, "x1": x1, "y1": y1, "z0": za, "z1": z1, "random": True,
                                  "dense": dense, "p": 0.18, "m": "brique"})
    else:                  # resille beton triangulee (Typologie urbaine 8)
        data["boxes"].append({"x0": x0, "y0": y0, "x1": x1, "y1": y1, "z0": z0, "z1": za, "m": "beton_brut"})
        data["boxes"].append({"x0": x0, "y0": y0, "x1": x1, "y1": y1, "z0": z1 - 0.12, "z1": z1, "m": "beton_brut"})
        mont = [x0, x1] + [a + d for a in F.DP_AXES for d in (-0.8, 0.8)]
        for m in mont:
            data["boxes"].append({"x0": m - 0.07, "y0": y0, "x1": m + 0.07, "y1": y1, "z0": za, "z1": z1, "m": "beton_brut"})
        segs = []
        H = z1 - 0.12 - za
        tri = 1.0
        n = max(1, round(H / (tri * 0.866)))
        h = H / n
        for k in range(n + 1):
            segs.append([x0, za + k * h, x1, za + k * h])
        x = x0 - H
        while x < x1 + H:
            segs.append([x, za, x + H / 1.732, za + H])
            segs.append([x + H / 1.732, za, x, za + H])
            x += tri
        data["diag"].append({"y0": y0, "y1": y1, "x0": x0, "x1": x1, "z0": za, "z1": z1 - 0.12, "w": 0.09,
                             "segs": segs, "m": "beton_clair"})


def murs_niveaux(data, opt, niv_z, explicites, mat, grp):
    for niveau, (z0, z1) in niv_z.items():
        cells = occ(opt["pieces"], niveau)
        if not cells:
            continue
        segs = walls(cells)
        ops = ouvertures(opt, niveau, segs, explicites)
        for sens, a, b, line in segs:
            mine = [o for o in ops if o["sens"] == sens and abs(o["line"] - line) < 0.06 and o["a"] < b and o["b"] > a]
            data["walls"].append({"sens": sens, "a": a, "b": b, "line": line, "z0": z0, "z1": z1,
                                  "m": mat(niveau, sens, line), "ops": mine, "grp": grp})
            for o in mine:
                if o["kind"] != "claustra":
                    continue
                d = outside(cells, sens, line, (o["a"] + o["b"]) / 2)
                lo, hi = sorted((line + d * 0.12, line + d * 0.27))
                box = ({"x0": o["a"] - 0.15, "y0": lo, "x1": o["b"] + 0.15, "y1": hi} if sens == "h"
                       else {"x0": lo, "y0": o["a"] - 0.15, "x1": hi, "y1": o["b"] + 0.15})
                data["claustras"].append({**box, "z0": z0 + 0.05, "z1": z1 - 0.05, "random": True, "grp": grp})
        for r in opt["pieces"]:
            if r["niveau"] != niveau or not r["clos"]:
                continue
            for x0, y0, x1, y1 in r["rects"]:
                data["slabs"].append({"x0": x0, "y0": y0, "x1": x1, "y1": y1, "z": z1, "t": 0.25,
                                      "m": "beton_brut", "grp": grp})


def pergola(data, rects, poteaux, z0, h, grp, sens_lattes=None):
    zt = z0 + h
    for px, py in poteaux:
        data["boxes"].append({"x0": px - 0.06, "y0": py - 0.06, "x1": px + 0.06, "y1": py + 0.06, "z0": z0,
                              "z1": zt, "m": "metal", "grp": grp})
    for k, (x0, y0, x1, y1) in enumerate(rects):
        horiz = (x1 - x0) >= (y1 - y0) if sens_lattes is None else sens_lattes[k]
        # poutres de rive
        data["boxes"] += [
            {"x0": x0, "y0": y0 - 0.06, "x1": x1, "y1": y0 + 0.06, "z0": zt, "z1": zt + 0.22, "m": "bois", "grp": grp},
            {"x0": x0, "y0": y1 - 0.06, "x1": x1, "y1": y1 + 0.06, "z0": zt, "z1": zt + 0.22, "m": "bois", "grp": grp},
        ]
        if horiz:      # lattes Nord-Sud, entraxe 0,45
            n = int((x1 - x0) / 0.45)
            for i in range(n + 1):
                x = x0 + i * (x1 - x0) / n
                data["boxes"].append({"x0": x - 0.03, "y0": y0, "x1": x + 0.03, "y1": y1, "z0": zt + 0.22,
                                      "z1": zt + 0.36, "m": "bois", "grp": grp})
        else:
            n = int((y1 - y0) / 0.45)
            for i in range(n + 1):
                y = y0 + i * (y1 - y0) / n
                data["boxes"].append({"x0": x0, "y0": y - 0.03, "x1": x1, "y1": y + 0.03, "z0": zt + 0.22,
                                      "z1": zt + 0.36, "m": "bois", "grp": grp})


def build(variante="V1"):
    data = {"walls": [], "slabs": [], "boxes": [], "rails": [], "trees": [], "water": [], "glass": [],
            "claustras": [], "lames": [], "diag": []}
    T = F.TOIT_Z
    # ------------------------------------------------------------------ villa
    def mat(niveau, sens, line):
        if niveau == "RDC":
            return "moellons" if (sens, round(line, 1)) in F.RUES else "enduit"
        return "beton_brut"
    murs_niveaux(data, OPTION_C, NIV, F.OUVERTURES, mat, "maison")
    # guerite et local GE (pieces RDC hors volume)
    for w in list(data["walls"]):
        if w["z0"] == 0.45 and ((w["sens"] == "h" and w["line"] < 3) or (w["sens"] == "v" and w["b"] <= 3)):
            w["grp"] = "guerite"
    data["slabs"].append({"x0": 4.0, "y0": 0.25, "x1": 7.3, "y1": 3.2, "z": 3.0, "t": 0.16, "m": "beton_brut", "grp": "guerite"})
    data["boxes"].append({"x0": 0.3, "y0": 0.3, "x1": 3.3, "y1": 2.5, "z0": 0, "z1": 2.3, "m": "enduit", "grp": "guerite"})
    data["slabs"].append({"x0": 0.2, "y0": 0.2, "x1": 3.4, "y1": 2.7, "z": 2.45, "t": 0.15, "m": "beton_brut", "grp": "guerite"})
    # socle, passage couvert, loggia et jardiniere
    data["boxes"].append({"x0": 3.5, "y0": 5.7, "x1": 19.0, "y1": 17.0, "z0": 0, "z1": 0.45, "m": "socle"})
    data["boxes"].append({"x0": 3.5, "y0": 4.5, "x1": 16.5, "y1": 5.7, "z0": 0, "z1": 0.3, "m": "socle"})
    data["slabs"].append({"x0": 3.5, "y0": 4.5, "x1": 19.0, "y1": 5.7, "z": 3.75, "t": 0.25, "m": "beton_brut"})
    data["slabs"].append({"x0": 3.5, "y0": 4.5, "x1": 19.0, "y1": 5.7, "z": T, "t": 0.25, "m": "beton_brut"})
    x0, y0, x1, y1, hj = F.JARDINIERE
    data["boxes"].append({"x0": x0, "y0": y0, "x1": x1, "y1": y1, "z0": T, "z1": T + hj, "m": "beton_brut"})
    data["boxes"].append({"x0": x0 + 0.08, "y0": y0 + 0.08, "x1": x1 - 0.08, "y1": y1 - 0.08, "z0": T + hj - 0.05,
                          "z1": T + hj + 0.02, "m": "vegetal_fonce"})
    double_peau(data, variante)
    plants_cascade(data, 3.6, 18.9, F.DOUBLE_PEAU[1] - 0.04, F.DOUBLE_PEAU[5], seed=11)
    # jardiniere Ouest de la chambre principale
    data["slabs"].append({"x0": 2.7, "y0": 13.8, "x1": 3.5, "y1": 17.0, "z": 3.75, "t": 0.22, "m": "beton_brut"})
    data["boxes"].append({"x0": 2.7, "y0": 13.8, "x1": 2.85, "y1": 17.0, "z0": 3.75, "z1": 4.55, "m": "beton_brut"})
    data["boxes"].append({"x0": 2.85, "y0": 13.9, "x1": 3.45, "y1": 16.9, "z0": 4.2, "z1": 4.5, "m": "vegetal_fonce"})
    # acroteres du toit-terrasse (sauf jardiniere Nord) et pergola
    for (a, b, c, d) in [(3.5, 5.7, 3.65, 17.0), (3.5, 16.85, 10.0, 17.0), (9.85, 11.2, 10.0, 17.0),
                         (10.0, 11.2, 19.0, 11.35), (18.85, 5.7, 19.0, 11.2)]:
        data["boxes"].append({"x0": a, "y0": b, "x1": c, "y1": d, "z0": T, "z1": T + F.ACROTERE, "m": "beton_brut"})
    pergola(data, F.PERGOLA, F.POTEAUX, T, F.PERGOLA_H, "maison", sens_lattes=[True, False])
    # terrasse couverte, toitures vegetalisees, poteaux bois
    data["slabs"].append({"x0": 10.0, "y0": 11.2, "x1": 15.5, "y1": 13.6, "z": 3.75, "t": 0.25, "m": "beton_brut"})
    for (a, b, c, d) in F.TOITURE_VEGETALE:
        data["boxes"].append({"x0": a + 0.15, "y0": b + 0.15, "x1": c - 0.15, "y1": d - 0.15, "z0": 3.75, "z1": 3.9, "m": "vegetal"})
        data["boxes"].append({"x0": a, "y0": b, "x1": c, "y1": d, "z0": 3.75, "z1": 3.95, "m": "beton_brut", "edge": True})
    for px in (10.1, 12.8, 15.4):
        data["boxes"].append({"x0": px - 0.1, "y0": 13.4, "x1": px + 0.1, "y1": 13.6, "z0": 0.45, "z1": 3.5, "m": "bois"})
    # galerie de l'etage : ecrans en lattes ; ecrans des chambres
    for a, b in F.ECRANS_GALERIE:
        data["lames"].append({"x0": a, "y0": 11.3, "x1": b, "y1": 11.38, "z0": 3.75, "z1": 6.6, "dir": "v",
                              "pas": 0.09, "ep": 0.04, "m": "bois"})
    zn = F.Z
    for niv, sens, line, a, b, z0, z1 in F.ECRANS:
        o = 1 if (sens == "h" and line > 15) or (sens == "v" and line > 10) else -1
        lo, hi = sorted((line + o * 0.13, line + o * 0.18))
        box = ({"x0": a, "y0": lo, "x1": b, "y1": hi} if sens == "h" else {"x0": lo, "y0": a, "x1": hi, "y1": b})
        data["lames"].append({**box, "z0": zn[niv] + z0, "z1": zn[niv] + z1, "dir": "v", "pas": 0.08, "ep": 0.04, "m": "bois"})
    for x0, y0, x1, y1, z0, z1 in F.CLAUSTRAS:
        data["claustras"].append({"x0": x0, "y0": y0, "x1": x1, "y1": y1, "z0": z0, "z1": z1, "random": True})
    # preau de la cuisine africaine
    data["slabs"].append({"x0": 16.5, "y0": 2.6, "x1": 19.0, "y1": 4.5, "z": 2.9, "t": 0.12, "m": "beton_brut"})
    for px, py in ((16.6, 2.7), (18.9, 2.7)):
        data["boxes"].append({"x0": px - 0.06, "y0": py - 0.06, "x1": px + 0.06, "y1": py + 0.06, "z0": 0, "z1": 2.9, "m": "bois"})
    # patio : arbre, bassins ; vegetation des bandes laterales
    tx, ty = F.ARBRE_PATIO
    data["trees"] += [{"x": tx, "y": ty, "r": 1.7, "h": 6.5},
                      {"x": 1.7, "y": 8.6, "r": 2.1, "h": 6.0, "grp": "arbres"},
                      {"x": 1.9, "y": 4.2, "r": 1.5, "h": 4.6, "grp": "arbres"},
                      {"x": 1.6, "y": 17.0, "r": 1.5, "h": 5.0, "grp": "arbres"},
                      {"x": 15.3, "y": 2.4, "r": 1.2, "h": 4.2, "grp": "arbres"}]
    for x0, y0, x1, y1 in F.BIO_BASSINS:
        data["boxes"].append({"x0": x0 - 0.2, "y0": y0 - 0.2, "x1": x1 + 0.2, "y1": y1 + 0.2, "z0": 0, "z1": 0.32, "m": "moellons"})
        data["water"].append({"x0": x0, "y0": y0, "x1": x1, "y1": y1, "z1": 0.36})
    for (a, b, c, d) in [(10.2, 15.9, 12.6, 17.6), (14.0, 13.8, 15.4, 17.6), (0.3, 3.0, 3.2, 11.7)]:
        data["boxes"].append({"x0": a, "y0": b, "x1": c, "y1": d, "z0": 0, "z1": 0.35, "m": "vegetal_fonce"})
    mur_vegetal(data, 0.0, 20.0, F.MUR_VEGETAL[1], F.MUR_VEGETAL[3], F.MUR_VEGETAL[4])
    # clotures sur rue : socle en moellons + brique ajouree ; portail ouvert, portillons en lames
    for x0, y0, x1, y1 in [(0.0, 0.0, 7.0, 0.2), (15.9, 0.0, 17.0, 0.2), (19.5, 0.0, 20.0, 0.2), (0.0, 0.2, 0.2, 17.82),
                           (0.0, 18.0, 0.2, 33.0)]:
        data["boxes"].append({"x0": x0, "y0": y0, "x1": x1, "y1": y1, "z0": 0, "z1": F.CLOTURE_SOCLE, "m": "moellons", "grp": "cloture"})
        data["claustras"].append({"x0": x0 + (0.05 if x1 - x0 < 0.3 else 0), "y0": y0 + (0.05 if y1 - y0 < 0.3 else 0),
                                  "x1": x1 - (0.05 if x1 - x0 < 0.3 else 0), "y1": y1 - (0.05 if y1 - y0 < 0.3 else 0),
                                  "z0": F.CLOTURE_SOCLE, "z1": F.CLOTURE_H, "random": True, "p": 0.2, "grp": "cloture"})
    for a, b, y0 in [(7.0, 8.4, 0.04), (17.0, 19.5, 0.04), (0.95, 8.35, 0.24)]:
        data["lames"].append({"x0": a + 0.05, "y0": y0, "x1": b - 0.05, "y1": y0 + 0.12, "z0": 0.05, "z1": F.CLOTURE_H,
                              "dir": "v", "pas": 0.13, "ep": 0.09, "m": "bois", "grp": "cloture"})
    data["boxes"].append({"x0": 19.8, "y0": 0.0, "x1": 20.0, "y1": 33.0, "z0": 0, "z1": 2.2, "m": "enduit", "grp": "cloture"})
    data["boxes"].append({"x0": 0.0, "y0": 32.8, "x1": 20.0, "y1": 33.0, "z0": 0, "z1": 2.2, "m": "enduit", "grp": "cloture"})
    # ------------------------------------------------------------------ locatif : 3 maisons duplex
    expl_m = [o for k, x0 in enumerate(MX[:3]) for o in F.ouvertures_maison(x0, k == 0)]
    murs_niveaux(data, LOCATIF_M, NIV_M, expl_m, lambda n, s_, l_: "enduit" if n == "RDC" else "beton_brut", "locatif")
    data["boxes"].append({"x0": 2.0, "y0": 21.0, "x1": 20.0, "y1": 30.0, "z0": 0, "z1": 0.15, "m": "socle", "grp": "locatif"})
    for k, x0 in enumerate(MX[:3]):
        Tm = NIV_M["TOIT"][0]
        for (a, b, c, d) in [(x0, 21.0, x0 + 6, 21.15), (x0, 29.85, x0 + 6, 30.0), (x0 + 5.85, 21.0, x0 + 6, 30.0),
                             (x0, 21.0, x0 + 0.15, 30.0)]:
            data["boxes"].append({"x0": a, "y0": b, "x1": c, "y1": d, "z0": Tm, "z1": Tm + 1.0, "m": "beton_brut", "grp": "locatif"})
        data["slabs"].append({"x0": x0 + 2.6, "y0": 26.5, "x1": x0 + 6, "y1": 30.0, "z": Tm, "t": 0.25, "m": "beton_brut", "grp": "locatif"})
        pergola(data, [(x0 + 0.1, 21.1, x0 + 5.9, 26.4)], [(x0 + 0.15, 21.15), (x0 + 5.85, 21.15), (x0 + 0.15, 26.35),
                                                            (x0 + 5.85, 26.35)], Tm, 2.5, "locatif")
        data["boxes"].append({"x0": x0 + 0.15, "y0": 20.85, "x1": x0 + 5.85, "y1": 21.45, "z0": Tm, "z1": Tm + 0.6,
                              "m": "beton_brut", "grp": "locatif"})
        plants_cascade(data, x0 + 0.2, x0 + 5.8, 20.8, Tm + 0.6, seed=20 + k, dens=4.0, drop=(0.3, 0.9), grp="locatif")
        data["trees"].append({"x": x0 + 1.5 + 1.5 * (k % 2), "y": 19.6, "r": 1.2, "h": 4.0, "grp": "arbres_m"})
        data["boxes"].append({"x0": x0, "y0": 18.1, "x1": x0 + 6, "y1": 18.7, "z0": 0, "z1": 0.4, "m": "vegetal_fonce", "grp": "locatif"})
    # contexte voisin
    data["boxes"].append({"x0": 22.0, "y0": 3.0, "x1": 33.0, "y1": 16.0, "z0": 0, "z1": 7.0, "m": "contexte"})
    data["boxes"].append({"x0": 22.0, "y0": 19.0, "x1": 33.0, "y1": 31.0, "z0": 0, "z1": 3.6, "m": "contexte"})
    data["boxes"].append({"x0": -22.0, "y0": 2.0, "x1": -9.0, "y1": 15.0, "z0": 0, "z1": 6.5, "m": "contexte"})
    data["boxes"].append({"x0": 2.0, "y0": -24.0, "x1": 16.0, "y1": -10.0, "z0": 0, "z1": 7.0, "m": "contexte"})
    data["boxes"].append({"x0": 2.0, "y0": 35.0, "x1": 18.0, "y1": 47.0, "z0": 0, "z1": 6.5, "m": "contexte"})
    OUT.mkdir(parents=True, exist_ok=True)
    name = f"scene_C_{variante}.json"
    (OUT / name).write_text(json.dumps(data))
    print(name, "murs", len(data["walls"]), "boites", len(data["boxes"]))


if __name__ == "__main__":
    build("V1")
    build("V2")
