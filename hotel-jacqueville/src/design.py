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
                       [('Case commune (accueil, restaurant)', R(8.0, 16.8, 15.0, 7.6))])
B['shapes']['tech'] = [('Locaux CIE/SODECI + GE (toit planté)', R(2.0, V0, 3.5, 5.0))]
B['shapes']['piscine'] = [('Bassin de nage 2,5 × 12 m', R(9.0, 25.6, 12.0, 2.5))]
B['shapes']['deck'] = [('Terrasse restaurant', R(23.0, 17.4, 1.2, 6.4)),
                       ('Plage bois', R(9.0, 24.6, 12.0, 1.0))]
B['shapes']['allee'] = [('Allée d\'arrivée', R(1.5, 15.0, 6.5, 1.8)),
                        ('Allée des cases', R(5.0, 14.4, 33.0, 1.4))]
B['shapes']['evergreen'] = [('Dépose-minute + 2 places (PMR, livraison)', R(1.8, 17.2, 4.4, 9.0))]
B['shapes']['pelouse'] = [('Pelouse-terrain 12,6 × 8,8 m (paspalum)', R(24.4, 16.3, 12.6, 8.8))]
# un escalier pour T1 (faille T1/T2) ; un escalier partagé T2/T3 avec passerelles (faille T2/T3)
B['stairs'] = [R(TU[0] + TW + 0.65, V0 + 0.2, 1.4, 6.0), R(TU[1] + TW + 0.65, V0 + 0.2, 1.4, 6.0)]
B['trees'] = ([(u, 2.0, 'feuillu') for u in (3.5, 12, 20, 28, 35.5)] +
              [(16.25, 9.0, 'palmier'), (27.95, 12.5, 'palmier'), (37.8, 15.4, 'palmier'),
               (4.0, 28.0, 'feuillu'), (22.0, 27.5, 'palmier'), (3.8, 11.5, 'palmier')])
VARIANTS['B'] = B

# ---- C : « Le Jardin du Onze » — hybride recommandé par la revue critique
V0C = 5.0                            # recul nord porté à 5,0 m (prospect H/2, acrotère +9,80)
UC = 6.1
C = dict(code='C', nom='Le Jardin du Onze', shapes={})
C['shapes']['bati'] = [('Barre hôtel R+2', R(UC, V0C, 9 * T, D_BARRE)),
                       ('Case-restaurant (RDC)', R(8.0, 17.6, 12.0, 7.4)),
                       ('Bloc technique (GE, TGBT, piscine, bâche enterrée)', R(20.6, 17.6, 4.0, 5.0))]
C['shapes']['piscine'] = [('Bassin de nage 2,5 × 11 m + bain froid', R(9.0, 26.0, 11.0, 2.5))]
C['shapes']['deck'] = [('Terrasse restaurant', R(8.0, 25.0, 12.0, 1.0))]
C['shapes']['allee'] = [('Allée d\'arrivée', R(1.5, 14.0, 4.6, 1.8)),
                        ('Voie de service nord (gravier)', R(1.0, 1.6, 6.0, 2.2)),
                        ('Allée jardin', R(UC, 15.6, 9 * T, 1.4))]
C['shapes']['evergreen'] = [('Dépose-minute + 2 places (PMR, livraison)', R(1.8, 16.0, 4.4, 10.5))]
C['shapes']['pelouse'] = [('Pelouse-terrain paspalum 12,4 × 8 m', R(25.6, 16.9, 12.4, 8.0))]
C['trees'] = ([(u, 2.2, 'feuillu') for u in (12, 20, 28, 35.5)] +
              [(3.8, 6.5, 'palmier'), (22.6, 25.5, 'palmier'), (24.5, 27.0, 'feuillu'), (6.0, 28.0, 'feuillu'),
               (37.6, 26.0, 'palmier'), (21.5, 16.8, 'palmier')])
VARIANTS['C'] = C

