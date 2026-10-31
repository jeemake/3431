"""Géométrie du terrain (lot 2511, îlot 225, Jacqueville) et des variantes A / B.

Repère local : origine B4, axe x le long de B4->B3 (limite sud), axe y vers le nord.
Les angles en B4 et B3 valent 100 gr (90°) : le terrain est un trapèze rectangle.
"""
import math
from shapely.geometry import Polygon, box, Point, LineString
from shapely import affinity

# Bornes (UTM 30N, levé N'GUESSAN 27-01-2026)
BORNES = {'B1': (351038.835, 575741.923), 'B2': (351079.462, 575738.749),
          'B3': (351082.214, 575714.794), 'B4': (351042.475, 575710.230)}
# azimut de B4->B3 : 83,4° -> le repère local est tourné de 6,6° par rapport au nord vrai
_dx, _dy = (BORNES['B3'][0] - BORNES['B4'][0], BORNES['B3'][1] - BORNES['B4'][1])
ROT = math.degrees(math.atan2(_dy, _dx))          # ≈ 6.6° (axe x au-dessus de l'est)

def to_local(e, n):
    x0, y0 = BORNES['B4']; c, s = math.cos(math.radians(ROT)), math.sin(math.radians(ROT))
    de, dn = e - x0, n - y0
    return (de * c + dn * s, -de * s + dn * c)

SITE = Polygon([to_local(*BORNES[k]) for k in ('B4', 'B3', 'B2', 'B1')])
P = {k: to_local(*v) for k, v in BORNES.items()}

# Hypothèses réglementaires (à confirmer au règlement du lotissement / permis de construire)
RECUL_NORD = 4.0      # limite nord : coursives ouvertes -> 4 m
RECUL_LAT = 3.0       # limites ouest (voie) / est / sud

TRAME = 3.60          # trame structurelle (longueur max de barre ≈ 32,4 m avec les reculs)
D_COURSIVE, D_PIECE, D_LOGGIA = 1.80, 7.00, 1.80
D_BARRE = D_COURSIVE + D_PIECE + D_LOGGIA   # 10.60

def north_dir():
    """Direction du nord vrai dans le repère local."""
    return (math.sin(math.radians(ROT)), math.cos(math.radians(ROT)))

# ---------- Variante A : barre parallèle à la limite nord ----------
def bar_frame():
    """Repère (u,v) : u le long de B1->B2, v vers le sud (dans le terrain), origine B1."""
    (x1, y1), (x2, y2) = P['B1'], P['B2']
    L = math.hypot(x2 - x1, y2 - y1); ux, uy = (x2 - x1) / L, (y2 - y1) / L
    vx, vy = uy, -ux                                  # perpendiculaire vers l'intérieur
    def f(u, v):
        return (x1 + u * ux + v * vx, y1 + u * uy + v * vy)
    return f, math.degrees(math.atan2(uy, ux))

def rect_uv(u0, v0, u1, v1):
    f, _ = bar_frame()
    return Polygon([f(u0, v0), f(u1, v0), f(u1, v1), f(u0, v1)])

N_TRAMES_A = 9
def barre_A():
    """Positionne la barre de 9 trames au plus près de l'ouest en respectant les reculs."""
    L = N_TRAMES_A * TRAME
    zone = buildable()
    best = None
    for i in range(0, 1200):
        u0 = i * 0.01
        r = rect_uv(u0, RECUL_NORD, u0 + L, RECUL_NORD + D_BARRE)
        if zone.buffer(1e-6).contains(r):
            best = u0; break
    return best, L

def buildable():
    """Zone constructible : retraits différenciés (nord 4 m, autres 3 m)."""
    poly = SITE
    edges = [('S', P['B4'], P['B3'], RECUL_LAT), ('E', P['B3'], P['B2'], RECUL_LAT),
             ('N', P['B2'], P['B1'], RECUL_NORD), ('W', P['B1'], P['B4'], RECUL_LAT)]
    for _, a, b, d in edges:
        ln = LineString([a, b])
        # demi-plan intérieur : on retranche une bande de largeur d le long du côté
        poly = poly.difference(ln.buffer(d, cap_style=2).intersection(SITE).buffer(0))
        poly = poly.difference(ln.buffer(d, cap_style=1))
    return poly

if __name__ == '__main__':
    print('rotation repère / est :', round(ROT, 2), '°')
    print('surface terrain :', round(SITE.area, 1), 'm²')
    for k, v in P.items(): print(k, tuple(round(c, 2) for c in v))
    print('zone constructible :', round(buildable().area, 1), 'm²')
    u0, L = barre_A(); print('barre A : u0 =', u0, 'L =', L)
    _, ang = bar_frame(); print('angle barre / repère local :', round(ang, 2), '°  -> azimut façade sud =', round(180 + (ROT + ang) * -1, 1))
