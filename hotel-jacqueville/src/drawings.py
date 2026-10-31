"""Génère toutes les planches SVG du dossier (plans, coupes, axonométries, graphiques)."""
import math, os
from shapely.geometry import Polygon
from geo import SITE, P, buildable, bar_frame, rect_uv, TRAME, RECUL_NORD, D_COURSIVE, D_PIECE, D_LOGGIA, D_BARRE, ROT
from svgkit import Sheet, en
import design as D

OUT = os.path.join(os.path.dirname(__file__), '..', 'build', 'svg')
os.makedirs(OUT, exist_ok=True)
T, V0 = TRAME, RECUL_NORD
INK, MUTED = '#1e2a24', '#6b6b63'
COL = {'bati': '#e8d9bf', 'bati_s': '#a8502d', 'tech': '#d6cfc2', 'piscine': '#9fd3d0', 'deck': '#c9a477',
       'allee': '#efe6d2', 'evergreen': 'url(#eg)', 'pelouse': 'url(#turf)', 'pleine_terre': '#cfe0bb', 'toit': '#7cae5e'}
AZ_U = 90 - (ROT + bar_frame()[1])          # azimut de l'axe u (≈ 94,5°)

def save(name, svg):
    open(os.path.join(OUT, name + '.svg'), 'w').write(svg)

def site_sheet(scale=15, pad=40):
    pts = [en(*c) for c in SITE.exterior.coords]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return Sheet(min(xs) - 6, min(ys) - 4, max(xs) + 4, max(ys) + 4, scale=scale, pad=pad)

def uv(u, v):
    return bar_frame()[0](u, v)

# ------------------------------------------------------------------ analyse de site
def site_analysis():
    s = site_sheet(14, 50)
    f = uv
    # voie ouest (hypothèse du plan cadastral : emprise en tireté à l'ouest)
    road = Polygon([(-9, -2), (-1.2, -2), (-1.2, 34), (-9, 34)])
    s.poly(road, fill='#e6e2da', stroke='none')
    s.text(-5, 16, 'VOIE (à confirmer)', 10, rot=-90 + ROT, fill=MUTED, weight=600)
    s.poly(SITE, fill='#f3efe4', sw=1.8)
    s.poly(buildable(), fill='none', stroke='#a8502d', dash='5 4', sw=1.1)
    for k, (x, y) in P.items():
        s.circle(x, y, 0.35, fill=INK)
        dx, dy = {'B1': (-1.2, 1.0), 'B2': (1.2, 1.0), 'B3': (1.3, -0.8), 'B4': (-1.3, -0.8)}[k]
        s.text(x + dx, y + dy, k, 10, weight=700)
    # cotes
    for a, b, lab, off in [('B1', 'B2', '40,75 m', 1.8), ('B2', 'B3', '24,11 m', 1.8), ('B3', 'B4', '40,00 m', 1.8), ('B4', 'B1', '31,90 m', 1.8)]:
        (x1, y1), (x2, y2) = P[a], P[b]
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        L = math.hypot(x2 - x1, y2 - y1); nx, ny = (y2 - y1) / L, -(x2 - x1) / L
        ang = -math.degrees(math.atan2(*reversed(en(x2, y2)))) if False else 0
        e1, n1 = en(x1, y1); e2, n2 = en(x2, y2)
        rot = -math.degrees(math.atan2(n2 - n1, e2 - e1))
        if rot > 90: rot -= 180
        if rot < -90: rot += 180
        s.text(mx - nx * off, my - ny * off, lab, 10, rot=rot, weight=600)
    s.text(20, 13, '1 120 m²', 22, weight=700, fill='#a8502d')
    s.text(20, 10.3, 'Lot 2511 — îlot 225 — Jacqueville', 10, fill=MUTED)
    s.text(20, 8.4, 'trapèze rectangle (angles B3, B4 = 100 gr)', 9, fill=MUTED)
    s.text(20, -2.2, 'Lot 2513', 10, fill=MUTED, italic=True)
    s.text(43.5, 12, 'Lots 2512 / 2514', 10, fill=MUTED, italic=True, rot=-90 + ROT)
    s.text(20, 26.0, 'limite nord : azimut 94,5° — quasi est-ouest', 9, fill=INK, rot=-(ROT - 11.0), italic=True)
    s.text(8, 22.5, 'zone constructible', 9, fill='#a8502d', rot=0)
    s.text(8, 21.1, 'reculs 4 m (N) / 3 m', 9, fill='#a8502d')
    s.north(s.w - 40, 45)
    # vent dominant SO + brise de mer
    ox, oy = 52, s.h - 70
    s.raw(f'<g transform="translate({ox},{oy})"><path d="M0,0 L60,-60" stroke="#2e7d7a" stroke-width="3" marker-end="url(#arr)"/>'
          f'<text x="-6" y="22" font-size="10" fill="#2e7d7a" font-weight="600">Mousson / brise de mer SO</text>'
          f'<text x="-6" y="35" font-size="9" fill="{MUTED}">3–5 m/s, océan à ~300 m au sud</text></g>')
    s.scalebar(s.w - 200, s.h - 30, 10)
    save('site', s.svg())

# ------------------------------------------------------------------ plans masse
def plan_masse(code):
    V = D.VARIANTS[code]
    s = site_sheet(15, 40)
    road = Polygon([(-9, -2), (-1.2, -2), (-1.2, 34), (-9, 34)])
    s.poly(road, fill='#e6e2da', stroke='none')
    s.text(-5, 16, 'VOIE', 10, rot=-90 + ROT, fill=MUTED, weight=600)
    s.poly(SITE, fill=COL['pleine_terre'], sw=1.6)
    order = ['allee', 'evergreen', 'deck', 'pelouse', 'piscine', 'tech', 'bati']
    for cat in order:
        for lab, g in V['shapes'].get(cat, []):
            fill = COL[cat]
            st = '#a8502d' if cat == 'bati' else '#8a7d6a'
            s.poly(g.intersection(SITE), fill=fill, stroke=st, sw=1.4 if cat == 'bati' else 0.7)
    if code == 'B':
        for g in V['stairs']:
            s.poly(g, fill='url(#hatch)', stroke='#8a7d6a', sw=0.6)
    for (u, v, kind) in V['trees']:
        x, y = uv(u, v); s.tree(x, y, 2.6 if kind == 'feuillu' else 2.0, kind)
    # étiquettes
    lab = {'A': [((U := D.U0) + 4.5 * T, V0 + 5.3, 'BARRE HÔTEL R+2', 11, 700), (U + 4.5 * T, V0 + 7.0, 'toit : restaurant + cage de foot', 9, 400),
                 (18.5, 22.3, 'bassin de nage', 9, 400), (28.8, 24.7, 'bain froid', 8, 400), (33.5, 19.0, 'fitness', 8, 400),
                 (4.0, 21.5, 'dépose', 8, 400), (3.8, 6.0, 'tech.', 8, 400), (20, 27.5, 'JARDIN-FORÊT', 12, 700),
                 (24, 0.9, 'lisière plantée (recul 4 m)', 8, 400)],
           'B': [(D.TU[0] + 4.5, V0 + 5.2, 'T1', 13, 700), (D.TU[1] + 4.5, V0 + 5.2, 'T2', 13, 700), (D.TU[2] + 4.5, V0 + 5.2, 'T3', 13, 700),
                 (D.TU[0] + 4.5, V0 + 7.0, 'case-tour R+2', 8, 400), (15.5, 20.0, 'CASE COMMUNE', 10, 700), (15.5, 21.4, 'accueil · restaurant', 8, 400),
                 (30.7, 20.6, 'PELOUSE-TERRAIN', 10, 700), (30.7, 22.0, 'paspalum', 8, 400), (15.0, 26.9, 'bassin de nage', 8, 400),
                 (4.0, 21.5, 'dépose', 8, 400), (3.8, 6.0, 'tech.', 8, 400), (24, 0.9, 'lisière plantée (recul 4 m)', 8, 400)],
           'C': [(D.UC + 4.5 * T, D.V0C + 5.0, 'BARRE HÔTEL R+2', 11, 700), (D.UC + 4.5 * T, D.V0C + 6.6, 'toit : PV + toiture végétalisée', 9, 400),
                 (14.0, 20.6, 'CASE-RESTAURANT', 9, 700), (14.0, 22.0, 'ouverte · 60 couverts', 8, 400), (22.6, 20.0, 'tech.', 8, 400),
                 (31.8, 20.8, 'PELOUSE-TERRAIN', 9, 700), (31.8, 22.2, 'paspalum', 8, 400), (14.5, 27.3, 'bassin de nage', 8, 400),
                 (4.0, 21.5, 'dépose', 8, 400), (4.0, 2.7, 'service', 8, 400), (24, 0.9, 'lisière plantée + écran (recul 5 m)', 8, 400)]}[code]
    for u, v, t, sz, w in lab:
        x, y = uv(u, v); s.text(x, y, t, sz, weight=w, rot=-(ROT + bar_frame()[1]) * -1 * 0 - (ROT + bar_frame()[1]) * 0 + 4.47 * 0)
    # flèche d'entrée
    a, b = uv(-3.0, 14.0), uv(1.3, 14.0)
    s.line([a, b], stroke='#a8502d', sw=2.2, marker=True)
    x, y = uv(-3.6, 12.7); s.text(x, y, 'entrée', 9, fill='#a8502d', weight=700)
    s.north(s.w - 38, 42)
    s.scalebar(s.w - 200, s.h - 22, 10)
    save(f'masse_{code}', s.svg())

