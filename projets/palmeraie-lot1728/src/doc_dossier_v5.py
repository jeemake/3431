"""Dossier de presentation de l'option C v5 (markups du 10-11-2026) et du locatif en 2 duplex.

Mise en page : regle Capitude PRESENTATION-PROJETS-ARCHI v4 (A3 paysage, grille unique de 12 colonnes x 4 rangs,
marges 14 / 27 / 22,5 mm, corps 7 / 9 / 14 / 28 pt, URW Gothic Book / Demi, noir et gris, un dominant par page).
Dessins : GABARIT-VISUEL-PLANS v3 (plans_capitude.py ; elevations et coupes au trait tirees de la maquette 3D,
poche noir au droit de la coupe, vegetation et personnages Archibooks). Vues d'ambiance : Sume, GPT Image 2.6.
"""
import base64
import io
import math
import pathlib

from PIL import Image

import facade as F
import plans_capitude as PC
from blocs_archibooks import CACHE, Bibliotheque
from doc import DIVISEUR, EXTERIEURS, FRAIS, IMPREVUS, OUT, RATIOS, TVA, a2, m, pct, to_pdf
from projet import (CY, LOCATIF_M, LOYERS, MX, OPTION_C, PLUS_VALUES, budget, pu, pu_ligne, surfaces)

C = OPTION_C
REND = OUT / "rendu"
IA = REND / "ia_v5"
UP = pathlib.Path("/root/.claude/uploads/7cae17a0-479c-5af5-b614-e1c26e51ae53")
SCRATCH = pathlib.Path("/tmp/claude-0/-home-user-3431/7cae17a0-479c-5af5-b614-e1c26e51ae53/scratchpad")
PROJET = "LOT 1728 · RIVIERA PALMERAIE, ABIDJAN"
Z0 = 0.15                                   # plancher fini RDC (+-0,00) au-dessus du terrain, dans la maquette
W_PX, H_PX, ZC = 2400, 1500, 4.5            # rendus au trait (vues.py)
INK, GRIS = "#3A332E", "#A49B95"


