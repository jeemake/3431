"""Maquette BIMCraft de l'option C v5 (villa a patio) et des 2 maisons duplex.

Tout part du meme modele que les autres documents : `projet.py` (pieces, portes, trame, niveaux) et `facade.py`
(ouvertures explicites des facades, peau de l'etage, couvertures, poteaux, clotures). Ce script ecrit un script de
commandes BIMCraft (une commande JSON par ligne, `out/bimcraft/Lot1728_v5.txt`), le fait tourner par
`bimcraft-cli`, puis enregistre la maquette (.bimc), l'IFC4, les plans (SVG), coupes, elevations et vues 3D (PNG),
les nomenclatures (CSV, XLSX) et le jeu de planches A3 (PDF).

Repere BIMCraft : millimetres, X vers l'Est, Y vers le Nord, Z vers le haut. Le plan du projet a y vers le Sud depuis la
rue Nord : X = 1000 x, Y = 1000 (33 - y).

    python3 bimcraft_modele.py          # BIMCRAFT_CLI=... pour un autre binaire
"""
import json
import os
import pathlib
import shutil
import subprocess

from shapely.geometry import box
from shapely.ops import unary_union

import facade as F
from projet import LOCATIF_M, MX, MY, OPTION_C

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "out" / "bimcraft"
CLI = os.environ.get("BIMCRAFT_CLI") or shutil.which("bimcraft-cli") or "/home/user/BIMCraft/target/release/bimcraft-cli"
NOM = "Lot1728_v5"
G = 0.05                                    # pas de la grille d'occupation (m)
Z_CROP = (-0.9, 10.2)                      # hauteurs du recadrage des coupes et elevations (m)
H = {"RDC": 0, "R+1": 3300, "TOIT": 6600, "COUV": 9000}
LEVEL = {"RDC": "RDC", "R+1": "R+1", "TOIT": "Toit-terrasse", "COUV": "Couverture"}


def P(x, y):
    return [round(x * 1000), round((33.0 - y) * 1000)]


def mm(v):
    return round(v * 1000)


class Script:
    def __init__(self):
        self.lines = []
        self.families = {}       # famille -> {type: params}

    def c(self, cmd, **params):
        self.lines.append(f"{cmd} {json.dumps(params, ensure_ascii=False)}")

    def note(self, text):
        self.lines.append(f"# {text}")

    def ftype(self, family, w, h, sill=None):
        name = f"{mm(w)} x {mm(h)}"
        p = {"Width": mm(w), "Height": mm(h)}
        if sill is not None:
            p["Sill Height"] = mm(sill)
        self.families.setdefault(family, {})[name] = p
        return name


# ------------------------------------------------------------------------------------------------ murs
def cellules(pieces, niveau):
    cells = {}
    for r in pieces:
        if r["niveau"] != niveau or not r["clos"]:
            continue
        for x0, y0, x1, y1 in r["rects"]:
            for i in range(round(x0 / G), round(x1 / G)):
                for j in range(round(y0 / G), round(y1 / G)):
                    cells[(i, j)] = r
    return cells


def segments(cells):
    """Aretes de la grille entre deux pieces differentes (cloison, mitoyen) ou entre une piece et le vide (exterieur),
    fusionnees en segments : (sens, a, b, ligne, genre)."""
    runs = {}

    def genre(a, b):
        if a is b:
            return None
        if a and b:
            la, lb = a.get("logement"), b.get("logement")
            return "mitoyen" if (la and lb and la != lb) else "int"
        return "ext"

    keys = set()
    for (i, j) in cells:
        keys |= {("h", i, j), ("h", i, j + 1), ("v", i, j), ("v", i + 1, j)}
    for sens, i, j in keys:
        if sens == "h":
            g = genre(cells.get((i, j - 1)), cells.get((i, j)))
            if g:
                runs.setdefault((sens, j, g), []).append(i)
        else:
            g = genre(cells.get((i - 1, j)), cells.get((i, j)))
            if g:
                runs.setdefault((sens, i, g), []).append(j)
    out = []
    for (sens, line, g), idx in runs.items():
        idx = sorted(idx)
        start = prev = idx[0]
        for k in idx[1:] + [None]:
            if k is None or k != prev + 1:
                out.append((sens, start * G, (prev + 1) * G, line * G, g))
                start = k
            prev = k if k is not None else prev
    return sorted(out, key=lambda s: (s[4], s[0], s[3], s[1]))


def pts(sens, a, b, line):
    return [P(a, line), P(b, line)] if sens == "h" else [P(line, a), P(line, b)]


def sur(segs, sens, line, c, genres=("ext",)):
    return any(s[0] == sens and abs(s[3] - line) < 0.06 and s[1] - 0.05 <= c <= s[2] + 0.05 and s[4] in genres for s in segs)


# ------------------------------------------------------------------------------------------------ ouvertures
def famille(kind, w):
    if kind == "baie":
        return "Porte coulissante", True
    if kind == "porte":
        return ("Porte simple" if w <= 1.05 else "Porte double"), True
    if kind == "fenetre":
        return "Fenêtre coulissante", False
    if kind == "claustra":
        return "Fenêtre fixe", False
    return "Fenêtre fixe", False          # jour haut


RANG = [("Hall", 0), ("Dégagement", 0), ("Galerie", 0), ("Entrée", 0), ("Escalier", 0), ("Salon", 1), ("Séjour", 1),
        ("Salle à manger", 1), ("Cuisine", 1), ("Chambre", 2), ("Bureau", 2), ("Dressing", 2), ("Guérite", 2)]


def rang(r):
    return next((k for mot, k in RANG if mot in r["nom"]), 3)


def ouvre_vers(cells, sens, line, c):
    """Cote ou s'ouvre la porte : vers l'interieur, sinon vers la piece la plus privee (salle d'eau, chambre) ;
    renvoie True s'il faut la retourner (BIMCraft l'ouvre au Nord sur un mur h, a l'Est sur un mur v)."""
    if cells is None:
        return False
    q = lambda x, y: cells.get((int(x / G), int(y / G)))
    moins, plus = ((q(c, line - 0.1), q(c, line + 0.1)) if sens == "h" else (q(line - 0.1, c), q(line + 0.1, c)))
    if moins is None and plus is None:
        return False
    if moins is None or plus is None:
        cote = "plus" if moins is None else "moins"
    else:
        cote = "plus" if rang(plus) > rang(moins) or (rang(plus) == rang(moins) and sens == "v") else "moins"
    defaut = "moins" if sens == "h" else "plus"
    return cote != defaut


