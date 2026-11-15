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
Z0 = 0.15                     # plancher fini du RDC (+-0,00) a 0,15 m au-dessus du terrain
NIV = {"RDC": (Z0, Z0 + 3.30), "R+1": (Z0 + 3.30, Z0 + 6.60), "TOIT": (Z0 + 6.60, Z0 + 6.60 + 2.15)}
NIV_M = {"RDC": (Z0, Z0 + 3.30), "R+1": (Z0 + 3.30, Z0 + 6.60), "TOIT": (Z0 + 6.60, Z0 + 6.60 + 2.4)}
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


def peau(data, variante, sens, line, a, b, out, axes, z0, z1, grp="maison", ep=0.14):
    """Peau de l'etage, commune a la villa et aux duplex.
    V1 : panneaux de lames de bois verticales en damier ; V2 : bardage a lames verticales + brise-soleil dans l'axe
    des baies. (sens, line) : facade ; [a, b] : etendue ; out = cote exterieur (-1 / +1) ; z0-z1 : hauteur."""
    lo, hi = sorted((line + out * 0.02, line + out * (0.02 + ep)))
    def bloc(u0, u1):
        return ({"x0": u0, "y0": lo, "x1": u1, "y1": hi} if sens == "h" else {"x0": lo, "y0": u0, "x1": hi, "y1": u1})
    if variante == "V1":
        rows, pw = 4, 0.62
        h = (z1 - z0) / rows
        n = max(1, round((b - a) / pw))
        pw = (b - a) / n
        for k in range(rows):
            for i in range(n):
                u = a + i * pw
                ouvert = (i + k) % 2 == 1
                data["lames"].append({**bloc(u + 0.01, u + pw - 0.01), "z0": z0 + k * h + 0.02, "z1": z0 + (k + 1) * h - 0.02,
                                      "dir": "v", "pas": 0.16 if ouvert else 0.075, "ep": 0.055 if ouvert else 0.065,
                                      "m": "bois_dur", "grp": grp})
        for k in range(rows + 1):                                  # traverses metalliques fines
            z = z0 + k * h
            data["boxes"].append({**bloc(a, b), "z0": z - 0.02, "z1": z + 0.02, "m": "metal", "grp": grp})
    else:
        ouverts = sorted((x - 0.8, x + 0.8) for x in axes)
        cur = a
        for (u0, u1) in ouverts + [(b, b)]:
            u0, u1 = max(a, u0), min(b, u1)
            if u0 > cur + 0.05:
                data["lames"].append({**bloc(cur, u0), "z0": z0, "z1": z1, "dir": "v", "pas": 0.105, "ep": 0.095,
                                      "m": "bois_dur", "grp": grp})
            u = u0 + 0.1
            while u < u1 - 0.05:                                    # brise-soleil pivotants (representes ouverts)
                fin = ({"x0": u - 0.025, "x1": u + 0.025, "y0": min(lo, hi - 0.34), "y1": max(hi, lo + 0.34)} if sens == "h"
                       else {"y0": u - 0.025, "y1": u + 0.025, "x0": min(lo, hi - 0.34), "x1": max(hi, lo + 0.34)})
                data["boxes"].append({**fin, "z0": z0 + 0.05, "z1": z1 - 0.05, "m": "bois_dur", "grp": grp})
                u += 0.3
            cur = max(cur, u1)


