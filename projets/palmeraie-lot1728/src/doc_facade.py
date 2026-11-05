"""Planches facades de l'option C (reference Capitude ABYA 2) : elevations annotees, vues clay, materiaux.

Les pages sont des fonctions reutilisees par le dossier de presentation de l'option C.
"""
import base64
import pathlib

import facade as F
from doc import OUT, html, page, to_pdf

REND = OUT / "rendu"
K = 1600 / 24.0          # px par metre des elevations (camera orthographique de 24 m sur 1600 px)
CROP = (40, 205, 1560, 780)   # x0, y0, x1, y1 en px (de z = +8,3 a z = -0,8)

# u = coordonnee horizontale du plan le long de la facade ; px = 800 + sens * (u - centre) * K
ELEV = {
    "N": ("Facade Nord, sur la rue d'acces", "elev_N.png", -1, 10.5, "x"),
    "O": ("Facade Ouest, sur la rue laterale", "elev_O.png", 1, 11.0, "y"),
    "S": ("Facade Sud, sur le jardin et le locatif", "elev_S.png", 1, 10.5, "x"),
    "E": ("Facade Est, en limite a 1,50 m", "elev_E.png", -1, 11.0, "y"),
}
# annotations : (u, z, texte, rang) ; rang 0 / 1 au-dessus, 2 au-dessous
NOTES = {
    "N": [(8.5, 7.0, "Toiture-ombriere en beton blanc, debord 1,2 m", 1),
          (4.4, 6.0, "Lanterne d'escalier en claustra BTC", 0),
          (9.2, 5.6, "Salon familial : persiennes bois coulissantes", 0),
          (12.5, 5.3, "Chambre 2 : porte-fenetre, barreaudage", 1),
          (17.0, 3.9, "Aile de service de plain-pied", 0),
          (7.5, 1.4, "Entree sous porche 1,7 m", 2),
          (9.2, 1.7, "SAM", 2), (12.5, 1.7, "Cuisine", 2),
          (17.7, 1.6, "Preau cuisine africaine, claustra BTC", 2)],
    "O": [(7.2, 6.0, "Lanterne d'escalier (2 niveaux)", 0),
          (14.3, 5.8, "Balcon de la suite derriere une double peau en claustra", 0),
          (10.9, 5.9, "Jour SdB", 1),
          (8.0, 7.0, "Debord 1,6 m", 1),
          (14.2, 1.5, "Salon : coulissant 3,2 m sous la dalle du balcon", 2)],
    "S": [(6.2, 5.5, "Chambre parentale", 0), (12.0, 3.0, "Pergola et claustra haute du patio", 1),
          (6.4, 1.4, "Salon : baie 4,0 m sur le jardin", 2), (16.7, 1.6, "Chambre nounou", 2)],
    "E": [(11.3, 6.0, "Chambre 3 : deux jours hauts", 0), (5.6, 1.5, "Sechoir couvert, claustra en limite", 2),
          (10.1, 1.1, "Buanderie", 2), (14.8, 1.1, "Nounou", 2)],
}
NIVEAUX = [(0.0, "±0,00 TN"), (0.45, "+0,45 RDC"), (3.75, "+3,75 R+1"), (7.07, "+7,07 toiture")]
MATERIAUX = [
    ("#c9a27a", "BTC apparents", "Murs du rez-de-chaussee, claustras, cloture : terre stabilisee locale"),
    ("#eeebe4", "Enduit blanc casse", "Murs de l'etage, sur maconnerie de parpaings"),
    ("#f4f2ed", "Beton blanc lisse", "Toiture-ombriere, casquettes, nez de dalle"),
    ("#8a5a3b", "Iroko ou teck", "Persiennes coulissantes, portail, portillons, passerelle"),
    ("#3d3d3b", "Aluminium sombre", "Menuiseries vitrees, barreaudage des portes-fenetres"),
    ("#6c645a", "Socle mineral sombre", "Soubassement de la cloture et de la maison (pierre ou laterite)"),
]