def ouvrir(s, niveau, sens, line, a, b, z0, z1, kind, cells=None):
    w = b - a
    c = (a + b) / 2
    fam, porte = famille(kind, w)
    at = P(c, line) if sens == "h" else P(line, c)
    if porte:
        kw = {"flip_facing": True} if ouvre_vers(cells, sens, line, c) else {}
        s.c("door", at=at, level=LEVEL[niveau], family=fam, type=s.ftype(fam, w, z1 - z0), **kw)
    else:
        s.c("window", at=at, level=LEVEL[niveau], family=fam, type=s.ftype(fam, w, z1 - z0, z0), sill=mm(z0))


def ouvertures(s, opt, niveau, segs, explicites, cells, h_int=2.1, h_ext=2.4, exceptions=None):
    ex = [o for o in explicites if o[0] == niveau]
    for o in ex:
        ouvrir(s, *o, cells=cells)
    for niv, x, y, sens, w in opt["portes"]:
        if niv != niveau:
            continue
        line, c = (y, x) if sens == "h" else (x, y)
        if any(e[1] == sens and abs(e[2] - line) < 0.06 and e[3] - 0.05 <= c <= e[4] + 0.05 for e in ex):
            continue
        if not sur(segs, sens, line, c, ("ext", "int", "mitoyen")):
            continue                          # porte vers un espace ouvert sans mur (ouverture libre)
        ext = sur(segs, sens, line, c)
        h = (exceptions or {}).get((niv, x, y), h_ext if ext else h_int)
        kind = "baie" if w >= 1.85 else "porte"
        ouvrir(s, niveau, sens, line, c - w / 2, c + w / 2, 0.0, h, kind, cells)


# ------------------------------------------------------------------------------------------------ dalles
def emprise(pieces, niveau, extra=(), clos=True):
    rects = [box(*r) for p in pieces if p["niveau"] == niveau and (p["clos"] or not clos) for r in p["rects"]]
    return unary_union(rects + [box(*r) for r in extra]).buffer(0.001, join_style=2).buffer(-0.001, join_style=2)


def contour(poly):
    polys = [poly] if poly.geom_type == "Polygon" else list(poly.geoms)
    out = []
    for p in polys:
        p = p.simplify(0.001)
        ring = [P(x, y) for x, y in list(p.exterior.coords)[:-1]]
        holes = [[P(x, y) for x, y in list(h.coords)[:-1]] for h in p.interiors]
        out.append((ring, holes))
    return out


def dalle(s, poly, niveau, type_, offset=0):
    for ring, holes in contour(poly):
        kw = {"boundary": ring, "level": LEVEL[niveau], "type": type_}
        if holes:
            kw["openings"] = holes
        if offset:
            kw["offset"] = offset
        s.c("floor", **kw)


# ------------------------------------------------------------------------------------------------ bibliotheque
def bibliotheque(s):
    s.note("Materiaux et types (references du client : moellons, enduit, lames de bois, claustra beton)")
    mats = [
        ("Enduit", "#E6E0D6", "plaster", None, None),
        ("Moellons", "#8E857B", "block", None, "crosshatch"),
        ("Béton clair", "#D9D6CF", "concrete", None, "concrete"),
        ("Bois dur", "#9A6A43", "boards", None, None),
        ("Lames bois (peau)", "#A1714A", "boards", 35, None),
        ("Claustra béton", "#CFCAC0", "block", 45, None),
        ("Végétal", "#5F7F4C", "fabric", None, None),
        ("Acier noir", "#2B2B2B", "metal", None, None),
    ]
    for name, col, tex, tr, cut in mats:
        kw = {"name": name, "color": col, "texture": {"kind": tex}}
        if tr:
            kw["transparency"] = tr
        if cut:
            kw["cut"] = cut
        s.c("material", **kw)
    W = lambda name, layers: s.c("type", category="wall", name=name,
                                 layers=[{"function": f, "material": m, "thickness": t} for f, m, t in layers])
    W("Mur ext. moellons 200", [("finish", "Moellons", 40), ("structure", "Bloc de béton", 145), ("finish", "Enduit", 15)])
    W("Mur ext. enduit 200", [("finish", "Enduit", 15), ("structure", "Bloc de béton", 170), ("finish", "Enduit", 15)])
    W("Mur mitoyen 200", [("finish", "Enduit", 15), ("structure", "Bloc de béton", 170), ("finish", "Enduit", 15)])
    W("Cloison 100", [("finish", "Enduit", 15), ("structure", "Bloc de béton", 70), ("finish", "Enduit", 15)])
    W("Acrotère 150", [("structure", "Béton clair", 150)])
    W("Clôture moellons 200", [("structure", "Moellons", 200)])
    W("Clôture claustra 200", [("structure", "Claustra béton", 200)])
    W("Clôture enduite 200", [("finish", "Enduit", 15), ("structure", "Bloc de béton", 170), ("finish", "Enduit", 15)])
    W("Portail lames bois 100", [("structure", "Lames bois (peau)", 100)])
    W("Mur végétalisé 180", [("finish", "Végétal", 40), ("structure", "Bloc de béton", 100), ("finish", "Végétal", 40)])
    W("Peau lames bois 140", [("structure", "Lames bois (peau)", 140)])
    s.c("type", category="floor", name="Dalle BA 250",
        layers=[{"function": "finish", "material": "Chape", "thickness": 50},
                {"function": "structure", "material": "Béton", "thickness": 200}])
    s.c("type", category="floor", name="Dalle mince 120",
        layers=[{"function": "structure", "material": "Béton clair", "thickness": 120}])
    s.c("type", category="roof", name="Couverture mince 180",
        layers=[{"function": "structure", "material": "Béton clair", "thickness": 180}])
    s.c("material", name="Latérite", color="#B07650", texture={"kind": "concrete"})
    s.c("material", name="Pelouse", color="#7E9A5A", texture={"kind": "fabric"})
    s.c("type", category="floor", name="Terrain (latérite)", layers=[{"function": "structure", "material": "Latérite", "thickness": 300}])
    s.c("type", category="floor", name="Jardin planté", layers=[{"function": "structure", "material": "Pelouse", "thickness": 100}])
    s.c("family", name="Arbre", category="generic",
        parameters=[{"name": "Rayon", "kind": "length", "value": 1500}, {"name": "Hauteur", "kind": "length", "value": 5200}],
        types={f"{mm(d)} x {mm(h)}": {"Rayon": mm(d / 2 * 0.8), "Hauteur": mm(h)} for _b, _x, _y, d, _t, _r, _c, h in VEGETATION},
        forms=[{"plane": "xy", "circle": {"centre": [0, 0], "radius": 110}, "from": 0, "to": "Hauteur * 0.45", "material": "Bois dur"},
               {"plane": "xy", "sketch": [{"centre": [0, 0], "radius": "Rayon * 0.55"}], "top": [{"centre": [0, 0], "radius": "Rayon"}],
                "from": "Hauteur * 0.4", "to": "Hauteur * 0.7", "material": "Végétal"},
               {"plane": "xy", "sketch": [{"centre": [0, 0], "radius": "Rayon"}], "top": [{"centre": [0, 0], "radius": "Rayon * 0.35"}],
                "from": "Hauteur * 0.7", "to": "Hauteur", "material": "Végétal"}])
    s.c("type", category="column", name="Poteau acier 140", width=140, depth=140)
    s.c("type", category="column", name="Poteau bois 200", width=200, depth=200)


