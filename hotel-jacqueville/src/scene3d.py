"""Export des maquettes 3D (repère u,v,z) au format JSON pour le rendu Three.js."""
import json, math, os, sys
import design as D
from drawings import site_uv_poly, V0, T
from geo import D_COURSIVE, D_PIECE, D_LOGGIA, D_BARRE, SITE, bar_frame, P

OUT = os.path.join(os.path.dirname(__file__), '..', 'build', '3d')
os.makedirs(OUT, exist_ok=True)
C = dict(slab='#e9e4da', wall='#f4efe6', render='#efe7da', wood='#7a5232', louvre='#9a6b42', brick='#b5653a',
         chaume='#c8a46a', green='#5f8f4f', turf='#5fa043', glass='#9fb9bd', grass='#a9c98a', sand='#e7dcc4',
         deck='#b88a5a', water='#4fb3b8', road='#cfc9bd', neigh='#d8d2c6', roofn='#a65a3a', path='#efe6d2', ever='#c9d4ab')

def uvpoly(g):
    (x1, y1), (x2, y2) = P['B1'], P['B2']
    L = math.hypot(x2 - x1, y2 - y1); ux, uy = (x2 - x1) / L, (y2 - y1) / L
    return [((x - x1) * ux + (y - y1) * uy, (x - x1) * uy - (y - y1) * ux) for x, y in g.exterior.coords]

class S:
    def __init__(self): self.o = []
    def box(self, u, v, z, w, d, h, c): self.o.append(dict(t='box', u=u, v=v, z=z, w=w, d=d, h=h, c=c))
    def pyr(self, u, v, z, w, d, h, c): self.o.append(dict(t='pyr', u=u, v=v, z=z, w=w, d=d, h=h, c=c))
    def poly(self, pts, z, c): self.o.append(dict(t='poly', p=pts, z=z, c=c))
    def tree(self, u, v, h, r, palm): self.o.append(dict(t='tree', u=u, v=v, h=h, r=r, palm=palm))
    def net(self, u, v, z, w, d, h): self.o.append(dict(t='net', u=u, v=v, z=z, w=w, d=d, h=h))

def context(s, V):
    s.poly([(-30, -25), (75, -25), (75, 55), (-30, 55)], -0.05, '#e3e4d6')
    s.poly([(-12, -20), (-3.5, -20), (2.6, 50), (-6, 50)], -0.03, C['road'])
    sp = site_uv_poly()
    s.poly(sp, 0.0, C['grass'])
    for (a, b) in zip(sp[:-1], sp[1:]):
        s.o.append(dict(t='edge', a=a, b=b))
    for cat, col in [('allee', C['path']), ('evergreen', C['ever']), ('deck', C['deck']), ('pelouse', C['turf']), ('piscine', C['water'])]:
        for _, g in V['shapes'].get(cat, []):
            s.poly(uvpoly(g.intersection(SITE)), 0.03 if cat != 'piscine' else 0.04, col)
    # voisinage (volumes indicatifs)
    for (u, v, w, d, h) in [(45, 2, 10, 9, 3.2), (47, 16, 9, 10, 6.4), (8, 36, 11, 8, 3.2), (24, 35, 10, 9, 3.2), (6, -22, 12, 9, 3.2), (26, -21, 10, 9, 6.4)]:
        s.box(u, v, 0, w, d, h, C['neigh']); s.pyr(u - 0.5, v - 0.5, h, w + 1, d + 1, 2.2, C['roofn'])
    for u, v, kind in V['trees']:
        s.tree(u, v, 10 if kind == 'palmier' else 7.5, 1.8 if kind == 'palmier' else 2.8, kind == 'palmier')
    s.box(2.0, V0, 0, 3.5, 5.0, 2.6, C['render']); s.box(2.0, V0, 2.6, 3.5, 5.0, 0.25, C['green'])

def louvres(s, u0, u1, v, z, h, step=0.3):
    n = int((u1 - u0) / step)
    for i in range(n):
        s.box(u0 + i * step + 0.05, v - 0.06, z, 0.07, 0.06, h, C['louvre'])