# ------------------------------------------------------------------------------------------------ outils
def b64(path, quality=84, maxw=2000, crop=None):
    im = Image.open(path).convert("RGB")
    if crop:
        im = im.crop(crop)
    im.thumbnail((maxw, maxw))
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=quality)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def trait_png(path, crop):
    """Rendu au trait -> PNG transparent (traits noirs, fond transparent) pour poser la vegetation derriere."""
    im = Image.open(path).convert("L").crop(crop)
    a = im.point(lambda v: 255 - v)
    rgba = Image.new("RGBA", im.size, (0, 0, 0, 0))
    rgba.putalpha(a)
    buf = io.BytesIO()
    rgba.save(buf, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def police_css():
    lib = CACHE / "lib"
    out = []
    for f, w in (("URWGothic-Book.otf", 400), ("URWGothic-Demi.otf", 700)):
        d = base64.b64encode((lib / f).read_bytes()).decode()
        out.append(f'@font-face{{font-family:"URW Gothic";src:url(data:font/otf;base64,{d}) format("opentype");font-weight:{w}}}')
    return "".join(out)


def fr(x, d=2):
    return f"{x:,.{d}f}".replace(",", " ").replace(".", ",")


# ------------------------------------------------------------------------------------------------ coupes et elevations
class Vue:
    """Rendu au trait (ortho) + habillage SVG au gabarit : sol, niveaux, vegetation, personnages, poche de coupe."""

    def __init__(self, fichier, ortho, centre, sens, u0, u1, z1=10.6):
        self.K = W_PX / ortho
        self.fichier, self.centre, self.sens = fichier, centre, sens
        xa, xb = sorted((self.px(u0), self.px(u1)))
        self.crop = (int(max(0, xa)), int(self.pz(z1)), int(min(W_PX, xb)), int(self.pz(-1.3)))
        self.w, self.h = self.crop[2] - self.crop[0], self.crop[3] - self.crop[1]
        self.fond, self.dessus = [], []
        self.lib = Bibliotheque()

    def px(self, u):
        return W_PX / 2 + self.sens * (u - self.centre) * self.K

    def pz(self, z):
        return H_PX / 2 - (z - ZC) * self.K

    def X(self, u):
        return self.px(u) - self.crop[0]

    def Y(self, z):
        return self.pz(z) - self.crop[1]

    def rect(self, u0, u1, z0, z1, fill="#000", calque="dessus"):
        a, b = sorted((self.X(u0), self.X(u1)))
        getattr(self, calque).append(f'<rect x="{a:.1f}" y="{self.Y(z1):.1f}" width="{b - a:.1f}" height="{self.Y(z0) - self.Y(z1):.1f}" fill="{fill}"/>')

    def veg(self, i, u, k=1.0, ton=None, miroir=False, opacite=1.0):
        fill = PC.TONS.get(ton, ton) if ton else None
        self.fond.append(self.lib.elevation(i, self.X(u), self.Y(0), self.K, k=k, mirror=miroir, opacity=opacite, fill=fill))

    def pers(self, i, u, z=Z0, miroir=False, opacite=0.9):
        self.dessus.append(self.lib.elevation(i, self.X(u), self.Y(z), self.K, k=1.0, mirror=miroir, opacity=opacite))

    def texte(self, u, z, t, size=18, weight=400, anchor="middle"):
        self.dessus.append(f'<text x="{self.X(u):.1f}" y="{self.Y(z):.1f}" font-size="{size}" font-weight="{weight}" '
                           f'text-anchor="{anchor}" fill="#000" paint-order="stroke" stroke="#fff" stroke-width="4">{t}</text>')

    def svg(self, niveaux=True, couv=9.0):
        w, h = self.w, self.h
        g = list(self.fond)
        g.append(f'<image href="{trait_png(REND / self.fichier, self.crop)}" x="0" y="0" width="{w}" height="{h}"/>')
        g += self.dessus
        ys = self.Y(0)
        g.append(f'<line x1="0" y1="{ys:.1f}" x2="{w}" y2="{ys:.1f}" stroke="#000" stroke-width="4"/>')
        for k in range(int(w / 9)):                    # terre en pointille qui s'estompe
            for j in range(4):
                x = (k * 9 + (j * 37 + k * 13) % 9)
                y = ys + 6 + j * 7 + (k * 7 + j * 3) % 6
                g.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.1" fill="#000" opacity="{0.55 - j * 0.12:.2f}"/>')
        if niveaux:
            for z, t in ((Z0, "±0,00"), (Z0 + 3.30, "+3,30"), (Z0 + 6.60, "+6,60"), (Z0 + couv, "+9,00")):
                y = self.Y(z)
                g.append(f'<circle cx="10" cy="{y:.1f}" r="5" fill="#000"/>'
                         f'<text x="22" y="{y - 6:.1f}" font-size="19" fill="#000">{t}</text>'
                         f'<line x1="18" y1="{y:.1f}" x2="92" y2="{y:.1f}" stroke="#000" stroke-width="1"/>')
        K = self.K
        sx, sy = w - 5 * K - 20, h - 18
        g.append(f'<line x1="{sx:.1f}" y1="{sy}" x2="{sx + 5 * K:.1f}" y2="{sy}" stroke="#000" stroke-width="2"/>')
        for mm_ in (0, 1, 3, 5):
            g.append(f'<line x1="{sx + mm_ * K:.1f}" y1="{sy - 8}" x2="{sx + mm_ * K:.1f}" y2="{sy}" stroke="#000" stroke-width="1.5"/>'
                     f'<text x="{sx + mm_ * K:.1f}" y="{sy + 17}" font-size="16" text-anchor="middle" fill="#000">{mm_}{" m" if mm_ == 5 else ""}</text>')
        return (f'<svg viewBox="0 0 {w} {h}" style="width:100%;height:100%;display:block" preserveAspectRatio="xMidYMid meet" '
                f'font-family="URW Gothic, sans-serif"><defs>{self.lib.defs()}</defs>{"".join(g)}</svg>')


def _intervals(opt, niveau, axis, at):
    out = []
    for r in opt["pieces"]:
        if r["niveau"] != niveau or not r["clos"]:
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


def poche(v, opt, explicit, axis, at, hauteurs=(3.30, 3.30, 2.15)):
    """Murs et dalles coupes en poche noir au droit de la coupe ; baies coupees laissees blanches (double trait)."""
    perp = "h" if axis == "x" else "v"
    for (niveau, zf), hn in zip((("RDC", Z0), ("R+1", Z0 + 3.30), ("TOIT", Z0 + 6.60)), hauteurs):
        ivs = _intervals(opt, niveau, axis, at)
        bounds = sorted({round(b, 2) for lo, hi, _ in ivs for b in (lo, hi)})
        for b in bounds:
            gaps = []
            for nv, x, y, s_, wd in opt["portes"]:
                line, along = (y, x) if s_ == "h" else (x, y)
                if nv == niveau and s_ == perp and abs(line - b) < 0.06 and abs(along - at) < wd / 2:
                    gaps.append((0.0, 2.4))
            for nv, s_, line, a, b2, z0, z1, kind in explicit:
                if nv == niveau and s_ == perp and abs(line - b) < 0.06 and a <= at <= b2:
                    gaps.append((z0, z1))
            zs = [(0.0, hn - (0.25 if niveau != "TOIT" else 0.0))]
            for z0, z1 in gaps:
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
                v.rect(b - 0.03, b - 0.01, zf + z0, zf + z1)
                v.rect(b + 0.01, b + 0.03, zf + z0, zf + z1)
            for a, b2 in zs:
                v.rect(b - 0.1, b + 0.1, zf + a, zf + b2)
        for lo, hi, r in ivs:
            if niveau != "TOIT":
                v.rect(lo - 0.1, hi + 0.1, zf + hn - 0.25, zf + hn)
        if niveau == "RDC" and ivs:
            v.rect(min(lo for lo, _, _ in ivs) - 0.1, max(hi for _, hi, _ in ivs) + 0.1, 0, Z0)


def coupe_AA(var):
    v = Vue(f"coupe_AA_{var}.png", 31.0, 10.0, 1, -1.5, 21.0)
    poche(v, C, F.OUVERTURES, "x", 10.75)
    T = Z0 + 6.60
    v.rect(4.36, 5.5, Z0 + 3.12, Z0 + 3.30)                 # dalle de la loggia
    v.rect(4.36, 5.5, T - 0.18, T)
    v.rect(4.36, 5.1, T, T + 0.6)                           # jardiniere
    v.rect(11.0, 13.4, Z0 + 3.05, Z0 + 3.30)                # dalle de la terrasse couverte
    v.rect(11.0, 11.15, T, T + 1.0)                         # garde-corps
    v.rect(17.82, 18.0, 0, 3.5)                             # mur vegetalise
    v.rect(0.0, 0.2, 0, 1.0)
    v.veg("veg_coupe_arbre_silhouette_pleine", 12.6, k=1.0, ton=30)
    v.veg("veg_coupe_grandes_feuilles", 13.9, k=0.9, ton=64)
    v.veg("veg_coupe_fougeres", 9.6, k=0.8, ton=55)
    v.veg("veg_coupe_bosquet_etage", 22.5, k=0.8, ton=36)
    v.pers("pers_tt_03_robe_motifs_face", 12.0)
    v.pers("pers_pmd_108_assis_profil", 7.0, z=T, miroir=True)
    return v.svg()


def coupe_BB(var):
    v = Vue(f"coupe_BB_{var}.png", 31.0, 10.0, 1, -1.5, 21.5)
    poche(v, C, F.OUVERTURES, "y", 14.8)
    T = Z0 + 6.60
    v.rect(1.7, 2.5, Z0 + 3.12, Z0 + 3.30)
    v.rect(1.7, 1.85, Z0 + 3.30, Z0 + 4.1)
    v.rect(2.5, 2.65, T, T + 1.0)
    v.rect(8.85, 9.0, T, T + 1.0)
    v.rect(14.5, 18.0, Z0 + 3.05, Z0 + 3.30)
    v.rect(0.0, 0.2, 0, 2.2)
    v.rect(19.8, 20.0, 0, 2.2)
    v.veg("veg_coupe_arbre_silhouette_pleine", 12.6, k=1.0, ton=30)
    v.veg("veg_coupe_palmier_retombant", 1.2, k=0.7, ton=46)
    v.veg("veg_coupe_grandes_feuilles", 10.2, k=0.9, ton=64)
    v.pers("pers_pmd_042_debout_face", 5.0)
    v.pers("pers_tt_05_tunique_face", 11.4, miroir=True)
    return v.svg()


def coupe_CC():
    v = Vue("coupe_CC_V1.png", 31.0, 25.0, 1, 16.0, 34.5)
    expl = [o for k, x0 in enumerate(MX[:2]) for o in F.ouvertures_maison(x0, k == 0)]
    poche(v, LOCATIF_M, expl, "x", 7.5, hauteurs=(3.30, 3.30, 2.4))
    T = Z0 + 6.60
    for y0, y1 in ((20.84, 21.0), (30.0, 30.16)):
        v.rect(y0, y1, Z0 + 3.12, Z0 + 3.30)
        v.rect(y0, y1, T - 0.18, T)
    v.rect(21.0, 21.15, T, T + 1.0)
    v.rect(29.85, 30.0, T, T + 1.0)
    v.rect(17.82, 18.0, 0, 3.5)
    v.rect(32.8, 33.0, 0, 2.2)
    v.veg("veg_coupe_petit_feuillu_dense", 19.5, k=0.9, ton=46)
    v.veg("veg_coupe_bosquet_etage", 14.5, k=0.8, ton=30)
    v.veg("veg_coupe_grandes_feuilles", 32.3, k=0.8, ton=64)
    v.pers("pers_tt_02_marche_profil_sac", 31.2, miroir=True)
    v.pers("pers_pmd_027_lecture_assis", 23.0)
    return v.svg()


def elevation(nom, var, ortho, centre, sens, u0, u1, arbres=(), gens=()):
    v = Vue(f"{nom}_{var}.png", ortho, centre, sens, u0, u1)
    for i, u, k, ton in arbres:
        v.veg(i, u, k=k, ton=ton)
    for i, u, mir in gens:
        v.pers(i, u, miroir=mir)
    return v.svg()


def elev_N(var):
    return elevation("elev_N", var, 31.0, 10.0, -1, 21.0, -1.0,
                     [("veg_coupe_arbre_silhouette_pleine", 13.0, 0.75, 30), ("veg_coupe_grandes_feuilles", 3.8, 0.8, 55),
                      ("veg_coupe_arbre_silhouette_pleine", 21.6, 0.8, 30)],
                     [("pers_tt_06_marche_face_motifs", 8.5, False)])


def elev_O(var):
    return elevation("elev_O", var, 37.0, 16.5, 1, -1.5, 34.5,
                     [("veg_coupe_arbre_silhouette_pleine", 9.0, 0.8, 30), ("veg_coupe_palmier_retombant", 12.2, 0.6, 46),
                      ("veg_coupe_arbre_silhouette_pleine", 19.5, 0.65, 36), ("veg_coupe_grandes_feuilles", 31.5, 0.8, 55)],
                     [("pers_va_02_bassine_enfant", 5.0, False), ("pers_pmd_130_marche_face", 25.5, True)])


def elev_S(var):
    return elevation("elev_S", var, 31.0, 10.0, 1, -1.0, 21.0,
                     [("veg_coupe_arbre_silhouette_pleine", 12.6, 0.95, 30), ("veg_coupe_grandes_feuilles", 9.8, 0.8, 55)],
                     [("pers_pmd_005_marche_dos", 6.0, False)])


def elev_E(var):
    return elevation("elev_E", var, 31.0, 10.0, -1, 19.0, 1.0,
                     [("veg_coupe_palmier_retombant", 7.0, 0.55, 46)], [])


def elev_LN(var):
    return elevation("elev_LN", var, 31.0, 10.0, -1, 21.0, -1.0,
                     [("veg_coupe_arbre_silhouette_pleine", 4.7, 0.7, 30), ("veg_coupe_petit_feuillu_dense", 7.0, 0.7, 55),
                      ("veg_coupe_arbre_silhouette_pleine", 13.3, 0.7, 36)],
                     [("pers_pmd_042_debout_face", 10.5, False)])


# ------------------------------------------------------------------------------------------------ details de facade
def details_svg():
    """Planche de details constructifs : coupes verticales de la facade Nord (V1, V2) et plans des peaux."""
    g = []

    def R(x, y, w, h, fill="#000", st="none", sw=0):
        g.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}" stroke="{st}" stroke-width="{sw}"/>')

    def L(x1, y1, x2, y2, sw=1.0, dash=None, col="#000"):
        d_ = f' stroke-dasharray="{dash}"' if dash else ""
        g.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{col}" stroke-width="{sw}"{d_}/>')

    def T(x, y, t, size=11, weight=400, anchor="start"):
        g.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" fill="#000">{t}</text>')

    def bulle(n, x, y):
        g.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="8" fill="#fff" stroke="#000" stroke-width="0.8"/>')
        T(x, y + 3.6, str(n), 9.5, 700, "middle")

    class Coupe:
        """Coupe verticale : u = distance au nu exterieur du mur de facade (negatif vers la rue), z = niveau (m)."""
        def __init__(self, ox, oy, M=80, ztop=9.35):
            self.ox, self.oy, self.M, self.zt = ox, oy, M, ztop

        def x(self, u):
            return self.ox + u * self.M

        def y(self, z):
            return self.oy + (self.zt - z) * self.M

        def rect(self, u0, u1, z0, z1, fill="#000", st="none", sw=0):
            R(self.x(min(u0, u1)), self.y(max(z0, z1)), abs(u1 - u0) * self.M, abs(z1 - z0) * self.M, fill, st, sw)

        def line(self, u0, z0, u1, z1, sw=1.0, dash=None, col="#000"):
            L(self.x(u0), self.y(z0), self.x(u1), self.y(z1), sw, dash, col)

    def ossature(c):
        for z in (3.30, 6.60):                                   # dalles : nez mince de 18 cm, dalle 25 cm
            c.rect(-1.14, 1.6, z - 0.18, z)
            c.rect(0.0, 1.6, z - 0.25, z - 0.18)
        c.rect(0.0, 0.2, 5.70, 6.35)                             # linteau de la baie sur la loggia
        c.line(0.1, 3.30, 0.1, 5.70, sw=0.8)                     # menuiserie (vue)
        c.line(0.06, 3.30, 0.06, 5.70, sw=0.5)
        c.line(-1.5, 3.30, 1.6, 3.30, sw=0.4, dash="3 3", col="#777")
        c.rect(-1.0, -0.94, 6.60, 7.20)                          # jardiniere : parois et substrat
        c.rect(-0.46, -0.40, 6.60, 7.20)
        c.rect(-0.94, -0.46, 6.60, 6.66)
        c.rect(-0.94, -0.46, 6.66, 7.10, fill="#fff", st="#000", sw=0.6)
        for k in range(9):
            u = -0.92 + k * 0.055
            c.line(u, 6.70, u + 0.05, 7.08, sw=0.4, col="#777")
        for k in range(5):                                       # plantation basse
            u = -0.88 + k * 0.1
            c.line(u, 7.10, u - 0.05, 7.32, sw=0.7)
            c.line(u, 7.10, u + 0.05, 7.30, sw=0.7)
        c.rect(1.4, 1.6, 6.60, 7.60)                             # garde-corps du toit-terrasse (au-dela)
        for z, t in ((3.30, "+3,30"), (6.60, "+6,60"), (9.00, "+9,00")):
            g.append(f'<circle cx="{c.x(2.3):.1f}" cy="{c.y(z):.1f}" r="3.5" fill="#000"/>')
            T(c.x(2.4), c.y(z) - 5, t, 11)
            L(c.x(1.75), c.y(z), c.x(2.3), c.y(z), sw=0.6)

    # ---------- 1. coupe V1
    c1 = Coupe(330, 80)
    T(40, 28, "1 · COUPE VERTICALE, FAÇADE NORD, V1 : LAMES EN DAMIER", 13, 700)
    ossature(c1)
    for k in range(4):                                           # 4 rangs de panneaux de lames (vus en coupe)
        z0 = 3.30 + k * 0.76
        c1.rect(-1.14, -1.10, z0 + 0.03, z0 + 0.73, fill="#fff", st="#000", sw=0.9)
        c1.rect(-1.10, -1.05, z0 - 0.02, z0 + 0.02)              # traverse acier 40 x 40
    c1.rect(-1.10, -1.05, 6.36, 6.42)
    c1.rect(-1.10, -1.00, 3.24, 3.27)                            # equerre en nez de dalle
    c1.rect(-1.10, -1.00, 6.36, 6.39)
    c1.rect(-2.0, 1.6, 8.82, 9.00)                               # couverture plate mince
    c1.line(-1.95, 8.82, -1.95, 8.79, sw=1.6)                    # goutte d'eau
    c1.rect(-0.07, 0.07, 6.60, 8.82, fill="#fff", st="#000", sw=1.2)   # poteau acier
    for n, u, z in ((1, -1.12, 4.40), (2, -1.075, 5.58), (3, -1.05, 3.255), (4, 0.1, 6.0), (5, -0.6, 3.21),
                    (6, -0.7, 6.9), (7, 0.6, 8.91), (8, 0.0, 7.7)):
        bulle(n, c1.x(-2.55), c1.y(z))
        L(c1.x(-2.46), c1.y(z), c1.x(u), c1.y(z), sw=0.5)
        g.append(f'<circle cx="{c1.x(u):.1f}" cy="{c1.y(z):.1f}" r="1.8" fill="#000"/>')
    # ---------- 2. coupe V2
    c2 = Coupe(1010, 80)
    T(720, 28, "2 · COUPE VERTICALE, FAÇADE NORD, V2 : BARDAGE, BRISE-SOLEIL, DÉBORDS", 13, 700)
    ossature(c2)
    c2.rect(-1.14, -1.12, 3.30, 6.42, fill="#fff", st="#000", sw=0.9)        # bardage (lames 22 mm)
    for k in range(6):
        z = 3.40 + k * 0.6
        c2.rect(-1.12, -1.06, z, z + 0.04)                                   # tasseaux 40 x 60
    c2.rect(-1.06, -1.00, 3.30, 6.42, fill="#fff", st="#000", sw=0.7)        # ossature secondaire acier
    c2.rect(-1.48, -1.44, 3.36, 6.36, fill="#fff", st="#000", sw=0.9)        # brise-soleil pivotant (vu)
    for z in (3.36, 6.36):
        g.append(f'<circle cx="{c2.x(-1.30):.1f}" cy="{c2.y(z):.1f}" r="2.4" fill="#000"/>')
        c2.line(-1.44, z, -1.14, z, sw=0.8)
    c2.rect(-2.6, -1.14, 3.30, 3.42)                                         # auvent bas
    for k in range(14):
        u = -2.58 + k * 0.104
        c2.rect(u, u + 0.07, 3.27, 3.30, fill="#fff", st="#000", sw=0.5)     # sous-face en lames
    eu, ez = -2.2, 8.70
    tan = math.tan(math.radians(15))
    ur = 0.2                                                                  # coupure : la croupe continue vers le faitage
    g.append(f'<path d="M{c2.x(eu):.1f},{c2.y(ez + 0.12):.1f} L{c2.x(ur):.1f},{c2.y(ez + 0.12 + (ur - eu) * tan):.1f} '
             f'L{c2.x(ur):.1f},{c2.y(ez + (ur - eu) * tan):.1f} L{c2.x(eu):.1f},{c2.y(ez):.1f} Z" fill="#000"/>')
    c2.line(ur + 0.05, ez + 0.95, ur - 0.05, ez + 0.6, sw=0.8)
    T(c2.x(ur + 0.1), c2.y(ez + 0.75), "vers le faîtage", 10)
    for k in range(17):
        u = eu + 0.05 + k * 0.22
        c2.rect(u, u + 0.16, ez - 0.03, ez, fill="#fff", st="#000", sw=0.5)  # sous-face ventilee en lames
    c2.line(eu, ez - 0.03, 1.6, ez - 0.03, sw=0.5, dash="2 2")
    c2.rect(eu - 0.16, eu, ez - 0.12, ez + 0.06, fill="#fff", st="#000", sw=1.0)   # cheneau
    c2.rect(-0.07, 0.07, 6.60, ez - 0.03, fill="#fff", st="#000", sw=1.2)
    for n, u, z in ((9, -1.13, 4.6), (10, -1.09, 5.42), (11, -1.46, 5.0), (12, -1.9, 3.28), (13, 0.8, 8.98),
                    (14, eu - 0.08, 8.67), (15, 0.0, 7.7)):
        bulle(n, c2.x(-2.95), c2.y(z))
        L(c2.x(-2.86), c2.y(z), c2.x(u), c2.y(z), sw=0.5)
        g.append(f'<circle cx="{c2.x(u):.1f}" cy="{c2.y(z):.1f}" r="1.8" fill="#000"/>')
    # ---------- 3. plans des peaux (1 m = 230 px)
    M2, py0 = 230, 680
    T(40, py0 - 22, "3 · PLAN DE LA PEAU V1 : PANNEAUX DENSE ET OUVERT ALTERNÉS, MODULE 0,62 M", 13, 700)
    x = 50
    for p in range(3):
        dense = p % 2 == 0
        pas, ep = (0.075, 0.065) if dense else (0.16, 0.055)
        n = int(0.62 / pas)
        for k in range(n):
            R(x + (k * pas + 0.005) * M2, py0, ep * M2, 0.14 * M2, fill="#fff", st="#000", sw=0.8)
        L(x, py0 + 0.14 * M2 + 6, x + 0.62 * M2, py0 + 0.14 * M2 + 6, sw=0.6, dash="4 3")
        T(x + 0.31 * M2, py0 + 0.14 * M2 + 22, "panneau dense" if dense else "panneau ouvert", 10, 400, "middle")
        x += 0.62 * M2
    T(50, py0 + 0.14 * M2 + 44, "Lames iroko 65 × 140 mm au pas de 75 mm (dense) et 55 × 140 mm au pas de 160 mm (ouvert) ;", 10)
    T(50, py0 + 0.14 * M2 + 58, "les rangs sont décalés d’un module d’un niveau à l’autre (damier) ; traverses acier en tirets.", 10)
    px0 = 720
    T(px0, py0 - 22, "4 · PLAN DE LA PEAU V2 : BARDAGE ET BRISE-SOLEIL PIVOTANTS", 13, 700)
    for k in range(9):
        R(px0 + 10 + k * 0.105 * M2, py0 + 20, 0.095 * M2, 0.022 * M2, fill="#fff", st="#000", sw=0.8)
    for k in range(2):
        R(px0 + 10 + k * 0.6 * M2, py0 + 20 + 0.022 * M2, 0.04 * M2, 0.06 * M2)
    for k in range(5):
        cx_, cy_ = px0 + 330 + k * 0.3 * M2, py0 + 20 + 0.011 * M2
        g.append(f'<g transform="translate({cx_:.1f},{cy_:.1f}) rotate(-35)"><rect x="{-0.025 * M2:.1f}" y="{-0.17 * M2:.1f}" '
                 f'width="{0.05 * M2:.1f}" height="{0.34 * M2:.1f}" fill="#fff" stroke="#000" stroke-width="0.8"/></g>'
                 f'<circle cx="{cx_:.1f}" cy="{cy_:.1f}" r="2.2" fill="#000"/>')
    L(px0 + 10, py0 + 20 + 0.10 * M2, px0 + 680, py0 + 20 + 0.10 * M2, sw=0.6, dash="4 3")
    T(px0, py0 + 0.14 * M2 + 44, "Bardage iroko 22 × 95 mm à joint de 10 mm sur tasseaux 40 × 60 ; brise-soleil 50 × 340 mm", 10)
    T(px0, py0 + 0.14 * M2 + 58, "sur axe inox tous les 300 mm, groupés dans l’axe des baies (représentés ouverts à 35°).", 10)
    # ---------- nomenclature
    nom = [
        "Claustra de lames de bois dur (iroko), panneaux de 0,62 m en damier, 4 rangs par étage",
        "Traverse acier 40 × 40 thermolaquée noire, filante tous les 0,76 m",
        "Équerre de fixation en nez de dalle, acier galvanisé chevillé",
        "Baie de la chambre ou du salon familial sur la loggia de 1,00 m",
        "Nez de dalle mince de 18 cm, béton blanc, même cote sur la villa et les duplex",
        "Jardinière en rive de toiture : plantation basse, étanchéité, drainage, goutte-à-goutte",
        "Couverture plate mince de 18 cm, débord de 1,0 à 1,5 m, goutte d’eau ; descentes en façade",
        "Poteau acier Ø 140 noir sur platine, sur les axes de la trame",
        "Bardage iroko 22 × 95, joint creux de 10 mm",
        "Tasseaux 40 × 60 traités classe 4, lame d’air ventilée",
        "Ossature secondaire acier entre nez de dalle ; brise-soleil pivotants 50 × 340 sur axe inox",
        "Auvent bas à +3,30 sur la rue, sous-face en lames de bois",
        "Toit en croupe à 15°, bac acier isolé, sous-face ventilée en lames de bois",
        "Chéneau et descente d’eaux pluviales en façade, aucune eau vers le patio",
        "Poteau acier Ø 140 noir",
    ]
    yy = 860
    T(40, yy, "NOMENCLATURE", 11, 700)
    for k, t in enumerate(nom):
        col, row = k // 8, k % 8
        x, y = 50 + col * 680, yy + 22 + row * 22
        bulle(k + 1, x, y - 4)
        T(x + 16, y, t, 10.5)
    T(40, 1082, "Principes d’esquisse, à valider par le BET structure et l’entreprise (sections, fixations, essences, classes d’emploi).", 10, 400)
    return (f'<svg viewBox="0 0 1400 1090" preserveAspectRatio="xMidYMid meet" style="width:100%;height:100%;display:block" '
            f'font-family="URW Gothic, sans-serif">{"".join(g)}</svg>')