# ------------------------------------------------------------------ plans de niveau (repère u,v)
class Plan:
    def __init__(self, u0, v0, u1, v1, k=22, pad=26):
        self.u0, self.v0, self.k, self.pad = u0, v0, k, pad
        self.w, self.h = (u1 - u0) * k + 2 * pad, (v1 - v0) * k + 2 * pad
        self.it = []
    def X(self, u): return (u - self.u0) * self.k + self.pad
    def Y(self, v): return (v - self.v0) * self.k + self.pad
    def rect(self, u, v, w, d, fill='none', stroke=INK, sw=1.0, dash=None, op=1):
        da = f' stroke-dasharray="{dash}"' if dash else ''
        self.it.append(f'<rect x="{self.X(u):.1f}" y="{self.Y(v):.1f}" width="{w * self.k:.1f}" height="{d * self.k:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{da} opacity="{op}"/>')
    def txt(self, u, v, s, size=9, w=400, fill=INK, anchor='middle', italic=False):
        st = ' font-style="italic"' if italic else ''
        self.it.append(f'<text x="{self.X(u):.1f}" y="{self.Y(v):.1f}" font-size="{size}" font-weight="{w}" fill="{fill}" text-anchor="{anchor}" dominant-baseline="middle"{st}>{s}</text>')
    def line(self, pts, stroke=INK, sw=1, dash=None):
        da = f' stroke-dasharray="{dash}"' if dash else ''
        d = ' L'.join(f'{self.X(u):.1f},{self.Y(v):.1f}' for u, v in pts)
        self.it.append(f'<path d="M{d}" fill="none" stroke="{stroke}" stroke-width="{sw}"{da}/>')
    def circ(self, u, v, r, fill='#8fb27a', op=0.6):
        self.it.append(f'<circle cx="{self.X(u):.1f}" cy="{self.Y(v):.1f}" r="{r * self.k:.1f}" fill="{fill}" opacity="{op}"/>')
    def north(self, x, y):
        self.it.append(f'<g transform="translate({x},{y}) rotate({-(AZ_U - 90):.1f})"><circle r="15" fill="#fff" stroke="{INK}" stroke-width="0.8"/>'
                       f'<path d="M0,-13 L5,8 L0,4 L-5,8 Z" fill="{INK}"/><text y="-19" font-size="10" font-weight="700" text-anchor="middle">N</text></g>')
    def scale(self, x, y, m=5):
        L = m * self.k
        self.it.append(f'<g><rect x="{x}" y="{y}" width="{L / 2:.1f}" height="4" fill="{INK}"/><rect x="{x + L / 2:.1f}" y="{y}" width="{L / 2:.1f}" height="4" fill="#fff" stroke="{INK}" stroke-width="0.6"/>'
                       f'<text x="{x}" y="{y + 14}" font-size="8">0</text><text x="{x + L:.1f}" y="{y + 14}" font-size="8" text-anchor="middle">{m} m</text></g>')
    def svg(self):
        defs = ('<defs><pattern id="h2" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="5" stroke="#b7aa95" stroke-width="0.8"/></pattern>'
                '<pattern id="turf" width="10" height="10" patternUnits="userSpaceOnUse"><rect width="10" height="10" fill="#7cae5e"/><rect width="5" height="10" fill="#86b868"/></pattern></defs>')
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w:.0f} {self.h:.0f}" width="{self.w:.0f}" height="{self.h:.0f}" font-family="Inter, sans-serif">{defs}'
                + '\n'.join(self.it) + '</svg>')

WET = '#d7e9ee'
def room(p, u, v, w, kind, label, area, flip=False, pmr=False):
    """Module chambre : bande humide côté coursive (pattern Djondji), lit face à la loggia."""
    d = D_PIECE
    p.rect(u, v, w, d, fill='#fffdf8', sw=1.4)
    # bande humide 2,0 m (SdE) + niche d'entrée 1,0 m
    sde_w = w - 1.1
    su = u + (0 if not flip else 1.1)
    p.rect(su, v, sde_w, 2.0, fill=WET, sw=0.8)
    p.txt(su + sde_w / 2, v + 1.0, 'SdE', 7, fill=MUTED)
    eu = u + sde_w if not flip else u
    p.txt(eu + 0.55, v + 0.5, '▼', 6, fill='#a8502d')
    # lit
    bu = u + w / 2 - 0.9 if kind == 'D' else u + (w - 1.8) - 0.6
    p.rect(bu, v + 4.7, 1.8, 2.0, fill='#efe6d2', sw=0.6)
    if kind in ('J', 'P'):
        p.rect(u + 0.4, v + 3.0, 0.8, 2.2, fill='#efe6d2', sw=0.5)            # canapé / salon
    if kind == 'P':
        p.line([(u + w / 2 - 0.2, v + 2.0), (u + w / 2 - 0.2, v + 4.2)], sw=1.0)
    p.txt(u + w / 2, v + 3.0, label, 8, 700)
    p.txt(u + w / 2, v + 3.7, f'{area:.1f} m²' + (' · PMR' if pmr else ''), 7, fill=MUTED)
    # loggia
    p.rect(u, v + d, w, D_LOGGIA, fill='#f1e3cc', sw=0.6)
    p.line([(u + 0.2, v + d + D_LOGGIA - 0.15), (u + w - 0.2, v + d + D_LOGGIA - 0.15)], stroke='#8a6a45', sw=2.2, dash='1.5 1')

def posts(p, u0, n, vs):
    for i in range(n + 1):
        for v in vs:
            p.rect(u0 + i * T - 0.15, v - 0.15, 0.3, 0.3, fill=INK, sw=0)