# ------------------------------------------------------------------------------------------------ batiments
def murs(s, opt, niveau, segs, hauteur=None, type_ext=lambda sens, line: "Mur ext. enduit 200", sauf=lambda seg: False):
    for seg in segs:
        sens, a, b, line, g = seg
        if sauf(seg):
            continue
        t = {"ext": type_ext(sens, line), "int": "Cloison 100", "mitoyen": "Mur mitoyen 200"}[g]
        kw = {"points": pts(sens, a, b, line), "type": t, "level": LEVEL[niveau]}
        if hauteur:
            kw["height"] = hauteur
        s.c("wall", **kw)


def pieces(s, opt, niveau, prefixe=None):
    for r in opt["pieces"]:
        if r["niveau"] != niveau or not r["clos"]:
            continue
        x0, y0, x1, y1 = max(r["rects"], key=lambda q: (q[2] - q[0]) * (q[3] - q[1]))
        nom = r["nom"]
        kw = {"point": P((x0 + x1) / 2, (y0 + y1) / 2), "level": LEVEL[niveau]}
        if prefixe and nom.startswith(r.get("logement", "") + " "):
            nom = nom[len(r["logement"]):].strip()
            rang_ = [q for q in opt["pieces"] if q["niveau"] == niveau and q.get("logement") == r["logement"] and q["clos"]]
            kw["number"] = f'{r["logement"]}.{"012"[["RDC", "R+1", "TOIT"].index(niveau)]}{rang_.index(r) + 1}'
        kw["name"] = nom
        s.c("room", **kw)


def villa(s):
    C = OPTION_C
    s.note("VILLA : murs par niveau, deduits des pieces de projet.py (grille de 5 cm)")
    for niveau in ("RDC", "R+1", "TOIT"):
        cells = cellules(C["pieces"], niveau)
        segs = segments(cells)
        guerite = lambda seg: (seg[3] < 3.0 if seg[0] == "h" else seg[2] <= 3.0)
        if niveau == "RDC":
            murs(s, C, niveau, segs, type_ext=lambda sens, line: "Mur ext. moellons 200" if (sens, round(line, 1)) in F.RUES
                 else "Mur ext. enduit 200", sauf=guerite)
            murs(s, C, niveau, [g for g in segs if guerite(g)], hauteur=2200,
                 type_ext=lambda *_: "Clôture moellons 200")
        elif niveau == "TOIT":
            murs(s, C, niveau, segs, hauteur=2150)
        else:
            murs(s, C, niveau, segs)
        ouvertures(s, C, niveau, segs, F.OUVERTURES, cells, exceptions={("RDC", 4.5, 2.7): 2.0})
        pieces(s, C, niveau)
    s.note("Dalles : RDC (emprise close), R+1 (RDC + terrasse couverte + loggia + jardiniere), toit-terrasse")
    rdc = emprise(C["pieces"], "RDC", extra=[(2.5, 4.5, 15.5, 5.5)]).difference(box(3.0, 0.0, 6.0, 3.0))
    dalle(s, rdc, "RDC", "Dalle BA 250")
    r1 = unary_union([emprise(C["pieces"], "RDC").difference(box(3.0, 0.0, 6.0, 3.0)), box(9.0, 11.0, 14.5, 13.4),
                      box(2.5, 4.5, 18.0, 5.5), box(1.7, 13.6, 2.5, 16.8)])
    dalle(s, r1, "R+1", "Dalle BA 250")
    toit = unary_union([emprise(C["pieces"], "R+1"), box(2.5, 4.5, 18.0, 5.5)])
    dalle(s, toit, "TOIT", "Dalle BA 250")
    dalle(s, box(3.1, 0.2, 5.9, 2.9), "RDC", "Dalle mince 120", offset=2300)       # guerite
    dalle(s, box(0.2, 0.2, 3.1, 2.6), "RDC", "Dalle mince 120", offset=2300)       # local GE
    dalle(s, box(15.5, 2.6, 18.0, 4.5), "RDC", "Dalle mince 120", offset=2900)     # preau cuisine africaine
    s.note("Escalier en U de 3 x 4,2 m, du RDC au toit-terrasse")
    for niveau in ("RDC", "R+1"):
        s.c("stair", start=P(4.75, 9.5), end=P(4.75, 5.6), level=LEVEL[niveau], width=1300, riser=175, tread=280,
            landings=[{"at": 10, "turn": 180}], railings=True)
    s.note("Toit-terrasse : acrotere, jardiniere Nord, poteaux acier et couverture mince a +9,00 (V1)")
    s.c("wall", points=[P(2.575, 9.7), P(2.575, 16.725), P(8.925, 16.725), P(8.925, 11.075), P(17.925, 11.075),
                        P(17.925, 5.5)], type="Acrotère 150", level=LEVEL["TOIT"], height=1000, room_bounding=False)
    s.c("wall", points=[P(2.5, 4.43), P(18.0, 4.43)], type="Acrotère 150", level=LEVEL["TOIT"], height=600,
        room_bounding=False)
    s.c("wall", points=[P(1.775, 13.6), P(1.775, 16.8)], type="Acrotère 150", level=LEVEL["R+1"], height=800,
        room_bounding=False)
    for px, py in F.POTEAUX:
        if (px, py) in ((2.5, 13.8), (2.5, 16.8), (9.0, 16.8), (5.5, 16.8)):   # dans l'acrotere : decales
            py = min(py, 16.65)
            px = max(px, 2.65)
        s.c("column", at=P(px, py), type="Poteau acier 140", level=LEVEL["TOIT"], top_level=LEVEL["COUV"], top_offset=0)
    couv = unary_union([box(*r) for r in F.COUV_V1])
    for ring, _ in contour(couv):
        s.c("roof", boundary=ring, level=LEVEL["COUV"], slope=0, type="Couverture mince 180")
    s.note("Terrasse couverte sur le patio (poteaux bois), preau de la cuisine africaine")
    for px in (9.1, 11.8, 14.4):
        s.c("column", at=P(px, 13.3), type="Poteau bois 200", level=LEVEL["RDC"], height=3050)
    for px, py in ((15.6, 2.7), (17.9, 2.7)):
        s.c("column", at=P(px, py), type="Poteau bois 200", level=LEVEL["RDC"], height=2900)
    s.note("Peau de l'etage (V1 : lames de bois en damier), sur les quatre faces")
    for sens, line, a, b, out, _axes in F.PEAU_VILLA:
        c = line + out * 0.09
        h = 3900 if line == 4.5 else 3100
        s.c("wall", points=pts(sens, a, b, c), type="Peau lames bois 140", level=LEVEL["R+1"], height=h,
            room_bounding=False)


