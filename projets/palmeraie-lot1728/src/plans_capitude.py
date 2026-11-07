"""Plans de l'option C et du locatif aux conventions graphiques Capitude, avec les blocs Archibooks.

Regles appliquees (regles_agents, Capitude) : GRAPHISME-APLATS-LEGENDE-TRAME (aplats pastel a 45 % par usage,
legende sur chaque plan, trame d'axes reperee en peripherie), GRAPHISME-OPACITES (murs, textes, cotes noirs
opaques ; vegetation, sols, mobilier a opacites variees), GRAPHISME-ELCROQUIS-EXTERIEURS (sols differencies et
recadres, strates, bassins), BLOCS-ARCHIBOOKS (portes, arbres, textures, eau depuis le bucket prive),
PAYSAGE-TROPICAL-COMPOSITION (tailles et essences variees selon le role).
Blocs absents du catalogue (signales) : appareils sanitaires, lits, canapes, tables, cuisines, voitures, cartouche.
"""
import math

import facade as F
from blocs_archibooks import Bibliotheque, porte_matrix
from plans import Canvas, draw_furniture, esc
from projet import CX, CY, LOCATIF_M, MX, MY, OPTION_C

INK = "#000000"
PAL = {   # usage : (couleur source, intitule) ; opacite 45 % appliquee une fois a l'aplat
    "SEJ": ("#F2E6C6", "Séjour, salon"),
    "RES": ("#EFD4BC", "Restauration : cuisines, salle à manger"),
    "CH": ("#E8CBD3", "Chambres, dressings"),
    "SAN": ("#C5DDEB", "Sanitaires"),
    "BUR": ("#D5E5DC", "Bureau"),
    "CIR": ("#E7E7E2", "Circulations, escaliers"),
    "SER": ("#D9DCE0", "Services, rangements, locaux techniques"),
}
PRIO = {None: 0, "ext": 0, "CIR": 1, "SEJ": 2, "RES": 3, "SER": 4, "BUR": 5, "CH": 6, "SAN": 7}


def usage(r):
    c, n = r["code"], r["nom"].lower()
    if not r["clos"]:
        return None
    if "bureau" in n:
        return "BUR"
    if c in ("chambre", "l_chambre") or n.startswith("dressing"):
        return "CH"
    if c in ("eau", "l_eau"):
        return "SAN"
    if c in ("cuisine", "cuis_afr", "l_kitch") or "manger" in n:
        return "RES"
    if c in ("sejour", "l_sejour"):
        return "SEJ"
    if c in ("circ", "escalier") or "escalier" in n or "dégagement" in n or "palier" in n:
        return "CIR"
    return "SER"


