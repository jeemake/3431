#!/usr/bin/env python3
"""Villa-atelier, San-Pedro (Cote d'Ivoire) - sketch-design drawing set generator.

Every drawing is produced from the same geometric model (metres, plot origin at
the street / north-west corner, x -> east, y -> south), so plans, sections,
elevations and the area schedule stay consistent.

    python3 villa-san-pedro/build.py  ->  villa-san-pedro/index.html
"""
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
LOGO = os.path.join(HERE, "logo-kda.b64")

# ---------------------------------------------------------------- palette (charte K&D)
NOIR, GRIS, VERT, GRIS_CL, GRIS_F = "#0B0C12", "#66747C", "#7AB648", "#F2F2F2", "#333333"
POCHE = "#3A3F44"
GARDEN = "#E6F0DC"
WATER = "#DCE6F1"
PAVING = "#F4F4F2"
FONT = '"Century Gothic", CenturyGothic, "Didact Gothic", sans-serif'

PLOT_W, PLOT_D = 25.0, 32.0
T_INT = 0.10      # half interior wall
T_EXT = 0.15      # exterior outset
FFL1 = 3.60       # R+1 finished floor
ROOF = 6.90       # roof slab top
ACRO = 7.20       # parapet top
GROUND = -0.45    # natural ground / street
SHED_LO, SHED_HI = 6.20, 7.80


def f(v):
    return f"{v:.3f}".rstrip("0").rstrip(".")


# ---------------------------------------------------------------- model
# room: (key, label, x1, y1, x2, y2, open_sides, group, zone)
GF_BLOCKS = [(0, 5, 9, 14), (0, 14, 22.5, 22), (18, 5, 22.5, 14)]
GF_ROOMS = [
    ("atelier", "SCULPTURE STUDIO", 0, 5, 9, 11.5, "s", "Sculpture studio (double height)", "art"),
    ("atelier_b", "", 5, 11.5, 9, 14, "n", "Sculpture studio (double height)", "art"),
    ("stock", "TOOLS / STOCK", 0, 11.5, 3.2, 14, "", "Tool & material store", "art"),
    ("wcat", "WC-SH.", 3.2, 11.5, 5, 14, "", "Studio WC + shower", "art"),
    ("gsde", "SH.", 0, 14, 2.5, 16.2, "", "Guest shower room", "day"),
    ("gdress", "DRESSING", 2.5, 14, 6.3, 16.2, "", "Guest dressing", "day"),
    ("guest", "GUEST / STUDY", 0, 16.2, 4.5, 22, "", "Guest room / study", "day"),
    ("wc", "WC", 4.5, 16.2, 6.3, 18, "", "Visitors' WC", "day"),
    ("stair", "", 6.3, 14, 9, 18, "", "Staircase", "circ"),
    ("lib", "LIBRARY", 4.5, 18, 9, 22, "", "Library / homework table", "day"),
    ("living", "LIVING / DINING", 9, 14, 17, 22, "", "Living + dining (through-room)", "day"),
    ("kitchen", "KITCHEN", 17, 14, 22.5, 19.5, "s", "Family kitchen + breakfast", "day"),
    ("kitchen_b", "", 17, 19.5, 19.5, 22, "n", "Family kitchen + breakfast", "day"),
    ("cellier", "PANTRY", 19.5, 19.5, 22.5, 22, "", "Pantry", "serv"),
    ("ct", "IVORIAN KITCHEN", 18, 10.8, 22.5, 14, "", "Technical / Ivorian kitchen", "serv"),
    ("laundry", "LAUNDRY", 18, 8.6, 22.5, 10.8, "", "Laundry", "serv"),
    ("staff", "STAFF", 18, 5, 21, 8.6, "", "Staff room", "serv"),
    ("staffsh", "SH.", 21, 5, 22.5, 8.6, "", "Staff shower room", "serv"),
]
GF_MERGE = [(8.88, 18.12, 9.12, 21.88), (6.42, 17.88, 8.88, 18.12)]   # library-living, stair foot

R1_BLOCKS = [(0, 14, 22.5, 23)]
R1_ROOMS = [
    ("sdb1", "BATH", 0, 14, 2.25, 18, "", "Children's bathroom 1", "night"),
    ("sdb2", "BATH", 2.25, 14, 4.5, 18, "", "Children's bathroom 2", "night"),
    ("linen", "LINEN", 4.5, 14, 6.3, 18, "", "Linen + laundry chute", "serv"),
    ("stair", "", 6.3, 14, 9, 18, "", "Staircase", "circ"),
    ("family", "FAMILY ROOM", 9, 14, 14, 18, "s", "Family room / play", "night"),
    ("corr", "", 0, 18, 14, 19.2, "n", "Landing + corridor", "circ"),
    ("studio", "DRAWING STUDIO", 14, 14, 17.5, 18, "", "Drawing studio / parents' office", "night"),
    ("bathp", "PARENTS' BATH", 17.5, 14, 22.5, 18, "", "Parents' bathroom", "night"),
    ("e1", "CHILD 1", 0, 19.2, 3.5, 23, "", "Child bedroom 1", "night"),
    ("e2", "CHILD 2", 3.5, 19.2, 7, 23, "", "Child bedroom 2", "night"),
    ("e3", "CHILD 3", 7, 19.2, 10.5, 23, "", "Child bedroom 3", "night"),
    ("e4", "CHILD 4", 10.5, 19.2, 14, 23, "", "Child bedroom 4", "night"),
    ("dress", "DRESSING", 14, 18, 16.5, 23, "", "Walk-through dressing", "night"),
    ("master", "PARENTS", 16.5, 18, 22.5, 23, "", "Parents' bedroom", "night"),
]
R1_MERGE = []

OUTDOOR = [  # label, x1,y1,x2,y2, area-schedule label
    ("Covered entrance gallery", 9, 5, 11.4, 14),
    ("Sculpture patio", 11.4, 5, 18, 14),
    ("Covered terrace", 0, 22, 22.5, 24.5),
    ("Work yard (half covered)", 0, 0, 9, 5),
    ("Carport (2 cars)", 17, 0, 22.5, 5),
    ("Upper balcony", 0, 23, 22.5, 24.5),
    ("Pool 11 x 3 m", 7, 27.2, 18, 30.2),
    ("Matt's kennel + run", 22.7, 15, 24.9, 22),
]


def net_area(r):
    _, _, x1, y1, x2, y2, op, *_ = r
    w = (x2 - x1) - (0 if "w" in op else T_INT) - (0 if "e" in op else T_INT)
    h = (y2 - y1) - (0 if "n" in op else T_INT) - (0 if "s" in op else T_INT)
    return w * h


# ---------------------------------------------------------------- svg helpers
def rect(x1, y1, x2, y2, fill="none", stroke="none", sw=0.02, extra=""):
    return (f'<rect x="{f(x1)}" y="{f(y1)}" width="{f(x2-x1)}" height="{f(y2-y1)}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{f(sw)}" {extra}/>')


def line(x1, y1, x2, y2, stroke=NOIR, sw=0.02, extra=""):
    return (f'<line x1="{f(x1)}" y1="{f(y1)}" x2="{f(x2)}" y2="{f(y2)}" '
            f'stroke="{stroke}" stroke-width="{f(sw)}" {extra}/>')


def text(x, y, s, size=0.34, fill=NOIR, anchor="middle", weight="400", extra=""):
    return (f'<text x="{f(x)}" y="{f(y)}" font-size="{f(size)}" fill="{fill}" '
            f'text-anchor="{anchor}" font-weight="{weight}" {extra}>{s}</text>')


def circle(cx, cy, r, fill="none", stroke=NOIR, sw=0.02, extra=""):
    return f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r)}" fill="{fill}" stroke="{stroke}" stroke-width="{f(sw)}" {extra}/>'


def poly(pts, fill="none", stroke=NOIR, sw=0.02, extra=""):
    p = " ".join(f"{f(a)},{f(b)}" for a, b in pts)
    return f'<polygon points="{p}" fill="{fill}" stroke="{stroke}" stroke-width="{f(sw)}" {extra}/>'


def pline(pts, stroke=NOIR, sw=0.02, extra=""):
    p = " ".join(f"{f(a)},{f(b)}" for a, b in pts)
    return f'<polyline points="{p}" fill="none" stroke="{stroke}" stroke-width="{f(sw)}" {extra}/>'


def arc_sweep(cx, cy, sx, sy, ex, ey):
    a1 = math.atan2(sy - cy, sx - cx)
    a2 = math.atan2(ey - cy, ex - cx)
    d = (a2 - a1 + math.pi) % (2 * math.pi) - math.pi
    return 1 if d > 0 else 0


