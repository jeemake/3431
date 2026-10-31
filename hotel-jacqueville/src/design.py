"""Variantes A et B : formes (repère barre u,v), programme, surfaces, biotope, estimatif."""
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
from geo import SITE, rect_uv, bar_frame, TRAME, RECUL_NORD, D_COURSIVE, D_PIECE, D_LOGGIA, D_BARRE

T = TRAME
V0 = RECUL_NORD                      # façade nord des bâtiments
U0 = 5.9                             # début de la barre A (calé sur le recul ouest)

# ---------------------------------------------------------------- formes au sol
def R(u, v, w, d):
    return rect_uv(u, v, u + w, v + d)

VARIANTS = {}

# ---- A : « Le Toit-Stade »
A = dict(code='A', nom='Le Toit-Stade', shapes={})
A['shapes']['bati'] = [('Barre hôtel R+2 + toit', R(U0, V0, 9 * T, D_BARRE))]
A['shapes']['tech'] = [('Locaux CIE/SODECI + GE (toit planté)', R(2.0, V0, 3.5, 5.0))]
A['shapes']['piscine'] = [('Bassin de nage 2,5 × 16 m', R(10.5, 21.0, 16.0, 2.5)),
                          ('Bain froid (récupération)', R(27.5, 21.0, 2.5, 2.5))]
A['shapes']['deck'] = [('Plage bois', R(10.5, 19.6, 19.5, 1.4)),
                       ('Deck fitness sous arbres', R(31.0, 17.0, 5.0, 4.0))]
A['shapes']['allee'] = [('Allée d\'arrivée', R(1.5, 13.0, 4.4, 1.8)),
                        ('Allée jardin', R(8.0, 14.6, 1.6, 7.0)),
                        ('Pas japonais', R(20.0, 14.6, 1.2, 5.0))]
A['shapes']['evergreen'] = [('Dépose-minute + 2 places (PMR, livraison)', R(1.8, 16.0, 4.4, 10.5))]
A['trees'] = ([(u, 26.5, 'palmier') for u in (9, 14, 19, 24)] +
              [(3.5, 2.0, 'feuillu'), (12, 2.0, 'feuillu'), (20, 1.8, 'feuillu'), (28, 1.6, 'feuillu'), (35.5, 1.4, 'feuillu'),
               (33.5, 19.0, 'feuillu'), (6.5, 27.5, 'feuillu'), (31.5, 24.0, 'palmier'), (36.5, 16.5, 'palmier'),
               (14.5, 17.0, 'palmier'), (25.0, 17.2, 'palmier'), (4.0, 28.5, 'feuillu')])
VARIANTS['A'] = A

# ---- B : « Le Village-Canopée »
TW, TD = 2.5 * T, D_BARRE - 0.2     # case-tour : 9,0 × 10,4 m
TU = (5.9, 17.6, 29.3)
B = dict(code='B', nom='Le Village-Canopée', shapes={})
B['shapes']['bati'] = ([(f'Case-tour T{i + 1} R+2', R(u, V0, TW, TD)) for i, u in enumerate(TU)] +
                       [('Case commune (accueil, restaurant)', R(7.0, 17.0, 14.0, 8.0))])
B['shapes']['tech'] = [('Locaux CIE/SODECI + GE (toit planté)', R(2.0, V0, 3.5, 5.0))]
B['shapes']['piscine'] = [('Bassin de nage 2,5 × 12 m', R(8.5, 26.3, 12.0, 2.5))]
B['shapes']['deck'] = [('Terrasse restaurant', R(21.0, 18.0, 1.6, 6.0)),
                       ('Plage bois', R(8.5, 25.4, 12.0, 0.9))]
B['shapes']['allee'] = [('Allée d\'arrivée', R(1.5, 15.0, 5.5, 1.8)),
                        ('Allée des cases', R(5.0, 14.4, 33.0, 1.4))]