def claustra_beton(data, x0, y0, x1, y1, z0, z1, grp="cloture", m=0.2):
    """Claustra de blocs de beton ajoures (grille carree de 0,20 m), comme l'image de reference 2."""
    along = (x1 - x0) >= (y1 - y0)
    L = (x1 - x0) if along else (y1 - y0)
    n = max(1, round(L / m))
    for i in range(n + 1):
        u = i * L / n
        b = ({"x0": x0 + u - 0.025, "y0": y0, "x1": x0 + u + 0.025, "y1": y1} if along
             else {"x0": x0, "y0": y0 + u - 0.025, "x1": x1, "y1": y0 + u + 0.025})
        data["boxes"].append({**b, "z0": z0, "z1": z1, "m": "beton_clair", "grp": grp})
    nz = max(1, round((z1 - z0) / m))
    for k in range(nz + 1):
        z = z0 + k * (z1 - z0) / nz
        data["boxes"].append({"x0": x0, "y0": y0, "x1": x1, "y1": y1, "z0": z - 0.025, "z1": z + 0.025,
                              "m": "beton_clair", "grp": grp})


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
                data["claustras"].append({**box, "z0": z0 + 0.05, "z1": z1 - 0.05, "m": "beton_clair", "bw": 0.16, "pas": 0.22, "rh": 0.22, "jt": 0.06, "grp": grp})
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


def couverture(data, variante, z_dessous):
    """Couverture du toit-terrasse a +9,00 : V1 dalle mince a grand debord ; V2 croupes a sous-face bois."""
    if variante == "V1":
        for (x0, y0, x1, y1) in F.COUV_V1:
            data["slabs"].append({"x0": x0, "y0": y0, "x1": x1, "y1": y1, "z": z_dessous + 0.18, "t": 0.18,
                                  "m": "beton_clair", "grp": "couverture"})
    else:
        for (x0, y0, x1, y1) in F.COUV_V2:
            data["roofs"].append({"x0": x0, "y0": y0, "x1": x1, "y1": y1, "z": z_dessous, "pente": 15,
                                  "m": "toit", "sous": "bois", "grp": "couverture"})


