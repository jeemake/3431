"""Dessins de presentation tires de la maquette BIMCraft, au gabarit Capitude (regles Supabase `regles_agents`).

GABARIT-VISUEL-PLANS v4 (11-11-2026), PRESENTATION-PROJETS-ARCHI v4, GRAPHISME-OPACITES, VEGETATION- et
PERSONNAGES-COUPES-ELEVATIONS, BLOCS-ARCHIBOOKS. La geometrie vient de BIMCraft seule (murs en poche noir, portes,
fenetres, escaliers, mobilier, coupes et elevations au trait) ; la mise en page y ajoute, en millimetres papier et a
l'echelle vraie : sols en textures Archibooks, canopees El Croquis a 3-4 valeurs de gris (masquees sur les espaces
couverts), projections au-dessus du plan de coupe en tirets, numeros de pieces dans un cercle (section 4 ter, legende
en colonne C10-12), reperes de coupe en equerres hors du dessin, trait de sol et terre en pointille, vegetation et
personnages en coupe et elevation, niveaux en bande a gauche. Police : URW Gothic (repli de Century Gothic).

Calibrage : chaque vue est rendue une fois avec des axes temporaires poses sur les limites de la parcelle (et ses
niveaux pour les coupes), ce qui donne la correspondance exacte pixels BIMCraft -> metres du projet.
"""
import io
import base64
import math
import re
import statistics

from PIL import Image

import bimcraft_modele as BM
import facade as F
from blocs_archibooks import Bibliotheque
from plans_capitude import TONS, nom_court
from projet import LOCATIF_M, MX, OPTION_C

V = BM.OUT / "vues"
INK = "#000000"
GRIS = "#A49B95"
FONT = '"Century Gothic", "URW Gothic", "TeX Gyre Adventor", Questrial, Jost, sans-serif'
PT = 0.3528                                     # 1 pt en mm (papier)
BLEU = "#3c6496"                                # axes de BIMCraft (calibrage seulement)


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ------------------------------------------------------------------------------------------------ calibrage
def _ajuste(paires):
    """Moindres carres : px = a * m + b."""
    ms = [m for m, _ in paires]
    ps = [p for _, p in paires]
    mm_, mp = statistics.mean(ms), statistics.mean(ps)
    a = sum((m - mm_) * (p - mp) for m, p in paires) / sum((m - mm_) ** 2 for m in ms)
    return a, mp - a * mm_


def calib_svg(nom):
    """(a, b, c, d) : X_px = a x + b, Y_px = c y + d, x et y en metres du projet (y vers le Sud)."""
    t = (V / f"calib_{nom}.svg").read_text(encoding="utf-8")
    vx, vy = [], []                                  # axes : un trace en tirets par axe
    for m in re.finditer(rf'<path d="M([\d.]+) ([\d.]+) L([\d.]+) ([\d.]+)"[^>]*stroke="{BLEU}"[^>]*stroke-dasharray', t):
        x1, y1, x2, y2 = map(float, m.groups())
        (vx.append(x1) if abs(x1 - x2) < 0.1 else vy.append(y1))
    vx, vy = sorted(vx), sorted(vy)
    a, b = _ajuste([(0.0, vx[0]), (20.0, vx[-1])])           # axes CAL-X0 et CAL-X20 : les plus a l'Ouest et a l'Est
    connus = [0.0, 4.5, 5.5, 11.0, 16.8, 18.0, 30.0, 33.0]     # files A-E et axes de calibrage
    c = a                                                      # echelle isotrope
    for y0 in connus:                                          # la premiere file visible : celle qui fait tomber
        d = vy[0] - c * y0                                     # toutes les autres sur des files connues
        if all(min(abs((v - d) / c - k) for k in connus) < 0.05 for v in vy):
            break
    else:
        raise RuntimeError(f"{nom} : files non reconnues")
    return a, b, c, d


def corps_svg(nom):
    """Contenu du SVG BIMCraft (sans fond blanc), traits epaissis a la grammaire Capitude."""
    t = (V / f"{nom}.svg").read_text(encoding="utf-8")
    t = t[t.index(">") + 1:t.rindex("</svg>")]
    t = re.sub(r'<rect width="\d+" height="\d+" fill="#ffffff"/>', "", t, count=1)
    return t