def duplex(s):
    M = LOCATIF_M
    s.note("DUPLEX : deux maisons de 8,5 m, mitoyennes")
    expl = [o for k, x0 in enumerate(MX[:2]) for o in F.ouvertures_maison(x0, k == 0)]
    for niveau in ("RDC", "R+1", "TOIT"):
        cells = cellules(M["pieces"], niveau)
        segs = segments(cells)
        murs(s, M, niveau, segs, hauteur=2400 if niveau == "TOIT" else None,
             type_ext=lambda sens, line: "Mur ext. moellons 200" if (niveau == "RDC" and sens == "v" and abs(line - 3.0) < 0.06)
             else "Mur ext. enduit 200")
        ouvertures(s, M, niveau, segs, expl, cells)
        pieces(s, M, niveau, prefixe="M")
    for k, x0 in enumerate(MX[:2]):
        x1 = x0 + 8.5
        dalle(s, box(x0, 21.0, x1, 30.0), "RDC", "Dalle BA 250")
        for niv in ("R+1", "TOIT"):
            dalle(s, box(x0 - (0.16 if k == 0 else 0), 20.84, x1, 30.16), niv, "Dalle BA 250")
        s.c("stair", start=P(x0 + 2.15, 29.3), end=P(x0 + 5.55, 29.3), level=LEVEL["RDC"], width=1150, riser=175,
            tread=250, landings=[{"at": 10, "turn": 180}], railings=True)
        s.c("stair", start=P(x0 + 2.15, 29.3), end=P(x0 + 5.55, 29.3), level=LEVEL["R+1"], width=1150, riser=175,
            tread=250, landings=[{"at": 10, "turn": 180}], railings=True)
        a = [P(x0 + 2.0, 29.925), P(x0 + 0.075, 29.925), P(x0 + 0.075, 21.075), P(x1 - 0.075, 21.075),
             P(x1 - 0.075, 29.925), P(x0 + 5.6, 29.925)]
        if k == 1:
            a = [P(x0 + 2.0, 29.925), P(x0 + 0.15, 29.925)], [P(x0 + 0.15, 21.075), P(x1 - 0.075, 21.075),
                                                               P(x1 - 0.075, 29.925), P(x0 + 5.6, 29.925)]
        for poly in (a if k == 1 else [a]):
            s.c("wall", points=poly, type="Acrotère 150", level=LEVEL["TOIT"], height=1000, room_bounding=False)
        for px in (x0 + 0.15, x0 + 4.25, x1 - 0.15):
            for py in (21.15, 27.35):
                s.c("column", at=P(px, py + (0.15 if py < 22 else 0)), type="Poteau acier 140", level=LEVEL["TOIT"],
                    top_level=LEVEL["COUV"], top_offset=0)
        cx0, cy0, cx1, cy1 = F.couv_maison(x0, k == 0)
        s.c("roof", boundary=[P(cx0, cy1), P(cx1, cy1), P(cx1, cy0), P(cx0, cy0)], level=LEVEL["COUV"], slope=0,
            type="Couverture mince 180")
        for sens, line, a_, b_, out, _axes in F.peau_maison(x0, k == 0):
            s.c("wall", points=pts(sens, a_, b_, line + out * 0.09), type="Peau lames bois 140", level=LEVEL["R+1"],
                height=3100, room_bounding=False)


def clotures(s):
    s.note("Clotures sur rue (socle en moellons, claustra beton), portails en lames, limites, mur vegetalise de 3,50 m")

    def cl(p0, p1):
        s.c("wall", points=[p0, p1], type="Clôture moellons 200", level="RDC", height=1000, room_bounding=False)
        s.c("wall", points=[p0, p1], type="Clôture claustra 200", level="RDC", height=1200, base_offset=1000,
            room_bounding=False)
    for a, b in ((0.0, 6.0), (12.5, 18.5), (19.5, 20.0)):
        cl(P(a, 0.1), P(b, 0.1))
    for a, b in ((0.2, 17.82), (18.0, 18.5), (30.0, 30.2)):
        cl(P(0.1, a), P(0.1, b))
    for (a, b, y) in ((6.0, 7.0, 0.09), (18.5, 19.5, 0.09), (7.0, 12.5, 0.29)):
        s.c("wall", points=[P(a, y), P(b, y)], type="Portail lames bois 100", level="RDC", height=2200, room_bounding=False)
    for a, b in ((18.5, 30.0), (30.2, 33.0)):
        s.c("wall", points=[P(0.09, a), P(0.09, b)], type="Portail lames bois 100", level="RDC", height=2200,
            room_bounding=False)
    for a, b in ((0.0, 17.82), (18.0, 21.0), (30.0, 33.0)):
        s.c("wall", points=[P(19.9, a), P(19.9, b)], type="Clôture enduite 200", level="RDC", height=2200,
            room_bounding=False)
    s.c("wall", points=[P(0.0, 32.9), P(19.8, 32.9)], type="Clôture enduite 200", level="RDC", height=2200,
        room_bounding=False)
    s.c("wall", points=[P(0.0, 17.91), P(20.0, 17.91)], type="Mur végétalisé 180", level="RDC", height=3500,
        room_bounding=False)
    s.c("wall", points=[P(0.3, 0.3), P(3.0, 0.3), P(3.0, 2.5), P(0.3, 2.5)], closed=True, type="Clôture moellons 200",
        level="RDC", height=2180, room_bounding=False)                                # local GE (niche compteurs)


