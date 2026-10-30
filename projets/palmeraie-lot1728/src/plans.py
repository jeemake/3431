"""Generation des plans d'esquisse en SVG a partir de projet.py."""
import math
from projet import (OPTION_A, OPTION_B, LOCATIF, PARCELLE, RECUL_NORD, RECUL_OUEST,
                    VILLA_Y, LOCATIF_Y)

INK = "#23262b"
MUTED = "#6b6f76"
LINE = "#c9c3b8"
FILL = {
    "jour": "#efe4d2", "nuit": "#dfe4ee", "eau": "#d6e8ec", "service": "#e6e3de",
    "circ": "#faf8f4", "ext": "#e5ecd9", "bois": "#e9d3b5", "patio": "#cfe0bf",
}
CAT = {
    "sejour": "jour", "cuisine": "jour", "chambre": "nuit", "eau": "eau", "dressing": "nuit",
    "service": "service", "circ": "circ", "escalier": "circ", "terrasse": "bois",
    "balcon": "bois", "toit_jard": "patio", "patio": "patio", "l_sejour": "jour",
    "l_chambre": "nuit", "l_eau": "eau", "l_kitch": "jour", "l_circ": "circ",
    "l_coursive": "bois",
}

# Rotation du nord geographique par rapport a l'axe de la parcelle (B4 -> B1)
_b = PARCELLE["bornes"]
NORD_DEG = math.degrees(math.atan2(_b["B1"][0] - _b["B4"][0], _b["B1"][1] - _b["B4"][1]))


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;")


class Canvas:
    def __init__(self, x0, y0, x1, y1, s=26, pad=46):
        self.x0, self.y0, self.s, self.pad = x0, y0, s, pad
        self.w = (x1 - x0) * s + 2 * pad
        self.h = (y1 - y0) * s + 2 * pad
        self.el = []

    def X(self, x):
        return self.pad + (x - self.x0) * self.s

    def Y(self, y):
        return self.pad + (y - self.y0) * self.s

    def rect(self, x0, y0, x1, y1, fill="none", stroke=INK, sw=0.8, dash=None, extra=""):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.el.append(f'<rect x="{self.X(x0):.1f}" y="{self.Y(y0):.1f}" width="{(x1-x0)*self.s:.1f}" '
                       f'height="{(y1-y0)*self.s:.1f}" fill="{fill}" stroke="{stroke}" '
                       f'stroke-width="{sw}"{d} {extra}/>')

    def line(self, x0, y0, x1, y1, stroke=INK, sw=0.8, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.el.append(f'<line x1="{self.X(x0):.1f}" y1="{self.Y(y0):.1f}" x2="{self.X(x1):.1f}" '
                       f'y2="{self.Y(y1):.1f}" stroke="{stroke}" stroke-width="{sw}"{d}/>')

    def text(self, x, y, t, size=9, fill=INK, anchor="middle", weight=400, rot=0, italic=False):
        tr = f' transform="rotate({rot} {self.X(x):.1f} {self.Y(y):.1f})"' if rot else ""
        st = ' font-style="italic"' if italic else ""
        self.el.append(f'<text x="{self.X(x):.1f}" y="{self.Y(y):.1f}" font-size="{size}" fill="{fill}" '
                       f'text-anchor="{anchor}" font-weight="{weight}"{st}{tr} paint-order="stroke" '
                       f'stroke="#ffffff" stroke-opacity="0.85" stroke-width="2.6">{esc(t)}</text>')

    def raw(self, s):
        self.el.append(s)

    def svg(self):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w:.0f} {self.h:.0f}" '
                f'font-family="Inter, Liberation Sans, sans-serif" class="plan">'
                + "".join(self.el) + "</svg>")


def stairs(c, x0, y0, x1, y1, n=12, horizontal=True):
    """Hachures de marches (escalier a deux volees)."""
    if horizontal:
        mid = (y0 + y1) / 2
        step = (x1 - x0 - 0.9) / n
        for i in range(n + 1):
            xx = x0 + i * step
            c.line(xx, y0 + 0.05, xx, y1 - 0.05, stroke=MUTED, sw=0.5)
        c.line(x0, mid, x1 - 0.9, mid, stroke=MUTED, sw=0.6)