# ------------------------------------------------------------------------------------------------ site
def satellite():
    """Vue aerienne (imagerie publique) recadree, contour du lot estime (angle Nord-Ouest de l'ilot)."""
    im = Image.open(SCRATCH / "tiles" / "sat.png").convert("RGB")
    from PIL import ImageDraw
    d = ImageDraw.Draw(im)
    o = (701, 697)
    a = math.radians(7.8)
    u, v = (math.cos(a), math.sin(a)), (-math.sin(a), math.cos(a))
    k = 1 / 0.297
    pts = [(o[0] + (x * u[0] + y * v[0]) * k, o[1] + (x * u[1] + y * v[1]) * k) for x, y in ((0, 0), (20, 0), (20, 33), (0, 33))]
    d.line(pts + [pts[0]], fill=(255, 255, 255), width=4)
    mid = [(o[0] + (x * u[0] + 18 * v[0]) * k, o[1] + (x * u[1] + 18 * v[1]) * k) for x in (0, 20)]
    d.line(mid, fill=(255, 255, 255), width=2)
    im = im.crop((470, 520, 1010, 925))
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=86)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


# ------------------------------------------------------------------------------------------------ tableaux
def tableau_surf(opt, niveaux, titre):
    rows = []
    tot = 0
    for niv in niveaux:
        ps = [p for p in opt["pieces"] if p["niveau"] == niv]
        if not ps:
            continue
        lab = {"RDC": "REZ-DE-CHAUSSÉE", "R+1": "ÉTAGE", "TOIT": "NIVEAU HAUT"}[niv]
        rows.append(f'<tr class="sec"><td colspan="2">{lab}</td></tr>')
        st = 0
        agg = {}
        for p in ps:
            key = PC.nom_court(p).capitalize() + ("" if p["clos"] else " (hors clos)")
            agg[key] = agg.get(key, 0) + p["surface"]
            if p["clos"] and niv != "TOIT":
                st += p["surface"]
        for k_, v_ in agg.items():
            rows.append(f'<tr><td>{k_}</td><td class="n">{fr(v_, 1)}</td></tr>')
        if niv != "TOIT":
            rows.append(f'<tr class="sub"><td>Surface close</td><td class="n">{fr(st, 1)}</td></tr>')
            tot += st
    rows.append(f'<tr class="tot"><td>TOTAL CLOS {titre}</td><td class="n">{fr(tot, 1)} m²</td></tr>')
    return f'<table><tr><th>PIÈCE</th><th class="n">M²</th></tr>{"".join(rows)}</table>'