# opening on a wall segment ------------------------------------------------------------
def opening(kind, a1, a2, at, horiz, swing=1, hinge=0):
    """kind: door | slide | win | dbl.  Horizontal wall at y=at spans x a1..a2 (or vertical)."""
    out = []
    g = 0.17
    if horiz:
        out.append(rect(a1, at - g, a2, at + g, fill="#fff"))
    else:
        out.append(rect(at - g, a1, at + g, a2, fill="#fff"))

    def L(p, q, r, s, sw=0.018, st=NOIR):
        if horiz:
            out.append(line(p, q, r, s, st, sw))
        else:
            out.append(line(q, p, s, r, st, sw))

    if kind == "win":
        for d in (-0.1, 0, 0.1):
            L(a1, at + d, a2, at + d, 0.012)
        L(a1, at - 0.12, a1, at + 0.12, 0.02)
        L(a2, at - 0.12, a2, at + 0.12, 0.02)
    elif kind == "slide":
        m = (a1 + a2) / 2
        L(a1, at - 0.04, m + 0.15, at - 0.04, 0.03)
        L(m - 0.15, at + 0.04, a2, at + 0.04, 0.03)
        L(a1, at - 0.12, a1, at + 0.12, 0.02)
        L(a2, at - 0.12, a2, at + 0.12, 0.02)
    elif kind in ("door", "dbl"):
        leaves = [(a1, a2)] if kind == "door" else [(a1, (a1 + a2) / 2), (a2, (a1 + a2) / 2)]
        if kind == "door" and hinge:
            leaves = [(a2, a1)]
        for h, o in leaves:
            w = abs(o - h)
            if horiz:
                cx, cy = h, at
                lx, ly = h, at + swing * w
                ex, ey = o, at
            else:
                cx, cy = at, h
                lx, ly = at + swing * w, h
                ex, ey = at, o
            out.append(line(cx, cy, lx, ly, NOIR, 0.025))
            sw_ = arc_sweep(cx, cy, lx, ly, ex, ey)
            out.append(f'<path d="M{f(lx)},{f(ly)} A{f(w)},{f(w)} 0 0 {sw_} {f(ex)},{f(ey)}" '
                       f'fill="none" stroke="{GRIS}" stroke-width="0.012" stroke-dasharray="0.06 0.04"/>')
    return "".join(out)


GF_OPEN = [
    ("slide", 2.0, 5.6, 5, True), ("win", 6.2, 8.6, 5, True),
    ("door", 6.5, 7.7, 9, False, -1), ("win", 8.5, 11.0, 9, False),
    ("door", 1.0, 1.9, 11.5, True, -1), ("door", 3.6, 4.4, 11.5, True, -1),
    ("dbl", 9.4, 11.2, 14, True, 1),                      # front door from gallery
    ("slide", 11.8, 16.8, 14, True), ("slide", 9.3, 16.7, 22, True),
    ("slide", 5.0, 8.5, 22, True), ("slide", 1.0, 3.5, 22, True),
    ("door", 0.6, 1.4, 16.2, True, -1), ("door", 2.9, 3.8, 16.2, True, -1),
    ("door", 18.6, 19.5, 4.5, False, -1), ("door", 4.8, 5.6, 18, True, -1),
    ("door", 19.0, 19.9, 14, True, -1), ("slide", 15.2, 18.8, 17, False),
    ("slide", 17.3, 19.3, 22, True), ("door", 20.2, 21.0, 19.5, False, 1),
    ("win", 15.0, 18.5, 22.5, False),
    ("door", 11.4, 12.3, 22.5, False, 1), ("win", 11.6, 13.6, 18, False),
    ("door", 9.2, 10.1, 22.5, False, 1), ("door", 18.6, 19.4, 10.8, True, -1),
    ("door", 18.5, 19.4, 5, True, 1), ("win", 19.8, 20.7, 5, True),
    ("door", 7.3, 8.1, 21, False, 1), ("win", 6.0, 7.0, 22.5, False),
]
R1_OPEN = [
    ("door", 1.0, 1.8, 18, True, -1), ("door", 2.9, 3.7, 18, True, -1),
    ("door", 4.8, 5.6, 18, True, -1), ("win", 9.6, 13.4, 14, True),
    ("win", 14.4, 17.1, 14, True), ("door", 14.6, 15.5, 18, True, -1),
    ("win", 18.5, 21.5, 14, True), ("door", 18.2, 19.1, 18, True, -1),
    ("win", 15.0, 17.0, 22.5, False), ("door", 18.1, 19.0, 14, False, 1),
    ("door", 21.0, 21.9, 16.5, False, 1), ("slide", 17.3, 21.7, 23, True),
    ("win", 19.5, 21.5, 22.5, False),
]
for i, (x1, x2) in enumerate([(0, 3.5), (3.5, 7), (7, 10.5), (10.5, 14)]):
    R1_OPEN.append(("door", x2 - 1.1, x2 - 0.3, 19.2, True, 1))
    R1_OPEN.append(("slide", x1 + 0.5, x1 + 2.3, 23, True))


def stair_plan(level):
    o = []
    for x1, x2 in ((6.4, 7.6), (7.7, 8.9)):
        for i in range(10):
            y = 15.4 + i * 0.28
            o.append(line(x1, y, x2, y, NOIR, 0.012))
        o.append(rect(x1, 15.4, x2, 17.92, stroke=NOIR, sw=0.015))
    o.append(rect(6.4, 14.2, 8.9, 15.4, stroke=NOIR, sw=0.015))
    if level == 0:
        o.append(pline([(8.3, 17.8), (8.3, 14.8), (7.0, 14.8), (7.0, 16.2)], GRIS, 0.02))
        o.append(line(6.4, 16.6, 8.9, 16.0, NOIR, 0.03))
        o.append(text(8.3, 18.05 + 0.2, "UP", 0.22, GRIS))
    else:
        o.append(pline([(7.0, 17.8), (7.0, 14.8), (8.3, 14.8), (8.3, 16.2)], GRIS, 0.02))
        o.append(text(7.0, 18.05 + 0.25, "DN", 0.22, GRIS))
    return "".join(o)


def tree(cx, cy, r, fill=VERT):
    return (circle(cx, cy, r, fill=fill, stroke=VERT, sw=0.03, extra='fill-opacity="0.18"')
            + circle(cx, cy, r * 0.12, fill=VERT, stroke="none"))


def dims_h(y, xs, label_off=-0.25):
    o = [line(xs[0], y, xs[-1], y, GRIS, 0.015)]
    for x in xs:
        o.append(line(x - 0.12, y + 0.12, x + 0.12, y - 0.12, GRIS, 0.025))
        o.append(line(x, y - 0.25, x, y + 0.25, GRIS, 0.01))
    for a, b in zip(xs, xs[1:]):
        o.append(text((a + b) / 2, y + label_off, f"{b-a:.2f}", 0.28, GRIS))
    return "".join(o)


def dims_v(x, ys):
    o = [line(x, ys[0], x, ys[-1], GRIS, 0.015)]
    for y in ys:
        o.append(line(x - 0.12, y + 0.12, x + 0.12, y - 0.12, GRIS, 0.025))
        o.append(line(x - 0.25, y, x + 0.25, y, GRIS, 0.01))
    for a, b in zip(ys, ys[1:]):
        m = (a + b) / 2
        o.append(text(x - 0.25, m, f"{b-a:.2f}", 0.28, GRIS,
                      extra=f'transform="rotate(-90 {f(x-0.25)} {f(m)})"'))
    return "".join(o)


def north_arrow(cx, cy):
    return (circle(cx, cy, 0.9, stroke=GRIS, sw=0.03)
            + poly([(cx, cy - 0.85), (cx + 0.35, cy + 0.5), (cx, cy + 0.25), (cx - 0.35, cy + 0.5)], fill=NOIR, stroke="none")
            + text(cx, cy - 1.1, "N", 0.42, NOIR, weight="700"))


def wind_arrow(cx, cy):
    # prevailing SW sea breeze (Gulf of Guinea) blowing towards NE
    o = []
    for d in (-0.5, 0, 0.5):
        x0, y0 = cx - 1.2 + d, cy + 1.2 + d
        o.append(line(x0, y0, x0 + 1.4, y0 - 1.4, VERT, 0.05, 'marker-end="url(#arrG)"'))
    o.append(text(cx + 0.3, cy + 2.6, "SW SEA BREEZE", 0.3, VERT, weight="700"))
    return "".join(o)


def section_mark(x1, y1, x2, y2, letter, dx, dy):
    o = [line(x1, y1, x2, y2, NOIR, 0.035, 'stroke-dasharray="0.6 0.15 0.1 0.15"')]
    for (x, y) in ((x1, y1), (x2, y2)):
        o.append(circle(x, y, 0.42, fill="#fff", stroke=NOIR, sw=0.03))
        o.append(text(x, y + 0.14, letter, 0.4, NOIR, weight="700"))
        o.append(poly([(x + dx * 0.95, y + dy * 0.95), (x + dx * 0.5 - dy * 0.3, y + dy * 0.5 - dx * 0.3),
                       (x + dx * 0.5 + dy * 0.3, y + dy * 0.5 + dx * 0.3)], fill=NOIR, stroke="none"))
    return "".join(o)


def dog_plan(x, y):
    return (f'<ellipse cx="{f(x)}" cy="{f(y)}" rx="0.38" ry="0.16" fill="{GRIS}"/>'
            + circle(x + 0.42, y - 0.02, 0.12, fill=GRIS, stroke="none"))


def walls(blocks, rooms, merges):
    o = []
    for (x1, y1, x2, y2) in blocks:
        o.append(rect(x1 - T_EXT, y1 - T_EXT, x2 + T_EXT, y2 + T_EXT, fill=POCHE))
    for r in rooms:
        _, _, x1, y1, x2, y2, op, *_ = r
        a = x1 + (-T_INT if "w" in op else T_INT)
        b = y1 + (-T_INT if "n" in op else T_INT)
        c = x2 - (-T_INT if "e" in op else T_INT)
        d = y2 - (-T_INT if "s" in op else T_INT)
        o.append(rect(a, b, c, d, fill="#fff"))
    for m in merges:
        o.append(rect(*m, fill="#fff"))
    return "".join(o)