def plans_A():
    U = D.U0
    rows = {
     'R0': [(U + 0.0, 2.0, 'com'), (U + 18.0 - 14.4 + 14.4, 1.5, 'J', 'Suite junior', 37.8), (None,)],
    }
    levels = {}
    def base(title):
        p = Plan(U - 1.5, V0 - 1.5, U + 9 * T + 1.5, V0 + D_BARRE + 2.8)
        p.rect(U, V0, 9 * T, D_BARRE, fill='none', sw=0.6, dash='3 2')
        posts(p, U, 9, [V0, V0 + D_COURSIVE, V0 + D_COURSIVE + D_PIECE, V0 + D_BARRE])
        # noyau
        cu = U + 4 * T
        p.rect(cu, V0, T, D_BARRE, fill='#ece7dd', sw=1.4)
        p.rect(cu + 0.3, V0 + 2.4, 2.6, 5.4, fill='url(#h2)', sw=0.7); p.txt(cu + 1.6, V0 + 5.1, 'esc.', 7)
        p.rect(cu + 0.6, V0 + 8.0, 1.8, 2.0, fill='#fff', sw=0.8); p.txt(cu + 1.5, V0 + 9.0, 'asc.', 7)
        p.txt(U + 4.5 * T, V0 + D_BARRE + 1.9, title, 10, 700, fill='#a8502d')
        p.north(p.w - 30, 30); p.scale(p.pad, p.h - 18)
        return p
    def coursive(p):
        for a, b in [(U, U + 4 * T), (U + 5 * T, U + 9 * T)]:
            p.rect(a, V0, b - a, D_COURSIVE, fill='#f6f1e7', sw=0.6)
            p.txt((a + b) / 2, V0 + 0.9, 'coursive ouverte — brise traversante', 7, fill=MUTED, italic=True)
    vr = V0 + D_COURSIVE
    # RDC
    p = base('RDC — accueil, lounge, spa à l’ouest · 3 clés jardin à l’est')
    p.rect(U, V0, 2 * T, D_BARRE, fill='#fbf3e6', sw=1.4)
    p.txt(U + T, V0 + 3.0, 'Réception', 8, 700); p.txt(U + T, V0 + 3.7, 'boutique-épicerie 18 m²', 7, fill=MUTED)
    p.line([(U, V0 + 4.6), (U + 2 * T, V0 + 4.6)], sw=0.8)
    p.txt(U + T, V0 + 7.6, 'Lobby-lounge 52 m²', 8, 700); p.txt(U + T, V0 + 8.3, 'écran matchs · ouvert jardin', 7, fill=MUTED)
    p.rect(U + 2 * T, V0, T, 4.2, fill='#fbf3e6', sw=1.2); p.txt(U + 2.5 * T, V0 + 1.8, 'Back-office', 7, 700); p.txt(U + 2.5 * T, V0 + 2.5, '15 m²', 7, fill=MUTED)
    p.rect(U + 2 * T, V0 + 4.2, T, 2.4, fill=WET, sw=1.0); p.txt(U + 2.5 * T, V0 + 5.4, 'Sanit. 9', 7)
    p.rect(U + 3 * T, V0, T, 6.6, fill='#efe9df', sw=1.0); p.txt(U + 3.5 * T, V0 + 3.0, 'Lingerie', 7, 700); p.txt(U + 3.5 * T, V0 + 3.7, 'TGBT 24', 7, fill=MUTED)
    p.rect(U + 2 * T, V0 + 6.6, 2 * T, 4.0, fill='#f3e7f0', sw=1.2); p.txt(U + 3 * T, V0 + 8.3, 'Spa — 2 cabines', 8, 700); p.txt(U + 3 * T, V0 + 9.0, '30 m² · patio douche', 7, fill=MUTED)
    room(p, U + 5 * T, vr, 1.5 * T, 'J', 'Junior', 37.8)
    room(p, U + 6.5 * T, vr, T, 'D', 'Deluxe', 25.2, pmr=True)
    room(p, U + 7.5 * T, vr, 1.5 * T, 'J', 'Junior', 37.8)
    p.rect(U + 5 * T, V0, 4 * T, D_COURSIVE, fill='#f6f1e7', sw=0.6); p.txt(U + 7 * T, V0 + 0.9, 'galerie d’accès', 7, fill=MUTED, italic=True)
    p.txt(U + 5.75 * T + 0.9, V0 + D_BARRE + 0.4, '◄ lock-off famille ►', 7, fill='#2e7d7a')
    save('A_R0', p.svg())
    # R+1
    p = base('R+1 — 6 clés (4 juniors, 2 deluxe) · 2 suites familiales lock-off')
    coursive(p)
    for a in (U, U + 5 * T):
        room(p, a, vr, 1.5 * T, 'J', 'Junior', 37.8); room(p, a + 1.5 * T, vr, T, 'D', 'Deluxe', 25.2); room(p, a + 2.5 * T, vr, 1.5 * T, 'J', 'Junior', 37.8)
        p.txt(a + 1.25 * T, V0 + D_BARRE + 0.4, '◄ lock-off ►', 7, fill='#2e7d7a')
    save('A_R1', p.svg())
    # R+2
    p = base('R+2 — 6 clés : 2 suites premium à l’ouest (hors aplomb de la cage), 4 deluxe')
    coursive(p)
    room(p, U, vr, 2 * T, 'P', 'Suite premium', 50.4); room(p, U + 2 * T, vr, 2 * T, 'P', 'Suite premium', 50.4)
    for i in range(4):
        room(p, U + (5 + i) * T, vr, T, 'D', 'Deluxe', 25.2)
    save('A_R2', p.svg())
    # Toit
    p = base('TOIT-STADE (+9,80) — restaurant-bar sous chaume · cage de foot 14,4 × 10,6')
    p.rect(U - 1.2, V0 - 1.2, 4 * T + 1.2, D_BARRE + 2.4, fill='none', stroke='#b08a4a', sw=1.0, dash='6 3')
    p.txt(U + 2 * T, V0 - 0.6, 'débord de chaume', 7, fill='#b08a4a', italic=True)
    p.rect(U, V0, 2 * T, 4.2, fill='#efe9df', sw=1.2); p.txt(U + T, V0 + 1.8, 'Cuisine 30 m²', 8, 700); p.txt(U + T, V0 + 2.6, 'monte-plats ↔ réserve RDC', 7, fill=MUTED)
    p.rect(U + 2 * T, V0, T, 4.2, fill=WET, sw=1.0); p.txt(U + 2.5 * T, V0 + 2.1, 'Sanit.', 7)
    p.rect(U + 3 * T, V0, T, 4.2, fill='#e2d2b8', sw=0.8); p.txt(U + 3.5 * T, V0 + 1.8, 'bar', 8, 700); p.txt(U + 3.5 * T, V0 + 2.5, '+ réserve', 7, fill=MUTED)
    p.rect(U, V0 + 4.2, 4 * T, D_BARRE - 4.2, fill='#fbf3e6', sw=0.6)
    for i in range(6):
        for j in range(2):
            p.circ(U + 1.3 + i * 2.3, V0 + 6.0 + j * 2.6, 0.55, fill='#c9a477', op=0.9)
    p.txt(U + 2 * T, V0 + 9.8, 'Salle sous chaume 80 couverts — vue océan au sud', 8, 700)
    p.rect(U + 5 * T, V0, 4 * T, D_BARRE, fill='url(#turf)', sw=1.8, stroke='#1f3d2b')
    p.rect(U + 5 * T + 0.6, V0 + D_BARRE / 2 - 1.5, 0.6, 3.0, fill='#fff', sw=0.8)
    p.rect(U + 9 * T - 1.2, V0 + D_BARRE / 2 - 1.5, 0.6, 3.0, fill='#fff', sw=0.8)
    p.line([(U + 7 * T, V0), (U + 7 * T, V0 + D_BARRE)], stroke='#fff', sw=1.2)
    p.it.append(f'<circle cx="{p.X(U + 7 * T):.1f}" cy="{p.Y(V0 + D_BARRE / 2):.1f}" r="{1.5 * p.k:.1f}" fill="none" stroke="#fff" stroke-width="1.2"/>')
    p.txt(U + 7 * T, V0 + 3.0, 'CAGE DE FOOT 3 c. 3', 9, 700, fill='#fff'); p.txt(U + 7 * T, V0 + 7.8, 'filets h 5 m + toit-filet', 7, fill='#fff')
    p.txt(U + 7 * T, V0 + D_BARRE - 0.8, 'gazon synth. sur dalle flottante (acoustique)', 7, fill='#fff')
    p.rect(U - 1.4, V0 + 2.0, 1.4, 6.0, fill='url(#h2)', sw=0.7); p.txt(U - 0.7, V0 + 8.8, 'esc. 2', 7)
    save('A_toit', p.svg())