MOBILIER = [   # (niveau, famille, type, x, y, angle) : repere du projet, angle BIMCraft (degres, sens trigo)
    ("RDC", "Canapé", "2000 x 900", 5.2, 16.25, 0), ("RDC", "Canapé", "1600 x 900", 3.05, 13.3, -90),
    ("RDC", "Table", "2000 x 1000", 10.0, 8.25, 0),
    ("RDC", "Lit", "900 x 2000", 15.0, 15.7, 90), ("RDC", "Bureau", "1400 x 700", 17.6, 12.0, -90),
    ("RDC", "WC", "400 x 650", 3.0, 10.35, -90), ("RDC", "Lavabo", "500 x 400", 17.75, 13.7, -90),
    ("RDC", "Douche", "800 x 800", 15.0, 13.5, 0), ("RDC", "WC", "400 x 650", 16.6, 13.4, 0),
    ("RDC", "Meuble bas", "1800 x 600", 13.0, 9.6, 0), ("RDC", "Évier de cuisine", "1200 x 550", 12.85, 7.5, -90),
    ("RDC", "Évier de cuisine", "800 x 500", 17.65, 7.0, -90), ("RDC", "Meuble bas", "1800 x 600", 16.0, 5.85, 180),
    ("R+1", "Lit", "1800 x 2000", 5.75, 15.65, 0), ("R+1", "Lit", "1600 x 2000", 10.75, 6.6, 180),
    ("R+1", "Lit", "1600 x 2000", 17.1, 8.25, -90), ("R+1", "Canapé", "2000 x 900", 7.25, 10.4, 0),
    ("R+1", "Baignoire", "1700 x 750", 3.4, 12.3, 90), ("R+1", "Lavabo", "600 x 450", 5.15, 12.7, -90),
    ("R+1", "Armoire", "1200 x 600", 6.4, 11.4, 180), ("R+1", "Armoire", "1200 x 600", 8.0, 11.4, 180),
    ("R+1", "Douche", "800 x 800", 14.0, 6.0, 0), ("R+1", "WC", "400 x 650", 13.0, 7.2, 0),
    ("R+1", "Douche", "800 x 800", 14.0, 9.3, 0), ("R+1", "WC", "400 x 650", 13.0, 8.15, 180),
]


def mobilier_maison(x0):
    return [("RDC", "Canapé", "2000 x 900", x0 + 1.8, 24.2, 0), ("RDC", "Table", "1600 x 900", x0 + 7.0, 22.6, 90),
            ("RDC", "Meuble bas", "1800 x 600", x0 + 7.0, 27.2, 0), ("RDC", "Évier de cuisine", "1200 x 550", x0 + 8.2, 25.4, -90),
            ("RDC", "WC", "400 x 650", x0 + 6.3, 29.6, 0),
            ("R+1", "Lit", "1600 x 2000", x0 + 6.0, 22.15, 180), ("R+1", "Lit", "900 x 2000", x0 + 0.6, 22.6, 90),
            ("R+1", "Armoire", "1200 x 600", x0 + 7.0, 27.15, 0), ("R+1", "Baignoire", "1700 x 750", x0 + 7.05, 29.55, 0),
            ("R+1", "Douche", "800 x 800", x0 + 1.0, 28.0, 0)]


# Vegetation, source unique du plan (blocs El Croquis), des coupes / elevations (blocs veg_coupe) et de la maquette (Arbre) :
# (bloc en plan, x, y, diametre, ton % noir, rotation, bloc en coupe, hauteur ; repere du projet, metres)
VEGETATION = [
    ("arbre_plan_canopee_semis_grande", 12.9, 15.9, 6.4, 36, 20, "veg_coupe_arbre_silhouette_pleine", 6.5),   # patio
    ("arbre_plan_canopee_pleine_moyenne", 0.9, 8.2, 4.8, 46, 15, "veg_coupe_bosquet_etage", 5.5),
    ("arbre_plan_canopee_pleine_petite", 1.1, 4.4, 3.2, 64, 80, "veg_coupe_petit_feuillu_dense", 4.3),
    ("arbre_plan_canopee_semis_moyenne", 0.8, 15.4, 5.0, 42, 200, "veg_coupe_bosquet_etage", 5.0),
    ("palmier_plan_penne", 1.3, 12.0, 3.0, 55, 30, "veg_coupe_palmier_retombant", 4.6),
    ("palmier_plan_eventail", 19.0, 6.2, 2.0, 55, 0, "veg_coupe_palmier_retombant", 3.6),
    ("palmier_plan_eventail", 19.1, 7.6, 1.6, 64, 40, None, 3.0),
    ("arbre_plan_canopee_pleine_petite", 13.5, 2.0, 2.8, 55, 150, "veg_coupe_petit_feuillu_dense", 4.0),
    ("arbre_plan_canopee_semis_moyenne", 4.7, 19.3, 4.2, 42, 40, "veg_coupe_bosquet_etage", 4.5),            # jardins
    ("arbre_plan_canopee_pleine_petite", 7.0, 19.5, 2.6, 64, 110, "veg_coupe_petit_feuillu_dense", 3.5),
    ("arbre_plan_canopee_semis_moyenne", 13.3, 19.2, 4.2, 36, 200, "veg_coupe_bosquet_etage", 4.5),
    ("palmier_plan_eventail", 19.0, 19.0, 2.0, 55, 0, "veg_coupe_palmier_retombant", 3.6),
]
ACCENTS = [(9.6, 17.2, 1.6, 0), (10.6, 17.3, 1.3, 70), (14.0, 14.0, 1.5, 140), (13.9, 17.2, 1.4, 30), (1.0, 3.3, 1.4, 40),
           (3.6, 32.3, 1.4, 108), (12.2, 32.3, 1.4, 6), (18.6, 32.3, 1.4, 198)]     # plante_plan_grandes_feuilles


def site(s):
    s.note("Terrain (rues en laterite), jardins et patio plantes, arbres (positions de rendu/scene.py)")
    s.c("floor", boundary=[P(-14, 47), P(34, 47), P(34, -14), P(-14, -14)], level="RDC", type="Terrain (latérite)", offset=-150)
    for r in ((9.0, 13.4, 14.5, 17.82), (0.2, 2.8, 2.5, 17.82), (3.0, 18.0, 19.8, 21.0)):
        dalle(s, box(*r), "RDC", "Jardin planté", offset=-60)
    for _b, x, y, d, _t, _r, _c, h in VEGETATION:
        s.c("component", family="Arbre", type=f"{mm(d)} x {mm(h)}", at=P(x, y), level="RDC", offset=-150)


def mobilier(s):
    s.note("Mobilier et sanitaires (familles de BIMCraft)")
    for niv, fam, typ, x, y, ang in MOBILIER + [m for x0 in MX[:2] for m in mobilier_maison(x0)]:
        s.c("component", family=fam, type=typ, at=P(x, y), level=LEVEL[niv], angle=ang)