def lignes(opt):
    k = opt["code"]
    rows = []
    for niv, lab in (("RDC", "Rez-de-chaussée"), ("R+1", "Étage"), ("TOIT", "Niveau haut")):
        ps = [p for p in opt["pieces"] if p["niveau"] == niv]
        if not ps:
            continue
        rows.append(("sec", lab.upper()))
        agg = {}
        for p in ps:
            key = PC.nom_court(p).capitalize()
            a = agg.setdefault(key, [0, p["code"]])
            a[0] += p["surface"]
        for key, (sf, code) in agg.items():
            rows.append(("l", key + (" (× 2)" if k == "M" and code not in ("parvis",) else ""), RATIOS[code][0], f"{fr(sf, 1)} m²",
                         m(pu(code)), m(sf * pu(code))))
    for titre, liste in (("AMÉNAGEMENTS EXTÉRIEURS ET VRD", EXTERIEURS), ("PLUS-VALUES DU PARTI", PLUS_VALUES)):
        ls = [lg for lg in liste if lg[4].get(k, 0)]
        if not ls:
            continue
        rows.append(("sec", titre))
        for lg in ls:
            q = lg[4][k]
            rows.append(("l", lg[0], f"base ÷ {DIVISEUR}" if lg[5] else "prix de marché", f"{fr(q, 1)} {lg[1]}",
                         m(pu_ligne(lg)), m(q * pu_ligne(lg))))
    b = budget(opt)
    rows.append(("tot", "TOTAL TRAVAUX HT", m(b["travaux"])))
    for lib, taux in FRAIS + [("Imprévus (stade esquisse)", IMPREVUS)]:
        rows.append(("l", lib, "", pct(taux, 2), "", m(taux * b["travaux"])))
    rows.append(("tot", "TOTAL HT", m(b["total_ht"])))
    rows.append(("l", "TVA", "", pct(TVA, 0), "", m(b["tva"])))
    rows.append(("tot", "TOTAL TTC", m(b["total_ttc"])))
    return rows