def labels(rooms, merged_area):
    o = []
    for r in rooms:
        key, lab, x1, y1, x2, y2, op, grp, _ = r
        if not lab:
            continue
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        a = merged_area.get(grp, net_area(r))
        size = 0.32 if (x2 - x1) > 2.4 else 0.24
        if key == "atelier":
            cy = 8.6
        if key == "living":
            cy = 15.6; cx = 12.2
        if key == "kitchen":
            cy = 15.0; cx = 19.2
        if key == "family":
            cy = 15.0
        o.append(text(cx, cy, lab, size, NOIR, weight="700", extra='letter-spacing="0.02"'))
        o.append(text(cx, cy + size * 1.15, f"{a:.1f} m²", size * 0.85, GRIS))
    return "".join(o)


def group_areas(rooms):
    g = {}
    for r in rooms:
        g[r[7]] = g.get(r[7], 0) + net_area(r)
    return g


DEFS = f'''<defs>
<marker id="arrG" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{VERT}"/></marker>
<marker id="arrK" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{NOIR}"/></marker>
<pattern id="hatchEarth" width="0.4" height="0.4" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="0.4" stroke="{GRIS}" stroke-width="0.02"/></pattern>
<pattern id="gravel" width="0.5" height="0.5" patternUnits="userSpaceOnUse"><circle cx="0.12" cy="0.15" r="0.03" fill="{GRIS}" opacity="0.5"/><circle cx="0.37" cy="0.38" r="0.025" fill="{GRIS}" opacity="0.5"/></pattern>
<pattern id="btc" width="0.6" height="0.3" patternUnits="userSpaceOnUse"><rect width="0.6" height="0.3" fill="#EFE9E1"/><line x1="0" y1="0.3" x2="0.6" y2="0.3" stroke="#C9BFB2" stroke-width="0.015"/><line x1="0.3" y1="0" x2="0.3" y2="0.15" stroke="#C9BFB2" stroke-width="0.015"/><line x1="0" y1="0.15" x2="0.6" y2="0.15" stroke="#C9BFB2" stroke-width="0.015"/><line x1="0.0" y1="0.15" x2="0.0" y2="0.3" stroke="#C9BFB2" stroke-width="0.015"/></pattern>
<pattern id="claustra" width="0.3" height="0.3" patternUnits="userSpaceOnUse"><rect width="0.3" height="0.3" fill="#fff"/><rect x="0.06" y="0.06" width="0.18" height="0.18" fill="none" stroke="{GRIS}" stroke-width="0.02"/></pattern>
<pattern id="slats" width="0.14" height="1" patternUnits="userSpaceOnUse"><rect width="0.14" height="1" fill="#fff"/><line x1="0.07" y1="0" x2="0.07" y2="1" stroke="{GRIS}" stroke-width="0.03"/></pattern>
</defs>'''


def svg(vb, body, label):
    return (f'<svg viewBox="{vb}" role="img" aria-label="{label}" '
            f'font-family=\'{FONT}\' xmlns="http://www.w3.org/2000/svg">{DEFS}{body}</svg>')


# ---------------------------------------------------------------- plans
def site_base():
    o = [rect(0, 0, PLOT_W, PLOT_D, fill=GARDEN, stroke="none")]
    # street
    o.append(rect(-2.5, -3.2, PLOT_W + 2.5, -0.6, fill=GRIS_CL))
    o.append(text(PLOT_W / 2, -1.7, "STREET", 0.45, GRIS, weight="700", extra='letter-spacing="0.3"'))
    # paved zones
    o.append(rect(0, 0, 9, 5, fill=PAVING))
    o.append(rect(17, 0, 25, 5, fill=PAVING))
    o.append(rect(22.5, 5, 25, 32, fill=PAVING))
    o.append(rect(9, 5, 11.4, 14, fill=PAVING))
    o.append(rect(11.4, 5, 18, 14, fill="url(#gravel)"))
    o.append(rect(0, 22, 22.5, 24.5, fill=PAVING))
    o.append(rect(9.6, 0, 11.0, 5, fill=PAVING))
    # pool + deck
    o.append(rect(6, 26.4, 19.5, 31, fill=PAVING))
    o.append(rect(7, 27.2, 18, 30.2, fill=WATER, stroke=GRIS, sw=0.04))
    for i in range(1, 4):
        o.append(line(7.3, 27.2 + i * 0.75, 17.7, 27.2 + i * 0.75, "#B8C9DC", 0.015))
    o.append(text(12.5, 28.85, "POOL 11.00 x 3.00", 0.3, GRIS, weight="700"))
    o.append(pline([(5.6, 26.0), (19.9, 26.0), (19.9, 31.4), (5.6, 31.4), (5.6, 26.0)], GRIS, 0.025, 'stroke-dasharray="0.25 0.12"'))
    o.append(text(19.9, 31.85, "child-safety pool fence h 1.20", 0.24, GRIS, anchor="end"))
    # boundary
    o.append(rect(0, 0, PLOT_W, PLOT_D, stroke=NOIR, sw=0.06, extra='stroke-dasharray="0.8 0.2 0.15 0.2"'))
    return "".join(o)


def front_wall():
    o = []
    o.append(rect(0, -0.12, 9, 0.12, fill="url(#claustra)", stroke=NOIR, sw=0.02))     # claustra to work yard
    o.append(rect(9, -0.1, 17, 0.1, fill=POCHE))
    o.append(rect(22.5, -0.1, 25, 0.1, fill=POCHE))
    o.append(rect(1.0, -0.18, 5.5, 0.18, fill="#fff"))
    o.append(line(1.0, -0.3, 5.5, -0.3, NOIR, 0.04))
    o.append(text(3.25, -0.42, "4.50 sliding gate (deliveries)", 0.22, GRIS))
    o.append(rect(9.6, -0.15, 11.0, 0.15, fill="#fff"))
    o.append(opening("door", 9.6, 11.0, 0, True, 1))
    o.append(rect(17, -0.18, 22.5, 0.18, fill="#fff"))
    o.append(line(17, -0.3, 22.5, -0.3, NOIR, 0.04))
    o.append(text(19.75, -0.42, "5.50 car gate", 0.22, GRIS))
    # side + rear boundary walls
    o.append(rect(-0.12, 0, 0.0, PLOT_D, fill=GRIS))
    o.append(rect(PLOT_W, 0, PLOT_W + 0.12, PLOT_D, fill=GRIS))
    o.append(rect(0, PLOT_D, PLOT_W, PLOT_D + 0.12, fill=GRIS))
    # claustra screen between front garden and patio
    o.append(rect(11.5, 4.9, 18, 5.1, fill="url(#claustra)", stroke=NOIR, sw=0.015))
    return "".join(o)