B['shapes']['evergreen'] = [('Dépose-minute + 2 places (PMR, livraison)', R(1.8, 17.2, 4.4, 9.0))]
B['shapes']['pelouse'] = [('Pelouse-terrain 13 × 9 m (gazon naturel)', R(23.0, 16.3, 13.0, 9.0))]
B['stairs'] = [R(u + TW + 0.15, V0 + 0.2, 1.4, 6.0) for u in TU[:2]] + [R(TU[2] - 1.55, V0 + 0.2, 1.4, 6.0)]
B['trees'] = ([(u, 2.0, 'feuillu') for u in (3.5, 12, 20, 28, 35.5)] +
              [(16.25, 9.0, 'palmier'), (27.95, 9.5, 'palmier'), (37.5, 18.0, 'palmier'),
               (4.0, 28.0, 'feuillu'), (22.0, 27.5, 'palmier'), (3.8, 11.5, 'palmier')])
VARIANTS['B'] = B

# ---------------------------------------------------------------- bilan des sols
POIDS = {  # coefficient de biotope par surface (CBS) – valeurs usuelles
    'pleine_terre': 1.0, 'pelouse': 1.0, 'evergreen': 0.5, 'allee': 0.3, 'deck': 0.3,
    'piscine': 0.0, 'bati': 0.0, 'tech': 0.0,
    'toit_vegetal': 0.7, 'facade_vegetale': 0.5}

def sols(V):
    out = {}
    union = []
    for cat, items in V['shapes'].items():
        g = unary_union([p for _, p in items]).intersection(SITE)
        g = g.difference(unary_union(union)) if union else g
        out[cat] = g.area
        union.append(g)
    out['pleine_terre'] = SITE.area - sum(out.values())
    return out

# toitures et façades végétalisées (m²) – compte du CBS
EXTRA = {'A': {'toit_vegetal': 17.5 + 0.0, 'facade_vegetale': 2 * 10.6 * 10.5},
         'B': {'toit_vegetal': 17.5, 'facade_vegetale': 3 * 2 * 10.4 * 6.0}}

def biotope(code):
    s = sols(VARIANTS[code])
    eco = sum(POIDS[k] * v for k, v in s.items()) + sum(POIDS[k] * v for k, v in EXTRA[code].items())
    return s, eco / SITE.area

# ---------------------------------------------------------------- programmes
# (désignation, nb, SU unitaire, catégorie de coût)
ORIGINE = [
    ('Hébergement (R+1)', [('Chambre deluxe', 4, 15), ('Suite junior', 6, 20), ('Suite familiale 2 ch.', 3, 45),
                           ('Suite premium 1 ch.', 2, 45), ('Circulations 20 %', 1, 81)]),
    ('Administration & accueil (RDC)', [('Accueil', 1, 30), ('Zone administrative', 1, 35)]),
    ('Équipements (RDC)', [('Restaurant 100 pers. + cuisine', 1, 130), ('Salle polyvalente & bureaux', 1, 100),
                           ('Spa + salle de sport', 1, 140), ('Supérette', 1, 60), ('Zone technique et services', 1, 200)]),
    ('Extérieurs', [('Piscine et plage', 1, 100), ('Soccer cage', 1, 150), ('Parking 20 places (evergreen)', 1, 400),
                    ('Jardin & cheminement', 1, 20)]),
]

D_SU = round(T * D_PIECE, 1)            # 25,2
J_SU = round(1.5 * T * D_PIECE, 1)      # 37,8
P_SU = round(2 * T * D_PIECE, 1)        # 50,4
PB_SU = round(TW * D_PIECE, 1)          # 63,0 (suite premium sous chaume, B)
JB_SU = round(1.5 * T * D_PIECE, 1)     # 37,8
DB_SU = round((TW - 1.5 * T) * D_PIECE, 1)  # 25,2