# ------------------------------------------------------------------------------------------------ plans
def _r(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


CIRCULATIONS = ("Hall", "Dégagement", "Escalier", "Galerie", "Entrée", "Édicule", "Jardinière")


class Plan:
    """Planche de plan en mm papier ; repere du projet (x Est, y Sud, metres)."""

    def __init__(self, vue, cadre, echelle=100, sid="p", recadrage=None):
        self.vue, self.sid = vue, sid
        self.recadrage = recadrage or cadre         # recadrage de la vue BIMCraft (son titre reste dehors)
        self.x0, self.y0, self.x1, self.y1 = cadre
        self.S = 1000 / echelle                     # mm papier par metre
        self.W, self.H = (self.x1 - self.x0) * self.S, (self.y1 - self.y0) * self.S
        self.lib = Bibliotheque()
        self.fond, self.masque, self.dessus = [], [], []
        self.n = 0

    def X(self, x):
        return (x - self.x0) * self.S

    def Y(self, y):
        return (y - self.y0) * self.S

    def mm(self, v):                                # epaisseur ou taille sur le papier, en mm
        return v

    # ---------------------------------------------------------------- couches
    def texture(self, i, poly, op=0.6, holes=(), couche="fond"):
        self.n += 1
        getattr(self, couche).append(self.lib.texture(i, poly, self.S, self.X, self.Y, opacity=op, holes=holes,
                                                      cid=f"{self.sid}_t{self.n}"))

    def arbre(self, i, x, y, diam, ton, rot=0.0):
        b = self.lib.info(i)["dimensions_m"]
        k = diam / max(b["largeur"], b["hauteur"])
        self.fond.append(self.lib.plan(i, x, y, self.S, k=k, rot=rot, X=self.X, Y=self.Y, fill=TONS.get(ton, ton)))

    def blanc(self, poly):
        d = "M" + " L".join(f"{self.X(x):.2f},{self.Y(y):.2f}" for x, y in poly) + " Z"
        self.masque.append(f'<path d="{d}" fill="#fff" stroke="none"/>')

    def tirets(self, pts, ferme=True):
        d = "M" + " L".join(f"{self.X(x):.2f},{self.Y(y):.2f}" for x, y in pts) + (" Z" if ferme else "")
        self.dessus.append(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="0.25" stroke-dasharray="2.5 1.2"/>')

    def limite(self, pts):
        d = "M" + " L".join(f"{self.X(x):.2f},{self.Y(y):.2f}" for x, y in pts)
        self.dessus.append(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="0.25" stroke-dasharray="6 1.5 1 1.5"/>')

    def texte(self, x, y, t, pt=7, poids=400, ancre="start", rot=0):
        tr = f' transform="rotate({rot} {self.X(x):.2f} {self.Y(y):.2f})"' if rot else ""
        self.dessus.append(f'<text x="{self.X(x):.2f}" y="{self.Y(y):.2f}" font-size="{pt * PT:.2f}" font-weight="{poids}" '
                           f'text-anchor="{ancre}" fill="{INK}"{tr}>{esc(t)}</text>')

    def voiture(self, x, y, rot=0):
        S = self.S
        self.dessus.append(
            f'<g transform="translate({self.X(x):.2f},{self.Y(y):.2f}) rotate({rot})">'
            f'<rect x="{-0.9 * S:.2f}" y="{-2.25 * S:.2f}" width="{1.8 * S:.2f}" height="{4.5 * S:.2f}" rx="{0.35 * S:.2f}" fill="#fff" stroke="{INK}" stroke-width="0.15"/>'
            f'<rect x="{-0.75 * S:.2f}" y="{-0.9 * S:.2f}" width="{1.5 * S:.2f}" height="{2.0 * S:.2f}" rx="{0.2 * S:.2f}" fill="#fff" stroke="{INK}" stroke-width="0.13"/></g>')

    def equerre(self, x, y, vers, lettre):
        """Repere de coupe : equerre courte en trait fort hors du dessin, tournee vers le regard (N, S, E, O)."""
        px, py, L = self.X(x), self.Y(y), 5.0
        dx, dy = {"N": (0, -1), "S": (0, 1), "E": (1, 0), "O": (-1, 0)}[vers]
        if vers in ("E", "O"):
            d = f"M{px:.2f},{py - L / 2:.2f} L{px:.2f},{py + L / 2:.2f} M{px:.2f},{py - L / 2:.2f} L{px + dx * L * 0.6:.2f},{py - L / 2:.2f}"
            tx, ty = px - dx * 2.2, py + 1.1
        else:
            d = f"M{px - L / 2:.2f},{py:.2f} L{px + L / 2:.2f},{py:.2f} M{px - L / 2:.2f},{py:.2f} L{px - L / 2:.2f},{py + dy * L * 0.6:.2f}"
            tx, ty = px + L / 2 + 1.8, py + 1.1
        self.dessus.append(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="0.45"/>'
                           f'<text x="{tx:.2f}" y="{ty:.2f}" font-size="{9 * PT:.2f}" font-weight="700" text-anchor="middle" fill="{INK}">{lettre}</text>')

    def numero(self, x, y, n):
        r = 1.9
        self.dessus.append(f'<circle cx="{self.X(x):.2f}" cy="{self.Y(y):.2f}" r="{r}" fill="#fff" stroke="{INK}" stroke-width="0.13"/>'
                           f'<text x="{self.X(x):.2f}" y="{self.Y(y) + 0.88:.2f}" font-size="{7 * PT:.2f}" font-weight="700" '
                           f'text-anchor="middle" fill="{INK}">{n}</text>')

    # ---------------------------------------------------------------- BIMCraft
    def bimcraft(self, nom, epaissir=1.35):
        a, b, c, d = calib_svg(nom)
        kx, ky = self.S / a, self.S / c
        e, f = -(b / a + self.x0) * self.S, -(d / c + self.y0) * self.S
        corps = corps_svg(nom)
        corps = re.sub(r'stroke-width="([\d.]+)"', lambda m_: f'stroke-width="{float(m_.group(1)) * epaissir:.4f}"', corps)
        clip = f"{self.sid}_cadre"
        rx0, ry0, rx1, ry1 = self.recadrage
        return (f'<clipPath id="{clip}"><rect x="{self.X(rx0):.2f}" y="{self.Y(ry0):.2f}" width="{(rx1 - rx0) * self.S:.2f}" '
                f'height="{(ry1 - ry0) * self.S:.2f}"/></clipPath>'
                f'<g clip-path="url(#{clip})"><g transform="matrix({kx:.6f},0,0,{ky:.6f},{e:.3f},{f:.3f})">{corps}</g></g>')

    def svg(self, nom_bimcraft):
        coeur = self.bimcraft(nom_bimcraft)
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.W:.2f} {self.H:.2f}" width="{self.W:.2f}mm" '
                f'height="{self.H:.2f}mm" font-family=\'{FONT}\'><defs>{self.lib.defs()}</defs>'
                f'{"".join(self.fond)}{"".join(self.masque)}{coeur}{"".join(self.dessus)}</svg>')


# ------------------------------------------------------------------------------------------------ pieces et numeros
def surfaces_bim():
    """Surfaces des pieces de la maquette (aux axes des murs) : {(niveau, logement, nom) : m2}."""
    import csv
    niv = {"RDC": "RDC", "R+1": "R+1", "Toit-terrasse": "TOIT"}
    out = {}
    for r in csv.DictReader(open(V / "pieces_axes.csv", encoding="utf-8")):
        log = r["Number"].split(".")[0] if r["Number"].startswith("M") else None
        out[(niv[r["Level"]], log, r["Name"])] = float(r["Area (m²)"])
    return out


def obstacles(niveau):
    """Mobilier, portes, escaliers et canopees a eviter pour poser un numero (rectangles en metres)."""
    obs = []
    for niv, _fam, typ, x, y, ang in BM.MOBILIER + [m for x0 in MX[:2] for m in BM.mobilier_maison(x0)]:
        if niv != niveau:
            continue
        w, d = (float(v) / 1000 for v in typ.split(" x "))
        if abs(ang) % 180 == 90:
            w, d = d, w
        obs.append((x - w / 2 - 0.12, y - d / 2 - 0.12, x + w / 2 + 0.12, y + d / 2 + 0.12))
    for opt in (OPTION_C, LOCATIF_M):
        for niv, x, y, sens, w in opt["portes"]:
            if niv == niveau:
                obs.append((x - 0.55 - (w / 2 if sens == "h" else 0), y - 0.55 - (w / 2 if sens == "v" else 0),
                            x + 0.55 + (w / 2 if sens == "h" else 0), y + 0.55 + (w / 2 if sens == "v" else 0)))
    obs.append((2.5, 5.5, 5.5, 9.7))
    for x0 in MX[:2]:
        obs.append((x0 + 2.0, 27.5, x0 + 5.6, 30.0))
    if niveau == "RDC":
        for _b, x, y, dm, *_ in BM.VEGETATION:
            if dm < 4:
                obs.append((x - dm / 2, y - dm / 2, x + dm / 2, y + dm / 2))
    return obs


def place(rects, obs, r=0.3):
    """Point libre le plus proche du centre visuel de la plus grande partie de la piece."""
    x0, y0, x1, y1 = max(rects, key=lambda q: (q[2] - q[0]) * (q[3] - q[1]))
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    best = None
    pas = 0.1
    for i in range(int((x1 - x0) / pas) + 1):
        for j in range(int((y1 - y0) / pas) + 1):
            x, y = x0 + i * pas, y0 + j * pas
            if x - r < x0 + 0.15 or x + r > x1 - 0.15 or y - r < y0 + 0.15 or y + r > y1 - 0.15:
                continue
            if any(a - r < x < c + r and b - r < y < d + r for a, b, c, d in obs):
                continue
            dist = math.hypot(x - cx, y - cy)
            if best is None or dist < best[0]:
                best = (dist, x, y)
    return (best[1], best[2]) if best else (cx, cy)


def numeroter(p, opts, niveau, ignorer=(), deplace=None):
    """Numeros de pieces (GABARIT-VISUEL-PLANS 4 ter) : haut -> bas puis gauche -> droite, recommence a 1 par niveau.
    Renvoie la legende [(n, NOM, surface, logement)]."""
    surf = surfaces_bim()
    obs = obstacles(niveau)
    items = []
    for opt in opts:
        for r in opt["pieces"]:
            if r["niveau"] != niveau or r["nom"] in ignorer or any(m in r["nom"] for m in CIRCULATIONS):
                continue
            log = r.get("logement")
            nom_bim = r["nom"][len(log) + 1:] if log and r["nom"].startswith(log + " ") else r["nom"]
            s = surf.get((niveau, log, nom_bim)) if r["clos"] else None
            s = s if s is not None else r["surface"]
            pt = (deplace or {}).get(r["nom"]) or place(r["rects"], obs)
            items.append((pt, nom_court(r), s, log))
    items.sort(key=lambda t: (round(t[0][1] / 3.0), t[0][0]))
    leg = []
    for k, ((x, y), nom, s, log) in enumerate(items, 1):
        p.numero(x, y, k)
        leg.append((k, nom, s, log))
    return leg


# ------------------------------------------------------------------------------------------------ villa et duplex
CADRE_VILLA = (-3.0, -3.2, 22.4, 19.6)
CADRE_DUPLEX = (-3.0, 16.4, 22.4, 35.2)


def vegetation_plan(p, niveau, zone):
    ys = (-5, 18.0) if zone == "villa" else (17.5, 40)
    for b, x, y, d, ton, rot, *_ in BM.VEGETATION:
        if ys[0] <= y <= ys[1] and (niveau == "RDC" or d >= 5):
            p.arbre(b, x, y, d, ton if niveau == "RDC" else 30, rot)
    if niveau == "RDC":
        for x, y, d, rot in BM.ACCENTS:
            if ys[0] <= y <= ys[1]:
                p.arbre("plante_plan_grandes_feuilles", x, y, d, 64, rot)
        if zone == "villa":
            p.arbre("arbre_plan_canopee_pleine_moyenne", 21.6, 9.0, 2.8, 30, 60)          # contexte Est (voisin)


def villa(niveau):
    nom = {"RDC": "P_RDC_Villa", "R+1": "P_R1_Villa", "TOIT": "P_Toit-terrasse_Villa"}[niveau]
    p = Plan(nom, CADRE_VILLA, sid=f"v{niveau.replace('+', '')}", recadrage=(-2.2, -2.2, 21.0, 18.6))
    if niveau == "RDC":
        p.texture("texture_paves", _r(7.0, 0.2, 12.5, 4.5), 0.6)
        p.texture("texture_pierre_bandes", _r(5.7, 0.2, 7.0, 4.5), 0.65)
        p.texture("texture_granulat_fin", _r(14.5, 0.34, 18.0, 2.6), 0.6)
        p.texture("texture_granulat_fin", _r(18.0, 0.2, 19.8, 17.82), 0.55)
        p.texture("texture_pas_irreguliers", _r(2.5, 16.8, 18.0, 17.82), 0.8)
        p.texture("texture_couvre_sol", _r(0.2, 2.7, 2.5, 17.82), 0.55)
        p.texture("texture_litiere", _r(9.0, 13.4, 14.5, 17.82), 0.6, holes=[_r(11.7, 13.4, 12.5, 17.6)])
        p.texture("texture_pas_irreguliers", _r(11.7, 13.4, 12.5, 17.6), 0.85)
        p.texture("texture_massif_tropical", _r(0.2, 17.4, 19.8, 17.82), 0.7)
    elif niveau == "R+1":
        p.texture("texture_couvre_sol", _r(14.5, 11.0, 18.0, 16.8), 0.45)
        p.texture("texture_couvre_sol", _r(9.0, 11.0, 14.5, 13.4), 0.45)
        p.texture("texture_massif_tropical", _r(1.7, 13.6, 2.5, 16.8), 0.7)
    else:
        for (a, b, c, d) in F.TOITURE_VEGETALE:
            p.texture("texture_couvre_sol", _r(a, b, c, d), 0.45)
    vegetation_plan(p, niveau, "villa")
    # espaces couverts : la canopee s'arrete (section 9 bis, point 9) ; leurs sols par-dessus
    clos = [r for r in OPTION_C["pieces"] if r["niveau"] == niveau and r["clos"]]
    for r in clos:
        for q in r["rects"]:
            p.blanc(_r(*q))
    if niveau == "RDC":
        for q in ((2.5, 4.5, 15.5, 5.5), (9.0, 11.0, 14.5, 13.4), (15.5, 2.6, 18.0, 5.5)):
            p.blanc(_r(*q))
            p.texture("texture_pierre_bandes", _r(*q), 0.6, couche="masque")
        p.tirets([(2.5, 4.36), (18.0, 4.36)], ferme=False)               # nez de dalle de l'etage (loggia)
        p.tirets(_r(15.5, 2.6, 18.0, 4.5))                                # dalle du preau
        p.tirets([(9.0, 13.4), (14.5, 13.4)], ferme=False)                # rive de la terrasse couverte
        p.voiture(8.4, 2.45)
        p.voiture(11.1, 2.45)
        p.equerre(10.75, -1.0, "E", "A")
        p.equerre(10.75, 18.55, "E", "A")
        p.equerre(-0.8, 14.8, "N", "B")
        p.equerre(20.6, 14.8, "N", "B")
        p.texte(7.0, -1.6, "RUE NORD", 7, 700)
        p.texte(-1.6, 9.0, "RUE OUEST", 7, 700, rot=-90, ancre="middle")
    elif niveau == "R+1":
        p.blanc(_r(5.5, 4.5, 18.0, 5.5))
        p.texture("texture_pierre_bandes", _r(5.5, 4.5, 18.0, 5.5), 0.55, couche="masque")
        p.limite([(0.0, 18.0), (0.0, 0.0), (20.0, 0.0), (20.0, 18.0)])
    else:
        p.blanc([(2.5, 4.5), (18.0, 4.5), (18.0, 11.0), (9.0, 11.0), (9.0, 16.8), (2.5, 16.8)])
        p.texture("texture_pierre_bandes", _r(5.5, 5.5, 18.0, 11.0), 0.5, couche="masque")
        p.texture("texture_pierre_bandes", _r(2.5, 9.7, 9.0, 16.8), 0.5, holes=[_r(5.5, 9.7, 9.0, 11.0)], couche="masque")
        x0, y0, x1, y1, _ = F.JARDINIERE
        p.texture("texture_massif_tropical", _r(x0, y0, x1, y1), 0.7, couche="masque")
        p.limite([(0.0, 18.0), (0.0, 0.0), (20.0, 0.0), (20.0, 18.0)])
    if niveau in ("R+1", "TOIT"):
        (a0, b0, a1, b1), (c0, d0, c1, d1) = F.COUV_V1
        p.tirets([(a0, b0), (a1, b0), (a1, b1), (c1, b1), (c1, d1), (c0, d1)])     # couverture a +9,00
    dep = {"Terrasse couverte sur patio": (10.2, 12.4), "Passage couvert d'entrée": (9.2, 5.0),
           "Préau cuisine africaine": (16.75, 3.9), "Séchoir à ciel ouvert": (16.25, 1.5), "Local GE + niche compteurs": (1.65, 1.4),
           "Loggia Nord (rangements)": (12.0, 5.0), "Toit-terrasse couvert": (12.0, 8.2)}
    leg = numeroter(p, [OPTION_C], niveau, ignorer=("Jardinière (plantation basse)", "Patio planté"), deplace=dep)
    return p.svg(nom), leg


def duplex(niveau):
    nom = {"RDC": "P_RDC_Duplex", "R+1": "P_R1_Duplex", "TOIT": "P_Toit-terrasse_Duplex"}[niveau]
    p = Plan(nom, CADRE_DUPLEX, sid=f"d{niveau.replace('+', '')}", recadrage=(-2.2, 17.75, 21.0, 34.0))
    if niveau == "RDC":
        p.texture("texture_paves", _r(0.2, 18.0, 3.0, 30.0), 0.6)
        p.texture("texture_pierre_bandes", _r(0.2, 30.0, 19.8, 32.8), 0.6)
        for x0 in MX[:2]:
            p.texture("texture_couvre_sol", _r(x0, 18.0, x0 + 8.5, 21.0), 0.5)
        p.texture("texture_massif_tropical", _r(3.0, 18.0, 19.8, 18.4), 0.7)
    vegetation_plan(p, niveau, "duplex")
    for r in LOCATIF_M["pieces"]:
        if r["niveau"] == niveau and r["clos"]:
            for q in r["rects"]:
                p.blanc(_r(*q))
    if niveau == "RDC":
        p.voiture(1.5, 21.4)
        p.voiture(1.5, 27.0)
        p.equerre(7.5, 17.1, "E", "C")
        p.equerre(7.5, 33.6, "E", "C")
        p.texte(-1.6, 25.0, "RUE OUEST", 7, 700, rot=-90, ancre="middle")
    else:
        p.limite([(0.0, 18.0), (0.0, 33.0), (20.0, 33.0), (20.0, 18.0)])
        for k, x0 in enumerate(MX[:2]):
            p.tirets(_r(*F.couv_maison(x0, k == 0)))
    if niveau == "TOIT":
        for x0 in MX[:2]:
            p.blanc([(x0, 21.0), (x0 + 8.5, 21.0), (x0 + 8.5, 30.0), (x0, 30.0)])
            p.texture("texture_pierre_bandes", [(x0, 21.0), (x0 + 8.5, 21.0), (x0 + 8.5, 30.0), (x0 + 5.6, 30.0), (x0 + 5.6, 27.5),
                                                (x0 + 2.0, 27.5), (x0 + 2.0, 30.0), (x0, 30.0)], 0.5, couche="masque")
    dep = {f"M{n} Jardin privé": (x0 + 1.4, 18.9) for n, x0 in ((1, 3.0), (2, 11.5))}
    dep.update({f"M{n} Cour d'entrée": (x0 + 4.25, 31.6) for n, x0 in ((1, 3.0), (2, 11.5))})
    dep.update({"Stationnement 2 places (rue Ouest)": (1.5, 24.2), "Allée piétonne": (1.5, 31.6)})
    leg = numeroter(p, [LOCATIF_M], niveau, deplace=dep)
    from projet import surfaces as _surf
    clos = _surf(LOCATIF_M)["clos"] / 2
    for k, x0 in enumerate(MX[:2]):                  # identifiant et surface du logement, une fois, hors des pieces
        p.texte(x0 + 4.25, 34.4 if niveau == "RDC" else 31.4, f"MAISON {k + 1} · {clos:.1f} m²".replace(".", ","), 7, 700,
                ancre="middle")
    return p.svg(nom), leg


def plan_masse():
    p = Plan("Plan_masse", (-4.0, -4.5, 24.0, 37.5), echelle=200, sid="pm", recadrage=(-3.0, -3.0, 23.0, 36.0))
    p.texture("texture_paves", _r(7.0, 0.2, 12.5, 4.5), 0.6)
    p.texture("texture_paves", _r(0.2, 18.0, 3.0, 30.0), 0.6)
    p.texture("texture_couvre_sol", _r(0.2, 2.7, 2.5, 17.82), 0.55)
    p.texture("texture_litiere", _r(9.0, 13.4, 14.5, 17.82), 0.6)
    for x0 in MX[:2]:
        p.texture("texture_couvre_sol", _r(x0, 18.0, x0 + 8.5, 21.0), 0.5)
    for b, x, y, d, ton, rot, *_ in BM.VEGETATION:
        p.arbre(b, x, y, d, ton, rot)
    for x, y in ((-2.2, 3.0), (-2.4, 10.5), (-2.1, 18.0), (-2.3, 25.5), (-2.2, 33.0)):     # rue Ouest, entraxe 7,5 m
        p.arbre("arbre_plan_canopee_pleine_moyenne", x, y, 3.6 + (x * 7 % 0.8), 30 if y % 2 else 46, rot=y * 23)
    for r in OPTION_C["pieces"] + LOCATIF_M["pieces"]:
        if r["niveau"] == "RDC" and r["clos"]:
            for q in r["rects"]:
                p.blanc(_r(*q))
    p.limite([(0, 0), (20, 0), (20, 33), (0, 33), (0, 0)])
    p.texte(7.0, -2.2, "RUE NORD", 7, 700)
    p.texte(-3.0, 15.0, "RUE OUEST", 7, 700, rot=-90, ancre="middle")
    p.texte(21.0, 9.0, "LOT 1730", 7, 400)
    p.texte(5.8, 13.6, "VILLA", 9, 700, ancre="middle")
    p.texte(11.5, 32.2, "DUPLEX", 9, 700, ancre="middle")
    return p.svg("Plan_masse")


def legende_html(leg, titre):
    """Legende des numeros : titre du niveau 9 pt Demi, puis « 1  NOM · 24,6 m² » (numero Demi, surface 7 pt)."""
    lignes = []
    for n, nom, s, lg in leg:
        lignes.append(f'<div class="lg"><b>{n}</b><span>{esc(nom)} · {s:,.1f} m²</span></div>'.replace(",", " ").replace(".", ","))
    return f'<div class="leg"><div class="lg-t">{esc(titre)}</div>{"".join(lignes)}</div>'


def nord_echelle(echelle=100, rot=-7.56):
    """Nord compact et echelle graphique a traits 0-1-3-5 m (0-5-10 m au 1:200), en mm papier."""
    S = 1000 / echelle
    marques = (0, 1, 3, 5) if echelle <= 100 else (0, 5, 10)
    L = marques[-1] * S
    a = math.radians(rot)
    cx, cy, R = 5.0, 7.0, 4.0
    tip = (cx + R * math.sin(a), cy - R * math.cos(a))
    l_ = (cx + 0.45 * R * math.sin(a - 2.6), cy - 0.45 * R * math.cos(a - 2.6))
    r_ = (cx + 0.45 * R * math.sin(a + 2.6), cy - 0.45 * R * math.cos(a + 2.6))
    x0, y0 = 14.0, 9.0
    g = [f'<polygon points="{tip[0]:.2f},{tip[1]:.2f} {l_[0]:.2f},{l_[1]:.2f} {cx},{cy} {r_[0]:.2f},{r_[1]:.2f}" fill="{INK}"/>',
         f'<text x="{tip[0]:.2f}" y="{tip[1] - 1.2:.2f}" font-size="{7 * PT:.2f}" text-anchor="middle" font-weight="700">N</text>',
         f'<line x1="{x0}" y1="{y0}" x2="{x0 + L:.2f}" y2="{y0}" stroke="{INK}" stroke-width="0.25"/>']
    for m_ in marques:
        g.append(f'<line x1="{x0 + m_ * S:.2f}" y1="{y0 - 1}" x2="{x0 + m_ * S:.2f}" y2="{y0}" stroke="{INK}" stroke-width="0.18"/>'
                 f'<text x="{x0 + m_ * S:.2f}" y="{y0 + 3:.2f}" font-size="{7 * PT:.2f}" text-anchor="middle">{m_}{" m" if m_ == marques[-1] else ""}</text>')
    w = x0 + L + 6
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.1f} 14" width="{w:.1f}mm" height="14mm" '
            f'font-family=\'{FONT}\' fill="{INK}">{"".join(g)}</svg>')