def plan_gf():
    o = [site_base(), front_wall()]
    # trees and planting
    o += [tree(13.4, 9.3, 2.0), tree(14.5, 2.4, 1.6), tree(3.0, 28.8, 2.6), tree(22.0, 28.6, 1.8), tree(1.6, 25.8, 1.2)]
    # work yard canopy + hoist rail
    o.append(rect(0, 1.5, 9, 5, stroke=GRIS, sw=0.02, extra='stroke-dasharray="0.2 0.1"'))
    o.append(line(3.8, 0.6, 3.8, 10.2, VERT, 0.05, 'stroke-dasharray="0.5 0.12 0.1 0.12"'))
    o.append(text(4.0, 1.2, "2 t monorail hoist", 0.24, VERT, anchor="start", weight="700"))
    o.append(text(6.6, 2.6, "WORK YARD", 0.3, NOIR, weight="700"))
    o.append(text(6.6, 2.95, "carving outdoors, 45 m²", 0.22, GRIS))
    # carport
    o.append(rect(17, 0.2, 22.5, 5, stroke=GRIS, sw=0.02, extra='stroke-dasharray="0.2 0.1"'))
    for x in (17.6, 20.1):
        o.append(rect(x, 0.6, x + 1.9, 4.6, stroke=GRIS, sw=0.02, extra='rx="0.35"'))
    o.append(text(19.75, 2.7, "CARPORT", 0.3, NOIR, weight="700"))
    o.append(text(19.75, 3.05, "pergola, 2 cars", 0.22, GRIS))
    o.append(rect(22.6, 0.2, 24.9, 2.4, fill="#fff", stroke=GRIS, sw=0.02))
    o.append(text(23.75, 1.4, "BINS", 0.22, GRIS, weight="700"))
    o.append(text(12.0, 1.0, "FRONT GARDEN", 0.26, NOIR, weight="700"))
    o.append(rect(15.8, 3.0, 16.6, 3.8, fill="#fff", stroke=NOIR, sw=0.02))
    o.append(text(16.2, 4.3, "sculpture", 0.2, GRIS))
    # gallery
    o.append(rect(9, 5, 11.65, 14, stroke=GRIS, sw=0.02, extra='stroke-dasharray="0.2 0.1"'))
    for y in (5.15, 8.0, 11.0, 13.85):
        o.append(rect(11.28, y - 0.12, 11.52, y + 0.12, fill=NOIR))
    o.append(text(10.2, 9.0, "GALLERY", 0.26, NOIR, weight="700", extra='transform="rotate(-90 10.2 9)"'))
    o.append(text(10.65, 9.0, "covered entrance, 21.6 m²", 0.2, GRIS, extra='transform="rotate(-90 10.65 9)"'))
    for y in (6.0, 9.6, 12.4):
        o.append(rect(9.15, y, 9.45, y + 0.9, fill="#fff", stroke=GRIS, sw=0.015))
    # patio
    o.append(rect(15.0, 5.8, 17.5, 7.8, fill=WATER, stroke=GRIS, sw=0.02))
    o.append(text(16.25, 6.95, "water", 0.2, GRIS))
    o.append(text(14.7, 11.9, "SCULPTURE PATIO", 0.3, NOIR, weight="700"))
    o.append(text(14.7, 12.25, "59 m², frangipani tree", 0.22, GRIS))
    for (x, y) in ((12.3, 6.2), (16.6, 12.9)):
        o.append(rect(x, y, x + 0.7, y + 0.7, fill="#fff", stroke=NOIR, sw=0.02))
    # terrace columns
    for x in (0.15, 4.5, 9, 13, 17, 22.35):
        o.append(rect(x - 0.13, 24.37, x + 0.13, 24.63, fill=NOIR))
    o.append(text(11.0, 23.5, "COVERED TERRACE", 0.28, NOIR, weight="700"))
    o.append(text(11.0, 23.85, "2.50 deep, under the balcony", 0.22, GRIS))
    # service alley + Matt
    o.append(text(23.75, 10.4, "SERVICE ALLEY", 0.24, NOIR, weight="700", extra='transform="rotate(-90 23.75 10.4)"'))
    for y in (6.5, 7.3, 8.1, 8.9):
        o.append(line(22.8, y + 1.7, 24.7, y + 1.7, GRIS, 0.012, 'stroke-dasharray="0.1 0.06"'))
    o.append(text(24.25, 12.4, "drying", 0.2, GRIS, extra='transform="rotate(-90 24.25 12.4)"'))
    o.append(rect(22.7, 15.0, 24.9, 18.0, fill="#fff", stroke=NOIR, sw=0.03))
    o.append(text(23.8, 16.3, "MATT", 0.3, VERT, weight="700"))
    o.append(text(23.8, 16.65, "kennel", 0.2, GRIS))
    o.append(dog_plan(23.6, 17.4))
    o.append(rect(22.7, 18.0, 24.9, 22.0, stroke=VERT, sw=0.03, extra='stroke-dasharray="0.15 0.08"'))
    o.append(text(23.8, 19.9, "shaded run", 0.2, VERT))
    o.append(text(23.8, 20.2, "dog shower", 0.2, VERT))
    o.append(line(23.4, 22.0, 24.4, 22.0, "#fff", 0.08))
    o.append(text(23.9, 22.45, "gate to garden", 0.18, GRIS))
    o.append(text(12.5, 25.6, "GARDEN", 0.3, NOIR, weight="700"))
    # building
    o.append(walls(GF_BLOCKS, GF_ROOMS, GF_MERGE))
    for op in GF_OPEN:
        k, a1, a2, at, hz, *rest = op
        o.append(opening(k, a1, a2, at, hz, *(rest or [1])))
    o.append(stair_plan(0))
    # mezzanine + studio stair
    o.append(rect(0.1, 11.5, 8.9, 13.9, stroke=GRIS, sw=0.02, extra='stroke-dasharray="0.25 0.1"'))
    o.append(text(7.0, 12.9, "mezzanine above +2.90", 0.2, GRIS))
    for i in range(15):
        o.append(line(0.1, 7.7 + i * 0.25, 0.95, 7.7 + i * 0.25, NOIR, 0.01))
    o.append(rect(0.1, 7.7, 0.95, 11.45, stroke=NOIR, sw=0.015))
    # furniture
    fur = [(1.6, 6.3, 4.0, 7.2), (5.4, 9.2, 7.8, 10.1), (19.0, 16.0, 21.2, 16.9), (21.8, 14.2, 22.4, 19.3),
           (14.0, 17.4, 16.4, 18.4), (9.6, 20.6, 12.8, 21.4), (9.6, 18.6, 10.4, 20.6), (11.0, 19.0, 12.2, 19.9),
           (5.3, 20.3, 8.3, 21.2), (0.1, 18.4, 2.2, 20.0), (3.6, 16.6, 4.3, 18.0), (18.1, 6.5, 19.0, 8.4),
           (18.2, 10.9, 21.8, 11.5), (17.5, 20.3, 19.0, 21.3), (18.2, 8.7, 18.8, 9.3), (18.9, 8.7, 19.5, 9.3),
           (4.6, 19.8, 4.95, 21.9)]
    for (a, b, c, d) in fur:
        o.append(rect(a, b, c, d, fill="#fff", stroke=GRIS, sw=0.015))
    for (x, y) in ((4.6, 8.4), (6.6, 6.9)):
        o.append(circle(x, y, 0.55, stroke=GRIS, sw=0.015))
        o.append(circle(x, y, 0.08, fill=GRIS, stroke="none"))
    for i in range(4):
        o.append(circle(14.4 + i * 0.55, 17.15, 0.17, stroke=GRIS, sw=0.012))
        o.append(circle(14.4 + i * 0.55, 18.65, 0.17, stroke=GRIS, sw=0.012))
    o.append(labels(GF_ROOMS, group_areas(GF_ROOMS)))
    # annotations
    o.append(dims_h(-4.0, [0, 9, 11.4, 18, 22.5, 25], -0.2))
    o.append(dims_v(-1.6, [0, 5, 14, 22, 24.5, 32]))
    o.append(section_mark(13, -3.6, 13, 33.2, "A", -1, 0))
    o.append(section_mark(-1.0, 20.5, 26.2, 20.5, "B", 0, -1))
    o.append(north_arrow(27.6, 1.5))
    o.append(wind_arrow(27.4, 29.5))
    o.append(text(12.5, 34.6, "±0.00 = +0.45 above street level", 0.28, GRIS))
    return svg("-3.4 -5.0 33.4 40.4", "".join(o), "Ground floor plan")


def plan_r1():
    o = [rect(0, 0, PLOT_W, PLOT_D, fill="#FAFBF8", stroke=NOIR, sw=0.05, extra='stroke-dasharray="0.8 0.2 0.15 0.2"')]
    o.append(rect(-2.5, -3.2, PLOT_W + 2.5, -0.6, fill=GRIS_CL))
    o.append(text(PLOT_W / 2, -1.7, "STREET", 0.45, GRIS, weight="700", extra='letter-spacing="0.3"'))
    # roofs below
    o.append(rect(0, 5, 9, 14, fill=GRIS_CL, stroke=GRIS, sw=0.03))
    for y in (8, 11):
        o.append(line(0, y, 9, y, GRIS, 0.04))
    for y in (5, 8, 11):
        o.append(rect(0.3, y + 0.05, 8.7, y + 0.35, fill=WATER, stroke=GRIS, sw=0.015))
    o.append(text(4.5, 9.7, "STUDIO ROOF", 0.3, GRIS, weight="700"))
    o.append(text(4.5, 10.05, "3 north-light sheds, top +7.80", 0.22, GRIS))
    o.append(rect(9, 5, 11.65, 14, fill=GRIS_CL, stroke=GRIS, sw=0.02))
    o.append(text(10.3, 9.5, "GALLERY ROOF +3.20", 0.22, GRIS, extra='transform="rotate(-90 10.3 9.5)"'))
    o.append(rect(18, 5, 22.5, 14, fill=GRIS_CL, stroke=GRIS, sw=0.02))
    for i in range(4):
        o.append(rect(18.4, 5.6 + i * 1.6, 22.1, 6.8 + i * 1.6, fill="#fff", stroke=GRIS, sw=0.015))
        o.append(line(18.4, 6.2 + i * 1.6, 22.1, 6.2 + i * 1.6, GRIS, 0.01))
    o.append(text(20.25, 12.7, "SOLAR PV ROOF +3.90", 0.22, GRIS, weight="700"))
    o.append(text(20.25, 13.05, "water tank 3 m³", 0.2, GRIS))
    o.append(tree(13.4, 9.3, 2.0))
    o.append(text(14.8, 12.2, "PATIO (void)", 0.26, GRIS, weight="700"))
    # balcony + roof overhang
    o.append(rect(0, 23, 22.5, 24.5, fill=PAVING, stroke=NOIR, sw=0.02))
    o.append(line(0, 24.45, 22.5, 24.45, NOIR, 0.05))
    o.append(text(11.25, 24.0, "BALCONY 1.50, louvred shutters", 0.24, GRIS, weight="700"))
    o.append(rect(0, 13.2, 23.3, 25.5, stroke=GRIS, sw=0.025, extra='stroke-dasharray="0.3 0.12"'))
    o.append(text(23.2, 25.95, "roof overhang", 0.22, GRIS, anchor="end"))
    o.append(walls(R1_BLOCKS, R1_ROOMS, R1_MERGE))
    for op in R1_OPEN:
        k, a1, a2, at, hz, *rest = op
        o.append(opening(k, a1, a2, at, hz, *(rest or [1])))
    o.append(stair_plan(1))
    # skylights
    for x in (1.1, 3.4, 5.4):
        o.append(rect(x - 0.4, 14.35, x + 0.4, 15.05, stroke=GRIS, sw=0.015))
        o.append(line(x - 0.4, 14.35, x + 0.4, 15.05, GRIS, 0.01))
        o.append(line(x + 0.4, 14.35, x - 0.4, 15.05, GRIS, 0.01))
    o.append(text(3.2, 17.0, "skylights", 0.18, GRIS))
    fur = []
    for x1 in (0, 3.5, 7, 10.5):
        fur += [(x1 + 0.15, 20.9, x1 + 1.05, 22.85), (x1 + 2.4, 22.25, x1 + 3.35, 22.85), (x1 + 0.15, 19.35, x1 + 1.6, 19.95)]
    fur += [(20.4, 19.6, 22.4, 21.4), (9.6, 16.5, 12.4, 17.3), (14.6, 15.0, 16.4, 16.0),
            (14.1, 19.3, 14.6, 22.85), (15.9, 19.3, 16.4, 22.85), (17.7, 14.2, 19.5, 15.0), (21.6, 14.2, 22.4, 17.8)]
    for (a, b, c, d) in fur:
        o.append(rect(a, b, c, d, fill="#fff", stroke=GRIS, sw=0.015))
    o.append(labels(R1_ROOMS, group_areas(R1_ROOMS)))
    o.append(text(7.2, 18.75, "LANDING / CORRIDOR", 0.2, GRIS, weight="700"))
    o.append(dims_h(-4.0, [0, 3.5, 7, 10.5, 14, 16.5, 22.5, 25], -0.2))
    o.append(dims_v(-1.6, [0, 5, 14, 18, 19.2, 23, 24.5, 32]))
    o.append(section_mark(13, -3.6, 13, 33.2, "A", -1, 0))
    o.append(section_mark(-1.0, 20.5, 26.2, 20.5, "B", 0, -1))
    o.append(north_arrow(27.6, 1.5))
    o.append(text(12.5, 34.6, "R+1 floor level +3.60", 0.28, GRIS))
    return svg("-3.4 -5.0 33.4 40.4", "".join(o), "First floor plan")