def img64(path, crop=None, quality=None):
    from PIL import Image
    import io
    im = Image.open(path).convert("RGB")
    if crop:
        im = im.crop(crop)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=quality or 88)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def accents(s):
    rep = {"Facade": "Façade", "facade": "façade", "laterale": "latérale", "a 1,50": "à 1,50", "Toiture-ombriere": "Toiture-ombrière",
           "beton": "béton", "debord": "débord", "Debord": "Débord", "Lanterne d'escalier": "Lanterne d’escalier",
           "Entree": "Entrée", "Preau": "Préau", "Guerite": "Guérite", "Sechoir": "Séchoir", "derriere": "derrière",
           "etage": "étage", "rez-de-chaussee": "rez-de-chaussée", "maconnerie": "maçonnerie", "cloture": "clôture",
           "Beton": "Béton", "mineral": "minéral", "Menuiseries vitrees": "Menuiseries vitrées",
           "porte-fenetre": "porte-fenêtre", "portes-fenetres": "portes-fenêtres", "stabilisee": "stabilisée",
           "Enduit blanc casse": "Enduit blanc cassé", "Murs de l'etage": "Murs de l’étage", "SdB": "SdB",
           "d'acces": "d’accès", "la rue d’accès": "la rue d’accès"}
    for a, b in rep.items():
        s = s.replace(a, b)
    return s


