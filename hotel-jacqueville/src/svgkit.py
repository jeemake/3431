"""Petit moteur SVG : dessin en repère local, rendu nord vrai en haut."""
import math
from shapely.geometry import Polygon, MultiPolygon
from geo import ROT

C, S = math.cos(math.radians(ROT)), math.sin(math.radians(ROT))

def en(x, y):
    """Repère local -> (Est, Nord) relatifs à B4."""
    return (x * C - y * S, x * S + y * C)

class Sheet:
    def __init__(self, xmin, ymin, xmax, ymax, scale=16, pad=30):
        """Bornes en coordonnées (E,N) ; scale en px/m."""
        self.k, self.pad = scale, pad
        self.x0, self.y1 = xmin, ymax
        self.w = (xmax - xmin) * scale + 2 * pad
        self.h = (ymax - ymin) * scale + 2 * pad
        self.items = []

    def p(self, x, y, local=True):
        e, n = en(x, y) if local else (x, y)
        return ((e - self.x0) * self.k + self.pad, (self.y1 - n) * self.k + self.pad)

    def poly(self, geom, fill='none', stroke='#1e2a24', sw=1.0, dash=None, op=1, local=True, extra=''):
        geoms = geom.geoms if isinstance(geom, MultiPolygon) else [geom]
        for g in geoms:
            if g.is_empty:
                continue
            rings = [g.exterior] + list(g.interiors)
            d = ' '.join('M' + ' L'.join('%.1f,%.1f' % self.p(*c, local=local) for c in r.coords) + ' Z' for r in rings)
            da = f' stroke-dasharray="{dash}"' if dash else ''
            self.items.append(f'<path d="{d}" fill="{fill}" fill-rule="evenodd" stroke="{stroke}" stroke-width="{sw}"{da} opacity="{op}" {extra}/>')

    def line(self, pts, stroke='#1e2a24', sw=1, dash=None, marker=False, local=True, op=1):
        d = ' L'.join('%.1f,%.1f' % self.p(*c, local=local) for c in pts)
        da = f' stroke-dasharray="{dash}"' if dash else ''
        mk = ' marker-end="url(#arr)"' if marker else ''
        self.items.append(f'<path d="M{d}" fill="none" stroke="{stroke}" stroke-width="{sw}"{da}{mk} opacity="{op}"/>')

    def circle(self, x, y, r, fill='#6f9a5b', stroke='none', op=1, sw=1, local=True):
        cx, cy = self.p(x, y, local)
        self.items.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r * self.k:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" opacity="{op}"/>')

    def tree(self, x, y, r=2.2, kind='feuillu'):
        cx, cy = self.p(x, y)
        R = r * self.k
        if kind == 'palmier':
            spokes = ''.join(f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{cx + R * math.cos(a):.1f}" y2="{cy + R * math.sin(a):.1f}" stroke="#4f7a43" stroke-width="1.2"/>'
                             for a in [i * math.pi / 4 + 0.2 for i in range(8)])
            self.items.append(f'<g opacity="0.85">{spokes}<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{R * 0.18:.1f}" fill="#4f7a43"/></g>')
        else:
            self.items.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{R:.1f}" fill="#8fb27a" fill-opacity="0.55" stroke="#5d8a4c" stroke-width="0.8"/>'
                              f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="1.6" fill="#5d8a4c"/>')

    def text(self, x, y, s, size=10, anchor='middle', weight=400, fill='#1e2a24', rot=0, local=True, italic=False):
        cx, cy = self.p(x, y, local)
        tr = f' transform="rotate({rot:.1f} {cx:.1f} {cy:.1f})"' if rot else ''
        st = ' font-style="italic"' if italic else ''
        s = s.replace('&', '&amp;')
        self.items.append(f'<text x="{cx:.1f}" y="{cy:.1f}" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}" fill="{fill}"{st}{tr} dominant-baseline="middle">{s}</text>')

    def raw(self, s):
        self.items.append(s)

    def north(self, x, y, size=26):
        """Flèche nord (coordonnées écran)."""
        self.items.append(f'<g transform="translate({x},{y})"><circle r="{size * 0.62}" fill="none" stroke="#1e2a24" stroke-width="0.8"/>'
                          f'<path d="M0,{-size * 0.55} L{size * 0.2},{size * 0.3} L0,{size * 0.15} L{-size * 0.2},{size * 0.3} Z" fill="#1e2a24"/>'
                          f'<text y="{-size * 0.78}" font-size="11" font-weight="700" text-anchor="middle">N</text></g>')

    def scalebar(self, x, y, meters=10):
        L = meters * self.k
        segs = ''.join(f'<rect x="{x + i * L / 5:.1f}" y="{y}" width="{L / 5:.1f}" height="5" fill="{"#1e2a24" if i % 2 == 0 else "#fff"}" stroke="#1e2a24" stroke-width="0.6"/>' for i in range(5))
        self.items.append(f'<g>{segs}<text x="{x}" y="{y + 16}" font-size="9">0</text><text x="{x + L}" y="{y + 16}" font-size="9" text-anchor="middle">{meters} m</text></g>')

    def svg(self, extra_defs=''):
        defs = ('<defs><marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
                '<path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker>'
                '<pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
                '<line x1="0" y1="0" x2="0" y2="6" stroke="#9a8f80" stroke-width="1"/></pattern>'
                '<pattern id="eg" width="8" height="8" patternUnits="userSpaceOnUse"><rect width="8" height="8" fill="#e9e3d3"/>'
                '<rect x="1" y="1" width="3" height="3" fill="#b9cf9f"/><rect x="5" y="5" width="2" height="2" fill="#b9cf9f"/></pattern>'
                '<pattern id="turf" width="10" height="10" patternUnits="userSpaceOnUse"><rect width="10" height="10" fill="#7cae5e"/>'
                '<rect width="5" height="10" fill="#86b868"/></pattern>'
                f'{extra_defs}</defs>')
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w:.0f} {self.h:.0f}" width="{self.w:.0f}" height="{self.h:.0f}" '
                f'font-family="Inter, sans-serif">{defs}' + '\n'.join(self.items) + '</svg>')