# ---------------------------------------------------------------- sections & elevations
def Z(z):
    return -z


def level_tag(x, z, label, anchor="start", col=NOIR):
    y = Z(z)
    tri = poly([(x, y), (x - 0.18, y - 0.3), (x + 0.18, y - 0.3)], fill="#fff", stroke=col, sw=0.02)
    dx = 0.3 if anchor == "start" else -0.3
    return (tri + line(x - 0.6, y, x + 0.6, y, col, 0.015)
            + text(x + dx, y - 0.08, label, 0.3, col, anchor=anchor))


def person(x, z0, h=1.75, col=GRIS, kid=False):
    s = h / 1.75
    head = circle(x, Z(z0 + h - 0.12 * s), 0.12 * s, fill=col, stroke="none")
    body = poly([(x - 0.2 * s, Z(z0 + h - 0.27 * s)), (x + 0.2 * s, Z(z0 + h - 0.27 * s)),
                 (x + 0.15 * s, Z(z0 + 0.8 * s)), (x + 0.1 * s, Z(z0)), (x - 0.1 * s, Z(z0)),
                 (x - 0.15 * s, Z(z0 + 0.8 * s))], fill=col, stroke="none", extra='opacity="0.75"')
    return head + body


def dog(x, z0, col=GRIS, flip=False):
    k = -1 if flip else 1
    pts = [(0, 0.28), (0.05, 0.0), (0.12, 0.0), (0.15, 0.25), (0.5, 0.25), (0.53, 0.0), (0.6, 0.0), (0.62, 0.3),
           (0.72, 0.52), (0.85, 0.52), (0.9, 0.62), (0.78, 0.72), (0.66, 0.66), (0.58, 0.48), (0.1, 0.48), (-0.08, 0.6)]
    return poly([(x + k * a, Z(z0 + b)) for a, b in pts], fill=col, stroke="none")


def tree_el(x, z0, h, r, col=VERT):
    return (rect(x - 0.1, Z(z0 + h * 0.55), x + 0.1, Z(z0), fill=GRIS)
            + f'<ellipse cx="{f(x)}" cy="{f(Z(z0 + h - r * 0.8))}" rx="{f(r)}" ry="{f(r*0.8)}" fill="{col}" fill-opacity="0.22" stroke="{col}" stroke-width="0.03"/>')


def palm_el(x, z0, h):
    o = [line(x, Z(z0), x + 0.3, Z(z0 + h), GRIS, 0.12)]
    tx, tz = x + 0.3, z0 + h
    for ang in (-160, -130, -100, -70, -40, -15, -190):
        a = math.radians(ang)
        o.append(f'<path d="M{f(tx)},{f(Z(tz))} q{f(math.cos(a)*0.9)},{f(math.sin(a)*0.9-0.3)} {f(math.cos(a)*1.8)},{f(math.sin(a)*1.2+0.5)}" fill="none" stroke="{VERT}" stroke-width="0.07"/>')
    return "".join(o)