def table_estim(rows):
    out = ['<table class="est"><tr><th>DÉSIGNATION</th><th>SOURCE</th><th class="n">QTÉ</th><th class="n">PU HT</th><th class="n">TOTAL HT</th></tr>']
    for r in rows:
        if r[0] == "sec":
            out.append(f'<tr class="sec"><td colspan="5">{r[1]}</td></tr>')
        elif r[0] == "tot":
            out.append(f'<tr class="tot"><td colspan="4">{r[1]}</td><td class="n">{r[2]}</td></tr>')
        else:
            out.append(f'<tr><td>{r[1]}</td><td class="g">{r[2]}</td><td class="n">{r[3]}</td><td class="n">{r[4]}</td><td class="n">{r[5]}</td></tr>')
    return "".join(out) + "</table>"


# ------------------------------------------------------------------------------------------------ mise en page
CSS = """
@page { size: 420mm 297mm; margin: 0; }
* { box-sizing: border-box; }
body { margin: 0; font-family: "URW Gothic", sans-serif; color: #3A332E; font-size: 9pt; line-height: 12.75pt; }
.page { width: 420mm; height: 297mm; position: relative; page-break-after: always; overflow: hidden; background: #fff;
  display: grid; grid-template-columns: repeat(12, 1fr); column-gap: 4.5mm; grid-template-rows: repeat(4, 58.5mm);
  row-gap: 4.5mm; padding: 27mm 14mm 22.5mm 14mm; }
.hd { position: absolute; top: 12.2mm; left: 14mm; right: 14mm; display: grid; grid-template-columns: repeat(12, 1fr);
  column-gap: 4.5mm; align-items: baseline; }
.hd .n { grid-column: 1; font-weight: 700; font-size: 14pt; }
.hd .t { grid-column: 2 / 10; font-weight: 700; font-size: 14pt; letter-spacing: 1.4pt; text-transform: uppercase; }
.hd .s { grid-column: 10 / 13; text-align: right; font-size: 7pt; color: #A49B95; letter-spacing: 1pt; text-transform: uppercase; }
.ft { position: absolute; bottom: 11mm; left: 14mm; right: 14mm; font-size: 7pt; color: #A49B95; display: flex;
  justify-content: space-between; letter-spacing: 0.6pt; }
.b { min-width: 0; min-height: 0; position: relative; }
.dess { display: flex; flex-direction: column; }
.dess .svgw { flex: 1; min-height: 0; }
.dess .svgw svg { width: 100%; height: 100%; }
.titre { font-size: 9pt; margin-top: 1.5mm; } .titre b { font-weight: 700; letter-spacing: 1pt; text-transform: uppercase; }
.titre span { color: #A49B95; }
.img { width: 100%; height: 100%; object-fit: cover; display: block; }
.cap { font-size: 7pt; color: #A49B95; margin-top: 1mm; letter-spacing: 0.4pt; }
.data { font-size: 9pt; }
.data p { margin: 0 0 4.5mm; }
.data .k { font-size: 7pt; letter-spacing: 1.2pt; color: #A49B95; text-transform: uppercase; display: block; }
.data .v { font-weight: 400; }
table { border-collapse: collapse; width: 100%; font-size: 7pt; line-height: 9.5pt; }
th { text-align: left; font-weight: 700; letter-spacing: 1pt; border-bottom: 0.25pt solid #3A332E; padding: 0.8mm 1mm; }
td { padding: 0.45mm 1mm; vertical-align: top; } td.n, th.n { text-align: right; white-space: nowrap; }
td.g { color: #A49B95; }
tr.sec td { font-weight: 700; letter-spacing: 1pt; padding-top: 2.2mm; }
tr.sub td { border-top: 0.25pt solid #A49B95; } tr.tot td { font-weight: 700; border-top: 0.25pt solid #3A332E; }
.cover h1 { font-size: 28pt; line-height: 32pt; font-weight: 400; margin: 0 0 4mm; }
.cover .l { font-size: 9pt; letter-spacing: 2pt; text-transform: uppercase; }
"""


