"""Plans de l'option C v5 et du locatif au gabarit Capitude GABARIT-VISUEL-PLANS (v3, 10-11-2026).

Noir et gris sur fond blanc, sans aplats d'usage (regle GRAPHISME-APLATS-LEGENDE-TRAME retiree) : murs coupes en
poche noir, menuiseries en double trait fin, mobilier au trait (interieur blanc), sols en textures Archibooks grises,
vegetation en canopees El Croquis (vegetation-elcroquis-v1) a 3-4 valeurs de gris, etiquettes de pieces en capitales
avec surface, projections au-dessus du plan de coupe en tirets, reperes de coupe en equerres hors du dessin,
police de la chaine Century Gothic (URW Gothic, lib/ du bucket blocs-archibooks).
Blocs absents du catalogue (signales) : appareils sanitaires, lits, canapes, tables, cuisines, vehicules en plan,
personnages vus de dessus : dessines au trait dans la grammaire du gabarit.
"""
import math

import facade as F
from blocs_archibooks import Bibliotheque, porte_matrix
from plans import Canvas, draw_furniture, esc
from projet import CX, CY, LOCATIF_M, MX, MY, OPTION_C

INK = "#000000"
FONT = '"Century Gothic", "URW Gothic", "TeX Gyre Adventor", Questrial, Jost, sans-serif'
TONS = {30: "#b3b3b3", 36: "#a3a3a3", 42: "#949494", 46: "#8a8a8a", 55: "#737373", 64: "#5c5c5c", 75: "#404040"}
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


def nom_court(r):
    """Etiquette : forme courte du libelle, sans parenthese ni variante (GABARIT-VISUEL-PLANS, section 4)."""
    n = r["nom"].split(" ", 1)[1] if "logement" in r and r["nom"][:1] == "M" else r["nom"]
    n = n.split(" (")[0]
    table = {"Guérite + WC gardien": "Guérite", "Local GE + niche compteurs": "Local GE", "Hall d'entrée": "Hall",
             "WC visiteurs": "WC", "Passage couvert d'entrée": "Passage couvert", "Terrasse couverte sur patio": "Terrasse couverte",
             "Patio planté": "Patio", "SE nounou": "Salle d'eau", "SE ch.1": "Salle d'eau", "SE ch.2": "Salle d'eau",
             "SE": "Salle d'eau", "SdB parentale": "Salle de bains", "Dressing parental": "Dressing",
             "Galerie sur patio": "Galerie", "Loggia Nord": "Loggia", "Jardinière Ouest": "Jardinière",
             "Préau cuisine africaine": "Préau", "Séchoir à ciel ouvert": "Séchoir", "Édicule d'escalier": "Édicule",
             "Toit-terrasse couvert": "Toit-terrasse", "Toit-terrasse sous pergola": "Toit-terrasse", "Séjour-SAM": "Séjour",
             "Cour d'entrée": "Cour", "Stationnement 2 places": "Stationnement", "Jardin privé": "Jardin"}
    return table.get(n, n).upper()


