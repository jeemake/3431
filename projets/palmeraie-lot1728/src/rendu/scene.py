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


def build():
    data = {"walls": [], "slabs": [], "boxes": [], "rails": [], "trees": [], "water": [], "glass": []}
    for niveau, (z0, z1) in NIV.items():
        cells = occ(OPTION_C["pieces"], niveau)
        segs = walls(cells)
        ops = openings(OPTION_C, niveau, segs, cells)
        for sens, a, b, line in segs:
            data["walls"].append({"sens": sens, "a": a, "b": b, "line": line, "z0": z0, "z1": z1,
                                  "ops": [o for o in ops if o["sens"] == sens and abs(o["line"] - line) < 0.06
                                          and o["a"] < b and o["b"] > a]})
        # dalle haute de chaque piece close + debords de 1,2 m sur les cotes exterieurs
        for r in OPTION_C["pieces"]:
            if r["niveau"] != niveau or not r["clos"]:
                continue
            for x0, y0, x1, y1 in r["rects"]:
                data["slabs"].append({"x0": x0, "y0": y0, "x1": x1, "y1": y1, "z": z1, "t": 0.25})
    # debords de toiture (couronne de 1,0 m) au sommet de chaque volume
    for (x0, y0, x1, y1, z) in [(3.2, 5.0, 14.9, 9.2, 6.85), (3.2, 9.2, 9.2, 16.5, 6.85), (14.9, 8.6, 18.5, 13.6, 6.85),
                                (14.9, 5.0, 18.5, 8.6, 3.75), (14.9, 13.6, 18.5, 16.5, 3.75)]:
        data["slabs"].append({"x0": max(2.4, x0 - 0.8), "y0": max(4.2, y0 - 0.8), "x1": min(19.2, x1 + 0.6),
                              "y1": min(17.3, y1 + 0.6), "z": z + 0.35, "t": 0.12, "roof": True})
    # terrasse couverte + passerelle (meme dalle), poteaux, garde-corps a lames de la passerelle
    data["slabs"].append({"x0": 9.2, "y0": 9.2, "x1": 14.9, "y1": 11.6, "z": 3.75, "t": 0.25})
    for px in (9.4, 12.05, 14.7):
        data["boxes"].append({"x0": px - 0.1, "y0": 11.4, "x1": px + 0.1, "y1": 11.6, "z0": 0.45, "z1": 3.5, "m": "bois"})
    data["rails"].append({"x0": 9.2, "y0": 10.35, "x1": 14.9, "y1": 10.45, "z0": 3.75, "z1": 4.85})
    data["slabs"].append({"x0": 9.2, "y0": 9.2, "x1": 14.9, "y1": 10.4, "z": 6.95, "t": 0.12, "roof": True})
    # balcon Ouest de la suite
    data["slabs"].append({"x0": 2.0, "y0": 12.2, "x1": 3.2, "y1": 16.5, "z": 3.75, "t": 0.2})
    data["rails"].append({"x0": 2.0, "y0": 12.2, "x1": 2.1, "y1": 16.5, "z0": 3.75, "z1": 4.85})
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
    data["boxes"].append({"x0": 4.4, "y0": 0.3, "x1": 6.8, "y1": 2.7, "z0": 0, "z1": 2.8, "m": "mur"})
    # socle de la maison
    data["boxes"].append({"x0": 3.2, "y0": 5.0, "x1": 18.5, "y1": 16.5, "z0": 0, "z1": 0.45, "m": "socle"})
    # patio : arbre, bassin, massifs
    data["trees"] += [{"x": 12.8, "y": 14.8, "r": 1.5, "h": 6.0}, {"x": 1.5, "y": 9.0, "r": 1.4, "h": 5.0},
                      {"x": 1.6, "y": 2.2, "r": 1.5, "h": 5.5}, {"x": 1.5, "y": 14.5, "r": 1.2, "h": 4.5}]
    data["water"].append({"x0": 9.8, "y0": 12.0, "x1": 12.2, "y1": 12.8})
    # clotures (2,2 m) avec portail, portillons ; mur separatif 2,5 m
    data["rails"] += [
        {"x0": 0.0, "y0": 0.0, "x1": 7.0, "y1": 0.2, "z0": 0, "z1": 2.2},
        {"x0": 15.9, "y0": 0.0, "x1": 17.0, "y1": 0.2, "z0": 0, "z1": 2.2},
        {"x0": 19.5, "y0": 0.0, "x1": 20.0, "y1": 0.2, "z0": 0, "z1": 2.2},
        {"x0": 0.0, "y0": 0.0, "x1": 0.2, "y1": 33.0, "z0": 0, "z1": 2.2},
        {"x0": 19.8, "y0": 0.0, "x1": 20.0, "y1": 33.0, "z0": 0, "z1": 2.2},
        {"x0": 0.0, "y0": 17.9, "x1": 9.2, "y1": 18.0, "z0": 0, "z1": 2.5},
        {"x0": 14.9, "y0": 17.9, "x1": 20.0, "y1": 18.0, "z0": 0, "z1": 2.5},
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