# ------------------------------------------------------------------------------------------------ coupes et elevations
LIGNE = {   # vue : (axe du plan pour l'horizontale, axes de calibrage gauche -> droite, filtre de vegetation)
    "Coupe_AA": ("y", [0.0, 4.5, 5.5, 11.0, 16.8, 18.0], lambda x, y: x > 10.4 and x < 19.75),
    "Coupe_BB": ("x", [0.0, 2.5, 5.5, 9.0, 12.5, 14.5, 18.0, 20.0], lambda x, y: 6.0 < y < 15.2),
    "Coupe_CC": ("y", [30.0, 33.0], lambda x, y: 7.5 < x < 16.5 and y > 18.3),
    # elevations : seuls les arbres que la facade ne cache pas (devant, ou a cote du bati)
    "Elevation_Nord": ("x", [20.0, 18.0, 14.5, 12.5, 9.0, 5.5, 2.5, 0.0], lambda x, y: y < 18 and not (2.5 < x < 18 and y > 5)),
    "Elevation_Ouest": ("y", [0.0, 4.5, 5.5, 11.0, 16.8, 18.0, 30.0, 33.0],
                        lambda x, y: not ((4.5 < y < 16.8 and x > 2.5) or (21 < y < 30 and x > 3))),
    "Elevation_Sud": ("x", [0.0, 2.5, 5.5, 9.0, 12.5, 14.5, 18.0, 20.0], lambda x, y: y > 30 or (y > 17.9 and x < 3)),
    "Elevation_Est": ("y", [33.0, 30.0, 18.0, 16.8, 11.0, 5.5, 4.5, 0.0],
                      lambda x, y: not ((5.5 < y < 16.8 and x < 18) or (21 < y < 30 and x < 20))),
}
NIVEAUX = ((0.0, "±0,00"), (3.30, "+3,30"), (6.60, "+6,60"), (9.00, "+9,00"))