class Feuille:
    def __init__(self, opt, niveau, x0, y0, x1, y1, s, sid):
        self.opt, self.niveau, self.sid = opt, niveau, sid
        self.c = Canvas(x0, y0, x1, y1, s=s, pad=8)
        self.S = s
        self.lib = Bibliotheque()
        self.pieces = [r for r in opt["pieces"] if r["niveau"] == niveau]
        self.portes = [p for p in opt["portes"] if p[0] == niveau]
        self.G = 0.05
        self._grid()

    # ------------------------------------------------------------------ geometrie
    def _grid(self):
        G = self.G
        self.cell = {}
        for r in self.pieces:
            for x0, y0, x1, y1 in r["rects"]:
                for i in range(round(x0 / G), round(x1 / G)):
                    for j in range(round(y0 / G), round(y1 / G)):
                        if r["clos"] or (i, j) not in self.cell:
                            self.cell[(i, j)] = r

    def at(self, x, y):
        return self.cell.get((math.floor(x / self.G), math.floor(y / self.G)))

    def murs(self):
        """Segments de murs : frontieres entre pieces closes differentes ou entre clos et exterieur."""
        G, cell = self.G, self.cell
        clos = {k: v for k, v in cell.items() if v["clos"]}
        segs = {}
        for (i, j), r in clos.items():
            for di, dj, key in ((0, -1, ("h", j, i)), (0, 1, ("h", j + 1, i)), (-1, 0, ("v", i, j)), (1, 0, ("v", i + 1, j))):
                o = clos.get((i + di, j + dj))
                if o is r:
                    continue
                ext = o is None
                if o is not None and (i + di, j + dj) < (i, j):
                    continue        # frontiere interieure comptee une fois
                segs[key] = ext or segs.get(key, False)
        runs = []
        for sens in ("h", "v"):
            lines = {}
            for (s_, line, pos), ext in segs.items():
                if s_ == sens:
                    lines.setdefault((line, ext), []).append(pos)
            for (line, ext), ps in lines.items():
                ps.sort()
                start = prev = ps[0]
                for p in ps[1:] + [None]:
                    if p is None or p != prev + 1:
                        runs.append((sens, line * G, start * G, (prev + 1) * G, ext))
                        if p is not None:
                            start = p
                    if p is not None:
                        prev = p
        return runs

    # ------------------------------------------------------------------ dessin
    def raw(self, s):
        self.c.raw(s)

    def texture(self, i, poly, opacity=0.6, holes=()):
        c = self.c
        self.raw(self.lib.texture(i, poly, self.S, c.X, c.Y, opacity=opacity, holes=holes,
                                  cid=f"{self.sid}_{len(c.el)}"))

    def arbre(self, i, x, y, diam, opacity=0.6):
        b = self.lib.info(i)["dimensions_m"]
        k = diam / max(b["largeur"], b["hauteur"])
        self.raw(self.lib.plan(i, x, y, self.S, k=k, opacity=opacity, X=self.c.X, Y=self.c.Y))

    def poly(self, pts, fill="none", stroke=INK, sw=0.8, op=1.0, dash=None):
        c = self.c
        d = "M" + " L".join(f"{c.X(x):.1f},{c.Y(y):.1f}" for x, y in pts) + " Z"
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.raw(f'<path d="{d}" fill="{fill}" fill-opacity="{op}" stroke="{stroke}" stroke-width="{sw}"{da}/>')

    def aplats(self):
        for r in self.pieces:
            u = usage(r)
            if not u:
                continue
            for x0, y0, x1, y1 in r["rects"]:
                self.c.rect(x0, y0, x1, y1, fill=PAL[u][0], stroke="none", sw=0, extra='fill-opacity="0.45"')

    def mobilier(self):
        c = self.c
        n0 = len(c.el)
        draw_furniture(c, self.pieces, self.niveau, self.portes)
        sub = c.el[n0:]
        del c.el[n0:]
        self.raw('<g opacity="0.8">' + "".join(sub) + "</g>")

    def escalier_u(self, x0, y0, x1, y1, palier="N", fleche=True, n=8):
        """Escalier a deux volees le long de y, palier au Nord (y0) ou au Sud."""
        c = self.c
        xm = (x0 + x1) / 2
        lp = 1.2
        ya, yb = (y0 + lp, y1) if palier == "N" else (y0, y1 - lp)
        step = (yb - ya) / n
        g = []
        for k in range(n + 1):
            y = ya + k * step
            g.append(f'<line x1="{c.X(x0 + 0.05):.1f}" y1="{c.Y(y):.1f}" x2="{c.X(x1 - 0.05):.1f}" y2="{c.Y(y):.1f}" stroke="{INK}" stroke-width="0.45"/>')
        g.append(f'<line x1="{c.X(xm):.1f}" y1="{c.Y(ya):.1f}" x2="{c.X(xm):.1f}" y2="{c.Y(yb):.1f}" stroke="{INK}" stroke-width="0.9"/>')
        if fleche:
            yy0, yy1 = (yb - 0.2, ya + 0.3) if palier == "N" else (ya + 0.2, yb - 0.3)
            xa = (x0 + xm) / 2
            g.append(f'<line x1="{c.X(xa):.1f}" y1="{c.Y(yy0):.1f}" x2="{c.X(xa):.1f}" y2="{c.Y(yy1):.1f}" stroke="{INK}" stroke-width="0.7" marker-end="url(#{self.sid}_fl)"/>')
        self.raw("".join(g))

    def murs_dessin(self):
        c = self.c
        for sens, line, a, b, ext in self.murs():
            t = 0.22 if ext else 0.12
            if sens == "h":
                c.rect(a - (t / 2 if ext else 0), line - t / 2, b + (t / 2 if ext else 0), line + t / 2, fill=INK, stroke="none", sw=0)
            else:
                c.rect(line - t / 2, a, line + t / 2, b, fill=INK, stroke="none", sw=0)

    def _cut(self, sens, line, a, b, t=0.3):
        if sens == "h":
            self.c.rect(a, line - t / 2, b, line + t / 2, fill="#ffffff", stroke="none", sw=0)
        else:
            self.c.rect(line - t / 2, a, line + t / 2, b, fill="#ffffff", stroke="none", sw=0)

    def vitrage(self, sens, line, a, b, jour=False):
        c = self.c
        col = "#2f6f8a"
        da = ' stroke-dasharray="3 2"' if jour else ""
        for d in (-0.05, 0.05):
            if sens == "h":
                self.raw(f'<line x1="{c.X(a):.1f}" y1="{c.Y(line + d):.1f}" x2="{c.X(b):.1f}" y2="{c.Y(line + d):.1f}" stroke="{col}" stroke-width="0.7"{da}/>')
            else:
                self.raw(f'<line x1="{c.X(line + d):.1f}" y1="{c.Y(a):.1f}" x2="{c.X(line + d):.1f}" y2="{c.Y(b):.1f}" stroke="{col}" stroke-width="0.7"{da}/>')
        for p in (a, b):
            if sens == "h":
                c.rect(p - 0.04, line - 0.12, p + 0.04, line + 0.12, fill=INK, stroke="none", sw=0)
            else:
                c.rect(line - 0.12, p - 0.04, line + 0.12, p + 0.04, fill=INK, stroke="none", sw=0)

    def brique(self, x0, y0, x1, y1):
        c = self.c
        c.rect(x0, y0, x1, y1, fill="#e7c3a9", stroke="#8a4f2f", sw=0.6)
        horiz = (x1 - x0) >= (y1 - y0)
        L = (x1 - x0) if horiz else (y1 - y0)
        n = max(1, int(L / 0.22))
        for k in range(1, n):
            u = k * L / n
            if horiz:
                c.line(x0 + u, y0, x0 + u, y1, stroke="#8a4f2f", sw=0.35)
            else:
                c.line(x0, y0 + u, x1, y0 + u, stroke="#8a4f2f", sw=0.35)

    def ouvertures(self, liste):
        """Portes (blocs Archibooks), baies coulissantes et fenetres sur les murs du niveau."""
        c = self.c
        portes = list(self.portes)
        for niv, sens, line, a, b, z0, z1, kind in liste:
            if niv != self.niveau:
                continue
            if kind == "porte" and any(p[3] == sens and abs((p[2] if sens == "h" else p[1]) - line) < 0.06
                                       and abs((p[1] if sens == "h" else p[2]) - (a + b) / 2) < 0.1 for p in portes):
                continue
            if kind == "porte":
                portes.append((niv, (a + b) / 2 if sens == "h" else line, line if sens == "h" else (a + b) / 2, sens, b - a))
                continue
            self._cut(sens, line, a, b)
            if kind == "claustra":
                d = -1 if (sens == "v" and line < 10) or (sens == "h" and line < 9) else 1
                lo, hi = sorted((line + d * 0.14, line + d * 0.32))
                if sens == "h":
                    self.brique(a - 0.1, lo, b + 0.1, hi)
                else:
                    self.brique(lo, a - 0.1, hi, b + 0.1)
                self.vitrage(sens, line, a, b, jour=True)
            else:
                self.vitrage(sens, line, a, b, jour=(kind == "jour"))
        for niv, x, y, sens, w in portes:
            a, b = (x - w / 2, x + w / 2) if sens == "h" else (y - w / 2, y + w / 2)
            line = y if sens == "h" else x
            self._cut(sens, line, a, b)
            if w > 1.85:          # baie coulissante : deux vantaux vitres
                self.vitrage(sens, line, a, b)
                m = (a + b) / 2
                if sens == "h":
                    c.line(a, line - 0.05, m + 0.15, line - 0.05, stroke=INK, sw=0.9)
                    c.line(m - 0.15, line + 0.05, b, line + 0.05, stroke=INK, sw=0.9)
                else:
                    c.line(line - 0.05, a, line - 0.05, m + 0.15, stroke=INK, sw=0.9)
                    c.line(line + 0.05, m - 0.15, line + 0.05, b, stroke=INK, sw=0.9)
                continue
            # cote d'ouverture : vers la piece la plus privee (ou vers l'interieur)
            if sens == "h":
                p1, p2 = self.at(x, y - 0.3), self.at(x, y + 0.3)
            else:
                p1, p2 = self.at(x - 0.3, y), self.at(x + 0.3, y)
            u1 = usage(p1) if p1 else None
            u2 = usage(p2) if p2 else None
            swing = 1 if PRIO.get(u2, 0) >= PRIO.get(u1, 0) else -1
            room = p2 if swing == 1 else p1
            hinge_low = True
            if room:
                rx0 = min(q[0] for q in room["rects"]) if sens == "h" else min(q[1] for q in room["rects"])
                rx1 = max(q[2] for q in room["rects"]) if sens == "h" else max(q[3] for q in room["rects"])
                hinge_low = (a - rx0) <= (rx1 - b)
            ident = "porte_battante_90" if w < 1.15 else "porte_double"
            m = porte_matrix(x, y, sens, w, swing, hinge_low, self.S, c.X, c.Y)
            self.raw(self.lib.use(ident, *m))

    def etiquettes(self):
        c = self.c
        for r in self.pieces:
            x0, y0, x1, y1 = max(r["rects"], key=lambda q: (q[2] - q[0]) * (q[3] - q[1]))
            w, h = x1 - x0, y1 - y0
            nom = r["nom"].split(" ", 1)[1] if "logement" in r else r["nom"]
            if r["code"] in ("parvis", "jardin", "patio", "terrasse", "balcon", "toit_jard") and w * h < 4:
                continue
            area = f"{r['surface']:.2f}".replace(".", ",") + " m²"
            if not r["clos"] and r["code"] in ("parvis",):
                area = ""
            size = 7.4 if w > 2.4 and h > 1.6 else 6.2
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            if h > w * 1.6 and w < 1.8:
                c.text(cx, cy, f"{nom} {area}".strip(), size=size - 0.6, fill=INK, rot=-90)
                continue
            words, lines, cur = nom.split(" "), [], ""
            maxch = max(6, int(w * c.s / (size * 0.56)))
            for wd in words:
                if len(cur) + len(wd) + 1 > maxch and cur:
                    lines.append(cur)
                    cur = wd
                else:
                    cur = (cur + " " + wd).strip()
            lines.append(cur)
            lh = size * 1.15 / c.s
            top = cy - len(lines) * lh / 2 + lh * 0.55
            for k, ln in enumerate(lines):
                c.text(cx, top + k * lh, ln, size=size, fill=INK, weight=600)
            if area:
                c.text(cx, top + len(lines) * lh, area, size=size - 0.8, fill=INK)

    # ------------------------------------------------------------------ habillage
    def cotes(self, xs, ys, xpos, ypos, total_x=None, total_y=None):
        c = self.c
        g = []

        def tick(px, py):
            g.append(f'<line x1="{px - 3:.1f}" y1="{py + 3:.1f}" x2="{px + 3:.1f}" y2="{py - 3:.1f}" stroke="{INK}" stroke-width="0.8"/>')

        for chain, yy in ((xs, ypos),) + (((total_x, ypos - 0.62),) if total_x else ()):
            py = c.Y(yy)
            g.append(f'<line x1="{c.X(chain[0]) - 6:.1f}" y1="{py:.1f}" x2="{c.X(chain[-1]) + 6:.1f}" y2="{py:.1f}" stroke="{INK}" stroke-width="0.4"/>')
            for k, x in enumerate(chain):
                tick(c.X(x), py)
                if k:
                    v = f"{chain[k] - chain[k - 1]:.2f}".rstrip("0").rstrip(".").replace(".", ",")
                    g.append(f'<text x="{(c.X(x) + c.X(chain[k - 1])) / 2:.1f}" y="{py - 3:.1f}" font-size="7" text-anchor="middle" fill="{INK}">{v}</text>')
        for chain, xx in ((ys, xpos),) + (((total_y, xpos - 0.7),) if total_y else ()):
            px = c.X(xx)
            g.append(f'<line x1="{px:.1f}" y1="{c.Y(chain[0]) - 6:.1f}" x2="{px:.1f}" y2="{c.Y(chain[-1]) + 6:.1f}" stroke="{INK}" stroke-width="0.4"/>')
            for k, y in enumerate(chain):
                tick(px, c.Y(y))
                if k:
                    v = f"{chain[k] - chain[k - 1]:.2f}".rstrip("0").rstrip(".").replace(".", ",")
                    ym = (c.Y(y) + c.Y(chain[k - 1])) / 2
                    g.append(f'<text x="{px - 3:.1f}" y="{ym:.1f}" font-size="7" text-anchor="middle" fill="{INK}" transform="rotate(-90 {px - 3:.1f} {ym:.1f})">{v}</text>')
        self.raw("".join(g))

    def axes(self, xs, ys, ytop, xleft, x_end, y_end):
        """Trame de reperage : bulles en peripherie, traits courts detaches du dessin."""
        c = self.c
        g = []
        r = 0.32 * c.s
        for k, x in enumerate(xs, 1):
            px, py = c.X(x), c.Y(ytop)
            g.append(f'<line x1="{px:.1f}" y1="{py + r:.1f}" x2="{px:.1f}" y2="{py + r + 0.5 * c.s:.1f}" stroke="{INK}" stroke-width="0.5"/>'
                     f'<line x1="{px:.1f}" y1="{c.Y(y_end) + 0.2 * c.s:.1f}" x2="{px:.1f}" y2="{c.Y(y_end) + 0.6 * c.s:.1f}" stroke="{INK}" stroke-width="0.5"/>'
                     f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{r:.1f}" fill="#fff" stroke="{INK}" stroke-width="0.7"/>'
                     f'<text x="{px:.1f}" y="{py + 3:.1f}" font-size="8" text-anchor="middle" font-weight="600" fill="{INK}">{k}</text>')
        for k, y in enumerate(ys):
            px, py = c.X(xleft), c.Y(y)
            g.append(f'<line x1="{px + r:.1f}" y1="{py:.1f}" x2="{px + r + 0.5 * c.s:.1f}" y2="{py:.1f}" stroke="{INK}" stroke-width="0.5"/>'
                     f'<line x1="{c.X(x_end) + 0.2 * c.s:.1f}" y1="{py:.1f}" x2="{c.X(x_end) + 0.6 * c.s:.1f}" y2="{py:.1f}" stroke="{INK}" stroke-width="0.5"/>'
                     f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{r:.1f}" fill="#fff" stroke="{INK}" stroke-width="0.7"/>'
                     f'<text x="{px:.1f}" y="{py + 3:.1f}" font-size="8" text-anchor="middle" font-weight="600" fill="{INK}">{chr(65 + k)}</text>')
        self.raw("".join(g))

    def legende(self, x, y, extra=()):
        c = self.c
        us = []
        for r in self.pieces:
            u = usage(r)
            if u and u not in us:
                us.append(u)
        g = [f'<text x="{c.X(x):.1f}" y="{c.Y(y):.1f}" font-size="8.5" font-weight="700" fill="{INK}">Légende</text>']
        yy = y + 0.8
        for u in [k for k in PAL if k in us]:
            g.append(f'<rect x="{c.X(x):.1f}" y="{c.Y(yy) - 7:.1f}" width="14" height="9" fill="{PAL[u][0]}" fill-opacity="0.45" stroke="{INK}" stroke-width="0.4"/>'
                     f'<text x="{c.X(x) + 19:.1f}" y="{c.Y(yy) + 1:.1f}" font-size="7.2" fill="{INK}"><tspan font-weight="700">{u}</tspan> {esc(PAL[u][1])}</text>')
            yy += 0.62
        for sym, lab in extra:
            g.append(f'<g transform="translate({c.X(x):.1f},{c.Y(yy) - 7:.1f})">{sym}</g>'
                     f'<text x="{c.X(x) + 19:.1f}" y="{c.Y(yy) + 1:.1f}" font-size="7.2" fill="{INK}">{esc(lab)}</text>')
            yy += 0.62
        self.raw("".join(g))
        return yy

    def nord_echelle(self, x, y):
        c = self.c
        cx, cy, R = c.X(x), c.Y(y), 0.8 * c.s
        a = math.radians(-7.56)
        tip = (cx + R * math.sin(a), cy - R * math.cos(a))
        l_ = (cx + 0.35 * R * math.sin(a - 2.4), cy - 0.35 * R * math.cos(a - 2.4))
        r_ = (cx + 0.35 * R * math.sin(a + 2.4), cy - 0.35 * R * math.cos(a + 2.4))
        S = c.s
        sx, sy = cx - 2.5 * S, cy + 1.6 * S
        self.raw(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{R:.1f}" fill="none" stroke="{INK}" stroke-width="0.6"/>'
                 f'<polygon points="{tip[0]:.1f},{tip[1]:.1f} {l_[0]:.1f},{l_[1]:.1f} {cx:.1f},{cy:.1f} {r_[0]:.1f},{r_[1]:.1f}" fill="{INK}"/>'
                 f'<text x="{tip[0]:.1f}" y="{tip[1] - 4:.1f}" font-size="9" text-anchor="middle" font-weight="700" fill="{INK}">N</text>'
                 f'<rect x="{sx:.1f}" y="{sy:.1f}" width="{5 * S:.1f}" height="4" fill="{INK}"/>'
                 f'<rect x="{sx + S:.1f}" y="{sy:.1f}" width="{S:.1f}" height="4" fill="#fff" stroke="{INK}" stroke-width="0.4"/>'
                 f'<rect x="{sx + 3 * S:.1f}" y="{sy:.1f}" width="{S:.1f}" height="4" fill="#fff" stroke="{INK}" stroke-width="0.4"/>'
                 f'<text x="{sx:.1f}" y="{sy + 13:.1f}" font-size="7" fill="{INK}">0</text>'
                 f'<text x="{sx + 5 * S:.1f}" y="{sy + 13:.1f}" font-size="7" text-anchor="middle" fill="{INK}">5 m</text>')

    def svg(self):
        defs = (f'<defs>{self.lib.defs()}<marker id="{self.sid}_fl" markerWidth="7" markerHeight="7" refX="5" refY="3" orient="auto">'
                f'<path d="M0,0 L6,3 L0,6 z" fill="{INK}"/></marker></defs>')
        s = self.c.svg()
        i = s.index(">") + 1
        return s[:i] + defs + s[i:]