def scene_A():
    s = S(); V = D.VARIANTS['A']; context(s, V); U = D.U0; L = 9 * T
    lv = [(0, 3.4), (3.4, 3.2), (6.6, 3.2)]
    for i, (z, h) in enumerate(lv):
        s.box(U, V0, z, L, D_BARRE, 0.25, C['slab'])
        s.box(U + 0.05, V0 + D_COURSIVE, z + 0.25, L - 0.1, D_PIECE, h - 0.25, C['wall'])
        if i > 0:
            s.box(U, V0, z + 0.25, L, 0.08, 1.0, C['wood'])              # garde-corps coursive
        louvres(s, U, U + L, V0 + D_BARRE, z + 0.25, h - 0.55)          # persiennes coulissantes des loggias (mi-ouvertes)
    for j in range(10):
        for v in (V0, V0 + D_BARRE - 0.3):
            s.box(U + j * T - 0.15, v, 0, 0.3, 0.3, 9.8, C['wood'])
    for u in (U - 0.35, U + L + 0.05):
        s.box(u, V0 + D_COURSIVE, 0, 0.3, D_PIECE, 9.8, C['green'])      # pignons végétalisés E/O
    s.box(U, V0, 9.8, L, D_BARRE, 0.35, C['slab'])
    s.box(U, V0, 10.15, L, 0.1, 1.1, C['render']); s.box(U, V0 + D_BARRE - 0.1, 10.15, L, 0.1, 1.1, C['render'])
    s.box(U + 5 * T, V0, 10.15, 4 * T, D_BARRE, 0.06, C['turf'])
    s.net(U + 5 * T, V0, 10.2, 4 * T, D_BARRE, 5.0)
    s.box(U, V0, 10.15, 2 * T, 4.2, 2.8, C['render'])                    # cuisine
    for j in range(5):
        for v in (V0 - 0.9, V0 + D_BARRE + 0.6):
            s.box(U + j * T - 0.15, v, 10.15, 0.3, 0.3, 2.6, C['wood'])
    s.pyr(U - 1.4, V0 - 1.4, 12.75, 4 * T + 2.8, D_BARRE + 2.8, 4.2, C['chaume'])
    s.box(U - 1.6, V0 + 2.0, 0, 1.3, 6.0, 0.2, C['wood'])
    for k in range(12):
        s.box(U - 1.6, V0 + 2.0 + k * 0.5, k * 0.85, 1.3, 0.5, 0.15, C['wood'])   # escalier extérieur ouest (2e dégagement)
    return s.o

def scene_B():
    s = S(); V = D.VARIANTS['B']; context(s, V); TW, TD = D.TW, D.TD
    for u in D.TU:
        for i, (z, h) in enumerate([(0, 3.4), (3.4, 3.2), (6.6, 2.0)]):
            s.box(u, V0, z, TW, TD, 0.25, C['slab'])
            s.box(u + 0.05, V0 + 1.6, z + 0.25, TW - 0.1, 7.0, h - 0.25, C['wall'])
            if h > 2.5:
                louvres(s, u, u + TW, V0 + TD, z + 0.25, h - 0.55)
        for j in range(3):
            for v in (V0, V0 + TD - 0.3):
                s.box(u + j * TW / 2 - 0.15, v, 0, 0.3, 0.3, 8.6, C['wood'])
        s.box(u - 0.3, V0 + 1.6, 0, 0.3, 7.0, 6.6, C['brick'])               # claustra brique de terre pignon
        s.pyr(u - 1.5, V0 - 1.5, 8.6, TW + 3.0, TD + 3.0, 6.0, C['chaume'])
    for g in V['stairs']:
        (u0, v0), (u1, v1) = uvpoly(g)[0], uvpoly(g)[2]
        ua, ub, va, vb = min(u0, u1), max(u0, u1), min(v0, v1), max(v0, v1)
        for k in range(14):
            s.box(ua, va + k * (vb - va) / 14, k * 0.48, ub - ua, (vb - va) / 14, 0.12, C['wood'])
    s.box(7.0, 17.0, 0, 14.0, 8.0, 0.3, C['slab']); s.box(7.0, 17.0, 0.3, 9.0, 8.0, 3.1, C['wall'])
    for j in range(5):
        for v in (17.0, 24.7):
            s.box(7.0 + j * 3.5 - 0.15, v, 0, 0.3, 0.3, 4.2, C['wood'])
    s.pyr(5.4, 15.4, 4.2, 8.6, 11.2, 5.4, C['chaume']); s.pyr(14.0, 15.4, 4.2, 8.6, 11.2, 5.4, C['chaume'])
    for gu in (23.4, 35.4):
        s.box(gu, 19.6, 0, 0.12, 2.6, 1.3, '#ffffff')
    return s.o

if __name__ == '__main__':
    json.dump({'A': scene_A(), 'B': scene_B()}, open(os.path.join(OUT, 'scenes.json'), 'w'))
    print('ok')
