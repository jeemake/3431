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
from projet import LOCATIF, OPTION_C  # noqa: E402
import facade as F  # noqa: E402

G = 0.1
NIV = {"RDC": (0.45, 3.75), "R+1": (3.75, 6.85)}
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


def build():
    data = {"walls": [], "slabs": [], "boxes": [], "rails": [], "trees": [], "water": [], "glass": [],
            "claustras": [], "lames": []}
    for niveau, (z0, z1) in NIV.items():
        cells = occ(OPTION_C["pieces"], niveau)
        segs = walls(cells)
        ops = explicit(niveau, segs, openings(OPTION_C, niveau, segs, cells))
        for sens, a, b, line in segs:
            mine = [o for o in ops if o["sens"] == sens and abs(o["line"] - line) < 0.06 and o["a"] < b and o["b"] > a]
            data["walls"].append({"sens": sens, "a": a, "b": b, "line": line, "z0": z0, "z1": z1,
                                  "m": "btc" if niveau == "RDC" else "mur", "ops": mine,
                                  "grp": "guerite" if (sens == "h" and line < 3) or (sens == "v" and b <= 3) else "maison"})
            for o in mine:   # claustra BTC devant les ouvertures « claustra » (cage d'escalier)
                if o["kind"] != "claustra":
                    continue
                d = outside(cells, sens, line, (o["a"] + o["b"]) / 2)
                off = (line + d * 0.12, line + d * 0.27)
                lo, hi = min(off), max(off)
                za, zb = z0 + 0.05, z1 - 0.05
                if sens == "h":
                    data["claustras"].append({"x0": o["a"] - 0.15, "y0": lo, "x1": o["b"] + 0.15, "y1": hi, "z0": za, "z1": zb})
                else:
                    data["claustras"].append({"x0": lo, "y0": o["a"] - 0.15, "x1": hi, "y1": o["b"] + 0.15, "z0": za, "z1": zb})
        # dalle haute de chaque piece close + debords de 1,2 m sur les cotes exterieurs
        for r in OPTION_C["pieces"]:
            if r["niveau"] != niveau or not r["clos"]:
                continue
            for x0, y0, x1, y1 in r["rects"]:
                data["slabs"].append({"x0": x0, "y0": y0, "x1": x1, "y1": y1, "z": z1, "t": 0.25})
    # toiture-ombriere (ABYA 2) : une dalle mince debordante sur tout l'etage
    for x0, y0, x1, y1, d in F.TOIT:
        data["slabs"].append({"x0": x0 - d["w"], "y0": y0 - d["n"], "x1": x1 + d["e"], "y1": y1 + d["s"],
                              "z": F.TOIT_Z, "t": F.TOIT_EP, "roof": True, "m": "ombriere"})
    for x0, y0, x1, y1, z in F.CASQUETTES:
        data["slabs"].append({"x0": x0, "y0": y0, "x1": x1, "y1": y1, "z": z, "t": 0.22, "m": "ombriere"})
    # aile de service de plain-pied : acrotere bas
    for (x0, y0, x1, y1, z) in [(14.9, 5.0, 18.5, 8.6, 3.75), (14.9, 13.6, 18.5, 16.5, 3.75)]:
        data["slabs"].append({"x0": max(2.4, x0 - 0.8), "y0": max(4.2, y0 - 0.8), "x1": min(19.2, x1 + 0.6),
                              "y1": min(17.3, y1 + 0.6), "z": z + 0.35, "t": 0.12, "roof": True})
    # terrasse couverte + passerelle (meme dalle), poteaux, garde-corps a lames de la passerelle
    data["slabs"].append({"x0": 9.2, "y0": 9.2, "x1": 14.9, "y1": 11.6, "z": 3.75, "t": 0.25})
    for px in (9.4, 12.05, 14.7):
        data["boxes"].append({"x0": px - 0.1, "y0": 11.4, "x1": px + 0.1, "y1": 11.6, "z0": 0.45, "z1": 3.5, "m": "bois"})
    data["rails"].append({"x0": 9.2, "y0": 10.35, "x1": 14.9, "y1": 10.45, "z0": 3.75, "z1": 4.85})
    # balcon Ouest de la suite
    data["slabs"].append({"x0": 2.0, "y0": 12.2, "x1": 3.2, "y1": 16.5, "z": 3.75, "t": 0.2})
    # persiennes coulissantes bois et barreaudages (ABYA 2), claustras BTC (aile de service, double peau Ouest)
    zn = {"RDC": 0.45, "R+1": 3.75}
    for niv, sens, line, a, b, z0, z1 in F.PERSIENNES:
        o = -1 if (sens == "h" and line in (5.0, 8.6)) or (sens == "v" and line < 10) else 1
        lo, hi = sorted((line + o * 0.12, line + o * 0.17))
        box = ({"x0": a, "y0": lo, "x1": b, "y1": hi} if sens == "h" else {"x0": lo, "y0": a, "x1": hi, "y1": b})
        data["lames"].append({**box, "z0": zn[niv] + z0, "z1": zn[niv] + z1, "dir": "h", "pas": 0.07, "m": "bois"})
    for niv, sens, line, a, b in F.BARREAUDAGES:
        lo, hi = sorted((line - 0.1, line - 0.13))
        data["lames"].append({"x0": a, "y0": lo, "x1": b, "y1": hi, "z0": zn[niv], "z1": zn[niv] + 1.0,
                              "dir": "v", "pas": 0.11, "ep": 0.025, "m": "metal"})
    for x0, y0, x1, y1, z0, z1 in F.CLAUSTRAS:
        data["claustras"].append({"x0": x0, "y0": y0, "x1": x1, "y1": y1, "z0": z0, "z1": z1})
    # pergola plantee + claustra haute au Sud du patio
    for i in range(8):
        x = 9.4 + i * 0.75
        data["boxes"].append({"x0": x, "y0": 16.5, "x1": x + 0.12, "y1": 18.0, "z0": 3.0, "z1": 3.2, "m": "bois"})
    data["rails"].append({"x0": 9.2, "y0": 17.85, "x1": 14.9, "y1": 18.0, "z0": 0.0, "z1": 4.0, "claustra": True})
    # preau, sechoir couvert (toitures legeres sur poteaux)
    for x0, y0, x1, y1 in [(15.9, 2.6, 18.5, 5.0), (18.5, 2.6, 20.0, 8.6)]:
        data["slabs"].append({"x0": x0, "y0": y0, "x1": x1, "y1": y1, "z": 2.9, "t": 0.1, "roof": True})
        for px, py in [(x0 + 0.1, y0 + 0.1), (x1 - 0.1, y0 + 0.1)]:
            data["boxes"].append({"x0": px - 0.06, "y0": py - 0.06, "x1": px + 0.06, "y1": py + 0.06, "z0": 0, "z1": 2.9, "m": "bois"})
    # guerite
    data["boxes"].append({"x0": 4.4, "y0": 0.3, "x1": 6.8, "y1": 2.7, "z0": 0, "z1": 2.8, "m": "btc", "grp": "guerite"})
    data["slabs"].append({"x0": 4.0, "y0": 0.25, "x1": 7.3, "y1": 3.2, "z": 3.0, "t": 0.16, "m": "ombriere", "grp": "guerite"})
    # socle de la maison
    data["boxes"].append({"x0": 3.2, "y0": 5.0, "x1": 18.5, "y1": 16.5, "z0": 0, "z1": 0.45, "m": "socle"})
    # patio : arbre, bassin, massifs
    data["trees"] += [{"x": 12.8, "y": 14.8, "r": 1.5, "h": 6.0}, {"x": 1.5, "y": 9.0, "r": 1.4, "h": 5.0, "grp": "arbres"},
                      {"x": 1.6, "y": 2.2, "r": 1.5, "h": 5.5, "grp": "arbres"},
                      {"x": 1.5, "y": 14.5, "r": 1.2, "h": 4.5, "grp": "arbres"}]
    data["water"].append({"x0": 9.8, "y0": 12.0, "x1": 12.2, "y1": 12.8})
    # clotures (2,2 m) avec portail, portillons ; mur separatif 2,5 m
    # cloture sur rue (Nord et Ouest de la villa) : socle 1,0 m + claustra BTC ; portail et portillons en lames bois
    for x0, y0, x1, y1 in [(0.0, 0.0, 7.0, 0.2), (15.9, 0.0, 17.0, 0.2), (19.5, 0.0, 20.0, 0.2), (0.0, 0.2, 0.2, 18.0)]:
        data["boxes"].append({"x0": x0, "y0": y0, "x1": x1, "y1": y1, "z0": 0, "z1": F.CLOTURE_SOCLE, "m": "socle_sombre", "grp": "cloture"})
        data["claustras"].append({"x0": x0 + (0.05 if x1 - x0 < 0.3 else 0), "y0": y0 + (0.05 if y1 - y0 < 0.3 else 0),
                                  "x1": x1 - (0.05 if x1 - x0 < 0.3 else 0), "y1": y1 - (0.05 if y1 - y0 < 0.3 else 0),
                                  "z0": F.CLOTURE_SOCLE, "z1": F.CLOTURE_H,
                                  "bw": 0.18, "pas": 0.40, "rh": 0.30, "jt": 0.08, "grp": "cloture"})
    # portillon, portillon de service ; portail coulissant de 7,5 m represente ouvert (glisse derriere la cloture Ouest)
    for a, b, y0 in [(7.0, 8.4, 0.04), (17.0, 19.5, 0.04), (0.95, 8.35, 0.24)]:
        data["lames"].append({"x0": a + 0.05, "y0": y0, "x1": b - 0.05, "y1": y0 + 0.12, "z0": 0.05, "z1": F.CLOTURE_H,
                              "dir": "v", "pas": 0.13, "ep": 0.09, "m": "bois", "grp": "cloture"})
    data["rails"] += [
        {"x0": 0.0, "y0": 18.0, "x1": 0.2, "y1": 33.0, "z0": 0, "z1": 2.2, "grp": "cloture"},
        {"x0": 19.8, "y0": 0.0, "x1": 20.0, "y1": 33.0, "z0": 0, "z1": 2.2, "grp": "cloture"},
        {"x0": 0.0, "y0": 17.9, "x1": 9.2, "y1": 18.0, "z0": 0, "z1": 2.5, "grp": "cloture"},
        {"x0": 14.9, "y0": 17.9, "x1": 20.0, "y1": 18.0, "z0": 0, "z1": 2.5, "grp": "cloture"},
    ]
    # contexte : locatif R+1 (barre 14,4 x 9,0 m + coursive) et voisins
    data["boxes"].append({"x0": 5.6, "y0": 22.0, "x1": 20.0, "y1": 31.0, "z0": 0, "z1": 6.6, "m": "contexte"})
    data["boxes"].append({"x0": 5.6, "y0": 20.8, "x1": 20.0, "y1": 22.0, "z0": 3.3, "z1": 3.5, "m": "contexte"})
    data["boxes"].append({"x0": 22.0, "y0": 3.0, "x1": 33.0, "y1": 16.0, "z0": 0, "z1": 7.0, "m": "contexte"})
    data["boxes"].append({"x0": 22.0, "y0": 19.0, "x1": 33.0, "y1": 31.0, "z0": 0, "z1": 3.6, "m": "contexte"})
    data["boxes"].append({"x0": -22.0, "y0": 2.0, "x1": -9.0, "y1": 15.0, "z0": 0, "z1": 6.5, "m": "contexte"})
    data["boxes"].append({"x0": 2.0, "y0": -24.0, "x1": 16.0, "y1": -10.0, "z0": 0, "z1": 7.0, "m": "contexte"})
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "scene_C.json").write_text(json.dumps(data))
    n_ops = sum(len(w["ops"]) for w in data["walls"])
    print("murs", len(data["walls"]), "ouvertures", n_ops)


if __name__ == "__main__":
    build()