def plans_C():
    U, VC = D.UC, D.V0C
    def base(title):
        p = Plan(U - 1.5, VC - 1.5, U + 9 * T + 1.5, VC + D_BARRE + 2.8)
        posts(p, U, 9, [VC, VC + D_COURSIVE, VC + D_COURSIVE + D_PIECE, VC + D_BARRE])
        cu = U + 4 * T
        p.rect(cu, VC, T, D_BARRE, fill='#ece7dd', sw=1.4)
        p.rect(cu + 0.3, VC + 2.4, 2.6, 5.4, fill='url(#h2)', sw=0.7); p.txt(cu + 1.6, VC + 5.1, 'esc.', 7)
        p.rect(cu + 0.6, VC + 8.0, 1.8, 2.0, fill='#fff', sw=0.8); p.txt(cu + 1.5, VC + 9.0, 'asc.', 7)
        p.txt(U + 4.5 * T, VC + D_BARRE + 1.9, title, 10, 700, fill='#a8502d')
        p.north(p.w - 30, 30); p.scale(p.pad, p.h - 18)
        return p
    vr = VC + D_COURSIVE
    p = base('C · RDC — accueil et cuisine à l’ouest, back-of-house et 2 clés jardin à l’est')
    p.rect(U, VC, 2 * T, D_BARRE, fill='#fbf3e6', sw=1.4)
    p.txt(U + T, VC + 2.6, 'Réception · boutique', 8, 700); p.txt(U + T, VC + 3.3, 'back-office 14 m²', 7, fill=MUTED)
    p.line([(U, VC + 4.4), (U + 2 * T, VC + 4.4)], sw=0.8)
    p.txt(U + T, VC + 7.4, 'Lobby-lounge 62 m²', 8, 700); p.txt(U + T, VC + 8.1, 'écran matchs', 7, fill=MUTED)
    p.rect(U + 2 * T, VC, 2 * T, 2.9, fill='#e6ddd0', sw=1.1); p.txt(U + 3 * T, VC + 1.2, 'Économat · CF · cave 22', 7, 700); p.txt(U + 3 * T, VC + 1.9, 'livraisons ← voie de service', 7, fill=MUTED)
    p.rect(U + 2 * T, VC + 2.9, 2 * T, D_BARRE - 2.9, fill='#efe9df', sw=1.3); p.txt(U + 3 * T, VC + 6.2, 'Cuisine tout électrique', 8, 700); p.txt(U + 3 * T, VC + 6.9, '40 m² · passe vers la case-restaurant ↓', 7, fill=MUTED)
    p.rect(U + 5 * T, VC, 2 * T, 4.4, fill='#eef0f3', sw=1.1); p.txt(U + 6 * T, VC + 1.8, 'Vestiaires H/F', 7.5, 700); p.txt(U + 6 * T, VC + 2.5, '+ sanitaires 25 m²', 7, fill=MUTED)
    p.rect(U + 5 * T, VC + 4.4, T, 6.2, fill='#eef0f3', sw=1.1); p.txt(U + 5.5 * T, VC + 7.0, 'Réfectoire', 7, 700); p.txt(U + 5.5 * T, VC + 7.7, '15 m²', 7, fill=MUTED)
    p.rect(U + 6 * T, VC + 4.4, T, 4.6, fill='#eef0f3', sw=1.1); p.txt(U + 6.5 * T, VC + 6.4, 'Lingerie', 7, 700); p.txt(U + 6.5 * T, VC + 7.1, '30 m²', 7, fill=MUTED)
    p.rect(U + 6 * T, VC + 9.0, T, 1.6, fill='#d9d2c6', sw=1.0); p.txt(U + 6.5 * T, VC + 9.8, 'déchets', 6.5)
    room(p, U + 7 * T, vr, T, 'D', 'Deluxe', 25.2, pmr=True); room(p, U + 8 * T, vr, T, 'D', 'Deluxe', 25.2)
    p.rect(U + 7 * T, VC, 2 * T, D_COURSIVE, fill='#f6f1e7', sw=0.6); p.txt(U + 8 * T, VC + 0.9, 'galerie', 7, fill=MUTED, italic=True)
    save('C_R0', p.svg())
    p = base('C · R+2 — 2 suites premium à l’ouest, 4 deluxe (R+1 identique à A : 4 juniors + 2 deluxe)')
    for a, b in [(U, U + 4 * T), (U + 5 * T, U + 9 * T)]:
        p.rect(a, VC, b - a, D_COURSIVE, fill='#f6f1e7', sw=0.6); p.txt((a + b) / 2, VC + 0.9, 'coursive ouverte + écran planté côté voisin', 7, fill=MUTED, italic=True)
    room(p, U, vr, 2 * T, 'P', 'Suite premium', 50.4); room(p, U + 2 * T, vr, 2 * T, 'P', 'Suite premium', 50.4)
    for i in range(4):
        room(p, U + (5 + i) * T, vr, T, 'D', 'Deluxe', 25.2)
    save('C_R2', p.svg())
    p = base('C · TOITURE (+9,20) — pergola photovoltaïque + terrasse ≤ 19 pers., toiture végétalisée')
    p.rect(U, VC, 4 * T, D_BARRE, fill='#eef2f5', sw=1.2)
    for i in range(8):
        p.rect(U + 0.3 + i * 1.75, VC + 0.4, 1.55, D_BARRE - 0.8, fill='#3b5b7a', stroke='#2a4560', sw=0.4, op=0.35)
    p.txt(U + 2 * T, VC + 4.6, 'Pergola PV ≈ 25 kWc (structure acier galva, incombustible)', 8, 700)
    p.txt(U + 2 * T, VC + 5.4, 'terrasse privatisable ≤ 19 pers. : étirements, coucher de soleil', 7, fill=MUTED)
    p.rect(U + 5 * T, VC, 4 * T, D_BARRE, fill='#a7c98c', sw=1.2); p.txt(U + 7 * T, VC + 5.3, 'Toiture végétalisée extensive (sedum, graminées côtières)', 8, 700)
    p.txt(U + 7 * T, VC + 6.1, 'non accessible au public · rétention des eaux de pluie', 7, fill=MUTED)
    save('C_toit', p.svg())

def plans_B():
    TW, TD = D.TW, D.TD
    p = Plan(-1.6, V0 - 1.5, TW + 1.6, V0 + TD + 2.4, k=26)
    def frame(title):
        q = Plan(-1.8, V0 - 1.5, TW + 1.8, V0 + TD + 2.4, k=26)
        posts(q, 0, 2, [V0, V0 + 1.6, V0 + 8.6, V0 + TD])
        q.rect(TW, V0, 0.0001, 0.0001)
        q.rect(TW + 0.15, V0 + 0.2, 1.4, 6.0, fill='url(#h2)', sw=0.7); q.txt(TW + 0.85, V0 + 6.7, 'esc. ext.', 7)
        q.rect(0, V0, TW, 1.6, fill='#f6f1e7', sw=0.6); q.txt(TW / 2, V0 + 0.8, 'galerie nord', 7, fill=MUTED, italic=True)
        q.txt(TW / 2, V0 + TD + 1.5, title, 9, 700, fill='#a8502d'); q.north(q.w - 24, 26); q.scale(q.pad, q.h - 16)
        return q
    vr = V0 + 1.6
    q = frame('Case-tour — RDC et R+1 : junior + deluxe (lock-off)')
    room(q, 0, vr, 1.5 * T, 'J', 'Junior', 37.8); room(q, 1.5 * T, vr, TW - 1.5 * T, 'D', 'Deluxe', 25.2, pmr=False)
    q.txt(TW / 2, V0 + TD + 0.45, '◄ porte communicante = suite familiale 2 ch. ►', 7, fill='#2e7d7a')
    save('B_tour_R0R1', q.svg())
    q = frame('Case-tour — R+2 : suite premium sous chaume + mezzanine')
    room(q, 0, vr, TW, 'P', 'Suite premium', 63.0)
    q.rect(0.3, vr + 2.2, 3.0, 2.2, fill='none', sw=0.8, dash='3 2'); q.txt(1.8, vr + 3.3, 'mezzanine', 7, fill=MUTED, italic=True)
    save('B_tour_R2', q.svg())
    # case commune 15 × 7,6 m
    c = Plan(-2.0, -2.0, 17.6, 10.2, k=22)
    c.rect(-1.6, -1.6, 18.2, 10.8, fill='none', stroke='#b08a4a', dash='6 3')
    c.txt(7.5, -1.0, 'débords de chaume 1,6 m (double pyramide) = galerie couverte du restaurant', 7, fill='#b08a4a', italic=True)
    c.rect(0, 0, 15, 7.6, fill='none', sw=0.5)
    c.rect(0, 0, 4.4, 4.6, fill='#fbf3e6', sw=1.3); c.txt(2.2, 2.0, 'Réception', 8, 700); c.txt(2.2, 2.7, '+ boutique 20 m²', 7, fill=MUTED)
    c.rect(0, 4.6, 4.4, 3.0, fill='#fbf3e6', sw=1.2); c.txt(2.2, 5.8, 'Back-office', 7, 700); c.txt(2.2, 6.5, 'bagagerie 13', 7, fill=MUTED)
    c.rect(4.4, 0, 4.6, 5.0, fill='#efe9df', sw=1.3); c.txt(6.7, 2.2, 'Cuisine', 8, 700); c.txt(6.7, 2.9, 'plonge 23 m²', 7, fill=MUTED)
    c.rect(4.4, 5.0, 2.6, 2.6, fill='#e6ddd0', sw=1.0); c.txt(5.7, 6.1, 'Réserve', 7); c.txt(5.7, 6.7, 'CF 12', 7, fill=MUTED)
    c.rect(7.0, 5.0, 2.0, 2.6, fill='url(#h2)', sw=0.8); c.txt(8.0, 6.3, 'esc.+élév.', 6.5)
    c.rect(9.0, 0, 6.0, 7.6, fill='#fff7ea', sw=0.6, dash='3 2')
    for i in range(2):
        for j in range(3):
            c.circ(10.5 + i * 3.0, 1.4 + j * 2.4, 0.55, fill='#c9a477', op=0.9)
    c.txt(12.0, 0.6, 'Restaurant ouvert', 8, 700)
    c.rect(15.0, 0.6, 1.2, 6.4, fill='#c9a477', sw=0.6); c.txt(15.6, 3.8, 'deck', 7)
    c.txt(7.5, 9.2, 'CASE COMMUNE — RDC · R+1 sous chaume : sport, spa 2 cabines, lingerie (élévateur PMR + monte-linge)', 8.5, 700, fill='#a8502d')
    c.north(c.w - 24, 26); c.scale(c.pad, c.h - 14)
    save('B_case_commune', c.svg())