SYM_PORTE = '<path d="M1,9 L1,1 M1,9 L10,9" stroke="#000" stroke-width="0.8" fill="none"/><path d="M1,1 A8,8 0 0 1 9,9" stroke="#000" stroke-width="0.5" fill="none"/>'
SYM_VITRE = '<line x1="0" y1="3" x2="14" y2="3" stroke="#2f6f8a" stroke-width="0.8"/><line x1="0" y1="6" x2="14" y2="6" stroke="#2f6f8a" stroke-width="0.8"/>'
SYM_JOUR = '<line x1="0" y1="3" x2="14" y2="3" stroke="#2f6f8a" stroke-width="0.8" stroke-dasharray="3 2"/><line x1="0" y1="6" x2="14" y2="6" stroke="#2f6f8a" stroke-width="0.8" stroke-dasharray="3 2"/>'
SYM_BRIQUE = '<rect x="0" y="1" width="14" height="7" fill="#e7c3a9" stroke="#8a4f2f" stroke-width="0.6"/><line x1="5" y1="1" x2="5" y2="8" stroke="#8a4f2f" stroke-width="0.4"/><line x1="10" y1="1" x2="10" y2="8" stroke="#8a4f2f" stroke-width="0.4"/>'
SYM_EAU = '<rect x="0" y="0" width="14" height="9" fill="#bcd6e0" fill-opacity="0.5" stroke="#000" stroke-width="0.5"/>'
SYM_VEG = '<rect x="0" y="0" width="14" height="9" fill="#cfe0bf" stroke="#4f6b3a" stroke-width="0.5"/>'
SYM_TRAME = '<circle cx="7" cy="4.5" r="4.2" fill="#fff" stroke="#000" stroke-width="0.6"/><text x="7" y="7" font-size="6" text-anchor="middle">1</text>'