def calib_png(nom):
    """(a, b, kz, z0px, crop) : u_px = a * coord + b ; z_px = z0px - kz * z (metres)."""
    im = Image.open(V / f"calib_{nom}.png").convert("RGB")
    W, H = im.size
    px = im.load()
    cols = []
    for x in range(W):
        n = 0
        for y in range(0, H, 2):
            r, g, b = px[x, y]
            if b > r + 40 and b > 110:
                n += 1
        cols.append(n)
    seuil = 0.12 * H / 2
    xs, run = [], []
    for x, n in enumerate(cols + [0]):
        if n > seuil:
            run.append(x)
        elif run:
            xs.append(sum(run) / len(run))
            run = []
    _axe, ref, _f = LIGNE[nom]
    if len(xs) != len(ref):
        raise RuntimeError(f"{nom} : {len(xs)} axes trouves pour {len(ref)} attendus")
    a, b = _ajuste(list(zip(ref, xs)))
    # vertical : BIMCraft rend a la meme echelle dans les deux sens et centre le recadrage (-0,90 a +10,20) dans l'image
    zc = sum(BM.Z_CROP) / 2
    return a, b, abs(a), H / 2 + abs(a) * zc


class Ligne:
    """Coupe ou elevation au 1:100 en mm papier : terre, vegetation (fond), dessin BIMCraft (multiplie), personnages,
    calepinage de la peau, niveaux en bande a gauche, trait de sol."""

    def __init__(self, nom, coord0, coord1, z0=-1.2, z1=10.4, echelle=100):
        self.nom = nom
        self.axe, _ref, self.filtre = LIGNE[nom]
        self.a, self.b, self.kz, self.zp = calib_png(nom)
        self.S = 1000 / echelle
        self.sens = 1 if self.a > 0 else -1
        self.c0, self.c1 = (coord0, coord1) if self.sens > 0 else (coord1, coord0)   # coordonnees aux bords gauche / droit
        self.z0, self.z1 = z0, z1
        self.W = abs(coord1 - coord0) * self.S + 16          # bande des niveaux a gauche
        self.H = (z1 - z0) * self.S
        self.lib = Bibliotheque()
        self.fond, self.dessus = [], []

    def U(self, c):
        return 16 + (c - self.c0) * self.sens * self.S

    def Z(self, z):
        return (self.z1 - z) * self.S

    def veg(self, i, c, h, ton=46, miroir=False):
        b = self.lib.info(i)["dimensions_m"]
        k = h / b["hauteur"]
        self.fond.append(self.lib.elevation(i, self.U(c), self.Z(0), self.S, k=k, mirror=miroir, fill=TONS.get(ton, ton)))

    def pers(self, i, c, z=0.0, miroir=False):
        self.dessus.append(self.lib.elevation(i, self.U(c), self.Z(z), self.S, k=1.0, mirror=miroir, opacity=0.9))

    def lames(self, c_a, c_b, za, zb, pas=0.105):
        """Calepinage de la peau de lames : traits tres fins gris, verticaux."""
        lo, hi = sorted((self.U(c_a), self.U(c_b)))
        n = int((hi - lo) / (pas * self.S))
        d = "".join(f"M{lo + k * pas * self.S:.2f},{self.Z(zb):.2f} V{self.Z(za):.2f} " for k in range(1, n))
        self.dessus.append(f'<path d="{d}" stroke="#7a7a7a" stroke-width="0.09" fill="none"/>')

    def vegetation(self):
        for _b, x, y, d, ton, _r, bloc, h in BM.VEGETATION:
            if bloc and self.filtre(x, y):
                c = x if self.axe == "x" else y
                if min(self.c0, self.c1) - 1 < c < max(self.c0, self.c1) + 1:
                    self.veg(bloc, c, h, 30 if h >= 6 else (42 if h >= 4.5 else 55), miroir=(int(x * 10) % 2 == 0))

    def image(self):
        im = Image.open(V / f"{self.nom}.png").convert("L")
        W, H = im.size
        # pixel -> mm : u_mm = U(coord) ou coord = (px - b) / a ; z_mm = Z(z) ou z = (zp - py) / kz
        sx = self.S / abs(self.a)
        sz = self.S / self.kz
        ox = self.U((0 - self.b) / self.a)
        oz = self.Z(self.zp / self.kz)
        buf = io.BytesIO()
        im.save(buf, "PNG", optimize=True)
        src = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
        return (f'<image href="{src}" x="{ox:.2f}" y="{oz:.2f}" width="{W * sx:.2f}" height="{H * sz:.2f}" '
                f'preserveAspectRatio="none" style="mix-blend-mode:multiply"/>')

    def svg(self, niveaux=True):
        clip = f"cl_{self.nom}"
        g = [f'<clipPath id="{clip}"><rect x="12" y="0" width="{self.W - 12:.2f}" height="{self.H:.2f}"/></clipPath>',
             f'<g clip-path="url(#{clip})">', *self.fond, self.image(), *self.dessus]
        ys = self.Z(0)
        g.append(f'<line x1="12" y1="{ys:.2f}" x2="{self.W:.2f}" y2="{ys:.2f}" stroke="{INK}" stroke-width="0.6"/>')
        for k in range(int((self.W - 12) / 1.6)):                       # terre en pointille qui s'estompe
            for j in range(4):
                x = 12 + k * 1.6 + ((j * 37 + k * 13) % 16) / 10
                y = ys + 1.0 + j * 1.3 + ((k * 7 + j * 3) % 10) / 10
                g.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="0.16" fill="{INK}" opacity="{0.55 - j * 0.12:.2f}"/>')
        g.append("</g>")
        if niveaux:
            for z, t in NIVEAUX:
                y = self.Z(z)
                g.append(f'<circle cx="1.2" cy="{y:.2f}" r="0.7" fill="{INK}"/>'
                         f'<text x="2.6" y="{y - 0.9:.2f}" font-size="{7 * PT:.2f}" fill="{INK}">{t}</text>'
                         f'<line x1="2.4" y1="{y:.2f}" x2="11" y2="{y:.2f}" stroke="{INK}" stroke-width="0.13"/>')
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.W:.2f} {self.H:.2f}" width="{self.W:.2f}mm" '
                f'height="{self.H:.2f}mm" font-family=\'{FONT}\'><defs>{self.lib.defs()}</defs>{"".join(g)}</svg>')