def page(n, titre, sous, corps, folio, plein=False):
    hd = "" if plein else (f'<div class="hd"><div class="n">{n}</div><div class="t">{titre}</div><div class="s">{sous}</div></div>'
                           f'<div class="ft"><span>{PROJET}</span><span>{folio:02d}</span></div>')
    return f'<section class="page">{hd}{corps}</section>'


def bloc(c0, c1, r0, r1, html, cls="b"):
    return f'<div class="{cls}" style="grid-column:{c0}/{c1 + 1};grid-row:{r0}/{r1 + 1}">{html}</div>'


def dessin(c0, c1, r0, r1, svg, titre, complement=""):
    t = f'<div class="titre"><b>{titre}</b> <span>{complement}</span></div>'
    return bloc(c0, c1, r0, r1, f'<div class="svgw">{svg}</div>{t}', "b dess")


def image(c0, c1, r0, r1, src, cap):
    return bloc(c0, c1, r0, r1, f'<img class="img" src="{b64(src)}" style="height:calc(100% - 5mm)"/><div class="cap">{cap}</div>')


def donnees(items):
    return '<div class="data">' + "".join(f'<p><span class="k">{k}</span><span class="v">{v}</span></p>' for k, v in items) + "</div>"


def plan_svg(svg):
    return svg.replace('<svg ', '<svg preserveAspectRatio="xMidYMid meet" style="width:100%;height:100%" ', 1)