class Feuille:
    def __init__(self, opt, niveau, x0, y0, x1, y1, s, sid):
        self.opt, self.niveau, self.sid = opt, niveau, sid
        self.c = Canvas(x0, y0, x1, y1, s=s, pad=8)
        self.S = s
        self.lib = Bibliotheque()
        self.pieces = [r for r in opt["pieces"] if r["niveau"] == niveau]
        self.portes = [p for p in opt["portes"] if p[0] == niveau]
        self.G = 0.05
        self.reserve = []           # boites d'etiquettes reservees (x0, y0, x1, y1) en metres
        self._grid()

    def pt(self, n):
        """Corps en points -> unites SVG, a l'echelle 1:100 (1 m = 10 mm)."""
        return n * 0.3528 * self.S / 10

    def mm(self, n):
        return n * self.S / 10

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

    def arbre(self, i, x, y, diam, ton=None, rot=0.0, opacity=1.0):
        """Canopee El Croquis (aplat gris opaque, ton en % de noir) ou arbre au trait (opacite)."""
        b = self.lib.info(i)["dimensions_m"]
        k = diam / max(b["largeur"], b["hauteur"])
        fill = TONS.get(ton, ton) if ton else None
        self.raw(self.lib.plan(i, x, y, self.S, k=k, rot=rot, opacity=opacity, X=self.c.X, Y=self.c.Y, fill=fill))

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
        """Mobilier et sanitaires au trait fin, interieur blanc (blocs absents du catalogue, dessines et signales)."""
        import re
        c = self.c
        n0 = len(c.el)
        draw_furniture(c, self.pieces, self.niveau, self.portes)
        sub = "".join(c.el[n0:])
        del c.el[n0:]
        sub = re.sub(r'fill="#(?!fff)[0-9a-fA-F]{6}"', 'fill="#ffffff"', sub)
        sub = re.sub(r'stroke="#[0-9a-fA-F]{6}"', 'stroke="#000000"', sub)
        sub = re.sub(r'stroke-width="[0-9.]+"', f'stroke-width="{self.mm(0.15):.2f}"', sub)
        self.raw('<g opacity="0.85">' + sub + "</g>")

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
            g.append(f'<line x1="{c.X(x0 + 0.05):.1f}" y1="{c.Y(y):.1f}" x2="{c.X(x1 - 0.05):.1f}" y2="{c.Y(y):.1f}" stroke="{INK}" stroke-width="{self.mm(0.18):.2f}"/>')
        g.append(f'<line x1="{c.X(xm):.1f}" y1="{c.Y(ya):.1f}" x2="{c.X(xm):.1f}" y2="{c.Y(yb):.1f}" stroke="{INK}" stroke-width="{self.mm(0.25):.2f}"/>')
        if fleche:
            yy0, yy1 = (yb - 0.2, ya + 0.3) if palier == "N" else (ya + 0.2, yb - 0.3)
            xa = (x0 + xm) / 2
            g.append(f'<line x1="{c.X(xa):.1f}" y1="{c.Y(yy0):.1f}" x2="{c.X(xa):.1f}" y2="{c.Y(yy1):.1f}" stroke="{INK}" stroke-width="{self.mm(0.18):.2f}" marker-end="url(#{self.sid}_fl)"/>')
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
        col = INK
        da = f' stroke-dasharray="{self.mm(1.2):.1f} {self.mm(0.8):.1f}"' if jour else ""
        for d in (-0.05, 0.05):
            if sens == "h":
                self.raw(f'<line x1="{c.X(a):.1f}" y1="{c.Y(line + d):.1f}" x2="{c.X(b):.1f}" y2="{c.Y(line + d):.1f}" stroke="{col}" stroke-width="{self.mm(0.15):.2f}"{da}/>')
            else:
                self.raw(f'<line x1="{c.X(line + d):.1f}" y1="{c.Y(a):.1f}" x2="{c.X(line + d):.1f}" y2="{c.Y(b):.1f}" stroke="{col}" stroke-width="{self.mm(0.15):.2f}"{da}/>')
        for p in (a, b):
            if sens == "h":
                c.rect(p - 0.04, line - 0.12, p + 0.04, line + 0.12, fill=INK, stroke="none", sw=0)
            else:
                c.rect(line - 0.12, p - 0.04, line + 0.12, p + 0.04, fill=INK, stroke="none", sw=0)

    def brique(self, x0, y0, x1, y1, pas=0.2):
        """Claustra (blocs de beton ajoures, ou lames) coupe : contour fort, cloisons tous les 0,20 m."""
        c = self.c
        c.rect(x0, y0, x1, y1, fill="#ffffff", stroke=INK, sw=self.mm(0.25))
        horiz = (x1 - x0) >= (y1 - y0)
        L = (x1 - x0) if horiz else (y1 - y0)
        n = max(1, int(L / pas))
        for k in range(1, n):
            u = k * L / n
            if horiz:
                c.line(x0 + u, y0, x0 + u, y1, stroke=INK, sw=self.mm(0.13))
            else:
                c.line(x0, y0 + u, x1, y0 + u, stroke=INK, sw=self.mm(0.13))

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
                    c.line(a, line - 0.05, m + 0.15, line - 0.05, stroke=INK, sw=self.mm(0.18))
                    c.line(m - 0.15, line + 0.05, b, line + 0.05, stroke=INK, sw=self.mm(0.18))
                else:
                    c.line(line - 0.05, a, line - 0.05, m + 0.15, stroke=INK, sw=self.mm(0.18))
                    c.line(line + 0.05, m - 0.15, line + 0.05, b, stroke=INK, sw=self.mm(0.18))
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

    def etiquettes(self, ignorer=(), deplace=None):
        """NOM en capitales (9 pt gras), surface (7 pt) ; tournee a 90 degres dans une piece etroite."""
        c = self.c
        deplace = deplace or {}
        cw = 0.62                                  # largeur moyenne d'un caractere (URW Gothic), en corps
        for r in self.pieces:
            nom = nom_court(r)
            if r["nom"] in ignorer or nom in ignorer:
                continue
            x0, y0, x1, y1 = max(r["rects"], key=lambda q: (q[2] - q[0]) * (q[3] - q[1]))
            w, h = x1 - x0, y1 - y0
            if r["code"] in ("parvis", "jardin", "patio", "terrasse", "balcon", "toit_jard") and w * h < 2.5:
                continue
            area = f"{r['surface']:.1f}".replace(".", ",") + " m²"
            if r["code"] in ("parvis", "jardin") or nom in ("LOCAL GE", "JARDINIÈRE"):
                area = ""
            s9, s7 = self.pt(9), self.pt(7)
            cx, cy = deplace.get(r["nom"], ((x0 + x1) / 2, (y0 + y1) / 2))
            words = nom.split(" ")
            lines = [nom]
            larg = lambda t, s: len(t) * s * cw / self.S        # noqa: E731  (metres)
            if larg(nom, s9) > w - 0.6 and len(words) > 1:
                cut = max(range(1, len(words)), key=lambda k: -abs(len(" ".join(words[:k])) - len(" ".join(words[k:]))))
                lines = [" ".join(words[:cut]), " ".join(words[cut:])]
            wid = max(larg(t, s9) for t in lines)
            haut = (len(lines) * s9 * 1.15 + (s7 * 1.2 if area else 0)) / self.S
            rot = wid > w - 0.3 and h > w
            if rot:
                lines = [nom]
                t = nom + ("  " + area if area else "")
                c.text(cx, cy, t, size=s7 * 1.1, fill=INK, weight=700, rot=-90)
                self.reserve.append((cx - 0.2, cy - larg(t, s7) / 2, cx + 0.2, cy + larg(t, s7) / 2))
                continue
            top = cy - haut / 2 + s9 * 0.85 / self.S
            for k, ln in enumerate(lines):
                c.text(cx, top + k * s9 * 1.15 / self.S, ln, size=s9, fill=INK, weight=700)
            if area:
                c.text(cx, top + len(lines) * s9 * 1.15 / self.S, area, size=s7, fill=INK)
            self.reserve.append((cx - wid / 2, cy - haut / 2, cx + wid / 2, cy + haut / 2))

    # ------------------------------------------------------------------ habillage
    def cotes(self, xs, ys, xpos, ypos, total_x=None, total_y=None):
        c = self.c
        g = []

        def tick(px, py):
            g.append(f'<line x1="{px - 3:.1f}" y1="{py + 3:.1f}" x2="{px + 3:.1f}" y2="{py - 3:.1f}" stroke="{INK}" stroke-width="{self.mm(0.25):.2f}"/>')

        for chain, yy in ((xs, ypos),) + (((total_x, ypos - 0.62),) if total_x else ()):
            py = c.Y(yy)
            g.append(f'<line x1="{c.X(chain[0]) - 6:.1f}" y1="{py:.1f}" x2="{c.X(chain[-1]) + 6:.1f}" y2="{py:.1f}" stroke="{INK}" stroke-width="{self.mm(0.1):.2f}"/>')
            for k, x in enumerate(chain):
                tick(c.X(x), py)
                if k:
                    v = f"{chain[k] - chain[k - 1]:.2f}".rstrip("0").rstrip(".").replace(".", ",")
                    g.append(f'<text x="{(c.X(x) + c.X(chain[k - 1])) / 2:.1f}" y="{py - 3:.1f}" font-size="{self.pt(7):.2f}" text-anchor="middle" fill="{INK}">{v}</text>')
        for chain, xx in ((ys, xpos),) + (((total_y, xpos - 0.7),) if total_y else ()):
            px = c.X(xx)
            g.append(f'<line x1="{px:.1f}" y1="{c.Y(chain[0]) - 6:.1f}" x2="{px:.1f}" y2="{c.Y(chain[-1]) + 6:.1f}" stroke="{INK}" stroke-width="{self.mm(0.1):.2f}"/>')
            for k, y in enumerate(chain):
                tick(px, c.Y(y))
                if k:
                    v = f"{chain[k] - chain[k - 1]:.2f}".rstrip("0").rstrip(".").replace(".", ",")
                    ym = (c.Y(y) + c.Y(chain[k - 1])) / 2
                    g.append(f'<text x="{px - 3:.1f}" y="{ym:.1f}" font-size="{self.pt(7):.2f}" text-anchor="middle" fill="{INK}" transform="rotate(-90 {px - 3:.1f} {ym:.1f})">{v}</text>')
        self.raw("".join(g))

    def axes(self, xs, ys, ytop, xleft, x_end, y_end):
        """Trame de reperage : bulles en peripherie, traits courts detaches du dessin."""
        c = self.c
        g = []
        r = self.mm(2.4)
        for k, x in enumerate(xs, 1):
            px, py = c.X(x), c.Y(ytop)
            g.append(f'<line x1="{px:.1f}" y1="{py + r:.1f}" x2="{px:.1f}" y2="{py + r + 0.5 * c.s:.1f}" stroke="{INK}" stroke-width="0.5"/>'
                     f'<line x1="{px:.1f}" y1="{c.Y(y_end) + 0.2 * c.s:.1f}" x2="{px:.1f}" y2="{c.Y(y_end) + 0.6 * c.s:.1f}" stroke="{INK}" stroke-width="0.5"/>'
                     f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{r:.1f}" fill="#fff" stroke="{INK}" stroke-width="0.7"/>'
                     f'<text x="{px:.1f}" y="{py + 3:.1f}" font-size="{self.pt(7):.2f}" text-anchor="middle" font-weight="700" fill="{INK}">{k}</text>')
        for k, y in enumerate(ys):
            px, py = c.X(xleft), c.Y(y)
            g.append(f'<line x1="{px + r:.1f}" y1="{py:.1f}" x2="{px + r + 0.5 * c.s:.1f}" y2="{py:.1f}" stroke="{INK}" stroke-width="0.5"/>'
                     f'<line x1="{c.X(x_end) + 0.2 * c.s:.1f}" y1="{py:.1f}" x2="{c.X(x_end) + 0.6 * c.s:.1f}" y2="{py:.1f}" stroke="{INK}" stroke-width="0.5"/>'
                     f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{r:.1f}" fill="#fff" stroke="{INK}" stroke-width="0.7"/>'
                     f'<text x="{px:.1f}" y="{py + 3:.1f}" font-size="{self.pt(7):.2f}" text-anchor="middle" font-weight="700" fill="{INK}">{chr(65 + k)}</text>')
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
        """Nord compact et echelle graphique a traits 0-1-3-5 m (bas a droite)."""
        c = self.c
        cx, cy, R = c.X(x), c.Y(y), self.mm(4)
        a = math.radians(-7.56)
        tip = (cx + R * math.sin(a), cy - R * math.cos(a))
        l_ = (cx + 0.45 * R * math.sin(a - 2.6), cy - 0.45 * R * math.cos(a - 2.6))
        r_ = (cx + 0.45 * R * math.sin(a + 2.6), cy - 0.45 * R * math.cos(a + 2.6))
        S = c.s
        sx, sy = cx + self.mm(9), cy + self.mm(1)
        g = [f'<polygon points="{tip[0]:.1f},{tip[1]:.1f} {l_[0]:.1f},{l_[1]:.1f} {cx:.1f},{cy:.1f} {r_[0]:.1f},{r_[1]:.1f}" fill="{INK}"/>',
             f'<text x="{tip[0]:.1f}" y="{tip[1] - self.mm(1.2):.1f}" font-size="{self.pt(7):.2f}" text-anchor="middle" font-weight="700" fill="{INK}">N</text>',
             f'<line x1="{sx:.1f}" y1="{sy:.1f}" x2="{sx + 5 * S:.1f}" y2="{sy:.1f}" stroke="{INK}" stroke-width="{self.mm(0.25):.2f}"/>']
        for m in (0, 1, 3, 5):
            g.append(f'<line x1="{sx + m * S:.1f}" y1="{sy - self.mm(1):.1f}" x2="{sx + m * S:.1f}" y2="{sy:.1f}" stroke="{INK}" stroke-width="{self.mm(0.18):.2f}"/>'
                     f'<text x="{sx + m * S:.1f}" y="{sy + self.mm(3):.1f}" font-size="{self.pt(7):.2f}" text-anchor="middle" fill="{INK}">{m}{" m" if m == 5 else ""}</text>')
        self.raw("".join(g))

    def equerre(self, x, y, vers, lettre):
        """Repere de coupe : equerre courte en trait fort, hors du dessin, tournee vers le sens du regard."""
        c = self.c
        L, t = self.mm(5), self.mm(0.45)
        dx, dy = {"N": (0, -1), "S": (0, 1), "E": (1, 0), "O": (-1, 0)}[vers]
        px, py = c.X(x), c.Y(y)
        if dx == 0:      # trait de coupe vertical (coupe Nord-Sud) : equerre horizontale -> regard Est/Ouest
            pass
        g = []
        if vers in ("E", "O"):
            g.append(f'<path d="M{px:.1f},{py - L:.1f} L{px:.1f},{py:.1f} L{px + dx * L * 0.7:.1f},{py:.1f}" fill="none" stroke="{INK}" stroke-width="{t:.2f}"/>')
            g.append(f'<text x="{px - dx * self.mm(2):.1f}" y="{py - L * 0.5:.1f}" font-size="{self.pt(9):.2f}" font-weight="700" text-anchor="middle" fill="{INK}">{lettre}</text>')
        else:
            g.append(f'<path d="M{px - L:.1f},{py:.1f} L{px:.1f},{py:.1f} L{px:.1f},{py + dy * L * 0.7:.1f}" fill="none" stroke="{INK}" stroke-width="{t:.2f}"/>')
            g.append(f'<text x="{px - L * 0.5:.1f}" y="{py - dy * self.mm(2):.1f}" font-size="{self.pt(9):.2f}" font-weight="700" text-anchor="middle" fill="{INK}">{lettre}</text>')
        self.raw("".join(g))

    def tirets(self, pts, ferme=True):
        """Projection au-dessus du plan de coupe : tirets noirs nets (0,25 mm, 2,5 / 1,2 mm)."""
        c = self.c
        d = "M" + " L".join(f"{c.X(x):.1f},{c.Y(y):.1f}" for x, y in pts) + (" Z" if ferme else "")
        self.raw(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{self.mm(0.25):.2f}" '
                 f'stroke-dasharray="{self.mm(2.5):.1f} {self.mm(1.2):.1f}"/>')

    def voiture(self, x, y, rot=0):
        """Vehicule en plan (absent du catalogue Archibooks) : 4,50 x 1,80 m au trait fin, interieur blanc."""
        c = self.c
        g = (f'<g transform="translate({c.X(x):.1f},{c.Y(y):.1f}) rotate({rot})">'
             f'<rect x="{-0.9 * c.s:.1f}" y="{-2.25 * c.s:.1f}" width="{1.8 * c.s:.1f}" height="{4.5 * c.s:.1f}" rx="{0.35 * c.s:.1f}" fill="#fff" stroke="{INK}" stroke-width="{self.mm(0.15):.2f}"/>'
             f'<rect x="{-0.75 * c.s:.1f}" y="{-0.9 * c.s:.1f}" width="{1.5 * c.s:.1f}" height="{2.0 * c.s:.1f}" rx="{0.2 * c.s:.1f}" fill="#fff" stroke="{INK}" stroke-width="{self.mm(0.13):.2f}"/></g>')
        self.raw(g)

    def texte(self, x, y, t, size=7, anchor="middle", weight=400, rot=0):
        self.c.text(x, y, t, size=self.pt(size), fill=INK, anchor=anchor, weight=weight, rot=rot)

    def svg(self):
        defs = (f'<defs>{self.lib.defs()}<marker id="{self.sid}_fl" markerWidth="7" markerHeight="7" refX="5" refY="3" orient="auto">'
                f'<path d="M0,0 L6,3 L0,6 z" fill="{INK}"/></marker></defs>')
        s = self.c.svg().replace('font-family="Inter, Liberation Sans, sans-serif"', f"font-family='{FONT}'")
        s = s.replace('stroke-width="2.6">', f'stroke-width="{self.mm(0.8):.2f}">')     # halo blanc fin sous les textes
        i = s.index(">") + 1
        return s[:i] + defs + s[i:]