def build(variante="V1"):
    data = {"walls": [], "slabs": [], "boxes": [], "rails": [], "trees": [], "water": [], "glass": [],
            "claustras": [], "lames": [], "diag": [], "roofs": []}
    T = NIV["TOIT"][0]
    R1 = NIV["R+1"][0]
    COUV = Z0 + F.COUV_Z                       # dessus de la couverture
    # ------------------------------------------------------------------ villa
    def mat(niveau, sens, line):
        if niveau == "RDC":
            return "moellons" if (sens, round(line, 1)) in F.RUES else "enduit"
        return "enduit"
    murs_niveaux(data, OPTION_C, NIV, F.OUVERTURES, mat, "maison")
    for w in list(data["walls"]):
        if w["z0"] == Z0 and ((w["sens"] == "h" and w["line"] < 3) or (w["sens"] == "v" and w["b"] <= 3)):
            w["grp"] = "guerite"
    # guerite (moellons) et local GE
    # guerite et local GE ramenes a la hauteur de la cloture (demande du client) : dessus a +2,30 depuis le terrain
    HG = F.CLOTURE_H + 0.08
    for w in data["walls"]:
        if w.get("grp") == "guerite":
            w["z1"] = HG - 0.12
            for o in w["ops"]:
                o["z1"] = min(o["z1"], HG - 0.12 - w["z0"] - 0.05)
    data["slabs"].append({"x0": 3.1, "y0": 0.2, "x1": 5.9, "y1": 2.9, "z": HG, "t": 0.12, "m": "beton_clair", "grp": "guerite"})
    data["boxes"].append({"x0": 0.3, "y0": 0.3, "x1": 3.0, "y1": 2.5, "z0": 0, "z1": HG - 0.12, "m": "moellons", "grp": "guerite"})
    data["slabs"].append({"x0": 0.2, "y0": 0.2, "x1": 3.1, "y1": 2.6, "z": HG, "t": 0.12, "m": "beton_clair", "grp": "guerite"})
    # socle, passage couvert, loggia et jardiniere
    data["boxes"].append({"x0": 2.5, "y0": 5.5, "x1": 18.0, "y1": 16.8, "z0": 0, "z1": Z0, "m": "socle"})
    data["boxes"].append({"x0": 2.5, "y0": 4.5, "x1": 15.5, "y1": 5.5, "z0": 0, "z1": Z0, "m": "socle"})
    data["slabs"].append({"x0": 2.5, "y0": 4.36, "x1": 18.0, "y1": 5.5, "z": R1, "t": 0.18, "m": "beton_clair"})
    data["slabs"].append({"x0": 2.5, "y0": 4.36, "x1": 18.0, "y1": 5.5, "z": T, "t": 0.18, "m": "beton_clair"})
    x0, y0, x1, y1, hj = F.JARDINIERE
    data["boxes"].append({"x0": x0, "y0": y0 - 0.14, "x1": x1, "y1": y1, "z0": T, "z1": T + hj, "m": "beton_clair"})
    data["boxes"].append({"x0": x0 + 0.08, "y0": y0 - 0.06, "x1": x1 - 0.08, "y1": y1 - 0.08, "z0": T + hj - 0.05,
                          "z1": T + hj + 0.02, "m": "vegetal_fonce"})
    for sens, line, a, b, out, axes in F.PEAU_VILLA:      # meme peau sur les quatre faces de l'etage
        ep = 0.14 if line != 4.5 else 0.12
        peau(data, variante, sens, line - (0.0 if line != 4.5 else 0.02), a, b, out, axes, R1, T - 0.2, ep=ep)
    # firecracker plants retirees de la toiture (demande du client du 10-11-2026) : jardiniere plantee basse
    # jardiniere Ouest de la chambre principale
    data["slabs"].append({"x0": 1.7, "y0": 13.6, "x1": 2.5, "y1": 16.8, "z": R1, "t": 0.18, "m": "beton_clair"})
    data["boxes"].append({"x0": 1.7, "y0": 13.6, "x1": 1.85, "y1": 16.8, "z0": R1, "z1": R1 + 0.8, "m": "beton_clair"})
    data["boxes"].append({"x0": 1.85, "y0": 13.7, "x1": 2.45, "y1": 16.7, "z0": R1 + 0.45, "z1": R1 + 0.75, "m": "vegetal_fonce"})
    # garde-corps du toit-terrasse (sauf jardiniere Nord), poteaux et couverture a +9,00
    for (a, b, c, d) in [(2.5, 5.5, 2.65, 16.8), (2.5, 16.65, 9.0, 16.8), (8.85, 11.0, 9.0, 16.8),
                         (9.0, 11.0, 18.0, 11.15), (17.85, 5.5, 18.0, 11.0)]:
        data["boxes"].append({"x0": a, "y0": b, "x1": c, "y1": d, "z0": T, "z1": T + F.ACROTERE, "m": "enduit"})
    zc = COUV - (0.18 if variante == "V1" else 0.3)
    for px, py in F.POTEAUX:
        data["boxes"].append({"x0": px - 0.07, "y0": py - 0.07, "x1": px + 0.07, "y1": py + 0.07, "z0": T,
                              "z1": zc, "m": "metal"})
    couverture(data, variante, zc)
    if variante == "V2":
        x0, y0, x1, y1, zz = F.AUVENT_V2       # auvent bas sur la rue, sous-face bois
        data["slabs"].append({"x0": x0, "y0": y0, "x1": x1, "y1": y1, "z": Z0 + zz + 0.05, "t": 0.12, "m": "bois_dur"})
        data["boxes"].append({"x0": x0, "y0": y0, "x1": x1, "y1": y0 + 0.06, "z0": Z0 + zz - 0.07,
                              "z1": Z0 + zz + 0.12, "m": "toit"})
    # terrasse couverte, toitures vegetalisees, poteaux bois
    data["slabs"].append({"x0": 9.0, "y0": 11.0, "x1": 14.5, "y1": 13.4, "z": R1, "t": 0.25, "m": "beton_clair"})
    for (a, b, c, d) in F.TOITURE_VEGETALE:
        data["boxes"].append({"x0": a + 0.15, "y0": b + 0.15, "x1": c - 0.15, "y1": d - 0.15, "z0": R1, "z1": R1 + 0.15, "m": "vegetal"})
        data["boxes"].append({"x0": a, "y0": b, "x1": c, "y1": d, "z0": R1, "z1": R1 + 0.2, "m": "beton_clair", "edge": True})
    for px in (9.1, 11.8, 14.4):
        data["boxes"].append({"x0": px - 0.1, "y0": 13.2, "x1": px + 0.1, "y1": 13.4, "z0": Z0, "z1": R1 - 0.25, "m": "bois_dur"})
    # galerie de l'etage : ecrans en lattes ; ecrans des chambres
    for a, b in F.ECRANS_GALERIE:
        data["lames"].append({"x0": a, "y0": 11.1, "x1": b, "y1": 11.18, "z0": R1, "z1": T - 0.25, "dir": "v",
                              "pas": 0.09, "ep": 0.04, "m": "bois_dur"})
    for niv, sens, line, a, b, z0, z1 in [e for e in F.ECRANS if e[0] == "RDC"]:
        o = 1 if (sens == "h" and line > 15) or (sens == "v" and line > 10) else -1
        lo, hi = sorted((line + o * 0.13, line + o * 0.18))
        box = ({"x0": a, "y0": lo, "x1": b, "y1": hi} if sens == "h" else {"x0": lo, "y0": a, "x1": hi, "y1": b})
        data["lames"].append({**box, "z0": Z0 + F.Z[niv] + z0, "z1": Z0 + F.Z[niv] + z1, "dir": "v", "pas": 0.08,
                              "ep": 0.04, "m": "bois_dur"})
    for x0, y0, x1, y1, z0, z1 in F.CLAUSTRAS:
        claustra_beton(data, x0, y0, x1, y1, z0, z1)
    # preau de la cuisine africaine
    data["slabs"].append({"x0": 15.5, "y0": 2.6, "x1": 18.0, "y1": 4.5, "z": 2.9, "t": 0.12, "m": "beton_clair"})
    for px, py in ((15.6, 2.7), (17.9, 2.7)):
        data["boxes"].append({"x0": px - 0.06, "y0": py - 0.06, "x1": px + 0.06, "y1": py + 0.06, "z0": 0, "z1": 2.9, "m": "bois_dur"})
    # patio et bandes plantees (aucun bassin, markup)
    tx, ty = F.ARBRE_PATIO
    data["trees"] += [{"x": tx, "y": ty, "r": 1.7, "h": 6.5, "grp": "arbres"},
                      {"x": 1.2, "y": 8.4, "r": 1.6, "h": 5.5, "grp": "arbres"},
                      {"x": 1.3, "y": 3.8, "r": 1.3, "h": 4.6, "grp": "arbres"},
                      {"x": 1.2, "y": 15.9, "r": 1.3, "h": 5.0, "grp": "arbres"},
                      {"x": 13.6, "y": 2.4, "r": 1.0, "h": 4.2, "grp": "arbres"},
                      {"x": 19.0, "y": 13.0, "r": 0.9, "h": 4.5, "grp": "arbres"}]
    for (a, b, c, d) in [(9.2, 15.6, 11.8, 17.6), (13.0, 13.6, 14.3, 17.6), (0.25, 2.8, 2.3, 17.6),
                         (0.25, 0.25, 6.9, 0.7), (12.6, 0.25, 14.4, 0.7)]:
        data["boxes"].append({"x0": a, "y0": b, "x1": c, "y1": d, "z0": 0, "z1": 0.45, "m": "vegetal_fonce"})
    mur_vegetal(data, 0.0, 20.0, F.MUR_VEGETAL[1], F.MUR_VEGETAL[3], F.MUR_VEGETAL[4])
    # clotures sur rue (image de reference 2) : socle en moellons, claustra beton, portail et portillons en lames
    S = F.CLOTURE_SOCLE
    pleins = [(0.0, 0.0, 6.0, 0.2), (12.5, 0.0, 18.5, 0.2), (19.5, 0.0, 20.0, 0.2), (0.0, 0.2, 0.2, 17.82),
              (0.0, 18.0, 0.2, 18.5), (0.0, 30.0, 0.2, 30.2)]
    for x0, y0, x1, y1 in pleins:
        data["boxes"].append({"x0": x0, "y0": y0, "x1": x1, "y1": y1, "z0": 0, "z1": S, "m": "moellons", "grp": "cloture"})
        claustra_beton(data, x0, y0, x1, y1, S, F.CLOTURE_H)
        data["boxes"].append({"x0": x0, "y0": y0, "x1": x1, "y1": y1, "z0": F.CLOTURE_H, "z1": F.CLOTURE_H + 0.08,
                              "m": "beton_clair", "grp": "cloture"})
    for a, b, y0 in [(6.0, 7.0, 0.04), (18.5, 19.5, 0.04), (7.0, 12.5, 0.24)]:
        data["lames"].append({"x0": a + 0.03, "y0": y0, "x1": b - 0.03, "y1": y0 + 0.1, "z0": 0.05, "z1": F.CLOTURE_H,
                              "dir": "v", "pas": 0.11, "ep": 0.085, "m": "bois_dur", "grp": "cloture"})
    for (a, b) in ((18.5, 30.0), (30.2, 33.0)):     # portails coulissants du stationnement locatif (rue Ouest)
        data["lames"].append({"x0": 0.04, "y0": a, "x1": 0.14, "y1": b, "z0": 0.05, "z1": F.CLOTURE_H,
                              "dir": "v", "pas": 0.11, "ep": 0.085, "m": "bois_dur", "grp": "cloture"})
    data["boxes"].append({"x0": 19.8, "y0": 0.0, "x1": 20.0, "y1": 33.0, "z0": 0, "z1": 2.2, "m": "enduit", "grp": "cloture"})
    data["boxes"].append({"x0": 0.0, "y0": 32.8, "x1": 20.0, "y1": 33.0, "z0": 0, "z1": 2.2, "m": "enduit", "grp": "cloture"})
    # ------------------------------------------------------------------ locatif : 2 maisons duplex
    expl_m = [o for k, x0 in enumerate(MX[:2]) for o in F.ouvertures_maison(x0, k == 0)]
    murs_niveaux(data, LOCATIF_M, NIV_M, expl_m,
                 lambda n, s_, l_: "moellons" if (n == "RDC" and s_ == "v" and abs(l_ - 3.0) < 0.06) else "enduit", "locatif")
    data["boxes"].append({"x0": 3.0, "y0": 21.0, "x1": 20.0, "y1": 30.0, "z0": 0, "z1": Z0, "m": "socle", "grp": "locatif"})
    Tm = NIV_M["TOIT"][0]
    R1m = NIV_M["R+1"][0]
    for k, x0 in enumerate(MX[:2]):
        x1 = x0 + 8.5
        for (a, b, c, d) in [(x0, 21.0, x1, 21.15), (x0, 29.85, x1, 30.0), (x1 - 0.15, 21.0, x1, 30.0),
                             (x0, 21.0, x0 + 0.15, 30.0)]:
            data["boxes"].append({"x0": a, "y0": b, "x1": c, "y1": d, "z0": Tm, "z1": Tm + 1.0, "m": "enduit", "grp": "locatif"})
        for (a, b, c, d) in [(x0, 27.5, x0 + 2.0, 30.0), (x0 + 5.6, 27.5, x1, 30.0)]:
            data["slabs"].append({"x0": a, "y0": b, "x1": c, "y1": d, "z": Tm, "t": 0.25, "m": "beton_clair", "grp": "locatif"})
        for z in (R1m, Tm):                                   # nez de dalle continus, comme la villa
            data["slabs"].append({"x0": x0 - (0.16 if k == 0 else 0), "y0": 20.84, "x1": x1, "y1": 30.16, "z": z, "t": 0.18,
                                  "m": "beton_clair", "grp": "locatif"})
        for sens, line, a, b, out, axes in F.peau_maison(x0, k == 0):
            peau(data, variante, sens, line, a, b, out, axes, R1m, Tm - 0.2, grp="locatif")
        cx0, cy0, cx1, cy1 = F.couv_maison(x0, k == 0)
        zc = Z0 + F.COUV_Z - (0.18 if variante == "V1" else 0.3)
        for px in (x0 + 0.15, x0 + 4.25, x1 - 0.15):
            for py in (21.15, 27.35):
                data["boxes"].append({"x0": px - 0.07, "y0": py - 0.07, "x1": px + 0.07, "y1": py + 0.07, "z0": Tm,
                                      "z1": zc, "m": "metal", "grp": "locatif"})
        if variante == "V1":
            data["slabs"].append({"x0": cx0, "y0": cy0, "x1": cx1, "y1": cy1, "z": zc + 0.18, "t": 0.18,
                                  "m": "beton_clair", "grp": "locatif"})
        else:
            data["roofs"].append({"x0": cx0, "y0": cy0, "x1": cx1, "y1": cy1, "z": zc, "pente": 15, "m": "toit",
                                  "sous": "bois", "grp": "locatif"})
        data["boxes"].append({"x0": x0 + 0.15, "y0": 20.85, "x1": x1 - 0.15, "y1": 21.45, "z0": Tm, "z1": Tm + 0.6,
                              "m": "beton_clair", "grp": "locatif"})
        data["trees"].append({"x": x0 + 2.0 + 3.5 * (k % 2), "y": 19.6, "r": 1.2, "h": 4.0, "grp": "arbres_m"})
        data["boxes"].append({"x0": x0, "y0": 18.1, "x1": x1, "y1": 18.7, "z0": 0, "z1": 0.4, "m": "vegetal_fonce", "grp": "locatif"})
    # ------------------------------------------------------------------ contexte (photos du site)
    # rue Ouest (x < 0) puis maisons de ville R+2 a toits rouges en face ; voisin Est R+2 gris ; rue Nord
    for y0 in (-2.0, 9.0, 20.0):
        data["boxes"].append({"x0": -21.0, "y0": y0, "x1": -10.0, "y1": y0 + 10.0, "z0": 0, "z1": 8.4, "m": "contexte"})
        data["roofs"].append({"x0": -21.4, "y0": y0 - 0.4, "x1": -9.6, "y1": y0 + 10.4, "z": 8.4, "pente": 30,
                              "m": "contexte", "sous": "contexte"})
    data["boxes"].append({"x0": 22.0, "y0": 2.0, "x1": 34.0, "y1": 17.0, "z0": 0, "z1": 7.2, "m": "contexte"})
    data["boxes"].append({"x0": 22.0, "y0": 19.0, "x1": 33.0, "y1": 31.0, "z0": 0, "z1": 4.0, "m": "contexte"})
    data["boxes"].append({"x0": 2.0, "y0": -30.0, "x1": 16.0, "y1": -18.0, "z0": 0, "z1": 7.0, "m": "contexte"})
    data["boxes"].append({"x0": 2.0, "y0": 35.0, "x1": 18.0, "y1": 47.0, "z0": 0, "z1": 6.5, "m": "contexte"})
    OUT.mkdir(parents=True, exist_ok=True)
    name = f"scene_C_{variante}.json"
    (OUT / name).write_text(json.dumps(data))
    print(name, "murs", len(data["walls"]), "boites", len(data["boxes"]), "lames", len(data["lames"]))


if __name__ == "__main__":
    build("V1")
    build("V2")