def north_arrow(c, x, y, r=0.9):
    a = math.radians(-NORD_DEG)
    cx, cy = c.X(x), c.Y(y)
    R = r * c.s
    tip = (cx + R * math.sin(a), cy - R * math.cos(a))
    left = (cx + 0.35 * R * math.sin(a - 2.4), cy - 0.35 * R * math.cos(a - 2.4))
    right = (cx + 0.35 * R * math.sin(a + 2.4), cy - 0.35 * R * math.cos(a + 2.4))
    c.raw(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{R:.1f}" fill="none" stroke="{MUTED}" stroke-width="0.6"/>')
    c.raw(f'<polygon points="{tip[0]:.1f},{tip[1]:.1f} {left[0]:.1f},{left[1]:.1f} {cx:.1f},{cy:.1f} '
          f'{right[0]:.1f},{right[1]:.1f}" fill="{INK}"/>')
    c.raw(f'<text x="{tip[0] + 6 * math.sin(a):.1f}" y="{tip[1] - 6 * math.cos(a) - 2:.1f}" font-size="10" '
          f'text-anchor="middle" font-weight="600" fill="{INK}">N</text>')


def label_room(c, r, small=False):
    xs = [(x0, y0, x1, y1) for x0, y0, x1, y1 in r["rects"]]
    # plus grand rectangle pour l'etiquette
    x0, y0, x1, y1 = max(xs, key=lambda q: (q[2] - q[0]) * (q[3] - q[1]))
    w, h = x1 - x0, y1 - y0
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    name = r["nom"]
    if "logement" in r:
        name = name.split(" ", 1)[1]
    size = 8.2 if not small else 7.2
    longest = max(len(wd) for wd in name.split(" "))
    while size > 5.8 and longest * size * 0.58 > w * c.s - 4:
        size -= 0.4
    vertical = h > w * 1.2 and w < 2.0
    if w < 1.3 and h < 1.3:
        return
    if vertical:
        c.text(cx + 0.12, cy, f"{name}  {r['surface']:.2f} m²", size=min(size, 7.4), rot=-90)
        return
    words = name.split(" ")
    lines, cur = [], ""
    maxch = max(6, int(w * c.s / (size * 0.56)))
    for wd in words:
        if len(cur) + len(wd) + 1 > maxch and cur:
            lines.append(cur)
            cur = wd
        else:
            cur = (cur + " " + wd).strip()
    lines.append(cur)
    lh = size * 1.15 / c.s
    top = cy - (len(lines)) * lh / 2 + lh * 0.6
    for i, ln in enumerate(lines):
        c.text(cx, top + i * lh, ln, size=size, weight=500)
    c.text(cx, top + len(lines) * lh, f"{r['surface']:.2f} m²", size=size - 1, fill=MUTED)


def draw_rooms(c, pieces, niveau, small=False, portes=None):
    rs = [r for r in pieces if r["niveau"] == niveau]
    for r in rs:
        cat = CAT[r["code"]]
        for x0, y0, x1, y1 in r["rects"]:
            dash = "3 2" if not r["clos"] else None
            c.rect(x0, y0, x1, y1, fill=FILL[cat], stroke=LINE if r["clos"] else MUTED,
                   sw=0.6, dash=dash)
        if r["code"] == "escalier":
            x0, y0, x1, y1 = r["rects"][0]
            if (x1 - x0) >= (y1 - y0):
                stairs(c, x0, y0, x1, y1)
            else:
                n = 12
                step = (y1 - y0 - 0.9) / n
                mid = (x0 + x1) / 2
                for i in range(n + 1):
                    c.line(x0 + 0.05, y0 + 0.9 + i * step, x1 - 0.05, y0 + 0.9 + i * step,
                           stroke=MUTED, sw=0.5)
                c.line(mid, y0 + 0.9, mid, y1, stroke=MUTED, sw=0.6)
    # murs exterieurs : contour epais des pieces closes
    for r in rs:
        if r["clos"]:
            for x0, y0, x1, y1 in r["rects"]:
                c.rect(x0, y0, x1, y1, stroke=INK, sw=0.9)
    for r in rs:
        if r["clos"] and len(r["rects"]) > 1:
            a, b = r["rects"][0], r["rects"][1]
            fill = FILL[CAT[r["code"]]]
            # arete commune horizontale
            if abs(a[1] - b[3]) < 1e-6 or abs(a[3] - b[1]) < 1e-6:
                yy = a[1] if abs(a[1] - b[3]) < 1e-6 else a[3]
                xa, xb = max(a[0], b[0]), min(a[2], b[2])
                c.line(xa + 0.04, yy, xb - 0.04, yy, stroke=fill, sw=2.2)
    if portes:
        draw_doors(c, portes, niveau)
    for r in rs:
        label_room(c, r, small)


def draw_doors(c, portes, niveau):
    for niv, x, y, sens, w in portes:
        if niv != niveau:
            continue
        if sens == "h":
            c.line(x - w / 2, y, x + w / 2, y, stroke="#ffffff", sw=3.2)
            c.line(x - w / 2, y - 0.12, x - w / 2, y + 0.12, stroke=INK, sw=1.0)
            c.line(x + w / 2, y - 0.12, x + w / 2, y + 0.12, stroke=INK, sw=1.0)
        else:
            c.line(x, y - w / 2, x, y + w / 2, stroke="#ffffff", sw=3.2)
            c.line(x - 0.12, y - w / 2, x + 0.12, y - w / 2, stroke=INK, sw=1.0)
            c.line(x - 0.12, y + w / 2, x + 0.12, y + w / 2, stroke=INK, sw=1.0)


def parcel_frame(c, y0, y1, streets=True, recul=True):
    c.rect(0, y0, 20, y1, stroke=INK, sw=1.6, dash="10 3 2 3")
    if streets:
        if y0 == 0:
            c.text(10, y0 - 1.0, "RUE (voie Nord, non revêtue)", size=9, fill=MUTED, weight=600)
        c.text(-1.0, (y0 + y1) / 2, "RUE (voie Ouest)", size=9, fill=MUTED, rot=-90, weight=600)
    if recul and y0 == 0:
        c.line(0, RECUL_NORD, 20, RECUL_NORD, stroke="#b5653a", sw=0.6, dash="4 3")
        c.text(19.8, RECUL_NORD - 0.2, f"recul {RECUL_NORD:.0f} m", size=7, fill="#b5653a", anchor="end")
    if recul:
        c.line(RECUL_OUEST, max(y0, 0), RECUL_OUEST, y1, stroke="#b5653a", sw=0.6, dash="4 3")


def tree(c, x, y, r=1.1, fill="#a9c08f"):
    c.raw(f'<circle cx="{c.X(x):.1f}" cy="{c.Y(y):.1f}" r="{r * c.s:.1f}" fill="{fill}" '
          f'fill-opacity="0.55" stroke="#7c9566" stroke-width="0.6"/>')


def stones(c, pts):
    for x, y in pts:
        c.raw(f'<ellipse cx="{c.X(x):.1f}" cy="{c.Y(y):.1f}" rx="{0.32 * c.s:.1f}" ry="{0.22 * c.s:.1f}" '
              f'fill="#d8d2c6" stroke="{MUTED}" stroke-width="0.4"/>')


def cars(c, x0, y0, n, w=2.5, d=5.0, vertical=True):
    for i in range(n):
        if vertical:
            c.rect(x0 + i * w, y0, x0 + (i + 1) * w, y0 + d, stroke=MUTED, sw=0.5)
            c.raw(f'<rect x="{c.X(x0 + i * w + 0.35):.1f}" y="{c.Y(y0 + 0.5):.1f}" width="{1.8 * c.s:.1f}" '
                  f'height="{4.0 * c.s:.1f}" rx="6" fill="none" stroke="{LINE}" stroke-width="0.8"/>')
        else:
            c.rect(x0, y0 + i * w, x0 + d, y0 + (i + 1) * w, stroke=MUTED, sw=0.5)
            c.raw(f'<rect x="{c.X(x0 + 0.5):.1f}" y="{c.Y(y0 + i * w + 0.35):.1f}" width="{4.0 * c.s:.1f}" '
                  f'height="{1.8 * c.s:.1f}" rx="6" fill="none" stroke="{LINE}" stroke-width="0.8"/>')


def villa_exterieurs(c, opt, niveau):
    # parking + portail
    cars(c, 7.9, 0.0, 3)
    c.text(11.65, -0.25, "portail coulissant 7,5 m · 3 places", size=7, fill=MUTED)
    # roji : pas japonais du portillon au genkan
    stones(c, [(5.6, 0.6), (5.9, 1.5), (6.4, 2.4), (6.8, 3.4), (7.2, 4.4)])
    c.text(5.6, -0.25, "portillon", size=7, fill=MUTED)
    c.text(17.6, 1.4, "claustras", size=6.5, fill=MUTED)
    c.line(15.4, 2.0, 20.0, 2.0, stroke=MUTED, sw=1.6, dash="1 1.5")
    c.line(15.4, 2.0, 15.4, 5.0, stroke=MUTED, sw=1.6, dash="1 1.5")
    # jardin d'entree
    tree(c, 2.4, 2.4, 1.3)
    # jardin
    if opt["code"] == "A":
        tree(c, 5.0, 16.0, 1.6)
        tree(c, 9.6, 16.4, 1.2, "#c4d4a8")
        tree(c, 1.4, 9.0, 1.1)
        c.text(7.2, 15.5, "JARDIN-COUR (niwa)", size=9, fill="#4f6b3a", weight=600)
        c.text(7.2, 16.2, "abrité N/E, ouvert aux vents SO", size=7, fill="#4f6b3a")
        c.text(7.2, 16.8, "≈ 78 m² en L + jardin d'entrée", size=7, fill="#4f6b3a")
    else:
        tree(c, 4.0, 16.0, 1.6)
        tree(c, 11.0, 16.5, 1.3, "#c4d4a8")
        tree(c, 17.6, 15.8, 1.2)
        tree(c, 1.4, 9.0, 1.1)
        c.text(8.0, 15.4, "JARDIN (niwa)", size=9, fill="#4f6b3a", weight=600)
        c.text(8.0, 16.1, "d'un seul tenant en L : 20 x 4 m + 3,2 m à l'Ouest", size=7, fill="#4f6b3a")
        c.text(8.0, 16.7, "≈ 109 m² + jardin d'entrée", size=7, fill="#4f6b3a")
    c.line(0, 18, 20, 18, stroke=INK, sw=1.2)
    c.text(10, 18.55, "mur séparatif + haie de bambous (vers parcelle locative)", size=7, fill=MUTED)


def plan_villa(opt, niveau, s=24):
    c = Canvas(-1.6, -1.6, 21.0, 19.2, s=s, pad=18)
    parcel_frame(c, 0, 18)
    if niveau == "RDC":
        villa_exterieurs(c, opt, niveau)
    else:
        # emprise RDC en pointille
        for r in opt["pieces"]:
            if r["niveau"] == "RDC" and r["clos"]:
                for x0, y0, x1, y1 in r["rects"]:
                    c.rect(x0, y0, x1, y1, fill="#f4f1ec", stroke=LINE, sw=0.4, dash="2 2")
        if opt["code"] == "A":
            c.rect(14.0, 10.4, 20.0, 18.0, fill=FILL["patio"], stroke=MUTED, sw=0.5, dash="3 2")
            c.rect(18.1, 5.0, 20.0, 10.4, fill=FILL["patio"], stroke=MUTED, sw=0.5, dash="3 2")
            c.text(19.05, 7.6, "jardinière 1,9 m", size=6.5, fill="#4f6b3a", rot=-90)
            c.text(17.0, 16.3, "toiture végétalisée", size=7.5, fill="#4f6b3a")
            c.text(17.0, 16.9, "(non accessible)", size=7, fill="#4f6b3a")
    draw_rooms(c, opt["pieces"], niveau, portes=opt["portes"])
    north_arrow(c, 19.6, 1.4, 0.7)
    return c.svg()


def plan_locatif(niveau, s=24):
    c = Canvas(-1.6, 17.2, 21.0, 34.4, s=s, pad=18)
    parcel_frame(c, 18, 33)
    c.line(RECUL_OUEST, 18, RECUL_OUEST, 33, stroke="#b5653a", sw=0.6, dash="4 3")
    if niveau == "RDC":
        cars(c, 0.2, 20.0, 5, vertical=False)
        c.text(3.9, 19.3, "portillon", size=7, fill=MUTED)
        c.text(2.6, 33.0 - 0.15, "5 places", size=7, fill=MUTED)
        stones(c, [(11.6, 19.6), (13.2, 19.8), (14.8, 19.6), (16.4, 19.8), (18.0, 19.6)])
        c.text(14.0, 18.75, "cour commune plantée (roji) – bambous le long du mur", size=7, fill="#4f6b3a")
        for x in (8.3, 12.8, 17.3):
            c.rect(x - 1.5, 20.8, x + 1.5, 22.0, fill=FILL["patio"], stroke=MUTED, sw=0.4, dash="2 2")
        c.text(12.8, 20.55, "terrasses privées sous coursive", size=6.5, fill="#4f6b3a")
    else:
        c.rect(0.2, 20.0, 5.2, 32.5, fill="#f4f1ec", stroke=LINE, sw=0.4, dash="2 2")
    pieces = [r for r in LOCATIF["pieces"] if not (niveau == "R+1" and r["nom"].startswith("Patios"))]
    draw_rooms(c, pieces, niveau, small=True, portes=LOCATIF["portes"])
    if niveau == "R+1":
        stairs_v = [r for r in LOCATIF["pieces"] if r["nom"] == "Escalier extérieur"][0]
        x0, y0, x1, y1 = stairs_v["rects"][0]
        c.rect(x0, y0, x1, y1, fill=FILL["circ"], stroke=INK, sw=0.9)
        c.text((x0 + x1) / 2, y0 - 0.25, "vide sur escalier (garde-corps plein côté villa)", size=6.5, fill=MUTED)
    # etiquettes logements
    for code, typ, x0, x1 in [("2P-a", "2P", 5.6, 11.0), ("T1-a", "T1bis", 11.0, 14.6),
                              ("2P-b", "2P", 14.6, 20.0)]:
        sl = 48.6 if typ == "2P" else 32.4
        lbl = "2 pièces" if typ == "2P" else "T1 bis"
        c.text((x0 + x1) / 2, 22.55, f"{lbl} - {sl:.1f} m²", size=7.6, weight=700, fill="#2f4a6d")
    for xx in (11.0, 14.6):
        c.line(xx, 22.0, xx, 31.0, stroke=INK, sw=1.8)
    north_arrow(c, 19.6, 19.0, 0.6)
    return c.svg()


def plan_masse(opt, s=15):
    c = Canvas(-2.4, -2.4, 22.0, 34.6, s=s, pad=14)
    c.rect(-2.4, -2.4, 22.0, 0, fill="#ece7dd", stroke="none")
    c.rect(-2.4, -2.4, 0, 34.6, fill="#ece7dd", stroke="none")
    c.text(11, -0.9, "RUE NORD", size=8, fill=MUTED, weight=600)
    c.text(-1.0, 16, "RUE OUEST", size=8, fill=MUTED, weight=600, rot=-90)
    c.rect(0, 0, 20, 33, fill="#f0f3ea", stroke=INK, sw=1.4)
    c.line(0, 18, 20, 18, stroke=INK, sw=1.0, dash="5 3")
    for r in opt["pieces"] + LOCATIF["pieces"]:
        if r["niveau"] != "RDC":
            continue
        for x0, y0, x1, y1 in r["rects"]:
            fill = "#cdbfa8" if r["clos"] else "#e9d3b5"
            if r["code"] in ("patio",):
                fill = "#cfe0bf"
            c.rect(x0, y0, x1, y1, fill=fill, stroke="none")
    # contours batis
    for r in opt["pieces"] + LOCATIF["pieces"]:
        if r["niveau"] == "RDC" and r["clos"]:
            for x0, y0, x1, y1 in r["rects"]:
                c.rect(x0, y0, x1, y1, stroke="#8c7f6c", sw=0.4)
    cars(c, 7.9, 0, 3)
    cars(c, 0.2, 20.0, 5, vertical=False)
    c.text(10, 9.0, "VILLA 360 m²", size=9, weight=700)
    c.text(12.8, 27.0, "LOCATIF 300 m²", size=9, weight=700)
    north_arrow(c, 21.0, 1.4, 0.8)
    return c.svg()


def plan_site(s=15):
    """Analyse de site : parcelle, voies, soleil, vents, decoupage."""
    c = Canvas(-5.0, -5.0, 25.0, 36.0, s=s, pad=10)
    c.rect(-5, -5, 25, 0, fill="#ece7dd", stroke="none")
    c.rect(-5, -5, 0, 36, fill="#ece7dd", stroke="none")
    c.text(10, -2.2, "RUE (Nord) – voie en terre", size=8.5, fill=MUTED, weight=600)
    c.text(-2.4, 7.0, "RUE (Ouest) – voie en terre", size=8.5, fill=MUTED, weight=600, rot=-90)
    c.text(22.6, 16.5, "Lot 1730", size=8, fill=MUTED, rot=90)
    c.text(10, 34.6, "Parcelle voisine (Sud)", size=8, fill=MUTED)
    c.rect(0, 0, 20, 18, fill="#efe4d2", stroke="none")
    c.rect(0, 18, 20, 33, fill="#dfe4ee", stroke="none")
    c.rect(0, 0, 20, 33, stroke=INK, sw=1.6)
    c.line(0, 18, 20, 18, stroke=INK, sw=0.9, dash="6 3")
    c.text(10, 8.6, "PARCELLE VILLA", size=10, weight=700)
    c.text(10, 9.6, "20,00 x 18,00 = 360 m²", size=8.5, fill=MUTED)
    c.text(10, 25.3, "PARCELLE LOCATIVE", size=10, weight=700)
    c.text(10, 26.3, "20,00 x 15,00 = 300 m²", size=8.5, fill=MUTED)
    for n, (x, y) in {"B1": (0, 0), "B2": (20, 0), "B3": (20, 33), "B4": (0, 33)}.items():
        c.raw(f'<circle cx="{c.X(x):.1f}" cy="{c.Y(y):.1f}" r="3" fill="{INK}"/>')
        c.text(x + (-0.6 if x == 0 else 0.6), y + (-0.4 if y == 0 else 0.9), n, size=8,
               anchor="end" if x == 0 else "start", weight=600)
    c.text(10, 0.9, "20,00", size=8, fill=MUTED)
    c.text(19.2, 30.0, "33,00", size=8, fill=MUTED, rot=90)
    c.line(0, RECUL_NORD, 20, RECUL_NORD, stroke="#b5653a", sw=0.7, dash="4 3")
    c.line(RECUL_OUEST, 0, RECUL_OUEST, 33, stroke="#b5653a", sw=0.7, dash="4 3")
    c.text(10, RECUL_NORD - 0.3, "recul hyp. 5 m", size=7, fill="#b5653a")
    # vents dominants SO
    for i, (x, y) in enumerate([(-3.4, 31.0), (-3.4, 27.0), (-3.4, 23.0)]):
        c.raw(f'<line x1="{c.X(x):.1f}" y1="{c.Y(y):.1f}" x2="{c.X(x + 3.2):.1f}" y2="{c.Y(y - 2.6):.1f}" '
              f'stroke="#2f4a6d" stroke-width="1.4" marker-end="url(#arr)"/>')
    c.text(-4.6, 21.2, "vents dominants", size=7.5, fill="#2f4a6d", anchor="start")
    c.text(-4.6, 21.9, "SO (mousson)", size=7.5, fill="#2f4a6d", anchor="start")
    # course solaire (lat. 5 N) - schematique : arc E -> O passant pres du zenith, cote Sud
    c.raw(f'<path d="M {c.X(23.5):.1f} {c.Y(14):.1f} Q {c.X(10):.1f} {c.Y(18.5):.1f} {c.X(-3.5):.1f} {c.Y(14):.1f}" '
          f'fill="none" stroke="#c98a2b" stroke-width="1.2" stroke-dasharray="5 3"/>')
    c.text(23.0, 13.2, "lever E", size=7.5, fill="#c98a2b")
    c.text(-4.6, 13.2, "coucher O", size=7.5, fill="#c98a2b", anchor="start")
    c.text(10, 13.3, "course solaire quasi zénithale (lat. 5° N)", size=7.5, fill="#c98a2b")
    c.text(10, 14.1, "déc. : soleil au Sud – juin : au Nord – protéger E et O", size=7, fill="#c98a2b")
    c.raw('<defs><marker id="arr" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">'
          '<path d="M0,0 L6,3 L0,6 z" fill="#2f4a6d"/></marker></defs>')
    north_arrow(c, 22.6, 2.0, 1.0)
    c.text(22.6, 4.0, f"N géo. à {NORD_DEG:.1f}°", size=7, fill=MUTED)
    # cloture existante
    c.rect(0, 0, 20, 33, stroke="#8c7f6c", sw=3.2, extra='stroke-opacity="0.25"')
    c.text(14.5, -0.35, "clôture + 2 portails existants", size=7, fill="#8c7f6c")
    return c.svg()


def coupe_B(s=26):
    """Coupe de principe N-S sur l'option B : ventilation, debords, engawa."""
    c = Canvas(-1.5, -1.0, 21.0, 9.8, s=s, pad=14)
    g = 8.5  # niveau sol
    Y = lambda z: g - z  # noqa: E731
    c.line(-1.5, Y(0), 21, Y(0), stroke=INK, sw=1.2)
    # socle +0,45
    c.rect(5.0, Y(0.45), 12.2, Y(0), fill="#d9d2c4", stroke=INK, sw=0.8)
    # RDC
    c.rect(5.0, Y(3.45), 12.2, Y(0.45), fill="#faf8f4", stroke=INK, sw=1.0)
    c.rect(5.0, Y(3.75), 12.2, Y(3.45), fill="#b8b2a6", stroke=INK, sw=0.6)
    # etage
    c.rect(5.0, Y(6.65), 12.2, Y(3.75), fill="#faf8f4", stroke=INK, sw=1.0)
    c.rect(5.0, Y(6.85), 12.2, Y(6.65), fill="#b8b2a6", stroke=INK, sw=0.6)
    # toiture debordante ventilee
    c.raw(f'<polygon points="{c.X(3.0):.1f},{c.Y(Y(6.95)):.1f} {c.X(8.6):.1f},{c.Y(Y(8.3)):.1f} '
          f'{c.X(14.2):.1f},{c.Y(Y(6.95)):.1f}" fill="none" stroke="{INK}" stroke-width="1.4"/>')
    c.text(14.6, Y(7.3), "toiture bac acier isolé + lame d'air ventilée, débords 1,8 m", size=7.5,
           fill=MUTED, anchor="start")
    # engawa
    c.rect(12.2, Y(0.45), 14.0, Y(0.2), fill="#e9d3b5", stroke=INK, sw=0.6)
    c.text(13.1, Y(0.75), "engawa", size=7.5)
    c.rect(12.2, Y(3.75), 13.4, Y(3.55), fill="#e9d3b5", stroke=INK, sw=0.6)
    c.text(12.8, Y(4.0), "balcon", size=7)
    c.line(14.0, Y(0.45), 14.0, Y(3.45), stroke=MUTED, sw=0.6, dash="3 2")
    # labels
    c.text(8.6, Y(2.0), "séjour traversant  HSP 3,00", size=8.5, weight=600)
    c.text(8.6, Y(5.2), "chambres traversantes + ranma", size=8.5, weight=600)
    # fleches ventilation (SO -> N)
    for z in (1.6, 4.9):
        c.raw(f'<line x1="{c.X(17.5):.1f}" y1="{c.Y(Y(z)):.1f}" x2="{c.X(1.0):.1f}" y2="{c.Y(Y(z)):.1f}" '
              f'stroke="#2f4a6d" stroke-width="1.1" stroke-dasharray="6 3" marker-end="url(#arr2)"/>')
    c.raw(f'<line x1="{c.X(8.6):.1f}" y1="{c.Y(Y(6.5)):.1f}" x2="{c.X(8.6):.1f}" y2="{c.Y(Y(8.8)):.1f}" '
          f'stroke="#b5653a" stroke-width="1.1" marker-end="url(#arr3)"/>')
    c.text(9.0, Y(8.9), "air chaud évacué en faîtage", size=7, fill="#b5653a", anchor="start")
    c.raw('<defs><marker id="arr2" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">'
          '<path d="M0,0 L6,3 L0,6 z" fill="#2f4a6d"/></marker>'
          '<marker id="arr3" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">'
          '<path d="M0,0 L6,3 L0,6 z" fill="#b5653a"/></marker></defs>')
    # soleil zenithal
    c.raw(f'<line x1="{c.X(16.5):.1f}" y1="{c.Y(Y(9.6)):.1f}" x2="{c.X(13.8):.1f}" y2="{c.Y(Y(6.95)):.1f}" '
          f'stroke="#c98a2b" stroke-width="1" stroke-dasharray="4 3"/>')
    c.text(16.7, Y(9.4), "soleil de midi (~75-85°)", size=7, fill="#c98a2b", anchor="start")
    # rue / jardin
    c.text(1.5, Y(-0.6), "RUE / parking (N)", size=7.5, fill=MUTED)
    c.text(17.0, Y(-0.6), "JARDIN (S)", size=7.5, fill="#4f6b3a")
    c.rect(0.0, Y(2.5), 0.25, Y(0), fill="#cdbfa8", stroke=INK, sw=0.6)
    c.text(0.1, Y(2.8), "clôture", size=6.5, fill=MUTED)
    c.rect(19.8, Y(2.5), 20.05, Y(0), fill="#cdbfa8", stroke=INK, sw=0.6)
    c.text(19.9, Y(2.8), "mur sép.", size=6.5, fill=MUTED)
    tree(c, 17.2, Y(3.2), 1.4)
    c.line(17.2, Y(1.8), 17.2, Y(0), stroke="#7c9566", sw=2)
    # cotes
    for z, t in ((0.45, "+0,45"), (3.75, "+3,75"), (6.85, "+6,85")):
        c.text(4.6, Y(z) + 0.1, t, size=7, fill=MUTED, anchor="end")
    return c.svg()


if __name__ == "__main__":
    import pathlib
    out = pathlib.Path(__file__).resolve().parent.parent / "out" / "svg"
    out.mkdir(parents=True, exist_ok=True)
    files = {
        "site.svg": plan_site(),
        "A_RDC.svg": plan_villa(OPTION_A, "RDC"), "A_R1.svg": plan_villa(OPTION_A, "R+1"),
        "B_RDC.svg": plan_villa(OPTION_B, "RDC"), "B_R1.svg": plan_villa(OPTION_B, "R+1"),
        "L_RDC.svg": plan_locatif("RDC"), "L_R1.svg": plan_locatif("R+1"),
        "masse_A.svg": plan_masse(OPTION_A), "masse_B.svg": plan_masse(OPTION_B),
        "coupe_B.svg": coupe_B(),
    }
    for n, s in files.items():
        (out / n).write_text(s)
    print("ok", NORD_DEG)