def annotations(s):
    s.note("Noms des espaces ouverts, sur les plans")
    notes = [("RDC", "PATIO PLANTÉ", 10.2, 15.6), ("RDC", "TERRASSE COUVERTE", 9.6, 11.6),
             ("RDC", "PASSAGE COUVERT", 8.0, 4.8), ("RDC", "SÉCHOIR", 15.0, 1.1), ("RDC", "PRÉAU", 16.0, 3.3),
             ("RDC", "STATIONNEMENT (2 PL.)", 7.3, 2.3), ("RDC", "JARDIN OUEST", 0.4, 12.0),
             ("RDC", "JARDIN M1", 5.5, 19.2), ("RDC", "JARDIN M2", 14.0, 19.2), ("RDC", "COUR M1", 5.5, 31.4),
             ("RDC", "COUR M2", 14.0, 31.4), ("RDC", "PASSAGE DE SERVICE", 18.15, 9.0),
             ("RDC", "PARKING", 0.4, 24.0), ("R+1", "LOGGIA", 9.0, 4.8), ("R+1", "TOITURE VÉGÉTALISÉE", 15.0, 14.0),
             ("TOIT", "TOIT-TERRASSE COUVERT", 9.5, 8.0), ("TOIT", "TOIT-TERRASSE", 5.0, 24.0),
             ("TOIT", "TOIT-TERRASSE", 13.5, 24.0)]
    s.c("text_type", name="Notes", font="BIMCraft Lettering", size=2.2)
    s.c("text_type", name="Rues", font="BIMCraft Lettering", size=3.5)
    for niv, t, x, y in notes:
        s.c("text", text=t, at=P(x, y), view=LEVEL[niv], type="Notes")
    s.c("text", text="RUE NORD (VOIE EN TERRE)", at=P(7.0, -0.9), view="RDC", type="Rues")
    s.c("text", text="RUE OUEST", at=P(-1.3, 26.0), view="RDC", angle=90, type="Rues")
    s.note("Cotes : trame (axes 1 a 6, files A a E) et parcelle")
    gx = [2.5, 5.5, 9.0, 12.5, 14.5, 18.0]
    gy = [4.5, 5.5, 11.0, 16.8, 18.0]
    for niv in ("RDC", "R+1"):
        s.c("dimension", refs=[P(x, -1.0) for x in gx], at=P(10.0, -1.75), level=LEVEL[niv])
        s.c("dimension", refs=[P(20.3, y) for y in gy], at=P(20.6, 11.0), level=LEVEL[niv])


def vues(s):
    s.note("Vues : plans recadres (villa, duplex), coupes AA / BB / CC, quatre elevations, 3D, cameras")
    for niv in ("RDC", "R+1", "TOIT"):
        for nom, (ya, yb) in (("Villa", (-2.2, 18.6)), ("Duplex", (17.4, 34.0))):
            v = f"{LEVEL[niv]} — {nom}"
            s.c("duplicate_view", view=LEVEL[niv], name=v, mode="detailing")
            s.c("crop", view=v, region=[P(-2.2, yb), P(21.0, ya)])
            s.c("scale", view=v, scale=100)
    s.c("section", start=P(10.75, -1.5), end=P(10.75, 21.0), name="Coupe AA", depth=9000)
    s.c("section", start=P(-1.5, 14.8), end=P(21.5, 14.8), name="Coupe BB", depth=9000)
    s.c("section", start=P(7.5, 18.3), end=P(7.5, 34.5), name="Coupe CC", depth=9000)
    # elevations par une ligne (on regarde a sa gauche), recadrees comme les coupes : -0,90 a +10,20
    for nom, a, b in (("Élévation Nord", P(21.5, -3.0), P(-1.5, -3.0)), ("Élévation Sud", P(-1.5, 36.0), P(21.5, 36.0)),
                      ("Élévation Ouest", P(-3.0, -1.5), P(-3.0, 34.5)), ("Élévation Est", P(23.0, 34.5), P(23.0, -1.5))):
        s.c("elevation", start=a, end=b, name=nom)
    s.c("graphics", view="{3D}", hide=["level", "grid", "section", "elevation", "text", "tag", "dimension", "propertyline"])
    for v in ("Coupe AA", "Coupe BB", "Coupe CC", "Élévation Nord", "Élévation Ouest", "Élévation Sud", "Élévation Est"):
        s.c("scale", view=v, scale=100)
    for v, u in (("Coupe AA", 21000), ("Coupe BB", 23000), ("Coupe CC", 16200), ("Élévation Nord", 23000),
                 ("Élévation Sud", 23000), ("Élévation Ouest", 36000), ("Élévation Est", 36000)):
        s.c("crop", view=v, region=[[0, mm(Z_CROP[0])], [u, mm(Z_CROP[1])]])
    for v in LIGNES:                                      # arbres : blocs Archibooks dans la mise en page
        s.c("graphics", view=v, hide=["generic"])
    noir = {"cut": {"fill": "#000000"}}
    poche = {c: noir for c in ("wall", "floor", "roof", "stair", "column")}
    for v in ["Coupe AA", "Coupe BB", "Coupe CC"] + [f"{LEVEL[n]} — {b}" for n in ("RDC", "R+1", "TOIT") for b in ("Villa", "Duplex")]:
        s.c("graphics", view=v, categories=poche)


CACHER = ["grid", "room", "roomreference", "tag", "text", "dimension", "section", "elevation", "generic", "propertyline",
          "level"]
PRESENTATION = {f"{LEVEL[n]} — {b}": f"Présentation {LEVEL[n]} — {b}" for b in ("Villa", "Duplex") for n in ("RDC", "R+1", "TOIT")}


def presentation(s):
    """Vues de presentation (regles Capitude GABARIT-VISUEL-PLANS v4) : la geometrie de BIMCraft seule, sans axes, cotes,
    etiquettes ni textes ; numeros de pieces, vegetation, reperes, nord et echelle sont poses dans la mise en page."""
    s.note("Vues de presentation : copies des plans recadres, annotations masquees ; plan masse au 1:200")
    for v, pv in PRESENTATION.items():
        s.c("duplicate_view", view=v, name=pv, mode="duplicate")
        s.c("graphics", view=pv, hide=CACHER)
    s.c("duplicate_view", view="RDC", name="Plan masse", mode="duplicate")
    s.c("crop", view="Plan masse", region=[P(-3.0, 36.0), P(23.0, -3.0)])
    s.c("scale", view="Plan masse", scale=200)
    s.c("graphics", view="Plan masse", hide=CACHER, categories={c: {"cut": {"fill": "#000000"}} for c in ("wall", "column", "stair")})