PROG = {
 'A': [
  ('Hébergement R0 à R+2 — 15 clés', [
     ('Chambre deluxe (SdE incluse) 3,6 × 7,0', 7, D_SU, 'heb'),
     ('Suite junior 5,4 × 7,0', 6, J_SU, 'heb'),
     ('Suite premium 7,2 × 7,0', 2, P_SU, 'heb'),
     ('Suites familiales : 3 paires junior + deluxe communicantes (lock-off)', 0, 0, 'heb'),
     ('Noyau escalier + ascenseur (×4 niveaux)', 4, round(T * D_BARRE - 8, 1), 'heb'),
     ('Loggias privatives (ext. couvert)', 20 * 1, round(T * D_LOGGIA, 2), 'ext'),
     ('Coursives nord ouvertes R+1 et R+2 (ext. couvert)', 2, round(8 * T * D_COURSIVE, 1), 'ext')]),
  ('Accueil & services — RDC ouest', [
     ('Lobby-lounge + réception (écran matchs)', 1, 52, 'com'),
     ('Boutique-épicerie (ex-supérette, ouverte sur rue)', 1, 18, 'com'),
     ('Back-office administratif + bagagerie', 1, 15, 'com'),
     ('Sanitaires publics', 1, 9, 'com'),
     ('Spa : 2 cabines + douche', 1, 30, 'spa'),
     ('Lingerie / office / TGBT', 1, 24, 'com')]),
  ('Toit-Stade (R+3)', [
     ('Restaurant-bar sous chaume 80 couverts', 1, 108, 'rest'),
     ('Cuisine + plonge', 1, 30, 'rest'),
     ('Sanitaires restaurant', 1, 15, 'rest'),
     ('Cage de foot 14,4 × 10,6 (gazon synthétique, filets)', 1, round(4 * T * D_BARRE, 1), 'toit')]),
  ('Extérieurs', [
     ('Bassin de nage 2,5 × 16 + bain froid', 1, 46.25, 'pisc'),
     ('Deck fitness plein air sous arbres', 1, 20, 'ext'),
     ('Locaux concessionnaires + GE (toit planté)', 1, 17.5, 'com'),
     ('Dépose-minute + 2 places (PMR, livraison) — 18 places mutualisées hors parcelle', 1, 46, 'vrd')]),
 ],
 'B': [
  ('Hébergement — 3 cases-tours R+2, 15 clés', [
     ('Chambre deluxe (SdE incluse) 3,6 × 7,0', 6, DB_SU, 'heb'),
     ('Suite junior 5,4 × 7,0', 6, JB_SU, 'heb'),
     ('Suite premium sous chaume 9,0 × 7,0 + mezzanine', 3, PB_SU, 'heb'),
     ('Suites familiales : 6 paires junior + deluxe communicantes (lock-off)', 0, 0, 'heb'),
     ('Loggias privatives (ext. couvert)', 15, round(TW * D_LOGGIA / 2 * 1.0, 2), 'ext'),
     ('Coursives + escaliers extérieurs (ext. couvert)', 3, round(3 * TW * 1.6 + 2 * 1.4 * 6, 1), 'ext')]),
  ('Case commune R0', [
     ('Accueil-réception + boutique-épicerie', 1, 28, 'com'),
     ('Back-office + bagagerie + sanitaires', 1, 20, 'com'),
     ('Cuisine + plonge', 1, 30, 'rest'),
     ('Restaurant ouvert sous chaume 50 couverts', 1, 34, 'rest'),
     ('Terrasse restaurant sur pelouse 30 couverts', 1, 9.6, 'ext')]),
  ('Case commune R+1 (sous chaume)', [
     ('Salle de sport / récupération', 1, 30, 'spa'),
     ('Spa : 2 cabines + douche', 1, 26, 'spa'),
     ('Lingerie / office', 1, 12, 'com')]),
  ('Extérieurs', [
     ('Pelouse-terrain gazon naturel 13 × 9 (foot à 4)', 1, 117, 'pel'),
     ('Bassin de nage 2,5 × 12', 1, 30, 'pisc'),
     ('Locaux concessionnaires + GE (toit planté)', 1, 17.5, 'com'),
     ('Dépose-minute + 2 places (PMR, livraison) — 18 places mutualisées hors parcelle', 1, 40, 'vrd')]),
 ],
}