# =============================================================================== villa
VILLA_CADRE = (-3.4, -4.6, 22.8, 20.6)
TIRET_AXE = None


def _pts(r):
    x0, y0, x1, y1 = r
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def _limite(f, pts):
    """Limite de propriete non batie : trait mixte long 0,25 mm."""
    c = f.c
    d = "M" + " L".join(f"{c.X(x):.1f},{c.Y(y):.1f}" for x, y in pts)
    f.raw(f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{f.mm(0.25):.2f}" '
          f'stroke-dasharray="{f.mm(6):.1f} {f.mm(1.5):.1f} {f.mm(1):.1f} {f.mm(1.5):.1f}"/>')


def _couv(f, couv):
    (a0, b0, a1, b1), (c0, d0, c1, d1) = couv
    f.tirets([(a0, b0), (a1, b0), (a1, b1), (c1, b1), (c1, d1), (c0, d1)])


def villa(niveau, s=19, sid=None, variante="V1"):
    f = Feuille(OPTION_C, niveau, *VILLA_CADRE, s, sid or f"vc_{niveau.replace('+', '')}")
    c = f.c
    # --- 1. sols et textures (au fond), recadres a leur emprise
    if niveau == "RDC":
        x0, y0, x1, y1 = F.STATIONNEMENT
        f.texture("texture_paves", _pts((x0, 0.2, x1, 4.5)), 0.6)
        f.texture("texture_pierre_bandes", _pts((5.7, 0.2, 7.0, 4.5)), 0.65)                 # allee du portillon
        f.texture("texture_pierre_bandes", _pts((2.5, 4.5, 15.5, 5.5)), 0.6)                 # passage couvert
        f.texture("texture_pierre_bandes", _pts((15.5, 2.6, 18.0, 5.5)), 0.6)                # preau
        f.texture("texture_granulat_fin", _pts((14.5, 0.34, 18.0, 2.6)), 0.6)                # sechoir
        f.texture("texture_granulat_fin", _pts((18.0, 0.2, 19.8, 17.82)), 0.55)              # passage de service Est
        f.texture("texture_pas_irreguliers", _pts((2.5, 16.8, 18.0, 17.82)), 0.8)            # passage Sud
        f.texture("texture_couvre_sol", _pts((0.2, 2.7, 2.5, 17.82)), 0.55)                  # bande Ouest
        f.texture("texture_pierre_bandes", _pts((9.0, 11.0, 14.5, 13.4)), 0.6)               # terrasse
        f.texture("texture_litiere", _pts((9.0, 13.4, 14.5, 17.82)), 0.6, holes=[_pts((11.7, 13.4, 12.5, 17.6))])
        f.texture("texture_pas_irreguliers", _pts((11.7, 13.4, 12.5, 17.6)), 0.85)          # pas japonais du patio
        # --- 2. vegetation El Croquis : grands sujets clairs, petits sombres, groupes, debords
        f.arbre("arbre_plan_canopee_semis_grande", 12.9, 15.9, 6.4, 36, rot=20)              # frangipanier du patio
        for (x, y, d, r_) in ((9.6, 17.2, 1.6, 0), (10.6, 17.3, 1.3, 70), (14.0, 14.0, 1.5, 140), (13.9, 17.2, 1.4, 30)):
            f.arbre("plante_plan_grandes_feuilles", x, y, d, 64, rot=r_)
        f.arbre("arbre_plan_canopee_pleine_moyenne", 0.9, 8.2, 4.8, 46, rot=15)             # ombre de la facade Ouest
        f.arbre("arbre_plan_canopee_pleine_petite", 1.1, 4.4, 3.2, 64, rot=80)
        f.arbre("arbre_plan_canopee_semis_moyenne", 0.8, 15.4, 5.0, 42, rot=200)
        f.arbre("palmier_plan_penne", 1.3, 12.0, 3.0, 55, rot=30)
        f.arbre("palmier_plan_eventail", 19.0, 6.2, 2.0, 55)
        f.arbre("palmier_plan_eventail", 19.1, 7.6, 1.6, 64, rot=40)
        f.arbre("arbre_plan_canopee_pleine_petite", 13.5, 2.0, 2.8, 55, rot=150)            # entre parking et sechoir
        f.arbre("arbre_plan_canopee_pleine_moyenne", 21.6, 9.0, 2.8, 30, rot=60)            # contexte Est (voisin)
        f.arbre("plante_plan_grandes_feuilles", 1.0, 3.3, 1.4, 64, rot=40)
        f.texture("texture_massif_tropical", _pts((0.2, 17.4, 19.8, 17.82)), 0.7)
    elif niveau == "R+1":
        f.texture("texture_couvre_sol", _pts((14.5, 11.0, 18.0, 16.8)), 0.45)
        f.texture("texture_couvre_sol", _pts((9.0, 11.0, 14.5, 13.4)), 0.45)
        f.texture("texture_pierre_bandes", _pts((5.5, 4.5, 18.0, 5.5)), 0.55)
        f.texture("texture_massif_tropical", _pts((1.7, 13.6, 2.5, 16.8)), 0.7)
        f.arbre("arbre_plan_canopee_semis_grande", 12.9, 15.9, 6.4, 30, rot=20)
        f.arbre("arbre_plan_canopee_pleine_moyenne", 0.9, 8.2, 4.8, 46, rot=15)
    else:
        f.texture("texture_pierre_bandes", _pts((5.5, 5.5, 18.0, 11.0)), 0.5)
        f.texture("texture_pierre_bandes", _pts((2.5, 9.7, 9.0, 16.8)), 0.5, holes=[_pts((5.5, 9.7, 9.0, 11.0))])
        x0, y0, x1, y1, _ = F.JARDINIERE
        f.texture("texture_massif_tropical", _pts((x0, y0, x1, y1)), 0.7)
        for (a, b, cc, d) in F.TOITURE_VEGETALE:
            f.texture("texture_couvre_sol", _pts((a, b, cc, d)), 0.45)
        f.arbre("arbre_plan_canopee_semis_grande", 12.9, 15.9, 6.4, 30, rot=20)
    # --- 3. mobilier, escalier, murs, ouvertures
    if niveau != "TOIT":
        f.mobilier()
    f.escalier_u(2.55, 5.55, 5.45, 9.65, palier="N", fleche=niveau != "TOIT")
    f.murs_dessin()
    f.ouvertures(F.OUVERTURES)
    # --- 4. peau de l'etage, projections au-dessus du plan de coupe (tirets)
    couv = F.COUV_V1 if variante == "V1" else F.COUV_V2
    if niveau == "R+1":
        for sens, line, a, b, out, _ax in F.PEAU_VILLA:
            lo, hi = sorted((line + out * 0.04, line + out * 0.16))
            f.brique(a, lo, b, hi, pas=0.31) if sens == "h" else f.brique(lo, a, hi, b, pas=0.31)
        for a, b in F.ECRANS_GALERIE:
            c.line(a, 11.12, b, 11.12, stroke=INK, sw=f.mm(0.35))
        c.rect(1.7, 13.6, 2.5, 16.8, stroke=INK, sw=f.mm(0.25))
        _couv(f, couv)
    if niveau == "RDC":
        f.tirets([(2.5, 4.36), (18.0, 4.36)], ferme=False)                  # nez de dalle de l'etage (loggia)
        f.tirets(_pts((15.5, 2.6, 18.0, 4.5)))                               # dalle du preau
        f.tirets([(9.0, 13.4), (14.5, 13.4)], ferme=False)                   # rive de la terrasse couverte
        f.voiture(8.4, 2.45)
        f.voiture(11.1, 2.45)
    if niveau == "TOIT":
        _couv(f, couv)
        for (px, py) in F.POTEAUX:
            c.rect(px - 0.08, py - 0.08, px + 0.08, py + 0.08, fill=INK, stroke="none", sw=0)
        f.poly([(2.5, 4.5), (18.0, 4.5), (18.0, 11.0), (9.0, 11.0), (9.0, 16.8), (2.5, 16.8)], stroke=INK, sw=f.mm(0.5))
    # --- 5. limites, clotures
    if niveau == "RDC":
        c.rect(0.0, 17.82, 20.0, 18.0, fill=INK, stroke="none", sw=0)                      # mur vegetalise h 3,50 (coupe)
        for x0, x1 in ((0.0, 6.0), (12.5, 18.5), (19.5, 20.0)):
            c.rect(x0, 0.0, x1, 0.2, fill=INK, stroke="none", sw=0)
        c.rect(0.0, 0.2, 0.2, 17.82, fill=INK, stroke="none", sw=0)
        c.rect(19.8, 0.2, 20.0, 17.82, fill=INK, stroke="none", sw=0)
        for a, b in ((6.0, 7.0), (7.0, 12.5), (18.5, 19.5)):                                 # portillons et portail (lames)
            c.line(a, 0.1, b, 0.1, stroke=INK, sw=f.mm(0.18))
            c.line(a, -0.02, b, -0.02, stroke=INK, sw=f.mm(0.13))
        f.brique(14.5, 0.2, 18.0, 0.34)
        c.rect(0.3, 0.3, 3.0, 2.5, fill="#ffffff", stroke=INK, sw=f.mm(0.35))
        f.texte(5.0, 18.7, "mur végétalisé en limite, h 3,50 m", 7)
        f.texte(9.0, -0.45, "portail coulissant 5,50 m", 7)
        f.texte(6.5, -0.45, "portillon", 7)
        f.texte(19.0, -0.45, "service", 7)
    else:
        _limite(f, [(0.0, 18.0), (0.0, 0.0), (20.0, 0.0), (20.0, 18.0)])
    f.texte(21.4, -0.6, "RUE NORD", 7, anchor="start", weight=700)
    f.texte(-2.6, 19.9, "RUE OUEST", 7, anchor="start", weight=700)
    # --- 6. etiquettes, cotes, axes, reperes de coupe, nord et echelle
    dep = {"Patio planté": (10.6, 14.4), "Passage couvert d'entrée": (9.0, 5.0), "Escalier": (4.0, 6.15),
           "Édicule d'escalier": (4.0, 6.15), "Cuisine": (13.75, 8.4), "Chambre 2": (16.25, 6.5),
           "Salon familial": (7.25, 9.4), "SdB parentale": (4.2, 12.5),
           "Terrasse couverte sur patio": (11.75, 12.2), "Séchoir à ciel ouvert": (16.25, 1.4),
           "Préau cuisine africaine": (16.75, 3.55), "Loggia Nord (rangements)": (12.0, 5.0),
           "Jardinière (plantation basse)": (12.0, 5.0), "Toit-terrasse couvert": (12.0, 8.2)}
    f.etiquettes(ignorer=("Local GE + niche compteurs", "Jardinière Ouest", "Jardinière (plantation basse)"),
                 deplace=dep)
    if niveau == "RDC":
        f.texte(1.65, 1.5, "LOCAL GE", 7, weight=700)
        f.texte(9.75, 4.15, "STATIONNEMENT · 2 PLACES", 7, weight=700)
    f.cotes([0.0] + list(CX) + [20.0], [0.0] + list(CY), -1.35, -1.25, total_x=[0.0, 20.0], total_y=[0.0, 18.0])
    f.axes(list(CX), list(CY[:4]), -3.5, -3.0, 20.7, 18.9)
    if niveau == "RDC":
        f.equerre(10.75, -0.2, "O", "A")
        f.equerre(10.75, 18.35, "O", "A")
        f.equerre(-0.25, 14.8, "N", "B")
        f.equerre(20.25, 14.8, "N", "B")
    f.nord_echelle(16.8, 20.0)
    return f.svg()