# ------------------------------------------------------------------ coupes bioclimatiques
def coupe(code):
    V0_ = D.V0C if code == 'C' else V0
    W, H, k = 780, 470, 20
    gx, gy = 120, 400                       # origine : limite nord au sol
    it = []
    X = lambda v: gx + v * k
    Y = lambda z: gy - z * k
    def r(v, z, w, h, fill, st=INK, sw=1):
        it.append(f'<rect x="{X(v):.1f}" y="{Y(z + h):.1f}" width="{w * k:.1f}" height="{h * k:.1f}" fill="{fill}" stroke="{st}" stroke-width="{sw}"/>')
    def t(v, z, s, size=9, w=400, fill=INK, anchor='middle'):
        it.append(f'<text x="{X(v):.1f}" y="{Y(z):.1f}" font-size="{size}" font-weight="{w}" fill="{fill}" text-anchor="{anchor}">{s}</text>')
    def arr(pts, col, sw=2.2, dash=None):
        da = f' stroke-dasharray="{dash}"' if dash else ''
        d = ' '.join(('M' if i == 0 else 'L') + f'{X(v):.1f},{Y(z):.1f}' for i, (v, z) in enumerate(pts))
        it.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{sw}"{da} marker-end="url(#a{col[1:]})"/>')
    depth = 28.5
    it.append(f'<rect x="{X(-1):.1f}" y="{Y(0):.1f}" width="{(depth + 2) * k:.1f}" height="22" fill="#e9dfcc"/>')
    it.append(f'<line x1="{X(-1):.1f}" y1="{Y(0):.1f}" x2="{X(depth + 1):.1f}" y2="{Y(0):.1f}" stroke="{INK}" stroke-width="1.5"/>')
    t(0, -1.0, 'limite N', 8, fill=MUTED); t(depth, -1.0, 'limite S', 8, fill=MUTED)
    it.append(f'<text x="{X(depth / 2):.1f}" y="{Y(-1.1):.1f}" font-size="8" fill="{MUTED}" text-anchor="middle">sable — nappe haute : pas de sous-sol · cuves EP semi-enterrées</text>')
    hz = [0, 3.2, 6.2, 9.2] if code == 'C' else [0, 3.4, 6.6, 9.8]
    if code in ('A', 'C'):
        b0 = V0_
        for i in range(3):
            z = hz[i]; h = hz[i + 1] - z
            r(b0, z, D_COURSIVE, 0.25, '#ccc'); r(b0 + D_COURSIVE, z, D_PIECE, h, '#fffaf0', sw=1.2)
            r(b0 + D_COURSIVE + D_PIECE, z, D_LOGGIA, 0.25, '#ccc')
            r(b0 + D_COURSIVE, z + h - 0.25, D_PIECE + D_LOGGIA, 0.25, '#bbb', sw=0.5)
            r(b0 + D_COURSIVE, z + 0.25, 2.0, 2.3, '#d7e9ee', sw=0.6)
        r(b0, hz[3], D_BARRE, 0.35, '#999')
        if code == 'A':
            # pavillon chaume (coupe transversale du restaurant) + filets
            it.append(f'<path d="M{X(b0 - 1.2):.1f},{Y(12.4):.1f} L{X(b0 + D_BARRE / 2):.1f},{Y(16.0):.1f} L{X(b0 + D_BARRE + 1.2):.1f},{Y(12.4):.1f} Z" fill="#d8b878" stroke="#8a6a35"/>')
            for v in (b0 + 0.3, b0 + D_BARRE - 0.3):
                r(v - 0.15, 10.15, 0.3, 2.3, '#8a6a35', sw=0)
            it.append(f'<rect x="{X(b0):.1f}" y="{Y(15.1):.1f}" width="{D_BARRE * k:.1f}" height="{5 * k:.1f}" fill="none" stroke="#1f3d2b" stroke-dasharray="2 3"/>')
            t(b0 + D_BARRE / 2, 15.4 + 1.6, 'cage de foot (filets h 5 m) — en arrière-plan', 8, fill='#1f3d2b')
            t(b0 + D_BARRE / 2, 13.0, 'restaurant sous chaume', 8, 700)
        else:
            r(b0 + 4.6, hz[3] + 0.35, D_BARRE - 4.6, 0.25, '#8fbf6e', sw=0.4)
            r(b0 + 0.2, hz[3] + 2.6, 4.2, 0.18, '#3b5b7a', sw=0.4)
            for v in (b0 + 0.4, b0 + 4.0):
                r(v, hz[3] + 0.35, 0.15, 2.3, '#777', sw=0)
            t(b0 + 2.3, hz[3] + 3.3, 'pergola PV', 8, 700)
            t(b0 + 7.8, hz[3] + 1.3, 'toiture végétalisée', 8, fill='#3d7a47')
            # écran planté côté voisin nord
            it.append(f'<line x1="{X(b0 - 0.6):.1f}" y1="{Y(0):.1f}" x2="{X(b0 - 0.6):.1f}" y2="{Y(8.5):.1f}" stroke="#5d8a4c" stroke-width="3" stroke-dasharray="2 2"/>')
            t(b0 - 0.8, 8.9, 'écran planté', 7, fill='#3d7a47', anchor='end')
            # case-restaurant
            cr = 17.6
            r(cr, 0, 7.4, 0.25, '#ccc'); r(cr + 0.2, 0.25, 0.25, 3.0, '#8a6a35', sw=0); r(cr + 7.0, 0.25, 0.25, 3.0, '#8a6a35', sw=0)
            it.append(f'<path d="M{X(cr - 1.4):.1f},{Y(3.2):.1f} L{X(cr + 3.7):.1f},{Y(7.4):.1f} L{X(cr + 8.8):.1f},{Y(3.2):.1f} Z" fill="#d8b878" stroke="#8a6a35"/>')
            t(cr + 3.7, 1.6, 'case-restaurant ouverte', 8, 700)
            # prospect H/2
            it.append(f'<line x1="{X(0):.1f}" y1="{Y(0):.1f}" x2="{X(b0):.1f}" y2="{Y(hz[3] + 0.6):.1f}" stroke="#a8502d" stroke-dasharray="4 3"/>')
            t(-0.6, 11.5, 'prospect nord : L = 5,0 m ≥ H/2 = 4,9 m', 8, 700, fill='#a8502d', anchor='start')
        # jardin
        for v, hgt in ([(19, 7), (24, 9), (27.0, 8)] if code == 'A' else [(27.0, 7), (28.0, 9)]):
            it.append(f'<line x1="{X(v):.1f}" y1="{Y(0):.1f}" x2="{X(v):.1f}" y2="{Y(hgt):.1f}" stroke="#6b5a3a" stroke-width="2"/>')
            it.append(f'<ellipse cx="{X(v):.1f}" cy="{Y(hgt):.1f}" rx="{2.6 * k:.1f}" ry="{1.4 * k:.1f}" fill="#8fb27a" opacity="0.7"/>')
        r(V0_ + D_BARRE + 2.4, -1.4, 2.5, 1.4, '#9fd3d0', sw=0.6); t(V0_ + D_BARRE + 3.6, -2.6 + 0.0, '', 7)
        it.append(f'<line x1="{X(1.8):.1f}" y1="{Y(0):.1f}" x2="{X(1.8):.1f}" y2="{Y(6):.1f}" stroke="#6b5a3a" stroke-width="2"/><ellipse cx="{X(1.8):.1f}" cy="{Y(6):.1f}" rx="{2.2 * k:.1f}" ry="{1.4 * k:.1f}" fill="#8fb27a" opacity="0.7"/>')
        top = 16.0 if code == 'A' else 12.0
    else:
        b0 = V0_
        for i in range(2):
            z = hz[i]; h = hz[i + 1] - z
            r(b0, z, 1.6, 0.25, '#ccc'); r(b0 + 1.6, z, 7.0, h, '#fffaf0', sw=1.2); r(b0 + 8.6, z, 1.8, 0.25, '#ccc')
            r(b0 + 1.6, z + 0.25, 2.0, 2.3, '#d7e9ee', sw=0.6)
        r(b0 + 1.6, 6.6, 7.0, 2.6, '#fffaf0', sw=1.2); r(b0 + 1.6, 6.6, 2.0, 2.3, '#d7e9ee', sw=0.6)
        it.append(f'<path d="M{X(b0 - 1.4):.1f},{Y(8.6):.1f} L{X(b0 + 5.2):.1f},{Y(14.0):.1f} L{X(b0 + TDB + 1.4):.1f},{Y(8.6):.1f} Z" fill="#d8b878" stroke="#8a6a35"/>'.replace('TDB', str(D.TD)) if False else
                  f'<path d="M{X(b0 - 1.4):.1f},{Y(8.4):.1f} L{X(b0 + D.TD / 2):.1f},{Y(14.0):.1f} L{X(b0 + D.TD + 1.4):.1f},{Y(8.4):.1f} Z" fill="#d8b878" stroke="#8a6a35"/>')
        r(b0 + 2.4, 9.6, 3.0, 0.2, '#bbb'); t(b0 + 3.9, 10.1, 'mezz.', 7, fill=MUTED)
        # lanterne
        r(b0 + D.TD / 2 - 0.6, 12.6, 1.2, 0.9, '#f3e7c9', sw=0.6)
        # case commune + pelouse
        cc0 = 17.0
        r(cc0, 0, 8.0, 3.4, '#fffaf0', sw=1.2)
        it.append(f'<path d="M{X(cc0 - 1.6):.1f},{Y(4.2):.1f} L{X(cc0 + 4):.1f},{Y(9.5):.1f} L{X(cc0 + 9.6):.1f},{Y(4.2):.1f} Z" fill="#d8b878" stroke="#8a6a35"/>')
        r(cc0 + 0.6, 3.4, 6.8, 0.25, '#bbb'); t(cc0 + 4, 1.6, 'case commune', 8, 700)
        r(26.3, -1.4, 2.0, 1.4, '#9fd3d0', sw=0.6)
        for v, hgt in [(15.2, 6), (1.8, 6)]:
            it.append(f'<line x1="{X(v):.1f}" y1="{Y(0):.1f}" x2="{X(v):.1f}" y2="{Y(hgt):.1f}" stroke="#6b5a3a" stroke-width="2"/><ellipse cx="{X(v):.1f}" cy="{Y(hgt):.1f}" rx="{2.0 * k:.1f}" ry="{1.3 * k:.1f}" fill="#8fb27a" opacity="0.7"/>')
        top = 14.0
    # soleil : 21 déc. h = 61,4° (sud), 21 juin h = 71,8° (nord) — latitude 5,2° N
    sv = V0_ + (D_BARRE if code == 'A' else D.TD)
    for ang, side, col, lab in [(61.4, 1, '#d9a21b', 'midi 21 déc. — h 61°'), (71.8, -1, '#e0b84a', 'midi 21 juin — h 72°')]:
        L = 6.5
        base_v = sv if side == 1 else V0_
        zt = (3.4 if code == 'A' else 3.4)
        x2, z2 = base_v + side * L * math.cos(math.radians(ang)), zt + L * math.sin(math.radians(ang))
        arr([(x2, z2), (base_v - side * 0.2, zt + 0.1)], col, 1.6, '5 3')
        t(x2 + side * 0.3, z2 + 0.5, lab, 8, fill='#8a6410', anchor='start' if side == 1 else 'end')
    # vent
    arr([(depth + 0.5, 1.6), (V0_ + 5, 1.6), (V0_ - 2.5, 2.0)], '#2e7d7a', 2.4)
    arr([(depth + 0.5, 5.0), (V0_ + 4, 5.0), (V0_ - 2.5, 5.4)], '#2e7d7a', 2.4)
    t(depth - 3.0, 2.3, 'brise SO rafraîchie par le jardin', 8, 600, fill='#2e7d7a')
    arr([(V0_ + 5, top - 1.0), (V0_ + 5, top + 1.6)], '#a8502d', 1.8)
    t(V0_ + 5.4, top + 1.9, 'air chaud évacué sous chaume' if code != 'C' else 'toiture ventilée et végétalisée', 8, fill='#a8502d', anchor='start')
    arr([(V0_ + 9.5 if code == 'A' else V0_ + 9, 9.6), (V0_ + 12.5, 0.2)], '#5a86b5', 1.5, '2 3')
    t(V0_ + 12.7, 1.0, 'EP → cuves', 8, fill='#5a86b5', anchor='start')
    for z, lab in zip(hz, ['±0,00'] + [('+%.2f' % h).replace('.', ',') for h in hz[1:]]):
        it.append(f'<line x1="{X(-1.0):.1f}" y1="{Y(z):.1f}" x2="{X(-0.4):.1f}" y2="{Y(z):.1f}" stroke="{INK}"/>')
        t(-1.2, z - 0.1, lab, 7, anchor='end')
    defs = ''.join(f'<marker id="a{c[1:]}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker>'
                   for c in ['#2e7d7a', '#a8502d', '#d9a21b', '#e0b84a', '#5a86b5'])
    t(depth / 2, 18.6, f'NORD  ◄ — coupe transversale {code} — ►  SUD (océan à ~300 m)', 9, 700)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Inter, sans-serif"><defs>{defs}</defs>' + '\n'.join(it) + '</svg>')
    save(f'coupe_{code}', svg)

# ------------------------------------------------------------------ axonométries
EL = math.radians(32)
def proj(u, v, z):
    sx = (u + v) / math.sqrt(2)
    sy = z * math.cos(EL) + (u - v) / math.sqrt(2) * math.sin(EL)
    dep = (u - v) / math.sqrt(2) * math.cos(EL) - z * math.sin(EL)
    return sx, sy, dep

class Axo:
    def __init__(self):
        self.faces = []
    def face(self, pts, fill, st='#3b3b35', sw=0.6, op=1):
        P3 = [proj(*p) for p in pts]
        dep = sum(p[2] for p in P3) / len(P3)
        self.faces.append((dep, [(p[0], p[1]) for p in P3], fill, st, sw, op))
    def box(self, u, v, w, d, z, h, top='#f4ecdc', south='#e6d6b8', west='#d9c6a2'):
        u1, v1, z1 = u + w, v + d, z + h
        self.face([(u, v1, z), (u1, v1, z), (u1, v1, z1), (u, v1, z1)], south)
        self.face([(u, v, z), (u, v1, z), (u, v1, z1), (u, v, z1)], west)
        self.face([(u, v, z1), (u1, v, z1), (u1, v1, z1), (u, v1, z1)], top)
    def pyramid(self, u, v, w, d, z, h, col='#cfa862'):
        a = (u + w / 2, v + d / 2, z + h)
        self.face([(u, v + d, z), (u + w, v + d, z), a], col)
        self.face([(u, v, z), (u, v + d, z), a], '#b88f4c')
        self.face([(u + w, v, z), (u + w, v + d, z), a], '#d8b878')
        self.face([(u, v, z), (u + w, v, z), a], '#c49a55')
    def flat(self, poly_uv, z, fill, st='none', op=1):
        self.face([(u, v, z) for u, v in poly_uv], fill, st, 0.5, op)
    def tree(self, u, v, h=7, r=2.3, palm=False):
        sx, sy, dep = proj(u, v, h)
        bx, by, _ = proj(u, v, 0)
        self.faces.append((dep - 0.01, ('tree', sx, sy, bx, by, r, palm), None, None, None, None))
    def svg(self, W=900, H=560, extra=''):
        allp = [pt for f in self.faces if f[2] is not None for pt in f[1]]
        xs, ys = [p[0] for p in allp], [p[1] for p in allp]
        k = min((W - 60) / (max(xs) - min(xs)), (H - 60) / (max(ys) - min(ys)))
        ox, oy = 30 - min(xs) * k, H - 30 + min(ys) * k
        out = []
        for dep, pts, fill, st, sw, op in sorted(self.faces, key=lambda f: -f[0]):
            if fill is None:
                _, sx, sy, bx, by, r, palm = pts
                X1, Y1, X0, Y0 = ox + sx * k, oy - sy * k, ox + bx * k, oy - by * k
                out.append(f'<line x1="{X0:.1f}" y1="{Y0:.1f}" x2="{X1:.1f}" y2="{Y1:.1f}" stroke="#6b5a3a" stroke-width="{2.2 if palm else 3}"/>')
                if palm:
                    out.append(''.join(f'<path d="M{X1:.1f},{Y1:.1f} q{r * k * 0.5 * math.cos(a):.1f},{-r * k * 0.4:.1f} {r * k * math.cos(a):.1f},{r * k * 0.35 * abs(math.sin(a)) + 4:.1f}" fill="none" stroke="#4f7a43" stroke-width="2.4"/>' for a in [0, 0.8, 1.6, 2.4, 3.14, 3.9, 4.7, 5.5]))
                else:
                    out.append(f'<ellipse cx="{X1:.1f}" cy="{Y1:.1f}" rx="{r * k:.1f}" ry="{r * k * 0.8:.1f}" fill="#7da866" stroke="#557d45" stroke-width="0.8" opacity="0.92"/>')
                continue
            d = 'M' + ' L'.join(f'{ox + x * k:.1f},{oy - y * k:.1f}' for x, y in pts) + ' Z'
            out.append(f'<path d="{d}" fill="{fill}" stroke="{st}" stroke-width="{sw}" opacity="{op}" stroke-linejoin="round"/>')
        return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Inter, sans-serif">' + ''.join(out) + extra + '</svg>'

def site_uv_poly():
    f, _ = bar_frame()
    # inverse : on échantillonne le contour du terrain dans le repère (u,v)
    (x1, y1), (x2, y2) = P['B1'], P['B2']
    L = math.hypot(x2 - x1, y2 - y1); ux, uy = (x2 - x1) / L, (y2 - y1) / L
    vx, vy = uy, -ux
    return [((x - x1) * ux + (y - y1) * uy, (x - x1) * vx + (y - y1) * vy) for x, y in SITE.exterior.coords]

def ground(ax, V):
    ax.flat(site_uv_poly(), 0, '#cfe0bb', '#55704a')
    def uvpoly(g):
        f, _ = bar_frame(); (x1, y1), (x2, y2) = P['B1'], P['B2']
        L = math.hypot(x2 - x1, y2 - y1); ux, uy = (x2 - x1) / L, (y2 - y1) / L
        return [((x - x1) * ux + (y - y1) * uy, (x - x1) * uy - (y - y1) * ux) for x, y in g.exterior.coords]
    for cat in ['allee', 'evergreen', 'deck', 'pelouse', 'piscine']:
        for _, g in V['shapes'].get(cat, []):
            ax.flat(uvpoly(g.intersection(SITE)), 0.02, {'allee': '#efe6d2', 'evergreen': '#d9dcc0', 'deck': '#c9a477', 'pelouse': '#7cae5e', 'piscine': '#7cc6c6'}[cat])

def axo_A():
    ax = Axo(); V = D.VARIANTS['A']; ground(ax, V); U = D.U0
    for i in range(3):
        z = [0, 3.4, 6.6][i]; h = [3.4, 3.2, 3.2][i]
        ax.box(U, V0 + D_COURSIVE, 9 * T, D_PIECE, z, h, south='#efe2c8')
        ax.box(U, V0 + D_COURSIVE + D_PIECE, 9 * T, D_LOGGIA, z + h - 0.3, 0.3, south='#b5532e')
        for j in range(10):
            ax.box(U + j * T - 0.15, V0 + D_BARRE - 0.3, 0.3, 0.3, z, h, south='#8a6a45', west='#7a5a35')
    ax.box(U - 0.3, V0 + D_COURSIVE - 0.3, 0.3, D_PIECE + 0.6, 0, 9.8, south='#5f8f4f', west='#5f8f4f')
    ax.box(U, V0, 9 * T, D_BARRE, 9.8, 0.35, top='#e8e0d0')
    ax.box(U + 5 * T, V0, 4 * T, D_BARRE, 10.15, 0.05, top='#6fa652')
    ax.face([(U + 5 * T, V0 + D_BARRE, 10.2), (U + 9 * T, V0 + D_BARRE, 10.2), (U + 9 * T, V0 + D_BARRE, 15.2), (U + 5 * T, V0 + D_BARRE, 15.2)], 'none', '#1f3d2b', 0.8)
    ax.face([(U + 5 * T, V0, 15.2), (U + 9 * T, V0, 15.2), (U + 9 * T, V0 + D_BARRE, 15.2), (U + 5 * T, V0 + D_BARRE, 15.2)], 'none', '#1f3d2b', 0.5)
    for j in range(5):
        for v in (V0, V0 + D_BARRE):
            ax.box(U + j * T * 1.0 - 0.15, v - 0.15, 0.3, 0.3, 10.15, 2.4, south='#8a6a45', west='#7a5a35')
    ax.pyramid(U - 1.2, V0 - 1.2, 4 * T + 2.4, D_BARRE + 2.4, 12.5, 4.0)
    ax.box(D.U0 - 3.9, V0, 3.5, 5.0, 0, 2.6, top='#7da866')
    for u, v, kind in V['trees']:
        ax.tree(u, v, 9 if kind == 'palmier' else 7, 1.6 if kind == 'palmier' else 2.6, kind == 'palmier')
    save('axo_A', ax.svg())

def axo_B():
    ax = Axo(); V = D.VARIANTS['B']; ground(ax, V)
    for u in D.TU:
        for i, (z, h) in enumerate([(0, 3.4), (3.4, 3.2), (6.6, 2.0)]):
            ax.box(u, V0 + 1.6, D.TW, 7.0, z, h, south='#efe2c8')
            ax.box(u, V0 + 8.6, D.TW, 1.8, z + h - 0.3, 0.3, south='#b5532e')
        for j in range(3):
            ax.box(u + j * (D.TW / 2) - 0.15, V0 + D.TD - 0.3, 0.3, 0.3, 0, 8.6, south='#8a6a45', west='#7a5a35')
        ax.pyramid(u - 1.4, V0 - 1.4, D.TW + 2.8, D.TD + 2.8, 8.4, 5.6)
    ax.box(7.0, 17.0, 14.0, 8.0, 0, 3.4, south='#efe2c8')
    ax.pyramid(5.4, 15.4, 8.6, 11.2, 4.2, 5.3); ax.pyramid(14.0, 15.4, 8.6, 11.2, 4.2, 5.3)
    ax.box(2.0, V0, 3.5, 5.0, 0, 2.6, top='#7da866')
    for (gx, gv) in [(23.6, 20.8), (35.4, 20.8)]:
        ax.box(gx, gv - 1.2, 0.2, 2.4, 0, 1.2, south='#ffffff', west='#eeeeee', top='#fff')
    for u, v, kind in V['trees']:
        ax.tree(u, v, 9 if kind == 'palmier' else 7, 1.6 if kind == 'palmier' else 2.6, kind == 'palmier')
    save('axo_B', ax.svg())

# ------------------------------------------------------------------ graphique : occupation du sol
PAL = {'Bâti': '#a8502d', 'Minéral (piscine, decks, allées, stationnement)': '#c08a2a', 'Végétal en pleine terre': '#3d7a47'}
def chart_sols():
    s0 = {'Bâti': 695, 'Minéral (piscine, decks, allées, stationnement)': 650 - 20, 'Végétal en pleine terre': 20}
    data = [('Programme d’origine*', s0)]
    for c in 'ABC':
        s, _ = D.biotope(c)
        data.append((f'{c} — {D.VARIANTS[c]["nom"]}', {
            'Bâti': s['bati'] + s.get('tech', 0),
            'Minéral (piscine, decks, allées, stationnement)': s['piscine'] + s['deck'] + s['allee'] + s['evergreen'],
            'Végétal en pleine terre': s['pleine_terre'] + s.get('pelouse', 0)}))
    W, rowh, x0, x1 = 620, 44, 150, 600
    top = 30 + 20 * len(PAL)
    H = top + rowh * len(data) + 34
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Inter, sans-serif">']
    for i, (lab, col) in enumerate(PAL.items()):
        out.append(f'<rect x="{x0}" y="{8 + i * 20}" width="12" height="12" rx="3" fill="{col}"/><text x="{x0 + 18}" y="{18 + i * 20}" font-size="12" fill="{INK}">{lab}</text>')
    for i, (name, vals) in enumerate(data):
        y = top + i * rowh
        tot = 1345 if i == 0 else sum(vals.values())
        out.append(f'<text x="{x0 - 8}" y="{y + 18}" font-size="12" text-anchor="end" fill="{INK}" font-weight="600">{name}</text>')
        x = x0
        for lab, col in PAL.items():
            v = vals[lab]; w = (x1 - x0) * v / 1345
            out.append(f'<rect x="{x:.1f}" y="{y}" width="{max(w - 2, 1.5):.1f}" height="28" rx="4" fill="{col}"><title>{lab} : {v:.0f} m²</title></rect>')
            if w > 40:
                out.append(f'<text x="{x + w / 2 - 1:.1f}" y="{y + 18.5}" font-size="11.5" text-anchor="middle" fill="#fff" font-weight="700">{v / 1120 * 100:.0f} %</text>')
            x += w
    xe = x0 + (x1 - x0) * 1120 / 1345
    out.append(f'<line x1="{xe:.1f}" y1="{top - 8}" x2="{xe:.1f}" y2="{top + rowh * len(data) - 8}" stroke="{INK}" stroke-dasharray="3 3"/>'
               f'<text x="{xe:.1f}" y="{top + rowh * len(data) + 6}" font-size="10.5" text-anchor="middle" fill="{INK}">limite du terrain : 1 120 m²</text>')
    out.append(f'<text x="{x0}" y="{H - 4}" font-size="10" fill="{MUTED}">* 1 345 m² d’emprises au sol pour 1 120 m² de terrain : +20 %. Pourcentages rapportés au terrain.</text></svg>')
    save('chart_sols', ''.join(out))

def situation():
    """Schéma de situation : cordon de Jacqueville entre lagune et océan."""
    W, H = 760, 300
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="Inter, sans-serif">',
         '<defs><marker id="ar" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#2e7d7a"/></marker></defs>',
         f'<rect width="{W}" height="95" fill="#cfe5e6"/><text x="20" y="40" font-size="15" fill="#2e6f72" font-weight="700">LAGUNE ÉBRIÉ</text>',
         f'<path d="M0,95 C200,85 420,108 {W},92 L{W},215 C520,224 260,206 0,218 Z" fill="#efe6d2"/>',
         f'<path d="M0,218 C260,206 520,224 {W},215 L{W},230 C520,240 260,222 0,234 Z" fill="#f7efd9"/>',
         f'<rect y="232" width="{W}" height="{H - 232}" fill="#9fcfd6"/><text x="20" y="{H - 22}" font-size="15" fill="#1f5f6a" font-weight="700">OCÉAN ATLANTIQUE</text>',
         '<path d="M70,150 C220,140 420,160 690,148" stroke="#c9bfa9" stroke-width="5" fill="none"/>',
         '<text x="80" y="140" font-size="11" fill="#6b6b63">axe routier de Jacqueville</text>',
         '<rect x="330" y="160" width="26" height="20" fill="#a8502d" transform="rotate(-6 343 170)"/>',
         '<text x="365" y="176" font-size="13" font-weight="700" fill="#a8502d">LE ONZE · lot 2511</text>',
         '<line x1="343" y1="182" x2="343" y2="228" stroke="#1e2a24" stroke-dasharray="3 3"/>',
         '<text x="350" y="208" font-size="11" fill="#1e2a24">≈ 300 m de la plage</text>',
         '<path d="M610,96 L610,10" stroke="#6b6b63" stroke-width="5"/><text x="620" y="30" font-size="11" fill="#3c4a44">pont de Jacqueville</text><text x="620" y="45" font-size="10" fill="#6b6b63">vers Abidjan (≈ 50 km)</text>',
         '<path d="M110,280 L170,240" stroke="#2e7d7a" stroke-width="3" marker-end="url(#ar)"/><text x="180" y="252" font-size="11" fill="#1f5f6a" font-weight="600">brise SO</text>',
         '<text x="20" y="128" font-size="10" fill="#6b6b63" font-style="italic">Schéma sans échelle</text>',
         '<g transform="translate(720,130)"><path d="M0,-14 L5,8 L0,4 L-5,8 Z" fill="#1e2a24"/><text y="-18" font-size="10" font-weight="700" text-anchor="middle">N</text></g></svg>']
    save('situation', ''.join(o))