def section_aa():
    """N-S cut at x = 13.00 looking west. Horizontal axis = y."""
    o = []
    # earth
    o.append(rect(-3, Z(GROUND), 34, Z(-2.4), fill="url(#hatchEarth)"))
    o.append(rect(-3, Z(-0.6), 0, Z(-2.4), fill=GRIS_CL))
    o.append(text(-1.5, Z(-1.2), "STREET", 0.3, GRIS, weight="700"))
    # ---- beyond: studio silhouette (x 0-9) with saw-tooth north-light roof
    saw = [(5, -0.3), (5, SHED_HI), (8, SHED_LO), (8, SHED_HI), (11, SHED_LO), (11, SHED_HI), (14, SHED_LO), (14, -0.3)]
    o.append(poly([(y, Z(z)) for y, z in saw], fill=GRIS_CL, stroke=GRIS, sw=0.03))
    for y0 in (5, 8, 11):
        o.append(rect(y0 + 0.02, Z(SHED_HI - 0.1), y0 + 0.12, Z(SHED_LO + 0.05), fill=WATER, stroke=GRIS, sw=0.01))
    o.append(text(7.4, Z(5.6), "SCULPTURE STUDIO (beyond)", 0.28, GRIS, weight="700"))
    o.append(text(7.4, Z(5.2), "6.00 m clear height", 0.24, GRIS))
    # gallery beyond
    o.append(rect(5, Z(3.2), 14.2, Z(3.0), fill=GRIS, stroke="none"))
    for y in (5.15, 8.0, 11.0, 13.85):
        o.append(rect(y - 0.12, Z(3.0), y + 0.12, Z(0.0), fill="#fff", stroke=GRIS, sw=0.02))
    # ---- ground & platforms
    o.append(line(-3, Z(-0.6), 0, Z(-0.6), NOIR, 0.05))
    o.append(pline([(0, Z(GROUND)), (5, Z(GROUND)), (5, Z(-0.15)), (14, Z(-0.15))], NOIR, 0.05))
    o.append(rect(0, Z(-0.45), 5, Z(-0.3), fill=GRIS_CL))
    # front wall
    o.append(rect(-0.1, Z(1.75), 0.1, Z(GROUND), fill=POCHE))
    # claustra screen y=5
    o.append(rect(4.9, Z(2.4), 5.1, Z(-0.15), fill="url(#claustra)", stroke=NOIR, sw=0.02))
    # patio tree + basin
    o.append(tree_el(10.4, -0.15, 5.0, 1.4))
    o.append(rect(5.8, Z(0.25), 7.8, Z(-0.15), fill=WATER, stroke=GRIS, sw=0.02))
    o.append(rect(3.0, Z(0.6), 3.8, Z(-0.3), fill="#fff", stroke=NOIR, sw=0.02))
    o.append(f'<path d="M3.1,{f(Z(0.6))} C3.0,{f(Z(1.6))} 3.9,{f(Z(1.4))} 3.5,{f(Z(2.4))}" fill="none" stroke="{NOIR}" stroke-width="0.12"/>')
    # ---- house cut
    o.append(rect(14 - T_EXT, Z(0.0), 24.5, Z(-0.3), fill=POCHE))                    # ground slab + terrace
    o.append(rect(13.9, Z(FFL1), 24.5, Z(FFL1 - 0.25), fill=POCHE))                 # R+1 slab + balcony
    o.append(rect(13.2, Z(ROOF), 25.5, Z(ROOF - 0.3), fill=POCHE))                  # roof slab w/ overhangs
    o.append(rect(13.2, Z(ACRO), 13.35, Z(ROOF), fill=POCHE))
    o.append(rect(25.35, Z(ACRO), 25.5, Z(ROOF), fill=POCHE))
    o.append(rect(13.35, Z(ROOF + 0.12), 25.35, Z(ROOF), fill=GRIS_CL, stroke=GRIS, sw=0.01))
    # GF north glazing (sliding onto patio)
    o.append(rect(13.9, Z(FFL1 - 0.25), 14.1, Z(2.7), fill=POCHE))
    o.append(rect(13.95, Z(2.7), 14.05, Z(0), fill=WATER, stroke=NOIR, sw=0.015))
    # GF south glazing
    o.append(rect(21.9, Z(FFL1 - 0.25), 22.1, Z(2.7), fill=POCHE))
    o.append(rect(21.95, Z(2.7), 22.05, Z(0), fill=WATER, stroke=NOIR, sw=0.015))
    # R1 north wall with window
    o.append(rect(13.9, Z(4.5), 14.1, Z(FFL1), fill=POCHE))
    o.append(rect(13.95, Z(6.2), 14.05, Z(4.5), fill=WATER, stroke=NOIR, sw=0.015))
    o.append(rect(13.9, Z(ROOF - 0.3), 14.1, Z(6.2), fill=POCHE))
    # corridor / child-4 wall at y 19.2 with door
    o.append(rect(19.1, Z(ROOF - 0.3), 19.3, Z(FFL1 + 2.15), fill=POCHE))
    # R1 south wall with sliding window
    o.append(rect(22.9, Z(ROOF - 0.3), 23.1, Z(6.0), fill=POCHE))
    o.append(rect(22.95, Z(6.0), 23.05, Z(FFL1), fill=WATER, stroke=NOIR, sw=0.015))
    # balcony railing + louvred shutter
    o.append(line(24.45, Z(FFL1), 24.45, Z(FFL1 + 1.0), NOIR, 0.04))
    o.append(rect(23.2, Z(ROOF - 0.3), 23.35, Z(FFL1), fill="url(#slats)", stroke=GRIS, sw=0.01))
    # terrace column (cut - a column sits on x = 13)
    o.append(rect(24.37, Z(FFL1 - 0.25), 24.63, Z(0), fill=POCHE))
    # steps to garden
    o.append(pline([(24.5, Z(0)), (24.8, Z(0)), (24.8, Z(-0.15)), (25.1, Z(-0.15)), (25.1, Z(-0.3)), (25.4, Z(-0.3)), (25.4, Z(GROUND))], NOIR, 0.04))
    # garden & pool
    o.append(line(25.4, Z(GROUND), 32, Z(GROUND), NOIR, 0.05))
    o.append(rect(27.0, Z(GROUND), 27.2, Z(-2.15), fill=POCHE))
    o.append(rect(30.2, Z(GROUND), 30.4, Z(-2.15), fill=POCHE))
    o.append(rect(27.0, Z(-1.95), 30.4, Z(-2.15), fill=POCHE))
    o.append(rect(27.2, Z(-0.6), 30.2, Z(-1.95), fill=WATER))
    o.append(line(27.2, Z(-0.6), 30.2, Z(-0.6), "#7FA2C9", 0.03))
    o.append(text(28.7, Z(-1.35), "POOL", 0.26, GRIS, weight="700"))
    o.append(rect(31.9, Z(1.75), 32.1, Z(GROUND), fill=POCHE))
    o.append(palm_el(31.0, GROUND, 6.5))
    # room labels
    o.append(text(18.0, Z(1.5), "LIVING / DINING", 0.32, NOIR, weight="700"))
    o.append(text(18.0, Z(1.1), "h 3.35", 0.24, GRIS))
    o.append(text(16.1, Z(5.0), "FAMILY ROOM", 0.26, NOIR, weight="700"))
    o.append(text(21.1, Z(5.0), "CHILD 4", 0.26, NOIR, weight="700"))
    o.append(text(21.1, Z(4.65), "h 3.00", 0.22, GRIS))
    o.append(text(23.3, Z(1.6), "TERRACE", 0.24, NOIR, weight="700"))
    o.append(text(1.4, Z(0.15) - 0.05, "FRONT GARDEN", 0.24, GRIS, weight="700"))
    o.append(text(12.4, Z(0.15) - 0.05, "PATIO", 0.24, GRIS, weight="700"))
    # climate: sun at noon + air paths
    o.append(line(26.6, Z(10.2), 25.5, Z(ROOF - 0.3), "#C0A000", 0.03, 'stroke-dasharray="0.25 0.12"'))
    o.append(line(25.5, Z(ROOF - 0.3), 23.0, Z(FFL1 + 0.1), "#C0A000", 0.03, 'stroke-dasharray="0.25 0.12"'))
    o.append(text(26.8, Z(10.3), "high sun: the overhang shades the glass", 0.24, "#9A8200", anchor="start"))
    o.append(f'<path d="M31.5,{f(Z(1.4))} C27,{f(Z(1.6))} 25,{f(Z(1.2))} 18,{f(Z(1.9))} S12.5,{f(Z(2.5))} 11.5,{f(Z(6.5))}" fill="none" stroke="{VERT}" stroke-width="0.06" stroke-dasharray="0.3 0.15" marker-end="url(#arrG)"/>')
    o.append(f'<path d="M31.5,{f(Z(4.6))} C28,{f(Z(4.8))} 22,{f(Z(4.4))} 17,{f(Z(5.3))} S14.5,{f(Z(6.2))} 13.0,{f(Z(8.6))}" fill="none" stroke="{VERT}" stroke-width="0.06" stroke-dasharray="0.3 0.15" marker-end="url(#arrG)"/>')
    o.append(text(31.6, Z(2.0), "SW sea breeze", 0.26, VERT, anchor="end", weight="700"))
    o.append(text(12.3, Z(9.5), "warm air out", 0.24, VERT, weight="700"))
    o.append(text(12.3, Z(9.15), "through the patio", 0.24, VERT))
    # people + dog for scale
    o.append(person(19.4, 0.0))
    o.append(person(20.2, 0.0, 1.2))
    o.append(dog(20.7, 0.0))
    o.append(person(17.4, FFL1, 1.35))
    # levels
    for z, lab in ((ACRO, "+7.20 parapet"), (ROOF, "+6.90 roof"), (FFL1, "+3.60 R+1"), (0, "±0.00 GF"), (GROUND, "-0.45 ground")):
        o.append(level_tag(33.0, z, lab))
    o.append(level_tag(1.6, SHED_HI, "+7.80 sheds"))
    # grid line refs
    for y, lab in ((0, "0"), (5, "5"), (14, "14"), (22, "22"), (24.5, "24.5"), (32, "32")):
        o.append(line(y, Z(-2.5), y, Z(-2.9), GRIS, 0.015))
        o.append(text(y, Z(-3.25), lab, 0.24, GRIS))
    o.append(text(16, Z(-3.7), "distance from street boundary (m)", 0.22, GRIS))
    return svg(f"-3.4 {f(Z(10.9))} 41 {f(15.1)}", "".join(o), "Section A-A")


def section_bb():
    """W-E cut at y = 20.50 looking north. Horizontal axis = x."""
    o = []
    o.append(rect(-1.5, Z(GROUND), 26.5, Z(-1.8), fill="url(#hatchEarth)"))
    # beyond: studio top showing above the roof
    o.append(rect(0.1, Z(SHED_HI), 9, Z(ROOF), fill=GRIS_CL, stroke=GRIS, sw=0.025))
    o.append(text(4.5, Z(SHED_HI) - 0.12, "studio sheds beyond +7.80", 0.22, GRIS))
    o.append(line(-1.5, Z(GROUND), 26.5, Z(GROUND), NOIR, 0.05))
    # slabs
    o.append(rect(0, Z(0), 22.5 + T_EXT, Z(-0.3), fill=POCHE))
    o.append(rect(0, Z(FFL1), 22.5 + T_EXT, Z(FFL1 - 0.25), fill=POCHE))
    o.append(rect(0, Z(ROOF), 23.3, Z(ROOF - 0.3), fill=POCHE))
    o.append(rect(23.15, Z(ACRO), 23.3, Z(ROOF), fill=POCHE))
    o.append(rect(-0.15, Z(ACRO), 0.1, Z(-0.3), fill=POCHE))               # west party wall
    o.append(rect(22.4, Z(ROOF - 0.3), 22.65, Z(-0.3), fill=POCHE))         # east wall
    for x in (4.5, 17, 19.5):
        o.append(rect(x - 0.1, Z(FFL1 - 0.25), x + 0.1, Z(0), fill=POCHE))
    for x in (3.5, 7, 10.5, 14, 16.5):
        o.append(rect(x - 0.1, Z(ROOF - 0.3), x + 0.1, Z(FFL1), fill=POCHE))
    # false ceilings
    o.append(line(0.1, Z(FFL1 - 0.25 - 0.1), 22.4, Z(FFL1 - 0.25 - 0.1), GRIS, 0.012, 'stroke-dasharray="0.15 0.08"'))
    # beyond doors (north walls)
    for (a, b, z0, z1) in ((4.8, 5.6, 0, 2.1), (9.4, 10.2, FFL1, FFL1 + 2.15), (12.9, 13.7, FFL1, FFL1 + 2.15),
                           (2.4, 3.2, FFL1, FFL1 + 2.15), (5.9, 6.7, FFL1, FFL1 + 2.15)):
        o.append(rect(a, Z(z1), b, Z(z0), stroke=GRIS, sw=0.02))
    # living opening to patio beyond (sliding glazing)
    o.append(rect(11.8, Z(2.7), 16.8, Z(0), fill=WATER, stroke=GRIS, sw=0.015, extra='fill-opacity="0.6"'))
    o.append(rect(9.4, Z(2.5), 11.2, Z(0), stroke=GRIS, sw=0.02))
    # kennel + run (cut through run)
    o.append(rect(24.9, Z(2.2), 25.1, Z(GROUND), fill=POCHE))
    o.append(poly([(22.7, Z(GROUND)), (22.7, Z(1.3)), (24.9, Z(1.7)), (24.9, Z(GROUND))], fill="#fff", stroke=GRIS, sw=0.02))
    o.append(rect(23.5, Z(0.4), 24.1, Z(GROUND), fill=GRIS_CL, stroke=GRIS, sw=0.015, extra='rx="0.2"'))
    o.append(line(22.75, Z(GROUND), 22.75, Z(1.2), VERT, 0.04))
    o.append(dog(23.0, GROUND, VERT))
    o.append(text(23.8, Z(2.2), "MATT", 0.26, VERT, weight="700"))
    # labels
    for cx, z, lab in ((2.25, 1.4, "GUEST / STUDY"), (6.75, 1.4, "LIBRARY"), (13.0, 1.6, "LIVING / DINING"), (18.25, 1.4, "BREAKFAST"),
                       (21.0, 1.4, "PANTRY"), (1.2, 4.9, "CHILD 1"), (4.7, 4.9, "CHILD 2"), (8.2, 4.9, "CHILD 3"),
                       (11.7, 4.9, "CHILD 4"), (15.25, 4.9, "DRESS."), (19.5, 4.9, "PARENTS")):
        o.append(text(cx, Z(z), lab, 0.26 if len(lab) < 12 else 0.24, NOIR, weight="700"))
    o.append(person(15.6, 0))
    o.append(person(16.3, 0, 1.65))
    o.append(person(7.9, 0, 1.25))
    o.append(person(21.6, FFL1, 1.75))
    for z, lab in ((ACRO, "+7.20"), (ROOF, "+6.90"), (FFL1, "+3.60"), (0, "±0.00"), (GROUND, "-0.45")):
        o.append(level_tag(25.6, z, lab))
    for x in (0, 4.5, 9, 17, 22.5, 25):
        o.append(line(x, Z(-1.9), x, Z(-2.2), GRIS, 0.015))
        o.append(text(x, Z(-2.55), f(x), 0.24, GRIS))
    return svg(f"-1.8 {f(Z(8.6))} 29.6 {f(11.6)}", "".join(o), "Section B-B")