def elevation_svg(code):
    titre, fichier, sens, centre, _ = ELEV[code]
    x0, y0, x1, y1 = CROP
    w, h = x1 - x0, y1 - y0
    px = lambda u: 800 + sens * (u - centre) * K - x0          # noqa: E731
    pz = lambda z: 500 - (z - 3.6) * K - y0                    # noqa: E731
    g = [f'<image href="{img64(REND / fichier, CROP)}" x="0" y="0" width="{w}" height="{h}"/>']
    # niveaux
    for z, t in NIVEAUX:
        y = pz(z)
        g.append(f'<line x1="{w - 128}" y1="{y:.1f}" x2="{w - 8}" y2="{y:.1f}" stroke="#8a8e94" stroke-width="1" stroke-dasharray="4 3"/>')
        g.append(f'<text x="{w - 8}" y="{y - 4:.1f}" font-size="15" fill="#6b6f76" text-anchor="end">{t}</text>')
    # annotations : rangs attribues automatiquement pour eviter les chevauchements
    rows_up, rows_dn = [22, 48, 74], [h - 46, h - 18]
    used = {}
    for u, z, t, rang in sorted(NOTES[code], key=lambda n: px(n[0])):
        x, y = px(u), pz(z)
        t = accents(t)
        half = len(t) * 4.6
        cand = rows_up if rang < 2 else rows_dn
        ty = cand[-1]
        for r in cand:
            if used.get(r, -1e9) < x - half - 10:
                ty = r
                break
        used[ty] = x + half
        g.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="#b5653a"/>')
        g.append(f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{x:.1f}" y2="{ty + (6 if rang < 2 else -18):.1f}" stroke="#b5653a" stroke-width="1.2"/>')
        g.append(f'<text x="{x:.1f}" y="{ty:.1f}" font-size="17" fill="#23262b" text-anchor="middle" font-weight="500" '
                 f'paint-order="stroke" stroke="#fff" stroke-width="4">{t}</text>')
    # echelle 5 m
    sx, sy = w - 300 - 5 * K, h - 26
    g.append(f'<rect x="{sx}" y="{sy}" width="{5 * K:.1f}" height="6" fill="#23262b"/>'
             f'<rect x="{sx + K:.1f}" y="{sy}" width="{K:.1f}" height="6" fill="#fff"/><rect x="{sx + 3 * K:.1f}" y="{sy}" width="{K:.1f}" height="6" fill="#fff"/>'
             f'<rect x="{sx}" y="{sy}" width="{5 * K:.1f}" height="6" fill="none" stroke="#23262b"/>'
             f'<text x="{sx}" y="{sy - 6}" font-size="14" fill="#6b6f76">0</text><text x="{sx + 5 * K:.1f}" y="{sy - 6}" font-size="14" fill="#6b6f76" text-anchor="middle">5 m</text>')
    return (f'<figure style="margin:0"><figcaption style="font-weight:600;font-size:9.5pt;margin-bottom:1mm">{accents(titre)}</figcaption>'
            f'<svg viewBox="0 0 {w} {h}" style="width:100%;max-height:78mm;height:auto;display:block" font-family="Inter, sans-serif">{"".join(g)}</svg></figure>')


def page_reference(n, doc):
    R = F.REFERENCE
    repris = "".join(f"<tr><td style='font-weight:600;padding:1.2mm 3mm 1.2mm 0;vertical-align:top'>{a}</td>"
                     f"<td style='padding:1.2mm 0;color:#45484e'>{b}</td></tr>" for a, b in [
        ("Toiture-ombrière débordante", "Une seule dalle mince en béton blanc sur tout l’étage, débord de 1,6 m à l’Ouest, 1,2 m au Nord, 0,8 m à l’Est."),
        ("Persiennes bois coulissantes", "Devant les baies de l’étage au Nord, à l’Est et au Sud : intimité côté rue, ventilation volets fermés."),
        ("Garde-corps à barreaudage", "Portes-fenêtres du salon familial et de la chambre 2, comme les balcons d’ABYA 2."),
        ("Claustra de briques ajourées", "Pour tout ce qui sert : cage d’escalier, aile de service, clôture. Ici en BTC, la terre du brief."),
        ("Séjour vitré sous débord", "Coulissant de 3,2 m du salon à l’Ouest sous la dalle du balcon, baie de 4,0 m au Sud."),
    ])
    compl = "".join(f"<li><b>{k}</b> : {t}</li>" for k, t in [
        ("CDD Cotonou", "claustra devant la cage d’escalier, qui devient la lanterne de l’angle des deux rues"),
        ("Typologie urbaine 8", "double peau Ouest : le balcon de la suite derrière un claustra pleine hauteur"),
        ("House on Pali Hill", "portail et portillons en planches de bois sur un socle minéral sombre"),
    ])
    mats = "".join(f"<div style='display:flex;gap:3mm;align-items:flex-start;margin-bottom:2.2mm'>"
                   f"<div style='width:8mm;height:8mm;flex:none;background:{c};border:0.4pt solid #cfc9bf'></div>"
                   f"<div><div style='font-weight:600'>{accents(t)}</div><div class='small muted'>{accents(d)}</div></div></div>"
                   for c, t, d in MATERIAUX)
    body = f"""
<div class="kicker">Option C · Façades</div>
<h2>Une écriture tirée d’ABYA 2 : une dalle qui fait de l’ombre, du bois qui filtre, de la terre qui ajoure</h2>
<div class="grid" style="grid-template-columns: 96mm 1fr; gap: 8mm; margin-top: 3mm">
  <div>
    <h3 style="margin-top:0">Pourquoi ABYA 2</h3>
    <p class="small">{R['pourquoi']}</p>
    <table class="small" style="border-collapse:collapse;width:100%">{repris}</table>
    <h3>Compléments pris dans Capitude</h3>
    <ul class="small" style="margin:0;padding-left:4mm">{compl}</ul>
  </div>
  <div>
    <img src="{img64(REND / 'clay_arrivee.png', quality=85)}" style="width:100%;display:block;border:0.4pt solid #e3ded5"/>
    <p class="small muted" style="margin-top:1.5mm">Arrivée depuis la rue Nord, portail ouvert, 8 h 30 en novembre (maquette de volumes, sans matières).
    À l’étage, les persiennes coulissantes et le barreaudage ; au rez-de-chaussée en BTC, le porche, la SAM et la cuisine
    sous une casquette de 0,9 m ; à droite la lanterne d’escalier en claustra et la guérite.</p>
    <h3>Matériaux</h3>
    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;column-gap:5mm">{mats}</div>
  </div>
</div>"""
    return page(body, n, doc)


def page_elevations(n, doc, codes=("N", "O")):
    figs = "".join(elevation_svg(c) for c in codes)
    climat = {
        ("N", "O"): ("Rues au Nord et à l’Ouest. Au Nord, le soleil ne vient qu’en juin, haut (72° à midi) : le débord "
                     "de 1,2 m ombre alors entièrement les baies de l’étage. À l’Ouest, le soleil de l’après-midi est rasant "
                     "(19,5° à 16 h 30 en novembre) : aucun débord ne suffit, d’où la double peau en claustra devant la suite, "
                     "les arbres de la bande de 3,2 m et des stores en toile ou en bambou pour le coulissant du salon."),
        ("S", "E"): ("Au Sud, le jardin arrière et le locatif à 5,5 m : la claustra haute de la pergola coupe les vues "
                     "du locatif vers le patio. À l’Est, la limite séparative est à 1,50 m : seulement des jours hauts "
                     "(allège à 1,80 m), pour respecter les distances de vues droites, et un claustra en limite au séchoir."),
    }[tuple(codes)]
    body = f"""
<div class="kicker">Option C · Façades</div>
<h2>Élévations {' et '.join({'N': 'Nord', 'O': 'Ouest', 'S': 'Sud', 'E': 'Est'}[c] for c in codes)}</h2>
<div class="grid" style="grid-template-columns: 1fr 52mm; gap: 6mm; margin-top: 2mm">
  <div style="display:grid;gap:3mm">{figs}</div>
  <div class="small muted" style="padding-top:6mm">
    <p>{climat}</p>
    <p>Élévations tirées de la maquette 3D du modèle (ouvertures listées dans <code>facade.py</code>), clôtures, guérite
    et arbres masqués ; lumière conventionnelle à 45°.</p>
    <p><b>Alignements.</b> Axes verticaux communs au rez-de-chaussée et à l’étage (claustra d’escalier, baies, jours) ; linteaux à 2,40 m partout ; allèges à 1,00 m pour les fenêtres, 1,80 m pour les jours hauts, 0 pour les baies.</p>
  </div>
</div>"""
    return page(body, n, doc)


def page_vues(n, doc):
    def fig(src, cap, q=82):
        return (f'<figure style="margin:0"><img src="{img64(src, quality=q)}" style="width:100%;height:62mm;object-fit:cover;display:block;'
                f'border:0.4pt solid #e3ded5"/><figcaption class="small muted" style="margin-top:1.2mm">{cap}</figcaption></figure>')
    body = f"""
<div class="kicker">Option C · Façades</div>
<h2>L’angle des deux rues et le patio</h2>
<p class="small muted" style="margin:0">Perspectives à deux points de fuite (axe de visée horizontal, cadrage par décentrement) : les verticales restent verticales.</p>
<div class="grid g2" style="gap:4mm 6mm;margin-top:2mm">
  {fig(REND / 'clay_rue.png', "Depuis le carrefour au Nord-Ouest, 16 h 30. La clôture (socle de 1,0 m et claustra en BTC jusqu’à 2,2 m) laisse passer l’air ; au-dessus, la toiture-ombrière, la lanterne d’escalier et la double peau de la suite.")}
  {fig(REND / 'clay_aerien.png', "Axonométrie depuis le Nord-Ouest : la dalle de toiture unique, la casquette et le porche au Nord, l’aile de service basse à l’Est, le patio ouvert au cœur.")}
  {fig(REND / 'clay_patio.png', "Le patio depuis le jardin Sud, 8 h 30 en novembre : terrasse couverte, poteaux bois, passerelle à lames de l’étage.")}
  {fig(REND / 'ia_v1_provisoire' / 'patio_1.png', "Rendu d’ambiance généré par IA (Sume) à partir de la maquette du patio, avant la reprise des façades sur rue ; les façades du patio n’ont pas changé. Image indicative : matières et végétation interprétées.")}
</div>"""
    return page(body, n, doc)


def pages(start=1, doc="Option C · Façades"):
    return [page_reference(start, doc), page_elevations(start + 1, doc, ("N", "O")),
            page_elevations(start + 2, doc, ("S", "E")), page_vues(start + 3, doc)]


if __name__ == "__main__":
    out_html = OUT / "C_Facades_Lot1728.html"
    out_html.write_text(html(pages(), "Option C, façades"))
    to_pdf(str(out_html), str(OUT / "C_Facades_Lot1728.pdf"))
    print("ok", OUT / "C_Facades_Lot1728.pdf")