# =============================================================================== locatif
LOC_CADRE = (-3.4, 15.0, 22.8, 35.4)


def maisons(niveau, s=19, sid=None, variante="V1"):
    f = Feuille(LOCATIF_M, niveau, *LOC_CADRE, s, sid or f"lm_{niveau.replace('+', '')}")
    c = f.c
    if niveau == "RDC":
        f.texture("texture_paves", _pts((0.2, 18.0, 3.0, 30.0)), 0.6)
        f.texture("texture_pierre_bandes", _pts((0.2, 30.0, 19.8, 32.8)), 0.6)
        for x0 in MX[:2]:
            f.texture("texture_couvre_sol", _pts((x0, 18.0, x0 + 8.5, 21.0)), 0.5)
        f.arbre("arbre_plan_canopee_semis_moyenne", 4.7, 19.3, 4.2, 42, rot=40)
        f.arbre("arbre_plan_canopee_pleine_petite", 7.0, 19.5, 2.6, 64, rot=110)
        f.arbre("arbre_plan_canopee_semis_moyenne", 13.3, 19.2, 4.2, 36, rot=200)
        f.arbre("palmier_plan_eventail", 19.0, 19.0, 2.0, 55)
        for x in (3.6, 12.2, 18.6):
            f.arbre("plante_plan_grandes_feuilles", x, 32.3, 1.4, 64, rot=x * 30)
        f.texture("texture_massif_tropical", _pts((3.0, 18.0, 19.8, 18.4)), 0.7)
        f.voiture(1.5, 21.4)
        f.voiture(1.5, 27.0)
    elif niveau == "TOIT":
        for x0 in MX[:2]:
            f.texture("texture_pierre_bandes", [(x0, 21.0), (x0 + 8.5, 21.0), (x0 + 8.5, 30.0), (x0 + 5.6, 30.0),
                                                (x0 + 5.6, 27.5), (x0 + 2.0, 27.5), (x0 + 2.0, 30.0), (x0, 30.0)], 0.5)
            f.texture("texture_massif_tropical", _pts((x0 + 0.15, 21.0, x0 + 8.35, 21.45)), 0.7)
    if niveau != "TOIT":
        f.mobilier()
    for x0 in MX[:2]:                      # escalier droit a volee unique le long de x, depart cote entree
        g = []
        for k in range(11):
            xx = x0 + 2.85 + k * 0.255
            g.append(f'<line x1="{c.X(xx):.1f}" y1="{c.Y(27.6):.1f}" x2="{c.X(xx):.1f}" y2="{c.Y(28.7):.1f}" stroke="{INK}" stroke-width="{f.mm(0.18):.2f}"/>'
                     f'<line x1="{c.X(xx):.1f}" y1="{c.Y(28.8):.1f}" x2="{c.X(xx):.1f}" y2="{c.Y(29.9):.1f}" stroke="{INK}" stroke-width="{f.mm(0.18):.2f}"/>')
        g.append(f'<line x1="{c.X(x0 + 2.85):.1f}" y1="{c.Y(28.75):.1f}" x2="{c.X(x0 + 5.55):.1f}" y2="{c.Y(28.75):.1f}" stroke="{INK}" stroke-width="{f.mm(0.25):.2f}"/>')
        if niveau != "TOIT":
            g.append(f'<line x1="{c.X(x0 + 3.0):.1f}" y1="{c.Y(29.35):.1f}" x2="{c.X(x0 + 5.3):.1f}" y2="{c.Y(29.35):.1f}" stroke="{INK}" stroke-width="{f.mm(0.18):.2f}" marker-end="url(#{f.sid}_fl)"/>'
                     f'<line x1="{c.X(x0 + 5.3):.1f}" y1="{c.Y(28.15):.1f}" x2="{c.X(x0 + 3.0):.1f}" y2="{c.Y(28.15):.1f}" stroke="{INK}" stroke-width="{f.mm(0.18):.2f}" marker-end="url(#{f.sid}_fl)"/>')
        f.raw("".join(g))
    f.murs_dessin()
    f.ouvertures([o for k, x0 in enumerate(MX[:2]) for o in F.ouvertures_maison(x0, k == 0)])
    if niveau == "R+1":
        for k, x0 in enumerate(MX[:2]):
            for sens, line, a, b, out, _ax in F.peau_maison(x0, k == 0):
                lo, hi = sorted((line + out * 0.04, line + out * 0.16))
                f.brique(a, lo, b, hi, pas=0.31) if sens == "h" else f.brique(lo, a, hi, b, pas=0.31)
    if niveau in ("R+1", "TOIT"):
        for k, x0 in enumerate(MX[:2]):
            f.tirets(_pts(F.couv_maison(x0, k == 0)))
    if niveau == "TOIT":
        for k, x0 in enumerate(MX[:2]):
            x1 = x0 + 8.5
            for px in (x0 + 0.15, x0 + 4.25, x1 - 0.15):
                for py in (21.15, 27.35):
                    c.rect(px - 0.08, py - 0.08, px + 0.08, py + 0.08, fill=INK, stroke="none", sw=0)
            f.poly(_pts((x0, 21.0, x1, 30.0)), stroke=INK, sw=f.mm(0.5))
    if niveau == "RDC":
        c.rect(0.0, 17.82, 20.0, 18.0, fill=INK, stroke="none", sw=0)
        c.rect(0.0, 18.0, 0.2, 18.5, fill=INK, stroke="none", sw=0)
        c.rect(0.0, 30.0, 0.2, 30.2, fill=INK, stroke="none", sw=0)
        c.rect(19.8, 18.0, 20.0, 33.0, fill=INK, stroke="none", sw=0)
        c.rect(0.0, 32.8, 20.0, 33.0, fill=INK, stroke="none", sw=0)
        for a, b in ((18.5, 30.0), (30.2, 33.0)):
            c.line(0.1, a, 0.1, b, stroke=INK, sw=f.mm(0.18))
        f.texte(14.0, 17.45, "mur végétalisé, h 3,50 m (limite avec la villa)", 7)
    else:
        _limite(f, [(0.0, 18.0), (0.0, 33.0), (20.0, 33.0), (20.0, 18.0)])
    f.texte(-2.6, 34.7, "RUE OUEST", 7, anchor="start", weight=700)
    if niveau == "RDC":
        for k, x0 in enumerate(MX[:2]):
            f.texte(x0 + 4.25, 33.75, f"MAISON {k + 1} · 153,0 m² SUR DEUX NIVEAUX", 7, weight=700)
    dep = {}
    for k, x0 in enumerate(MX[:2]):
        dep[f"M{k + 1} Séjour-SAM"] = (x0 + 2.7, 23.4)
        dep[f"M{k + 1} Toit-terrasse sous pergola"] = (x0 + 4.25, 24.2)
        dep[f"M{k + 1} Jardin privé"] = (x0 + 6.6, 20.3)
        dep[f"M{k + 1} Cour d'entrée"] = (x0 + 4.25, 31.5)
        dep[f"M{k + 1} Dégagement"] = (x0 + 1.8, 26.95)
    f.etiquettes(ignorer=("Allée piétonne", "Stationnement 2 places (rue Ouest)", "M1 Escalier", "M2 Escalier",
                          "M1 Édicule d'escalier", "M2 Édicule d'escalier"), deplace=dep)
    for x0 in MX[:2]:          # escalier : etiquette tournee sur le palier
        nom = "ÉDICULE  9,0 m²" if niveau == "TOIT" else "ESCALIER  9,0 m²"
        f.texte(x0 + 2.45, 28.75, nom, 6.5, weight=700, rot=-90)
    if niveau == "RDC":
        f.texte(1.5, 24.2, "STATIONNEMENT", 7, weight=700, rot=-90)
    f.cotes([0.0] + list(MX), list(MY), -1.35, 16.4, total_x=[0.0, 20.0], total_y=[18.0, 33.0])
    f.axes(list(MX), list(MY), 15.45, -3.0, 20.7, 33.9)
    if niveau == "RDC":
        f.equerre(7.5, 17.4, "O", "C")
        f.equerre(7.5, 33.4, "O", "C")
    f.nord_echelle(16.8, 34.8)
    return f.svg()