def elevation_north():
    o = []
    o.append(rect(-1.5, Z(GROUND), 26.5, Z(-1.2), fill=GRIS_CL))
    # 1. house behind (y = 14)
    o.append(rect(0, Z(ROOF - 0.3), 22.65, Z(0), fill="#fff", stroke=NOIR, sw=0.03))
    o.append(rect(0, Z(ACRO), 23.3, Z(ROOF - 0.3), fill=GRIS_CL, stroke=NOIR, sw=0.03))
    for (a, b, z0, z1) in ((9.6, 13.4, 4.5, 6.2), (14.4, 17.1, 4.5, 6.2), (18.5, 21.5, 5.4, 6.2)):
        o.append(rect(a, Z(z1), b, Z(z0), fill=WATER, stroke=NOIR, sw=0.02))
    for x in range(0, 14):
        xx = 9.75 + x * 0.55
        if xx < 17.2:
            o.append(rect(xx, Z(6.5), xx + 0.08, Z(4.3), fill=GRIS))
    o.append(rect(11.8, Z(2.7), 16.8, Z(0), fill=WATER, stroke=NOIR, sw=0.02))
    for x in (13.05, 14.3, 15.55):
        o.append(line(x, Z(2.7), x, Z(0), NOIR, 0.015))
    o.append(rect(9.4, Z(2.5), 11.2, Z(0), fill="#C9B79C", stroke=NOIR, sw=0.02))
    # 2. east wing (y = 5)
    o.append(rect(18, Z(3.9), 22.5 + T_EXT, Z(0), fill="#fff", stroke=NOIR, sw=0.03))
    o.append(rect(18, Z(3.9), 22.65, Z(3.35), fill=GRIS_CL, stroke=NOIR, sw=0.02))
    for i in range(4):
        o.append(poly([(18.4 + i * 1.05, Z(3.9)), (19.3 + i * 1.05, Z(3.9)), (19.3 + i * 1.05, Z(4.4))], fill=GRIS, stroke="none"))
    o.append(rect(18.5, Z(2.1), 19.4, Z(0), fill="#C9B79C", stroke=NOIR, sw=0.02))
    o.append(rect(19.8, Z(2.2), 20.7, Z(1.0), fill=WATER, stroke=NOIR, sw=0.02))
    o.append(rect(21.2, Z(2.6), 22.3, Z(0.6), fill="url(#claustra)", stroke=NOIR, sw=0.02))
    # 3. gallery
    o.append(rect(9, Z(3.2), 11.65, Z(3.0), fill=GRIS, stroke=NOIR, sw=0.02))
    o.append(rect(11.28, Z(3.0), 11.52, Z(0), fill="#fff", stroke=NOIR, sw=0.02))
    # claustra screen y=5 in front of patio
    o.append(rect(11.6, Z(2.4), 18, Z(-0.15), fill="url(#claustra)", stroke=NOIR, sw=0.025))
    # 4. studio (y = 5) in compressed-earth blocks + north-light glazing
    o.append(rect(0, Z(SHED_LO), 9, Z(-0.3), fill="url(#btc)", stroke=NOIR, sw=0.04))
    o.append(rect(0, Z(SHED_HI), 9, Z(SHED_LO), fill=WATER, stroke=NOIR, sw=0.04))
    for i in range(1, 6):
        o.append(line(i * 1.5, Z(SHED_HI), i * 1.5, Z(SHED_LO), NOIR, 0.02))
    o.append(rect(0, Z(SHED_HI + 0.15), 9, Z(SHED_HI), fill=POCHE))
    o.append(rect(2.0, Z(3.7), 5.6, Z(-0.3), fill="url(#slats)", stroke=NOIR, sw=0.03))
    o.append(rect(6.2, Z(3.4), 8.6, Z(1.0), fill=WATER, stroke=NOIR, sw=0.02))
    o.append(rect(-0.1, Z(4.1), 9.3, Z(3.95), fill=GRIS))  # canopy beam over work yard
    o.append(line(3.8, Z(4.0), 3.8, Z(3.6), NOIR, 0.03))
    o.append(rect(3.6, Z(3.6), 4.0, Z(3.35), fill=NOIR))
    # 5. carport pergola
    for x in (17.1, 22.4):
        o.append(rect(x - 0.08, Z(2.6), x + 0.08, Z(GROUND), fill=GRIS))
    o.append(rect(17.0, Z(2.8), 22.5, Z(2.6), fill=GRIS))
    # 6. trees + people
    o.append(tree_el(14.5, GROUND, 5.2, 1.7))
    o.append(palm_el(24.0, GROUND, 7.0))
    # 7. front boundary
    o.append(rect(0, Z(1.75), 9, Z(GROUND), fill="url(#claustra)", stroke=NOIR, sw=0.03))
    o.append(rect(1.0, Z(1.75), 5.5, Z(GROUND), fill="url(#slats)", stroke=NOIR, sw=0.03))
    o.append(rect(9, Z(0.75), 17, Z(GROUND), fill="#fff", stroke=NOIR, sw=0.03))
    for i in range(0, 54):
        x = 9.1 + i * 0.15
        if not (9.6 <= x <= 11.0):
            o.append(line(x, Z(1.75), x, Z(0.75), NOIR, 0.012))
    o.append(line(9, Z(1.75), 17, Z(1.75), NOIR, 0.03))
    o.append(rect(9.6, Z(1.75), 11.0, Z(GROUND), fill="url(#slats)", stroke=NOIR, sw=0.03))
    o.append(rect(17, Z(1.75), 22.5, Z(GROUND), fill="url(#slats)", stroke=NOIR, sw=0.03))
    o.append(rect(22.5, Z(1.75), 25, Z(GROUND), fill="#fff", stroke=NOIR, sw=0.03))
    o.append(rect(22.8, Z(1.2), 24.7, Z(GROUND + 0.05), fill=GRIS_CL, stroke=NOIR, sw=0.015))
    o.append(text(23.75, Z(0.35), "bins / meters", 0.18, GRIS))
    o.append(rect(11.1, Z(1.45), 11.35, Z(1.15), fill=NOIR))
    o.append(person(8.2, GROUND))
    o.append(dog(10.3, GROUND, NOIR))
    o.append(text(10.6, Z(GROUND) + 0.55, "MATT", 0.26, VERT, weight="700"))
    o.append(line(-1.5, Z(GROUND), 26.5, Z(GROUND), NOIR, 0.06))
    for z, lab in ((SHED_HI, "+7.80"), (ACRO, "+7.20"), (FFL1, "+3.60"), (0, "±0.00"), (GROUND, "-0.45")):
        o.append(level_tag(25.7, z, lab))
    for cx, lab in ((4.5, "STUDIO + WORK YARD"), (13.0, "ENTRANCE + PATIO"), (20.2, "CARPORT + SERVICE")):
        o.append(text(cx, Z(-0.95), lab, 0.26, GRIS, weight="700"))
    return svg(f"-1.8 {f(Z(9.0))} 29.6 {f(10.3)}", "".join(o), "North elevation (street)")