def _legende_commune(f, x, y, extra=()):
    yy = f.legende(x, y, extra=[(SYM_PORTE, "Porte (bloc Archibooks)"), (SYM_VITRE, "Fenêtre, baie vitrée"),
                                (SYM_JOUR, "Jour haut, allège 1,80 m"), (SYM_BRIQUE, "Brique ajourée"),
                                (SYM_EAU, "Bassin (texture eau)"), (SYM_VEG, "Végétation, jardin")] + list(extra))
    f.c.text(x, yy + 0.25, "Aplats à 45 % ; trame de conception", size=6.4, anchor="start", fill=INK)
    f.c.text(x, yy + 0.75, "du client, à confirmer par le BET.", size=6.4, anchor="start", fill=INK)
    return yy


# =============================================================================== villa
def villa(niveau, s=19, sid=None):
    f = Feuille(OPTION_C, niveau, -4.0, -3.4, 30.2, 20.4, s, sid or f"vc_{niveau.replace('+', '')}")
    c = f.c
    # --- sols, eau, vegetation (au fond)
    if niveau == "RDC":
        f.texture("texture_paves", [(7.0, 0.2), (16.4, 0.2), (16.4, 4.5), (7.0, 4.5)], 0.55,
                  holes=[[(7.0, 0.2), (8.4, 0.2), (8.4, 4.5), (7.0, 4.5)]])
        f.texture("texture_pierre_bandes", [(7.0, 0.2), (8.4, 0.2), (8.4, 4.5), (7.0, 4.5)], 0.7)
        f.texture("texture_pierre_bandes", [(3.5, 4.5), (16.5, 4.5), (16.5, 5.7), (3.5, 5.7)], 0.65)
        f.texture("texture_pierre_bandes", [(16.5, 2.6), (19.0, 2.6), (19.0, 5.7), (16.5, 5.7)], 0.65)
        f.texture("texture_granulat_fin", [(16.5, 0.2), (19.8, 0.2), (19.8, 2.6), (16.5, 2.6)], 0.6)
        f.texture("texture_granulat_fin", [(19.0, 2.6), (19.8, 2.6), (19.8, 17.4), (19.0, 17.4)], 0.6)
        f.texture("texture_pas_irreguliers", [(3.5, 17.0), (19.0, 17.0), (19.0, 17.4), (3.5, 17.4)], 0.8)
        bx0, by0, bx1, by1 = F.BIO_BASSINS[0]
        f.texture("texture_couvre_sol", [(0.2, 2.7), (3.5, 2.7), (3.5, 17.4), (0.2, 17.4)], 0.6,
                  holes=[[(bx0 - 0.2, by0 - 0.2), (bx1 + 0.2, by0 - 0.2), (bx1 + 0.2, by1 + 0.2), (bx0 - 0.2, by1 + 0.2)]])
        f.texture("texture_massif_tropical", [(0.2, 17.4), (20.0, 17.4), (20.0, 17.82), (0.2, 17.82)], 0.7)
        # patio : terrasse en pierre, massifs, pas, bassin
        f.texture("texture_pierre_bandes", [(10.0, 11.2), (15.5, 11.2), (15.5, 13.6), (10.0, 13.6)], 0.65)
        px0, py0, px1, py1 = F.BIO_BASSINS[1]
        f.texture("texture_massif_tropical", [(10.0, 13.6), (15.5, 13.6), (15.5, 17.82), (10.0, 17.82)], 0.6,
                  holes=[[(px0 - 0.2, py0 - 0.2), (px1 + 0.2, py0 - 0.2), (px1 + 0.2, py1 + 0.2), (px0 - 0.2, py1 + 0.2)],
                         [(12.9, 13.6), (13.9, 13.6), (13.9, 17.4), (12.9, 17.4)]])
        f.texture("texture_pas_irreguliers", [(12.9, 13.6), (13.9, 13.6), (13.9, 17.4), (12.9, 17.4)], 0.85)
        for (x0, y0, x1, y1) in F.BIO_BASSINS:
            c.rect(x0 - 0.2, y0 - 0.2, x1 + 0.2, y1 + 0.2, fill="#ffffff", stroke=INK, sw=0.6)
            c.rect(x0, y0, x1, y1, fill="#bcd6e0", stroke=INK, sw=0.6, extra='fill-opacity="0.35"')
            f.texture("texture_eau", [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], 0.3)
        # arbres : roles et tailles varies (PAYSAGE-TROPICAL-COMPOSITION)
        f.arbre("arbre_frangipanier", *F.ARBRE_PATIO, 5.2, 0.62)          # arbre repere du patio
        f.arbre("arbre_feuilles_ovales", 1.7, 8.6, 4.4, 0.5)              # ombre de la facade Ouest
        f.arbre("arbre_touffes_frisees", 1.9, 4.2, 3.0, 0.5)              # angle des deux rues
        f.arbre("arbre_feuillage_dense", 1.6, 17.0, 3.2, 0.48)            # fond de parcelle, devant le mur vegetal
        f.arbre("arbre_touffes_frisees", 15.3, 2.4, 2.4, 0.45)            # entre parking et sechoir
    elif niveau == "R+1":
        f.texture("texture_couvre_sol", [(15.5, 11.2), (19.0, 11.2), (19.0, 17.0), (15.5, 17.0)], 0.45)
        f.texture("texture_couvre_sol", [(10.0, 11.2), (15.5, 11.2), (15.5, 13.6), (10.0, 13.6)], 0.45)
        f.texture("texture_pierre_bandes", [(6.5, 4.5), (19.0, 4.5), (19.0, 5.7), (6.5, 5.7)], 0.6)
        f.texture("texture_massif_tropical", [(2.7, 13.8), (3.5, 13.8), (3.5, 17.0), (2.7, 17.0)], 0.7)
        f.arbre("arbre_frangipanier", *F.ARBRE_PATIO, 5.2, 0.4)
        for r in OPTION_C["pieces"]:      # emprise du RDC en pointille
            if r["niveau"] == "RDC" and r["clos"] and not r["nom"].startswith("Guérite"):
                for x0, y0, x1, y1 in r["rects"]:
                    c.rect(x0, y0, x1, y1, stroke="#555555", sw=0.35, dash="2 2")
    else:
        f.texture("texture_pierre_bandes", [(6.5, 5.7), (19.0, 5.7), (19.0, 11.2), (6.5, 11.2)], 0.55)
        f.texture("texture_pierre_bandes", [(3.5, 9.9), (10.0, 9.9), (10.0, 17.0), (3.5, 17.0)], 0.55,
                  holes=[[(6.5, 9.9), (10.0, 9.9), (10.0, 11.2), (6.5, 11.2)]])
        x0, y0, x1, y1, _ = F.JARDINIERE
        f.texture("texture_massif_tropical", [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], 0.75)
        for (a, b, cc, d) in F.TOITURE_VEGETALE:
            f.texture("texture_couvre_sol", [(a, b), (cc, b), (cc, d), (a, d)], 0.45)
        f.arbre("arbre_frangipanier", *F.ARBRE_PATIO, 5.2, 0.4)
    f.aplats()
    if niveau != "TOIT":
        f.mobilier()
    f.escalier_u(3.55, 5.75, 6.45, 9.85, palier="N", fleche=niveau != "TOIT")
    f.murs_dessin()
    f.ouvertures(F.OUVERTURES)
    # --- elements de facade
    if niveau == "R+1":
        x0, y0, x1, y1, z0, z1 = F.DOUBLE_PEAU
        f.brique(x0, y0 - 0.06, x1, y1)
        for a, b in F.ECRANS_GALERIE:
            c.line(a, 11.32, b, 11.32, stroke="#6b4a2f", sw=2.2)
        c.rect(2.7, 13.8, 3.5, 17.0, stroke=INK, sw=0.8)
    if niveau == "TOIT":
        for (a, b, cc, d) in F.PERGOLA:     # poutres de la pergola, entraxe 0,60 m
            n = int((cc - a) / 0.6)
            for k in range(n + 1):
                xx = a + k * (cc - a) / n
                c.line(xx, b, xx, d, stroke="#6b4a2f", sw=0.5)
        for (px, py) in F.POTEAUX:
            c.rect(px - 0.08, py - 0.08, px + 0.08, py + 0.08, fill=INK, stroke="none", sw=0)
        for pts in ([(3.5, 4.5), (19.0, 4.5), (19.0, 11.2), (10.0, 11.2), (10.0, 17.0), (3.5, 17.0)],):
            f.poly(pts, stroke=INK, sw=2.2)
        c.text(12.75, 14.6, "vide sur patio", size=7.5, fill=INK, italic=True)
        c.text(17.25, 14.2, "toiture végétalisée", size=6.8, fill=INK, italic=True)
        c.text(12.75, 12.4, "toiture végétalisée (terrasse)", size=6.4, fill=INK, italic=True)
    if niveau == "RDC":
        c.line(0.0, 17.91, 20.0, 17.91, stroke=INK, sw=3.0)
        c.text(10.0, 18.55, "mur végétalisé en limite (h 3,0 m), côté villa et côté jardins du locatif", size=7, fill=INK)
        # guerite, local GE, cloture
        f.brique(16.5, 0.2, 19.8, 0.34)
        c.rect(0.3, 0.3, 3.3, 2.5, fill="#D9DCE0", stroke=INK, sw=1.0, extra='fill-opacity="0.45"')
        for x0, x1 in ((0.0, 7.0), (15.9, 17.0), (19.5, 20.0)):
            c.rect(x0, 0.0, x1, 0.2, fill="#8a8a8a", stroke=INK, sw=0.4)
        c.rect(0.0, 0.2, 0.2, 17.82, fill="#8a8a8a", stroke=INK, sw=0.4)
        c.text(11.75, 2.4, "stationnement 3 places (4,50 m)", size=7, fill=INK)
        c.text(7.7, -0.35, "portillon", size=6.5, fill=INK)
        c.text(12.15, -0.35, "portail coulissant 7,5 m", size=6.5, fill=INK)
        c.text(18.25, -0.35, "portillon de service", size=6.5, fill=INK)
        c.text(10.0, -1.25, "", size=1)
    c.text(10.0, -2.95 if False else -3.05, "", size=1)
    f.etiquettes()
    # --- habillage
    f.cotes([0.0] + list(CX) + [20.0], [0.0] + list(CY), -1.0 if niveau != "RDC" else -1.0, -1.25,
            total_x=[0.0, 20.0], total_y=[0.0, 18.0])
    f.axes(list(CX), list(CY[:4]), -2.95, -3.15, 20.6, 18.6)
    if niveau == "RDC":
        for (x, y0, y1, lab) in ((12.75, 3.4, 19.2, "A"),):
            c.line(x, y0, x, y1, stroke=INK, sw=0.7, dash="8 3 2 3")
            for yy in (y0, y1):
                c.raw(f'<circle cx="{c.X(x):.1f}" cy="{c.Y(yy):.1f}" r="7" fill="{INK}"/>')
                c.text(x, yy + 0.12, lab, size=7.5, fill="#ffffff", weight=700)
        c.line(-0.4, 15.0, 20.4, 15.0, stroke=INK, sw=0.7, dash="8 3 2 3")
        for xx in (-0.4, 20.4):
            c.raw(f'<circle cx="{c.X(xx):.1f}" cy="{c.Y(15.0):.1f}" r="7" fill="{INK}"/>')
            c.text(xx, 15.12, "B", size=7.5, fill="#ffffff", weight=700)
    f.nord_echelle(25.5, 0.2)
    _legende_commune(f, 21.6, 3.6)
    return f.svg()