def feuilles(s):
    s.note("Jeu de planches A3 (cartouche de BIMCraft)")
    s.c("project_info", name="Lot 1728 · option C v5", number="1728-C5",
        client="Maître d'ouvrage privé", address="Lot 1728, îlot 174, Djorogobité 1\nCocody, Abidjan",
        status="Esquisse, option C v5", issue_date="15.11.2026", building="Villa à patio + 2 maisons duplex")
    planches = [
        ("Villa — rez-de-chaussée", [("RDC — Villa", [175, 165], 100)]),
        ("Villa — étage", [("R+1 — Villa", [175, 165], 100)]),
        ("Villa — toit-terrasse", [("Toit-terrasse — Villa", [175, 165], 100)]),
        ("Coupes AA et BB", [("Coupe AA", [190, 215], 150), ("Coupe BB", [190, 110], 150)]),
        ("Élévations Nord et Ouest", [("Élévation Nord", [200, 215], 200), ("Élévation Ouest", [200, 105], 200)]),
        ("Élévations Sud et Est", [("Élévation Sud", [200, 215], 200), ("Élévation Est", [200, 105], 200)]),
        ("Duplex — rez-de-chaussée et étage", [("RDC — Duplex", [110, 150], 150), ("R+1 — Duplex", [280, 150], 150)]),
        ("Duplex — toit et coupe CC", [("Toit-terrasse — Duplex", [110, 150], 150), ("Coupe CC", [290, 150], 150)]),
        ("Vue 3D", [("{3D}", [190, 165], 300)]),
    ]
    for k, (nom, vs) in enumerate(planches):
        num = f"A{101 + k}"
        s.c("sheet", number=num, name=nom, size="ISO A3")
        for v, at, sc in vs:
            kw = {"sheet": num, "view": v}
            if at:
                kw["at"] = at
            if sc:
                kw["scale"] = sc
            if v == "{3D}":
                kw.update(azimuth=-130, elevation=28)
            s.c("place", **kw)


def script():
    s = Script()
    s.c("new", name="Lot 1728 · Option C v5", language="fr")
    s.c("modify", id=100000, name=LEVEL["RDC"])
    s.c("modify", id=100001, name=LEVEL["R+1"], elevation=H["R+1"])
    s.c("level", elevation=H["TOIT"], name=LEVEL["TOIT"])
    s.c("level", elevation=H["COUV"], name=LEVEL["COUV"])
    for i in range(4):
        s.c("modify", id=100000 + i, extent=[[-2500, -1500], [22500, 35500]])
    s.c("property_line", points=[P(0, 0), P(20, 0), P(20, 33), P(0, 33)], name="Lot 1728")
    for x in (2.5, 5.5, 9.0, 12.5, 14.5, 18.0):
        s.c("grid", start=P(x, -2.0), end=P(x, 17.4))
    for y, n in zip((4.5, 5.5, 11.0, 16.8, 18.0), "ABCDE"):
        s.c("grid", start=P(-1.8, y), end=P(20.8, y), name=n)
    bibliotheque(s)
    body = Script()
    villa(body)
    duplex(body)
    clotures(body)
    mobilier(body)
    site(body)
    annotations(body)
    s.note("Types de portes et de fenetres a la taille des ouvertures du projet")
    for fam, types in sorted(body.families.items()):
        s.c("family", name=fam, types=types)
    s.lines += body.lines
    vues(s)
    presentation(s)
    feuilles(s)
    return s


# ------------------------------------------------------------------------------------------------ rendus
PLANS = [f"{LEVEL[n]} — {b}" for b in ("Villa", "Duplex") for n in ("RDC", "R+1", "TOIT")]
LIGNES = ["Coupe AA", "Coupe BB", "Coupe CC", "Élévation Nord", "Élévation Ouest", "Élévation Sud", "Élévation Est"]
# vues 3D : (fichier, azimut depuis l'Est sens trigo, hauteur, style, boite de coupe (min, max) ou None, perspective)
AXO = [
    ("axo_NO", 135, 32, "shaded", ([-2500, -1500, -400], [22000, 36500, 10500])),
    ("axo_SE", -45, 32, "shaded", ([-2500, -1500, -400], [22000, 36500, 10500])),
    ("axo_NE", 45, 30, "shaded", ([-2500, -1500, -400], [22000, 36500, 10500])),
    ("axo_NO_trait", 135, 32, "hidden_line", ([-2500, -1500, -400], [22000, 36500, 10500])),
    ("axo_RDC", 135, 50, "shaded", ([-1000, -500, -400], [21000, 34500, 2900])),
    ("axo_R1", 135, 50, "shaded", ([-1000, -500, -400], [21000, 34500, 6200])),
]
CAMERAS = [   # (fichier, oeil, cible, focale) : en mm, repere BIMCraft
    ("cam_angle", [-10000, 43000, 1600], [9000, 25000, 4300], 26),
    ("cam_rue_nord", [10000, 46000, 1600], [10000, 25000, 4600], 30),
    ("cam_rue_ouest", [-13000, 1500, 1600], [9000, 9500, 4000], 26),
    ("cam_patio", [9600, 15700, 1600], [12000, 22000, 3000], 18),
    ("cam_toit", [6000, 17500, 8200], [9000, 27000, 7600], 20),
]


PASTEL = {"Enduit": "#F1EDE6", "Moellons": "#D3CBC0", "Béton clair": "#E6E3DD", "Béton": "#DEDAD3", "Bloc de béton": "#E2DED8",
          "Bois dur": "#D8BC9E", "Lames bois (peau)": "#DDC3A6", "Claustra béton": "#E9E5DD", "Végétal": "#BCCAA8",
          "Latérite": "#E6CDB8", "Pelouse": "#CDD9B9", "Chape": "#E3E0DA", "Plâtre": "#F2EFEA", "Acier noir": "#6E6A66",
          "Métal": "#9A9590", "Bois": "#D2B596"}