def peau_vue(L, faces, garde=lambda s, line, a, b: True):
    """Calepinage de la peau sur les faces vues : (sens, cote exterieur) parmi les PEAU de facade.py."""
    peaux = [(s, line, a, b, out, 3.3, 6.4 if line != 4.5 else 7.2) for s, line, a, b, out, _ax in F.PEAU_VILLA]
    for k, x0 in enumerate(MX[:2]):
        peaux += [(s, line, a, b, out, 3.3, 6.4) for s, line, a, b, out, _ax in F.peau_maison(x0, k == 0)]
    for s, line, a, b, out, za, zb in peaux:
        if (s, out) in faces and garde(s, line, a, b):
            L.lames(a, b, za, zb)


def coupe(nom):
    c0, c1 = {"Coupe_AA": (-1.5, 19.5), "Coupe_BB": (-1.5, 21.5), "Coupe_CC": (18.3, 34.5)}[nom]
    L = Ligne(nom, c0, c1)
    L.vegetation()
    pers = {"Coupe_AA": [("pers_tt_03_robe_motifs_face", 12.0, 0.0, False), ("pers_pmd_108_assis_profil", 7.2, 6.6, True)],
            "Coupe_BB": [("pers_pmd_042_debout_face", 5.0, 0.0, False), ("pers_tt_05_tunique_face", 11.4, 0.0, True)],
            "Coupe_CC": [("pers_tt_02_marche_profil_sac", 31.2, 0.0, True), ("pers_pmd_027_lecture_assis", 23.0, 0.0, False)]}[nom]
    for i, c, z, m_ in pers:
        if i in L.lib.cat:
            L.pers(i, c, z, m_)
    return L.svg()