def typo_module():
    """Paire lock-off junior + deluxe à grande échelle."""
    p = Plan(-0.8, V0 - 0.3, 2.5 * T + 0.8, V0 + D_BARRE + 1.6, k=46)
    p.rect(0, V0, 2.5 * T, D_COURSIVE, fill='#f6f1e7', sw=0.6)
    p.txt(1.25 * T, V0 + 0.9, 'coursive nord 1,80 m — air frais, ombre', 9, fill=MUTED, italic=True)
    room(p, 0, V0 + D_COURSIVE, 1.5 * T, 'J', 'Suite junior', 37.8)
    room(p, 1.5 * T, V0 + D_COURSIVE, T, 'D', 'Deluxe', 25.2)
    p.rect(1.5 * T - 0.06, V0 + D_COURSIVE + 3.6, 0.12, 0.9, fill='#2e7d7a', stroke='#2e7d7a')
    p.txt(1.5 * T, V0 + D_COURSIVE + 4.9, 'porte communicante', 8, 700, fill='#2e7d7a')
    p.txt(1.25 * T, V0 + D_BARRE + 0.6, 'loggias 1,80 m — persiennes coulissantes iroko', 9, fill=MUTED, italic=True)
    for i, (v, lab) in enumerate([(V0, '1,80'), (V0 + D_COURSIVE, '2,00'), (V0 + D_COURSIVE + 2.0, '5,00'), (V0 + D_COURSIVE + D_PIECE, '1,80')]):
        nxt = [V0 + D_COURSIVE, V0 + D_COURSIVE + 2.0, V0 + D_COURSIVE + D_PIECE, V0 + D_BARRE][i]
        p.line([(-0.4, v), (-0.4, nxt)], sw=0.8); p.txt(-0.62, (v + nxt) / 2, lab, 8)
    p.line([(0, V0 + D_BARRE + 1.2), (2.5 * T, V0 + D_BARRE + 1.2)], sw=0.8)
    p.txt(0.75 * T, V0 + D_BARRE + 1.0, '5,40', 8); p.txt(2.0 * T, V0 + D_BARRE + 1.0, '3,60', 8)
    p.north(p.w - 22, 24)
    save('typo_module', p.svg())

if __name__ == '__main__':
    site_analysis(); plan_masse('A'); plan_masse('B'); plan_masse('C'); plans_A(); plans_B(); plans_C()
    coupe('A'); coupe('B'); coupe('C'); chart_sols(); situation(); typo_module()
    print(sorted(os.listdir(OUT)))