def prog_total(code, cats=None):
    t = 0
    for _, rows in PROG[code]:
        for _, n, su, cat in rows:
            if cats is None or cat in cats:
                t += n * su
    return t

# ---------------------------------------------------------------- estimatif
# Ratios Éco-données (FCFA HT / m²) – base « BASE DE DONNEES DES COUTS DES PROJETS 5 » ; divisés par 2
RATIOS_SOURCE = {
 'heb':  ('Hôtel du District, Abidjan (HO, ESQ 2024) — par m² SU', 954558),
 'com':  ('Hôtel du District, Abidjan (HO, ESQ 2024) — par m² SU', 954558),
 'spa':  ('Club House / Golf Course, Cotonou (Sport, ESQ) — par m² SPL', 984316),
 'rest': ('QCC Restaurations, Cotonou (ESQ) — par m² SPL', 850000),
 'pisc': ('Ratio hôtelier appliqué au m² de bassin (hypothèse, Hôtel du District)', 954558),
 'ext':  ('50 % du ratio Hôtel du District (surfaces couvertes ouvertes)', 954558 * 0.5),
 'toit': ('50 % du ratio Hôtel du District (toiture accessible renforcée + gazon synth. + filets)', 954558 * 0.5),
 'vrd':  ('QCC VRD et aménagements paysagers, Cotonou (ESQ) — par m²', 113296),
 'pel':  ('QCC VRD et aménagements paysagers, Cotonou (ESQ) — par m²', 113296),
}
CHECK_DJONDJI = ('Djondji Resort, Bénin (HOTELIER, ESQ) — tout compris par m² SPL', 2036287)
COEF = 0.5          # demande client : coûts Éco-données divisés par deux
ALEAS = 0.05

def estimatif(code):
    lignes = {}
    for _, rows in PROG[code]:
        for _, n, su, cat in rows:
            lignes[cat] = lignes.get(cat, 0) + n * su
    s = sols(VARIANTS[code])
    amenag = s['pleine_terre'] + s.get('allee', 0) + s.get('deck', 0) + s.get('evergreen', 0)
    lignes['vrd'] = lignes.get('vrd', 0) * 0 + amenag   # aménagements = toute la surface non bâtie hors bassin / pelouse
    rows = []
    for cat, surf in lignes.items():
        lib, r = RATIOS_SOURCE[cat]
        rows.append((cat, lib, surf, r, r * COEF, surf * r * COEF))
    ht = sum(r[-1] for r in rows)
    return rows, ht, ht * ALEAS, ht * (1 + ALEAS)

LIB_CAT = {'heb': 'Hébergement (chambres + noyaux)', 'com': 'Accueil, administration, services', 'spa': 'Spa & sport',
           'rest': 'Restaurant & cuisine', 'pisc': 'Bassin de nage', 'ext': 'Espaces extérieurs couverts (loggias, coursives, terrasses)',
           'toit': 'Toit-Stade : cage de foot en toiture', 'vrd': 'VRD, jardins, allées, dépose-minute', 'pel': 'Pelouse-terrain gazon naturel'}

if __name__ == '__main__':
    print('Programme d\'origine : SU =', sum(n * su for _, r in ORIGINE for _, n, su in r))
    for c in 'AB':
        s, cbs = biotope(c)
        print('\n==', c, VARIANTS[c]['nom'])
        for k, v in s.items(): print(f'  {k:14s} {v:7.1f} m²  {v / SITE.area * 100:5.1f} %')
        print('  CBS =', round(cbs, 2))
        print('  SU clos =', round(prog_total(c, {'heb', 'com', 'spa', 'rest'}), 1), ' ext couvert =', round(prog_total(c, {'ext'}), 1))
        rows, ht, al, tot = estimatif(c)
        for r in rows: print(f'  {r[0]:5s} {r[2]:8.1f} m² × {r[4]:10,.0f} = {r[5]:15,.0f}')
        print(f'  HT {ht:,.0f}  aléas {al:,.0f}  TOTAL {tot:,.0f} FCFA  ({tot / 655.957:,.0f} €)')