def elevation(nom):
    c0, c1 = {"Elevation_Nord": (-1.5, 21.5), "Elevation_Sud": (-1.5, 21.5), "Elevation_Ouest": (-1.5, 34.5),
              "Elevation_Est": (-1.5, 34.5)}[nom]
    L = Ligne(nom, c0, c1)
    L.vegetation()
    faces = {"Elevation_Nord": {("h", -1)}, "Elevation_Sud": {("h", 1)}, "Elevation_Ouest": {("v", -1)},
             "Elevation_Est": {("v", 1)}}[nom]
    garde = {"Elevation_Nord": lambda s, line, a, b: line < 18, "Elevation_Sud": lambda s, line, a, b: line > 18}
    peau_vue(L, faces, garde.get(nom, lambda *_: True))
    pers = {"Elevation_Nord": [("pers_tt_02_marche_profil_sac", 8.0, False)],
            "Elevation_Ouest": [("pers_pmd_130_marche_face", 24.5, False)],
            "Elevation_Sud": [("pers_tt_03_robe_motifs_face", 6.0, True)],
            "Elevation_Est": [("pers_pmd_005_marche_dos", 12.0, False)]}[nom]
    for i, c, m_ in pers:
        if i in L.lib.cat:
            L.pers(i, c, 0.0, m_)
    return L.svg()