def build():
    s, b = surfaces(C), budget(C)
    sm, bm = surfaces(LOCATIF_M), budget(LOCATIF_M)
    P = []

    def add(n, titre, sous, corps, plein=False):
        P.append(page(n, titre, sous, corps, len(P) + 1, plein))

    # 1. couverture
    add("", "", "", bloc(3, 10, 1, 3, f'<img class="img" src="{b64(IA / "arrivee_V1.jpg")}"/>')
        + bloc(3, 10, 4, 4, '<div class="cover"><h1>Villa à patio et deux maisons duplex</h1>'
                            '<div class="l">Lot 1728 · Riviera Palmeraie, Abidjan · Esquisse, option C v5 · 10.11.2026</div></div>'),
        plein=True)
    # 2. site
    photos = [(UP / "9cc1b788-image.jpg", "Clôture sur la rue Ouest"), (UP / "369408c8-image.jpg", "Rue Ouest vers le Sud"),
              (UP / "b2afac81-image.jpg", "Le lot vu depuis le voisin Est")]
    corps = bloc(1, 6, 1, 3, f'<img class="img" src="{satellite()}" style="height:calc(100% - 5mm)"/><div class="cap">Vue aérienne '
                 f'(imagerie publique, antérieure) : contour du lot estimé, angle Nord-Ouest de l’îlot</div>')
    for k, (p, cap) in enumerate(photos):
        corps += image(7 + 2 * k, 8 + 2 * k, 1, 2, p, cap)
    corps += bloc(7, 12, 3, 4, donnees([
        ("Parcelle", "20 × 33 m, 660 m² ; villa sur 360 m² au Nord, locatif sur 300 m² au Sud"),
        ("Rues", "rue Nord (accès villa) et rue Ouest (duplex), en latérite, non revêtues"),
        ("Contexte", "maisons R+1 / R+2 en béton brut ; en face, sur la rue Ouest, maisons de ville à toits rouges"),
    ]))
    add("01", "Site", "État des lieux", corps)
    # 3. references
    corps = (image(1, 4, 1, 3, UP / "da350794-image.jpg", "Référence 1 du client : lames de bois en damier, toiture mince")
             + image(5, 8, 1, 3, UP / "7cbdfd9c-image.jpg", "Référence 2 du client : bardage, grands débords, claustra béton")
             + bloc(9, 12, 1, 3, donnees([
                 ("V1", "peau de lames en damier, toiture plate mince"),
                 ("V2", "bardage et brise-soleil, toit en croupe à sous-face bois"),
                 ("Commun", "socle en moellons, claustra béton, patio planté (Casa Lineal, Palinda Kannangara)"),
             ])))
    add("02", "Références", "Images du client, références de style", corps)
    # 4. parti : trame et harmonie
    corps = (image(1, 9, 1, 4, IA / "aerien_V1.jpg", "Vue d’ambiance, variante 1 : villa et duplex sous une même écriture")
             + bloc(10, 12, 1, 4, donnees([
                 ("Horizontales", "±0,00, +3,30, +6,60, couverture +9,00 ; linteaux 2,40"),
                 ("Verticales", "baies de l’étage au droit de celles du RDC, sur les axes"),
                 ("Matières", "socle en moellons, étage dans une même peau bois, poteaux acier noirs"),
                 ("Limites", "mur végétalisé de 3,50 m entre villa et duplex"),
             ])))
    add("03", "Parti", "Une trame commune", corps)
    # 5-7. plans de la villa
    data_plan = {
        "RDC": [("Clos", f"{fr(s['RDC'], 1)} m²"), ("Trame", "2,5 · 3 · 3,5 · 3,5 · 2 · 3,5 · 2 m"),
                ("Markup", "cuisine sur l’axe 5, porte vers la terrasse supprimée, 2 places, bassins supprimés")],
        "R+1": [("Clos", f"{fr(s['R+1'], 1)} m²"), ("Plan", "en L : salon familial et chambres 1, 2 sur la rue, chambre principale au fond"),
                ("Peau", "lames de bois sur les quatre faces de l’étage")],
        "TOIT": [("Toit-terrasse", "110,3 m², couvert à +9,00"), ("Jardinière", "plantation basse, sans retombées"),
                 ("Tirets", "rive de la couverture V1")],
    }
    for n, niv, titre in (("04", "RDC", "Plan du rez-de-chaussée"), ("05", "R+1", "Plan de l’étage"), ("06", "TOIT", "Plan du niveau haut")):
        corps = (dessin(1, 9, 1, 4, plan_svg(PC.villa(niv, sid=f"p{n}")), titre, "/ échelle graphique, 1:100 env. en A3")
                 + bloc(10, 12, 1, 3, donnees(data_plan[niv])))
        add(n, "Villa", titre, corps)
    # 8. coupes
    corps = (dessin(1, 9, 1, 2, coupe_AA("V1"), "Coupe AA", "/ Nord-Sud, salle à manger, chambre 1, patio, mur végétalisé")
             + dessin(1, 9, 3, 4, coupe_BB("V1"), "Coupe BB", "/ Est-Ouest, salon, chambre principale, patio, chambre nounou")
             + bloc(10, 12, 1, 2, donnees([("Niveaux", "±0,00 · +3,30 · +6,60 · +9,00 (cotes du client)"),
                                           ("Bassins", "supprimés")])))
    add("07", "Villa", "Coupes", corps)
    # 9-11. facades
    corps = (dessin(1, 9, 1, 2, elev_N("V1"), "Élévation Nord, V1", "/ lames de bois en damier")
             + dessin(1, 9, 3, 4, elev_N("V2"), "Élévation Nord, V2", "/ bardage et brise-soleil")
             + bloc(10, 12, 1, 2, donnees([("Axes", "6,5 · 10,75 · 13,5 · 16,25"), ("Guérite", "à la hauteur de la clôture, 2,30 m")])))
    add("08", "Façades", "Rue Nord", corps)
    corps = (dessin(1, 12, 1, 2, elev_O("V1"), "Élévation Ouest, V1", "/ sur la rue : villa à gauche, duplex à droite")
             + dessin(1, 12, 3, 4, elev_O("V2"), "Élévation Ouest, V2", "/ même trame, même couverture"))
    add("09", "Façades", "Rue Ouest, villa et duplex", corps)
    corps = (dessin(1, 6, 1, 2, elev_S("V1"), "Élévation Sud, V1", "/ sur le mur végétalisé")
             + dessin(7, 12, 1, 2, elev_E("V1"), "Élévation Est, V1", "/ passage de service")
             + dessin(1, 6, 3, 4, elev_S("V2"), "Élévation Sud, V2", "")
             + dessin(7, 12, 3, 4, elev_E("V2"), "Élévation Est, V2", ""))
    add("10", "Façades", "Sud et Est", corps)
    # 12. details de facade
    corps = dessin(1, 12, 1, 4, details_svg(), "Détails de façade", "/ principes constructifs, sans échelle")
    add("11", "Détails", "Peau de l’étage, couverture", corps)
    # 13-15. ambiances
    corps = (image(1, 6, 2, 3, IA / "arrivee_V1.jpg", "Vue d’ambiance · rue Nord, V1, à la tombée de la nuit")
             + image(7, 12, 2, 3, IA / "arrivee_V2.jpg", "Vue d’ambiance · rue Nord, V2, après la pluie"))
    add("12", "Ambiances", "Rue Nord", corps)
    corps = (image(1, 6, 2, 3, IA / "angle_V1.jpg", "Vue d’ambiance · angle des deux rues, V1")
             + image(7, 12, 2, 3, IA / "angle_V2.jpg", "Vue d’ambiance · angle des deux rues, V2, saison des pluies"))
    add("13", "Ambiances", "Angle Nord-Ouest", corps)
    corps = (image(1, 6, 2, 3, IA / "patio.jpg", "Vue d’ambiance · le patio depuis la terrasse couverte")
             + image(7, 12, 2, 3, IA / "toit_V2.jpg", "Vue d’ambiance · le toit-terrasse couvert, V2"))
    add("14", "Ambiances", "Patio et toit", corps)
    # 16-19. locatif
    data_m = {
        "RDC": [("Maisons", "2 duplex de 153,0 m², 8,5 m de façade"), ("Trame", "3 · 8,5 · 8,5 m ; 3 · 6,5 · 2,5 · 3 m"),
                ("Stationnement", "2 places longitudinales dans la bande Ouest, portails sur la rue")],
        "R+1": [("Étage", "chambre principale avec dressing et salle de bains, chambre 2, salle d’eau"),
                ("Peau", "la même que la villa")],
        "TOIT": [("Toit-terrasse", "67,5 m² par maison, couvert à +9,00"), ("Couverture", "la même que la villa")],
    }
    for n, niv, titre in (("15", "RDC", "Plan du rez-de-chaussée"), ("16", "R+1", "Plan de l’étage"), ("17", "TOIT", "Plan du niveau haut")):
        corps = (dessin(1, 9, 1, 4, plan_svg(PC.maisons(niv, sid=f"m{n}")), titre, "/ échelle graphique")
                 + bloc(10, 12, 1, 3, donnees(data_m[niv])))
        add(n, "Duplex", titre, corps)
    corps = (dessin(1, 6, 1, 2, coupe_CC(), "Coupe CC", "/ Nord-Sud sur la maison 1")
             + dessin(7, 12, 1, 2, elev_LN("V1"), "Élévation Nord des duplex, V1", "/ sur les jardins")
             + image(1, 6, 3, 4, IA / "locatif_V1.jpg", "Vue d’ambiance · les duplex depuis la rue Ouest, V1")
             + image(7, 12, 3, 4, IA / "locatif_V2.jpg", "Vue d’ambiance · les duplex depuis la rue Ouest, V2"))
    add("18", "Duplex", "Coupe, façade, ambiances", corps)
    # 20. surfaces
    corps = (bloc(1, 4, 1, 4, tableau_surf(C, ("RDC", "R+1", "TOIT"), "VILLA"))
             + bloc(5, 8, 1, 4, tableau_surf({"pieces": [p for p in LOCATIF_M["pieces"] if p.get("logement") in (None, "M1")]},
                                             ("RDC", "R+1", "TOIT"), "MAISON 1"))
             + bloc(9, 12, 1, 2, donnees([("Villa, clos", f"{fr(s['clos'], 1)} m²"), ("Villa, emprise", f"{fr(s['emprise'], 1)} m²"),
                                          ("Duplex, clos", f"2 × 153,0 = {fr(sm['clos'], 1)} m²"),
                                          ("Loyer duplex", f"{LOYERS['MD']['nu'] // 1000} 000 FCFA / mois, hypothèse")])))
    add("19", "Surfaces", "Calculées sur le modèle", corps)
    # 21-22. estimatif
    for n, opt, titre in (("20", C, "Villa"), ("21", LOCATIF_M, "Duplex")):
        rows = lignes(opt)
        half = (len(rows) + 1) // 2
        corps = (bloc(1, 6, 1, 4, table_estim(rows[:half])) + bloc(7, 12, 1, 4, table_estim(rows[half:])))
        add(n, "Estimatif", f"{titre} · Éco-données ÷ {DIVISEUR}, FCFA", corps)
    # 23. suite
    corps = bloc(1, 6, 1, 3, donnees([
        ("Villa", f"travaux {fr(b['travaux'] / 1e6, 1)} M HT · {fr(b['total_ttc'] / 1e6, 1)} M TTC"),
        ("Duplex", f"travaux {fr(bm['travaux'] / 1e6, 1)} M HT · {fr(bm['total_ttc'] / 1e6, 1)} M TTC"),
        ("À arbitrer", "variante de façade V1 ou V2 ; stationnement longitudinal des duplex ; loyer à confirmer"),
        ("À vérifier", "R+1 maximum : le niveau couvert à +9,00 est un toit-terrasse ouvert, à faire valider"),
        ("Hors dossier", "esquisse, estimatif Excel et business plan 01 à 03 : versions précédentes"),
    ]))
    add("22", "Suite", "Points à arbitrer", corps)
    html = (f'<!doctype html><html><head><meta charset="utf-8"><style>{police_css()}{CSS}</style></head><body>'
            + "".join(P) + "</body></html>")
    out_html = OUT / "05_Dossier_Option_C_v5_Lot1728.html"
    out_html.write_text(html, encoding="utf-8")
    to_pdf(out_html, OUT / "05_Dossier_Option_C_v5_Lot1728.pdf")
    print("pages", len(P))


if __name__ == "__main__":
    build()