# ---------------------------------------------------------------- bilan des sols
POIDS = {  # coefficient de biotope par surface (CBS) – valeurs usuelles
    'pleine_terre': 1.0, 'pelouse': 0.6, 'evergreen': 0.5, 'allee': 0.3, 'deck': 0.3,
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
# A : pignons est/ouest plantés sur câbles inox avec arrosage goutte-à-goutte ; B : claustras non comptés
EXTRA = {'A': {'toit_vegetal': 17.5, 'facade_vegetale': 2 * 7.0 * 9.8},
         'B': {'toit_vegetal': 17.5, 'facade_vegetale': 0.0},
         'C': {'toit_vegetal': 5 * 3.6 * 10.6 + 20.0, 'facade_vegetale': 2 * 7.0 * 9.8}}

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
     ('Suite premium 7,2 × 7,0 (R+2 ouest, hors aplomb de la cage)', 2, P_SU, 'heb'),
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
  ('Toit-Stade (R+3 partiel)', [
     ('Restaurant-bar sous chaume 80 couverts', 1, 108, 'rest'),
     ('Cuisine + plonge', 1, 30, 'rest'),
     ('Sanitaires restaurant', 1, 15, 'rest'),
     ('Cage de foot 3 contre 3 (14,4 × 10,6 entre axes), gazon synthétique, filets', 1, round(4 * T * D_BARRE, 1), 'toit')]),
  ('Extérieurs', [
     ('Bassin de nage 2,5 × 16 + bain froid', 1, 46.25, 'pisc'),
     ('Deck fitness plein air sous arbres', 1, 20, 'ext'),
     ('Locaux concessionnaires + GE (toit planté)', 1, 17.5, 'com'),
     ('Dépose-minute + 2 places (PMR, livraison)', 1, 46, 'vrd')]),
 ],
 'B': [
  ('Hébergement — 3 cases-tours R+2, 15 clés', [
     ('Chambre deluxe (SdE incluse) 3,6 × 7,0', 6, DB_SU, 'heb'),
     ('Suite junior 5,4 × 7,0', 6, JB_SU, 'heb'),
     ('Suite premium sous chaume 9,0 × 7,0 + mezzanine', 3, PB_SU, 'heb'),
     ('Suites familiales : 6 paires junior + deluxe communicantes (lock-off)', 0, 0, 'heb'),
     ('Loggias privatives (ext. couvert)', 15, round(TW * D_LOGGIA / 2 * 1.0, 2), 'ext'),
     ('Galeries + 2 escaliers extérieurs + passerelles T2/T3 (ext. couvert)', 1, round(3 * TW * 1.6 * 3 + 2 * 1.4 * 6 * 3, 1), 'ext')]),
  ('Case commune R0 (15 × 7,6 m)', [
     ('Accueil-réception + boutique-épicerie', 1, 20, 'com'),
     ('Back-office + bagagerie', 1, 13, 'com'),
     ('Cuisine + plonge', 1, 23, 'rest'),
     ('Réserves + chambre froide', 1, 12, 'rest'),
     ('Restaurant ouvert sous chaume (salle)', 1, 45.6, 'rest'),
     ('Galerie sous débords : complément restaurant (60 couverts au total)', 1, 36, 'ext')]),
  ('Case commune R+1 sous chaume (élévateur PMR + monte-linge)', [
     ('Salle de sport / récupération', 1, 28, 'spa'),
     ('Spa : 2 cabines + douche', 1, 26, 'spa'),
     ('Lingerie', 1, 14, 'com')]),
  ('Extérieurs', [
     ('Pelouse-terrain paspalum 12,6 × 8,8 (foot à 4)', 1, 111, 'pel'),
     ('Bassin de nage 2,5 × 12', 1, 30, 'pisc'),
     ('Locaux concessionnaires + GE (toit planté)', 1, 17.5, 'com'),
     ('Dépose-minute + 2 places (PMR, livraison)', 1, 40, 'vrd')]),
 ],
 'C': [
  ('Hébergement R0 à R+2 — 14 clés', [
     ('Chambre deluxe (SdE incluse) 3,6 × 7,0 — dont 1 PMR au RDC', 8, D_SU, 'heb'),
     ('Suite junior 5,4 × 7,0', 4, J_SU, 'heb'),
     ('Suite premium 7,2 × 7,0', 2, P_SU, 'heb'),
     ('Suites familiales : 3 paires communicantes (lock-off)', 0, 0, 'heb'),
     ('Noyau escalier + ascenseur (×3 niveaux + sortie toiture)', 3, round(T * D_BARRE - 8, 1), 'heb'),
     ('Loggias privatives (ext. couvert)', 14 * 1, round(T * D_LOGGIA * 18 / 14, 2), 'ext'),
     ('Coursives nord ouvertes R+1 et R+2, écran planté côté voisin', 2, round(8 * T * D_COURSIVE, 1), 'ext')]),
  ('RDC de la barre — accueil, cuisine, back-of-house', [
     ('Lobby-lounge + réception + boutique (écran matchs)', 1, 62, 'com'),
     ('Back-office + bagagerie + sanitaires publics', 1, 14, 'com'),
     ('Cuisine tout électrique + plonge', 1, 40, 'rest'),
     ('Économat, réserve sèche, chambre froide, cave', 1, 22, 'rest'),
     ('Vestiaires H/F + sanitaires personnel', 1, 25, 'boh'),
     ('Réfectoire du personnel + chambre de garde', 1, 15, 'boh'),
     ('Lingerie-blanchisserie + séchage', 1, 30, 'boh'),
     ('Local déchets ventilé (accès voie de service)', 1, 6, 'boh')]),
  ('Jardin', [
     ('Case-restaurant ouverte 12 × 7,4 (60 couverts) + terrasse 20 couverts', 1, 88.8, 'rest'),
     ('Bloc technique : GE 160 kVA capoté + cuve, TGBT, local piscine, bâche 40 m³ enterrée lestée', 1, 20, 'tech'),
     ('Cabane de massage (appatam Ø 5 m, spa 1 cabine double)', 1, 20, 'ext'),
     ('Pelouse-terrain paspalum 12,4 × 8 (foot à 4, buts amovibles)', 1, 99, 'pel'),
     ('Bassin de nage 2,5 × 11 + bain froid', 1, 27.5, 'pisc'),
     ('Dépose-minute + 2 places, voie de service nord', 1, 46, 'vrd')]),
  ('Toiture', [
     ('Terrasse privatisable ≤ 19 pers. sous pergola photovoltaïque (≈ 25 kWc)', 1, round(4 * T * D_BARRE, 1), 'toit'),
     ('Toiture végétalisée extensive (5 travées)', 1, round(5 * T * D_BARRE, 1), 'tveg')]),
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
# Ratios Éco-données (FCFA HT / m²) – classeur « BASE DE DONNEES DES COUTS DES PROJETS 5 » ; divisés par 2 (consigne)
RATIOS_SOURCE = {
 'heb':  ('Hôtel du District, Abidjan (HO, ESQ 2024) — m² SU', 954558),
 'com':  ('Hôtel du District, Abidjan (HO, ESQ 2024) — m² SU', 954558),
 'boh':  ('Hôtel du District, Abidjan (HO, ESQ 2024) — m² SU', 954558),
 'spa':  ('Club House / Golf Course, Cotonou (Sport, ESQ) — m² SPL', 984316),
 'rest': ('QCC Restaurations, Cotonou (ESQ) — m² SPL', 850000),
 'pisc': ('Ratio hôtelier appliqué au m² de bassin (hypothèse)', 954558),
 'ext':  ('50 % du ratio Hôtel du District (couvert ouvert)', 954558 * 0.5),
 'toit': ('50 % du ratio Hôtel du District (toiture accessible aménagée)', 954558 * 0.5),
 'tveg': ('Espaces verts patios, Résidence MAEC Cotonou — m²', 80000),
 'tech': ('Local groupe électrogène, École de police Porto-Novo — m²', 200000),
 'vrd':  ('QCC VRD et aménagements paysagers, Cotonou (ESQ) — m²', 113296),
 'pel':  ('QCC VRD et aménagements paysagers, Cotonou (ESQ) — m²', 113296),
}
CHECK_DJONDJI = ('Djondji Resort, Bénin (HOTELIER, ESQ) — tout compris par m² SPL', 2036287)
COEF = 0.5          # consigne du maître d'ouvrage : coûts divisés par deux (hypothèse de prix cible)
ALEAS = 0.05
COEF_FORME = {'A': 1.00, 'B': 1.10, 'C': 1.00}   # B : 3 toitures, 3 escaliers, plus de façade par m²
CLOTURE_ML = 136.8                                # périmètre du terrain
# Provisions hors ratios (relevées par la revue) : montants avant division par deux
PROVISIONS = {
 'A': [('Clôture périphérique (Éco-données : 110 000 FCFA/ml, École de police Porto-Novo)', CLOTURE_ML * 110000),
       ('Surcoût toit-stade : dalle flottante, filets ancrés, étanchéité lourde (hypothèse auteur)', 45e6),
       ('Micro-station d\'épuration ~70 EH + bac à graisse (hypothèse auteur)', 40e6),
       ('Bâche 40 m³ + surpresseur + réserve incendie (hypothèse auteur)', 24e6),
       ('Groupe électrogène 160 kVA capoté + cuve (hypothèse auteur)', 60e6),
       ('Équipement de cuisine professionnelle (hypothèse auteur)', 50e6),
       ('Fondations sur sable : surcoût radier / micro-pieux (hypothèse auteur)', 40e6)],
 'B': [('Clôture périphérique (Éco-données : 110 000 FCFA/ml, École de police Porto-Novo)', CLOTURE_ML * 110000),
       ('Élévateur PMR + monte-linge case commune (hypothèse auteur)', 20e6),
       ('Micro-station d\'épuration ~70 EH + bac à graisse (hypothèse auteur)', 40e6),
       ('Bâche 40 m³ + surpresseur + réserve incendie (hypothèse auteur)', 24e6),
       ('Groupe électrogène 120 kVA capoté + cuve (hypothèse auteur)', 48e6),
       ('Équipement de cuisine professionnelle (hypothèse auteur)', 40e6),
       ('Fondations sur sable : 4 bâtiments (hypothèse auteur)', 45e6)],
 'C': [('Clôture périphérique (Éco-données : 110 000 FCFA/ml, École de police Porto-Novo)', CLOTURE_ML * 110000),
       ('Pergola photovoltaïque ≈ 25 kWc + onduleurs (hypothèse auteur)', 30e6),
       ('Micro-station d\'épuration ~70 EH + bac à graisse (hypothèse auteur)', 40e6),
       ('Bâche 40 m³ + surpresseur + réserve incendie (hypothèse auteur)', 24e6),
       ('Groupe électrogène 160 kVA capoté + cuve (hypothèse auteur)', 60e6),
       ('Équipement de cuisine professionnelle (hypothèse auteur)', 50e6),
       ('Fondations sur sable : surcoût radier / micro-pieux (hypothèse auteur)', 35e6)],
}
HONORAIRES = 0.10
TVA = 0.18
FFE_PAR_CLE = 8e6     # mobilier et équipements hôteliers (hors base Éco-données, non divisé)
CLES = {'A': 15, 'B': 15, 'C': 14}

def estimatif(code):
    lignes = {}
    for _, rows in PROG[code]:
        for _, n, su, cat in rows:
            lignes[cat] = lignes.get(cat, 0) + n * su
    s = sols(VARIANTS[code])
    lignes['vrd'] = s['pleine_terre'] + s.get('allee', 0) + s.get('deck', 0) + s.get('evergreen', 0)
    rows = []
    for cat, surf in lignes.items():
        lib, r = RATIOS_SOURCE[cat]
        k = COEF_FORME[code] if cat in ('heb', 'com', 'boh', 'rest', 'spa') else 1.0
        rows.append((cat, lib + (f' × forme {k:.2f}' if k != 1 else ''), surf, r * k, r * k * COEF, surf * r * k * COEF))
    ht_ratios = sum(r[-1] for r in rows)
    prov = [(lib, m, m * COEF) for lib, m in PROVISIONS[code]]
    ht = ht_ratios + sum(p[2] for p in prov)
    return rows, prov, ht_ratios, ht, ht * ALEAS, ht * (1 + ALEAS)

def cout_global(code):
    *_, travaux = estimatif(code)
    hon = travaux * HONORAIRES
    tva = (travaux + hon) * TVA
    ffe = CLES[code] * FFE_PAR_CLE
    return dict(travaux=travaux, honoraires=hon, tva=tva, ffe=ffe, total=travaux + hon + tva + ffe)

LIB_CAT = {'heb': 'Hébergement (chambres + noyaux)', 'com': 'Accueil, administration, services', 'boh': 'Back-of-house personnel',
           'spa': 'Spa & sport', 'rest': 'Restaurant & cuisine', 'pisc': 'Bassin de nage',
           'ext': 'Extérieurs couverts (loggias, coursives, galeries)', 'toit': 'Toiture accessible aménagée',
           'tveg': 'Toiture végétalisée', 'tech': 'Bloc technique', 'vrd': 'VRD, jardins, allées, dépose-minute',
           'pel': 'Pelouse-terrain paspalum'}

if __name__ == '__main__':
    for c in 'ABC':
        s, cbs = biotope(c)
        print('\n==', c, VARIANTS[c]['nom'], ' CBS =', round(cbs, 2))
        for k, v in s.items(): print(f'  {k:14s} {v:7.1f} m²  {v / SITE.area * 100:5.1f} %')
        print('  SU clos =', round(prog_total(c, {'heb', 'com', 'spa', 'rest', 'boh'}), 1), ' ext =', round(prog_total(c, {'ext'}), 1))
        rows, prov, hr, ht, al, tot = estimatif(c)
        print(f'  ratios {hr:,.0f}  provisions {ht - hr:,.0f}  total {tot:,.0f}  /clé {tot / CLES[c]:,.0f}')
        print('  global', {k: round(v / 1e6) for k, v in cout_global(c).items()})