def elevation_south():
    """Looking north from the rear garden; x' = 25 - x (east on the left)."""
    X = lambda x: PLOT_W - x
    o = []
    o.append(rect(-1.5, Z(GROUND), 26.5, Z(-1.2), fill=GARDEN))
    # studio behind (shows above the roof)
    o.append(rect(X(9), Z(SHED_HI), X(0), Z(0), fill=GRIS_CL, stroke=GRIS, sw=0.03))
    o.append(rect(X(9), Z(SHED_HI + 0.15), X(0), Z(SHED_HI), fill=POCHE))
    # house
    o.append(rect(X(22.5), Z(ROOF - 0.3), X(0), Z(0), fill="#fff", stroke=NOIR, sw=0.03))
    o.append(rect(X(23.3), Z(ACRO), X(0), Z(ROOF - 0.3), fill=GRIS_CL, stroke=NOIR, sw=0.03))
    # R+1 openings + shutters
    r1 = [(0.5, 2.3), (4.0, 5.8), (7.5, 9.3), (11.0, 12.8), (17.3, 21.7)]
    for a, b in r1:
        o.append(rect(X(b), Z(6.0), X(a), Z(FFL1), fill=WATER, stroke=NOIR, sw=0.02))
        o.append(rect(X(b + 0.95), Z(6.0), X(b + 0.05), Z(FFL1), fill="url(#slats)", stroke=GRIS, sw=0.015))
    o.append(rect(X(16.4), Z(6.2), X(14.1), Z(FFL1), fill="url(#slats)", stroke=NOIR, sw=0.02))
    # balcony slab + railing
    o.append(rect(X(22.5), Z(FFL1), X(0), Z(FFL1 - 0.25), fill=GRIS, stroke=NOIR, sw=0.02))
    o.append(line(X(22.5), Z(FFL1 + 1.0), X(0), Z(FFL1 + 1.0), NOIR, 0.04))
    for i in range(4):
        o.append(line(X(22.5), Z(FFL1 + 0.25 + i * 0.22), X(0), Z(FFL1 + 0.25 + i * 0.22), GRIS, 0.012))
    for i in range(16):
        x = i * 1.5
        o.append(line(X(x), Z(FFL1), X(x), Z(FFL1 + 1.0), NOIR, 0.025))
    # GF openings
    for a, b in ((1.0, 3.5), (5.0, 8.5), (9.3, 16.7), (17.3, 19.3)):
        o.append(rect(X(b), Z(2.7), X(a), Z(0), fill=WATER, stroke=NOIR, sw=0.02))
        n = max(2, round((b - a) / 1.25))
        for k in range(1, n):
            xx = a + k * (b - a) / n
            o.append(line(X(xx), Z(2.7), X(xx), Z(0), NOIR, 0.012))
    o.append(rect(X(22.2), Z(2.9), X(19.8), Z(2.5), fill="url(#claustra)", stroke=NOIR, sw=0.015))
    # terrace columns
    for x in (0.15, 4.5, 9, 13, 17, 22.35):
        o.append(rect(X(x) - 0.13, Z(FFL1 - 0.25), X(x) + 0.13, Z(0), fill="#fff", stroke=NOIR, sw=0.025))
    o.append(rect(X(22.5), Z(0), X(0), Z(GROUND), fill=GRIS_CL, stroke=NOIR, sw=0.02))
    # kennel + run (east end -> left)
    o.append(poly([(X(24.9), Z(GROUND)), (X(24.9), Z(1.7)), (X(22.7), Z(1.3)), (X(22.7), Z(GROUND))], fill="#fff", stroke=NOIR, sw=0.02))
    o.append(rect(X(24.1), Z(0.4), X(23.5), Z(GROUND), fill=GRIS_CL, stroke=NOIR, sw=0.015, extra='rx="0.2"'))
    o.append(rect(X(25.0), Z(2.2), X(24.9), Z(GROUND), fill=POCHE))
    o.append(dog(X(23.0), GROUND, VERT, flip=True))
    o.append(text(X(23.8), Z(2.0), "MATT", 0.26, VERT, weight="700"))
    # pool coping + trees + family
    o.append(rect(X(18), Z(GROUND + 0.05), X(7), Z(GROUND), fill=WATER, stroke=GRIS, sw=0.02))
    o.append(tree_el(X(0.9), GROUND, 6.8, 1.9))
    o.append(palm_el(X(22.0), GROUND, 6.0))
    o.append(person(X(12.0), 0))
    o.append(person(X(11.3), 0, 1.65))
    for i, h in enumerate((1.45, 1.25, 1.05, 0.9)):
        o.append(person(X(15.5 + i * 0.6), GROUND, h))
    o.append(dog(X(18.6), GROUND, NOIR, flip=True))
    o.append(line(-1.5, Z(GROUND), 26.5, Z(GROUND), NOIR, 0.06))
    for z, lab in ((SHED_HI, "+7.80"), (ACRO, "+7.20"), (FFL1, "+3.60"), (0, "±0.00"), (GROUND, "-0.45")):
        o.append(level_tag(26.0, z, lab))
    for cx, lab in ((X(19.5), "PARENTS"), (X(7.0), "CHILDREN"), (X(13.0), "LIVING")):
        o.append(text(cx, Z(-0.95), lab, 0.26, GRIS, weight="700"))
    return svg(f"-1.8 {f(Z(9.0))} 29.8 {f(10.3)}", "".join(o), "South elevation (garden)")


# ---------------------------------------------------------------- schedule
def schedule():
    def rows(rooms):
        g = {}
        order = []
        for r in rooms:
            if r[7] not in g:
                order.append(r[7])
                g[r[7]] = 0
            g[r[7]] += net_area(r)
        return [(k, g[k]) for k in order]

    gf, r1 = rows(GF_ROOMS), rows(R1_ROOMS)
    gf.insert(1, ("Studio mezzanine (+2.90)", 8.8 * 2.3))
    return gf, r1


def table(rows, title):
    tot = sum(a for _, a in rows)
    body = "".join(f"<tr><td>{n}</td><td class='num'>{a:.1f}</td></tr>" for n, a in rows)
    return (f"<table><thead><tr><th>{title}</th><th class='num'>m²</th></tr></thead><tbody>{body}"
            f"<tr class='sub'><td>Net floor area</td><td class='num'>{tot:.1f}</td></tr></tbody></table>"), tot


def main():
    with open(LOGO) as fh:
        logo = fh.read().strip()
    gf_rows, r1_rows = schedule()
    t_gf, a_gf = table(gf_rows, "GROUND FLOOR")
    t_r1, a_r1 = table(r1_rows, "FIRST FLOOR (R+1)")
    ext_rows = [(n, (x2 - x1) * (y2 - y1)) for n, x1, y1, x2, y2 in OUTDOOR]
    ext_body = "".join(f"<tr><td>{n}</td><td class='num'>{a:.1f}</td></tr>" for n, a in ext_rows)
    t_ext = f"<table><thead><tr><th>OUTDOOR + COVERED</th><th class='num'>m²</th></tr></thead><tbody>{ext_body}</tbody></table>"

    fp_closed = 9 * 9 + 22.5 * 8 + 4.5 * 9
    gross_r1 = 22.5 * 9
    gross = fp_closed + gross_r1 + 9 * 2.4   # + studio mezzanine
    covered = fp_closed + 9 * 2.6 + 22.5 * 2.5 + 5.5 * 5
    ces = fp_closed / 800 * 100
    cos = gross / 800 * 100
    paved = 9 * 5 + 2.5 * 32 + 2.4 * 9 + 22.5 * 2.5 + 13.5 * 4.6 + 1.4 * 5 + 5.5 * 5
    green = 800 - fp_closed - paved
    figures = [
        ("800 m²", "site, 25.00 x 32.00 m"),
        (f"{gross:.0f} m²", "gross floor area"),
        (f"{a_gf + a_r1:.0f} m²", "net floor area"),
        (f"{ces:.0f} %", "footprint ratio (CES)"),
        (f"{cos:.2f}", "plot ratio (COS)"),
        (f"{green:.0f} m²", "planted ground + patio"),
    ]
    fig_html = "".join(f"<div class='fig'><b>{a}</b><span>{b}</span></div>" for a, b in figures)

    html = TEMPLATE
    for k, v in {
        "{{LOGO}}": logo, "{{FIGS}}": fig_html,
        "{{PLAN_GF}}": plan_gf(), "{{PLAN_R1}}": plan_r1(),
        "{{SEC_A}}": section_aa(), "{{SEC_B}}": section_bb(),
        "{{EL_N}}": elevation_north(), "{{EL_S}}": elevation_south(),
        "{{T_GF}}": t_gf, "{{T_R1}}": t_r1, "{{T_EXT}}": t_ext,
        "{{TOTAL}}": f"{a_gf + a_r1:.1f}", "{{GROSS}}": f"{gross:.1f}",
    }.items():
        html = html.replace(k, v)
    with open(os.path.join(HERE, "index.html"), "w") as fh:
        fh.write(html)
    print("written", len(html), "bytes; net", round(a_gf + a_r1, 1), "gross", gross, "CES", round(ces, 1), "green", green)


TEMPLATE = open(os.path.join(HERE, "template.html")).read() if os.path.exists(os.path.join(HERE, "template.html")) else ""

if __name__ == "__main__":
    main()