# =============================================================================== locatif
def maisons(niveau, s=19, sid=None):
    f = Feuille(LOCATIF_M, niveau, -4.0, 14.6, 30.2, 35.4, s, sid or f"lm_{niveau.replace('+', '')}")
    c = f.c
    if niveau == "RDC":
        f.texture("texture_paves", [(2.0, 30.0), (20.0, 30.0), (20.0, 32.8), (2.0, 32.8)], 0.55)
        f.texture("texture_pierre_bandes", [(0.2, 18.0), (2.0, 18.0), (2.0, 32.8), (0.2, 32.8)], 0.65)
        for k, x0 in enumerate(MX[:3]):
            f.texture("texture_couvre_sol", [(x0, 18.1), (x0 + 6, 18.1), (x0 + 6, 21.0), (x0, 21.0)], 0.55)
            f.texture("texture_massif_tropical", [(x0, 18.1), (x0 + 6, 18.1), (x0 + 6, 18.6), (x0, 18.6)], 0.7)
            f.arbre(["arbre_touffes_frisees", "arbre_feuilles_ovales", "arbre_touffes_frisees"][k], x0 + 1.4 + 1.6 * k % 3, 19.6, 2.6, 0.5)
        c.line(0.0, 17.91, 20.0, 17.91, stroke=INK, sw=3.0)
        c.text(10.0, 17.45, "mur végétalisé (limite avec la villa)", size=7, fill=INK)
        c.rect(0.0, 18.0, 0.2, 33.0, fill="#8a8a8a", stroke=INK, sw=0.4)
    elif niveau == "TOIT":
        for x0 in MX[:3]:
            f.texture("texture_pierre_bandes", [(x0, 21.0), (x0 + 6, 21.0), (x0 + 6, 30.0), (x0 + 2.6, 30.0),
                                                (x0 + 2.6, 26.5), (x0, 26.5)], 0.55)
            f.texture("texture_massif_tropical", [(x0, 21.0), (x0 + 6, 21.0), (x0 + 6, 21.6), (x0, 21.6)], 0.75)
            for k in range(11):
                xx = x0 + 0.1 + k * 0.58
                c.line(xx, 21.0, xx, 26.5, stroke="#6b4a2f", sw=0.5)
            for (px, py) in ((x0 + 0.1, 21.1), (x0 + 5.9, 21.1), (x0 + 0.1, 26.4), (x0 + 5.9, 26.4)):
                c.rect(px - 0.07, py - 0.07, px + 0.07, py + 0.07, fill=INK, stroke="none", sw=0)
            f.poly([(x0, 21.0), (x0 + 6, 21.0), (x0 + 6, 30.0), (x0, 30.0)], stroke=INK, sw=2.0)
    f.aplats()
    if niveau != "TOIT":
        f.mobilier()
    for x0 in MX[:3]:
        f.escalier_u(x0 + 0.05, 26.55, x0 + 2.55, 29.95, palier="S", fleche=niveau != "TOIT", n=7)
    f.murs_dessin()
    ouv = [o for k, x0 in enumerate(MX[:3]) for o in F.ouvertures_maison(x0, k == 0)]
    f.ouvertures(ouv)
    f.etiquettes()
    f.cotes([0.0] + list(MX), list(MY), -1.0, 17.0, total_x=[0.0, 20.0], total_y=[18.0, 33.0])
    f.axes(list(MX), list(MY), 15.45, -3.15, 20.6, 33.6)
    f.nord_echelle(25.5, 16.2)
    _legende_commune(f, 21.6, 19.6)
    return f.svg()