def rendus():
    """Dessins et vues tires de la maquette (le .bimc n'est pas modifie : les cameras ne vivent que le temps du rendu)."""
    V = OUT / "vues"
    V.mkdir(parents=True, exist_ok=True)
    cmds = []
    # calibrage : axes temporaires sur les limites de la parcelle (x 0 / 20, y 0 / 30 / 33), jamais enregistres
    for nom, a, b in (("CAL-X0", P(0, -4), P(0, 37)), ("CAL-X20", P(20, -4), P(20, 37)), ("CAL-Y0", P(-4, 0), P(24, 0)),
                      ("CAL-Y30", P(-4, 30), P(24, 30)), ("CAL-Y33", P(-4, 33), P(24, 33))):
        cmds.append("grid " + json.dumps({"start": a, "end": b, "name": nom}))
    for v in PLANS:
        f = v.replace(" — ", "_").replace("+", "").replace(" ", "")
        cmds.append(f"render {json.dumps({'view': v, 'path': str(V / (f + '.svg'))}, ensure_ascii=False)}")
    for v in LIGNES:                       # au trait : calibrage (axes, niveaux) puis presentation (sans axes ni niveaux)
        f = v.replace(" ", "_").replace("É", "E").replace("é", "e")
        dim = {"width": 4000, "height": 2000}
        cmds.append("render " + json.dumps({"view": v, "path": str(V / f"calib_{f}.png"), **dim}, ensure_ascii=False))
        cmds.append("graphics " + json.dumps({"view": v, "hide": ["grid", "level", "section", "elevation"]}, ensure_ascii=False))
        cmds.append("render " + json.dumps({"view": v, "path": str(V / f"{f}.png"), **dim}, ensure_ascii=False))
    for pv in list(PRESENTATION.values()) + ["Plan masse"]:
        f = pv.replace("Présentation ", "P_").replace(" — ", "_").replace("+", "").replace(" ", "_")
        cmds.append("graphics " + json.dumps({"view": pv, "show": ["grid"]}, ensure_ascii=False))
        cmds.append("render " + json.dumps({"view": pv, "path": str(V / f"calib_{f}.svg")}, ensure_ascii=False))
        cmds.append("graphics " + json.dumps({"view": pv, "hide": ["grid"]}, ensure_ascii=False))
        cmds.append("render " + json.dumps({"view": pv, "path": str(V / f"{f}.svg")}, ensure_ascii=False))
    cmds.append('section_box {"view": "{3D}", "on": false}')
    cmds.append('visual_style {"view": "{3D}", "style": "shaded"}')
    for k, (f, eye, target, lens) in enumerate(CAMERAS, 1):
        cmds.append("camera " + json.dumps({"eye": eye, "target": target, "lens": lens, "name": f}))
        cmds.append("graphics " + json.dumps({"view": f, "hide": ["level", "grid", "section", "elevation", "text", "dimension", "propertyline"]}))
        cmds.append("graphic_display_options " + json.dumps({"view": f, "silhouette": 1, "ambient_shadows": True}))
        cmds.append("render " + json.dumps({"view": f, "path": str(V / (f + ".png")), "width": 3000, "height": 2000}))
    # axonometries « a plat » (PRESENTATION-PROJETS-ARCHI, section 6) : aplats pastel par materiau, sans texture
    for nom, col in PASTEL.items():
        cmds.append("material " + json.dumps({"name": nom, "color": col, "texture": None}, ensure_ascii=False))
    cmds.append('graphic_display_options {"view": "{3D}", "silhouette": 1, "ambient_shadows": true, "edges": true}')
    for f, az, el, style, sb in AXO:
        cmds.append(f'visual_style {json.dumps({"view": "{3D}", "style": style})}')
        cmds.append('section_box ' + json.dumps({"view": "{3D}", "on": True, "min": sb[0], "max": sb[1]} if sb else {"view": "{3D}", "on": False}))
        cmds.append("render " + json.dumps({"view": "{3D}", "path": str(V / (f + ".png")), "azimuth": az, "elevation": el,
                                            "width": 3600, "height": 2400}))
    cmds.append("schedule " + json.dumps({"category": "rooms", "fields": ["Number", "Name", "Level", "Area"],
                                          "sort": ["Level", "Number"], "path": str(V / "pieces_axes.csv")}))
    cmds.append('room_area {"at": "finish"}')
    cmds.append("schedule " + json.dumps({"category": "rooms", "fields": ["Number", "Name", "Level", "Area"],
                                          "sort": ["Level", "Number"], "path": str(V / "pieces_utiles.csv")}))
    cmds.append("schedule " + json.dumps({"category": "rooms", "fields": ["Number", "Name", "Level", "Area"],
                                          "sort": ["Level", "Number"], "path": str(OUT / f"{NOM}_pieces.xlsx")}))
    cmds.append("schedule " + json.dumps({"category": "doors", "path": str(V / "portes.csv")}))
    cmds.append("schedule " + json.dumps({"category": "windows", "path": str(V / "fenetres.csv")}))
    script = V / "_rendus.txt"
    script.write_text("\n".join(cmds) + "\n", encoding="utf-8")
    res = run(["run", str(OUT / f"{NOM}.bimc"), "--script", str(script)])
    script.unlink()
    from PIL import Image                                  # vues ombrees en JPEG (le depot reste leger)
    for png in V.glob("*.png"):
        if png.stem.startswith(("elev_", "cam_")):
            Image.open(png).convert("RGB").save(png.with_suffix(".jpg"), "JPEG", quality=88)
            png.unlink()
    for r in res:
        if r.get("notes"):
            print("note", r.get("view"), r["notes"])
    print("rendus", len(list(V.iterdir())))
    return res


def run(args, quiet=False):
    r = subprocess.run([CLI] + args, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"bimcraft-cli : {r.stderr.strip() or r.stdout.strip()}")
    return [json.loads(line) for line in r.stdout.splitlines() if line.startswith("{")]


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    s = script()
    txt = OUT / f"{NOM}.txt"
    txt.write_text("# Maquette BIMCraft du lot 1728, option C v5 (genere par src/bimcraft_modele.py)\n"
                   + "\n".join(s.lines) + "\n", encoding="utf-8")
    bimc = OUT / f"{NOM}.bimc"
    res = run(["run", "--script", str(txt), "--save", str(bimc), "--save", str(OUT / f"{NOM}.ifc"),
               "--save", str(OUT / f"{NOM}_planches.pdf"), "--save", str(OUT / f"{NOM}.glb")])
    # le terrain (48 x 61 m) n'a rien a faire dans les dessins au trait : masque dans les coupes et elevations
    sols = [(e["id"], e.get("type")) for r in run(["run", str(bimc), "--cmd", 'elements {"category": "floor"}'])
            for e in r.get("elements", [])]
    terrain = [i for i, t in sols if t == "Terrain (latérite)"]
    jardins = [i for i, t in sols if t in ("Terrain (latérite)", "Jardin planté")]
    post = [["--cmd", "graphics " + json.dumps({"view": v, "hide_elements": terrain}, ensure_ascii=False)] for v in LIGNES]
    post += [["--cmd", "graphics " + json.dumps({"view": v, "hide_elements": jardins}, ensure_ascii=False)]
             for v in list(PRESENTATION.values()) + ["Plan masse"]]
    run(["run", str(bimc)] + [a for c in post for a in c] + ["--save", str(bimc), "--save", str(OUT / f"{NOM}_planches.pdf")])
    print("commandes", len(s.lines), "->", bimc.name, "terrain", terrain)
    return res


if __name__ == "__main__":
    build()
    rendus()
