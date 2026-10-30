"""Modele de donnees du projet Lot 1728 - Riviera Palmeraie.

Source unique pour les plans (SVG), l'estimatif (XLSX) et le business plan.
Repere : x = Ouest -> Est (0 a 20 m), y = Nord -> Sud (0 a 33 m).
Rue Nord en y = 0, rue Ouest en x = 0.
Villa : y 0 -> 18 (360 m2). Locatif : y 18 -> 33 (300 m2).
"""

# ---------------------------------------------------------------------------
# Parcelle (plan cadastral CGE Coco Habib, 04-11-2025)
# ---------------------------------------------------------------------------
PARCELLE = {
    "titre": "Lot 1728 - Ilot 174 - Djorogobite 1 (Riviera Palmeraie), Cocody",
    "tf": "Morcellement du TF 358 - Livre foncier de Cocody",
    "largeur": 20.0,
    "profondeur": 33.0,
    "surface": 660.0,
    "bornes": {  # coordonnees du plan (systeme local cadastre)
        "B1": (394971.693, 596073.230),
        "B2": (394991.703, 596070.480),
        "B3": (394987.165, 596037.794),
        "B4": (394967.355, 596040.544),
    },
}
VILLA_Y = (0.0, 18.0)
LOCATIF_Y = (18.0, 33.0)

# Hypotheses reglementaires (a valider : cahier des charges du lotissement / permis)
RECUL_NORD = 5.0     # voie principale
RECUL_OUEST = 3.2    # voie secondaire (3 m + calage trame)

# ---------------------------------------------------------------------------
# Bordereau de ratios (base Eco-donnees, phase ESQ, FCFA HT / m2) puis / 2
# ---------------------------------------------------------------------------
# code: (libelle, PU base, source)
RATIOS = {
    "sejour":     ("Séjour / SAM / salon", 600_000, "Pavillon Akpo 2022 - sejour"),
    "chambre":    ("Chambres", 600_000, "Pavillon Akpo 2022 - chambres"),
    "eau":        ("Salles d'eau / SdB / WC", 1_500_000, "Pavillon Akpo 2022 - pièces d'eau"),
    "cuisine":    ("Cuisine", 850_000, "Pavillon Akpo 2022 - cuisine"),
    "dressing":   ("Dressing / vestibule-placard", 850_000, "Résidences Anthurium 2021 - dressing"),
    "service":    ("Réserve / buanderie / cellier", 500_000, "Pavillon Akpo 2022 - réserve"),
    "circ":       ("Circulations (genkan, rōka, palier)", 550_000, "Résidence Les Flamboyants - dégagements"),
    "escalier":   ("Escalier", 600_000, "Résidences Anthurium 2021 - circulations (haut de fourchette)"),
    "terrasse":   ("Engawa / terrasse couverte / séchoir", 350_000, "Pavillon Akpo 2022 - terrasse"),
    "balcon":     ("Balcon-engawa d'étage", 450_000, "Résidences Anthurium 2021 - balcons"),
    "toit_jard":  ("Toit-jardin accessible", 350_000, "Assimilé terrasse (Akpo 2022)"),
    "patio":      ("Patio / tsubo-niwa / cour", 85_000, "Villa Cacao 6 2023 - patio"),
    "parvis":     ("Parking et allées pavés", 85_000, "Villa Cacao 6 2023 - patio (assimilé)"),
    "jardin":     ("Espaces verts (aménagement)", 20_000, "Résidence Les Flamboyants - jardins et patios"),
    # Locatif (standard appartement)
    "l_sejour":   ("Séjour-cuisine (locatif)", 550_000, "Résidences Anthurium 2021 - sejour"),
    "l_chambre":  ("Chambre / alcôve (locatif)", 500_000, "Résidences Anthurium 2021 - chambres"),
    "l_eau":      ("Salle d'eau (locatif)", 1_000_000, "Résidence Les Flamboyants - salles de bain"),
    "l_kitch":    ("Kitchenette / bande humide", 850_000, "Pavillon Akpo 2022 - cuisine"),
    "l_circ":     ("Dégagement / placard / bureau", 400_000, "Résidences Anthurium 2021 - circulations (bas)"),
    "l_coursive": ("Coursive-engawa R+1", 400_000, "Résidences Anthurium 2021 - circulations (bas)"),
}
DIVISEUR = 2  # consigne client : prix de construction divises par 2


def pu(code, div=None):
    return RATIOS[code][1] / (DIVISEUR if div is None else div)


# ---------------------------------------------------------------------------
# Pieces : (nom, niveau, [rectangles (x0, y0, x1, y1)], code ratio, clos?)
# ---------------------------------------------------------------------------
def R(nom, niv, rects, code, clos=True, note=""):
    if isinstance(rects[0], (int, float)):
        rects = [rects]
    surf = round(sum((x1 - x0) * (y1 - y0) for x0, y0, x1, y1 in rects), 2)
    return {"nom": nom, "niveau": niv, "rects": rects, "code": code,
            "clos": clos, "surface": surf, "note": note}


SEJOUR_L = [(3.2, 8.6, 10.4, 12.2), (3.2, 5.0, 6.8, 8.6)]
# Noyau de distribution (revue architecte senior) : bande de 1,20 m x 10,4-11,6 reliant
# genkan, roka, escalier et palier ; escalier en U 2,40 x 3,60 decale en x 11,6-15,2.
ROKA_RDC = [(10.4, 7.4, 17.6, 8.6), (10.4, 5.0, 11.6, 7.4)]
PALIER = [(10.4, 7.4, 15.2, 8.6), (10.4, 5.0, 11.6, 7.4)]


def suites_etage():
    """Partie de l'etage commune aux deux options : roka, 2 suites, noyau, salon familial."""
    return [
        R("Rōka (couloir)", "R+1", (3.2, 5.0, 10.4, 6.2), "circ"),
        R("Vestibule ch.2", "R+1", (3.2, 6.2, 4.8, 8.6), "dressing"),
        R("SE ch.2", "R+1", (4.8, 6.2, 6.8, 8.6), "eau"),
        R("SE ch.3", "R+1", (6.8, 6.2, 8.8, 8.6), "eau"),
        R("Vestibule ch.3", "R+1", (8.8, 6.2, 10.4, 8.6), "dressing"),
        R("Chambre 2", "R+1", (3.2, 8.6, 6.8, 12.2), "chambre"),
        R("Chambre 3", "R+1", (6.8, 8.6, 10.4, 12.2), "chambre"),
        R("Escalier", "R+1", (11.6, 5.0, 15.2, 7.4), "escalier"),
        R("Palier", "R+1", PALIER, "circ"),
        R("Salon familial", "R+1", (10.4, 8.6, 14.0, 12.2), "sejour"),
    ]


def socle_jour():
    """Partie jour et noyau du RDC communs aux deux options."""
    return [
        R("Genkan (entrée)", "RDC", (6.8, 5.0, 10.4, 7.4), "circ"),
        R("WC visiteurs", "RDC", (6.8, 7.4, 8.6, 8.6), "eau"),
        R("Getabako (placard)", "RDC", (8.6, 7.4, 10.4, 8.6), "dressing"),
        R("Séjour - SAM", "RDC", SEJOUR_L, "sejour"),
        R("Rōka (galerie intérieure)", "RDC", ROKA_RDC, "circ"),
        R("Escalier", "RDC", (11.6, 5.0, 15.2, 7.4), "escalier"),
        R("Cuisine", "RDC", (10.4, 8.6, 14.0, 12.2), "cuisine"),
        R("Buanderie / cellier", "RDC", (15.2, 5.0, 17.6, 7.4), "service"),
        R("Chambre de service", "RDC", (17.6, 5.0, 20.0, 8.6), "chambre"),
        R("SE service", "RDC", (17.6, 8.6, 20.0, 10.4), "eau"),
        # Cour de service fermee de claustras dans la bande de recul (revue) : arriere-cuisine + sechoir
        R("Arrière-cuisine (préau)", "RDC", (15.4, 2.0, 17.6, 5.0), "terrasse", clos=False),
        R("Cour de service / séchoir", "RDC", (17.6, 2.0, 20.0, 5.0), "patio", clos=False),
    ]


# Portes : (niveau, x, y, sens, largeur)  sens 'h' = dans un mur horizontal, 'v' = vertical
PORTES_JOUR = [
    ("RDC", 7.3, 5.0, "h", 1.0),    # entree genkan (porte blindee)
    ("RDC", 6.8, 6.2, "v", 1.6),    # genkan -> sejour
    ("RDC", 10.4, 6.2, "v", 1.0),   # genkan -> roka
    ("RDC", 7.7, 7.4, "h", 0.7),    # WC
    ("RDC", 10.4, 10.4, "v", 1.4),  # SAM -> cuisine
    ("RDC", 11.8, 8.6, "h", 0.9),   # roka -> cuisine
    ("RDC", 13.4, 7.4, "h", 2.0),   # roka -> escalier (depart)
    ("RDC", 16.4, 7.4, "h", 0.9),   # roka -> buanderie
    ("RDC", 16.4, 5.0, "h", 0.9),   # buanderie -> arriere-cuisine
    ("RDC", 18.8, 5.0, "h", 0.8),   # chambre de service -> cour de service
    ("RDC", 18.8, 8.6, "h", 0.7),   # ch. service -> SE
    ("RDC", 6.8, 12.2, "h", 6.0),   # sejour -> engawa (coulissants)
    ("RDC", 12.2, 12.2, "h", 1.2),  # cuisine -> engawa
    ("R+1", 4.0, 6.2, "h", 0.8), ("R+1", 4.0, 8.6, "h", 0.8),
    ("R+1", 9.6, 6.2, "h", 0.8), ("R+1", 9.6, 8.6, "h", 0.8),
    ("R+1", 4.8, 7.4, "v", 0.7), ("R+1", 8.8, 7.4, "v", 0.7),   # SE depuis les vestibules
    ("R+1", 13.4, 7.4, "h", 2.0),   # escalier (arrivee) -> palier
    ("R+1", 12.2, 8.6, "h", 2.4),   # palier -> salon familial
    ("R+1", 10.4, 5.6, "v", 1.0),   # palier -> roka
    ("R+1", 5.0, 12.2, "h", 2.4), ("R+1", 8.6, 12.2, "h", 2.4),
]

OPTION_A = {
    "code": "A",
    "nom": "Option A — Maison en L sur cour-jardin",
    "titre_court": "Maison en L",
    "parti": ("Suite parentale de plain-pied dans une aile Est qui referme un jardin-cour "
              "au Sud-Ouest. Engawa en L, toit-jardin sur l'aile de service. Emprise maximale."),
    "pieces": socle_jour() + [
        R("Tsubo-niwa", "RDC", (17.6, 10.4, 20.0, 12.2), "patio", clos=False),
        R("Dressing traversant", "RDC", (14.0, 8.6, 17.6, 12.2), "dressing"),
        R("Chambre parentale", "RDC", (14.0, 12.2, 20.0, 15.6), "chambre"),
        R("SdB parentale", "RDC", (14.0, 15.6, 17.6, 18.0), "eau"),
        R("WC + rangement", "RDC", (17.6, 15.6, 20.0, 18.0), "eau"),
        R("Engawa", "RDC", [(3.2, 12.2, 14.0, 14.0), (12.2, 14.0, 14.0, 18.0)], "terrasse", clos=False),
    ] + suites_etage() + [
        # garde-corps recule a 1,90 m de la limite Est (vues droites, art. 678 C. civ.)
        R("Toit-jardin", "R+1", [(14.0, 8.6, 18.1, 10.4), (15.2, 5.0, 18.1, 8.6)], "toit_jard", clos=False),
    ],
    "portes": PORTES_JOUR + [
        ("RDC", 14.7, 8.6, "h", 0.9),   # roka -> dressing (suite)
        ("RDC", 15.8, 12.2, "h", 0.9),  # dressing -> chambre
        ("RDC", 15.8, 15.6, "h", 0.8),  # chambre -> SdB
        ("RDC", 17.6, 16.8, "v", 0.7),  # SdB -> WC
        ("RDC", 14.0, 13.9, "v", 2.4),  # chambre -> engawa
        ("R+1", 14.0, 9.5, "v", 1.6),   # salon familial -> toit-jardin
    ],
    "toiture": "Toitures-terrasses : toit-jardin accessible + toiture végétalisée sur l'aile parentale",
}

OPTION_B = {
    "code": "B",
    "nom": "Option B — Duplex compact sur jardin",
    "titre_court": "Duplex compact",
    "parti": ("Volume unique sous une grande toiture débordante, toutes les chambres à l'étage. Au RDC, un "
              "washitsu avec sa salle d'eau sert de bureau ou de chambre de plain-pied. Emprise minimale, jardin d'un seul tenant."),
    "pieces": socle_jour() + [
        R("Washitsu (bureau / chambre)", "RDC", (14.0, 8.6, 17.6, 12.2), "sejour"),
        R("SE invités", "RDC", (17.6, 10.4, 20.0, 12.2), "eau"),
        R("Engawa", "RDC", (3.2, 12.2, 20.0, 14.0), "terrasse", clos=False),
    ] + suites_etage() + [
        R("Sas-dressing parental", "R+1", (15.2, 5.0, 17.6, 8.6), "dressing"),
        R("SdB parentale", "R+1", (17.6, 5.0, 20.0, 8.6), "eau"),
        R("Chambre parentale", "R+1", (14.0, 8.6, 20.0, 12.2), "chambre"),
        R("Balcon-engawa", "R+1", (3.2, 12.2, 14.0, 13.4), "balcon", clos=False),
    ],
    "portes": PORTES_JOUR + [
        ("RDC", 15.8, 8.6, "h", 0.9),   # roka -> washitsu
        ("RDC", 15.8, 12.2, "h", 2.4),  # washitsu -> engawa (fusuma)
        ("RDC", 17.6, 11.3, "v", 0.7),  # washitsu -> SE invites
        ("R+1", 15.2, 8.0, "v", 0.9),   # palier -> sas parental
        ("R+1", 16.4, 8.6, "h", 0.9),   # sas -> chambre
        ("R+1", 17.6, 6.8, "v", 0.8),   # sas -> SdB
        ("R+1", 12.2, 12.2, "h", 1.8),  # salon -> balcon
    ],
    "toiture": ("Grande toiture bac acier isolé sur charpente bois, débords de 1,8 m au Nord, au Sud et à l'Ouest ; "
                "côté Est, mur pignon et acrotère en limite avec chéneau encaissé (pas de débord sur le lot 1730)"),
}

# ---------------------------------------------------------------------------
# Batiment locatif "Nagaya" R+1 : 4 x 2 pieces + 2 x T1 bis
# ---------------------------------------------------------------------------
LOC_Y0, LOC_Y1 = 22.0, 31.0
LOGEMENTS_X = [("2P-a", "2P", 5.6, 11.0), ("T1-a", "T1bis", 11.0, 14.6), ("2P-b", "2P", 14.6, 20.0)]


def logement(code, typ, x0, x1, niv):
    y0 = LOC_Y0
    p = []
    if typ == "2P":
        p += [
            R(f"{code} Séjour", niv, (x0, y0, x0 + 3.6, y0 + 3.6), "l_sejour"),
            R(f"{code} Cuisine fermée", niv, (x0 + 3.6, y0, x1, y0 + 3.6), "l_kitch"),
            R(f"{code} SE", niv, (x0, y0 + 3.6, x0 + 2.4, y0 + 5.4), "l_eau"),
            R(f"{code} Dégagement", niv, (x0 + 2.4, y0 + 3.6, x0 + 3.6, y0 + 5.4), "l_circ"),
            R(f"{code} Cellier", niv, (x0 + 3.6, y0 + 3.6, x1, y0 + 5.4), "l_circ"),
            R(f"{code} Chambre", niv, (x0, y0 + 5.4, x0 + 3.6, y0 + 9.0), "l_chambre"),
            R(f"{code} Bureau / dressing", niv, (x0 + 3.6, y0 + 5.4, x1, y0 + 9.0), "l_circ"),
        ]
    else:
        p += [
            R(f"{code} Séjour-cuisine", niv, (x0, y0, x1, y0 + 3.6), "l_sejour"),
            R(f"{code} SE", niv, (x0, y0 + 3.6, x0 + 2.0, y0 + 5.4), "l_eau"),
            R(f"{code} Dégagement", niv, (x0 + 2.0, y0 + 3.6, x1, y0 + 5.4), "l_circ"),
            R(f"{code} Alcôve nuit", niv, (x0, y0 + 5.4, x1, y0 + 9.0), "l_chambre"),
        ]
    for r in p:
        r["logement"] = f"{code}-{'RDC' if niv == 'RDC' else 'R1'}"
        r["type_log"] = typ
    return p


def portes_logement(x0, x1, typ, niv):
    y0 = LOC_Y0
    d = [(niv, x0 + 1.8, y0, "h", 0.9)]                    # entree depuis cour / coursive
    if niv == "RDC":
        d.append((niv, x0 + 1.8, y0 + 9.0, "h", 1.2))     # chambre -> patio prive
    if typ == "2P":
        d += [(niv, x0 + 3.6, y0 + 1.8, "v", 0.8),        # sejour -> cuisine
              (niv, x0 + 3.0, y0 + 3.6, "h", 0.8),        # sejour -> degagement
              (niv, x0 + 3.0, y0 + 5.4, "h", 0.8),        # degagement -> chambre
              (niv, x0 + 2.4, y0 + 4.5, "v", 0.7),        # degagement -> SE
              (niv, x0 + 4.5, y0 + 3.6, "h", 0.7),        # cuisine -> cellier
              (niv, x0 + 3.6, y0 + 7.2, "v", 0.8)]        # chambre -> bureau
    else:
        d += [(niv, x0 + 2.8, y0 + 3.6, "h", 0.8),        # sejour -> degagement
              (niv, x0 + 2.8, y0 + 5.4, "h", 0.8),        # degagement -> alcove
              (niv, x0 + 2.0, y0 + 4.5, "v", 0.7)]        # degagement -> SE
    return d


LOCATIF = {
    "code": "L",
    "portes": [d for niv in ("RDC", "R+1") for c, t, a, b in LOGEMENTS_X
               for d in portes_logement(a, b, t, niv)],
    "nom": "Bâtiment locatif R+1 — « Nagaya » de 6 logements",
    "pieces": (
        [r for c, t, a, b in LOGEMENTS_X for r in logement(c, t, a, b, "RDC")]
        + [r for c, t, a, b in LOGEMENTS_X for r in logement(c, t, a, b, "R+1")]
        + [
            # escalier droit le long de la facade Nord, garde-corps plein cote villa (revue)
            R("Escalier extérieur", "RDC", (5.6, 19.6, 10.7, 20.8), "escalier"),
            R("Guérite (gardien commun)", "RDC", (0.2, 18.0, 2.6, 20.0), "service"),
            R("Coursive-engawa", "R+1", (5.6, 20.8, 20.0, 22.0), "l_coursive", clos=False),
            R("Patios privés (tsubo-niwa)", "RDC", (5.6, 31.0, 20.0, 33.0), "patio", clos=False),
        ]
    ),
}

# Logements : surfaces et loyers de marche (Riviera Palmeraie, 2026)
# Fourchettes de marche nu : studio 90-160 k, 2 pieces 160-280 k FCFA / mois
LOYERS = {
    "2P":    {"nu": 230_000, "meuble": 320_000, "nuit": 40_000},
    "T1bis": {"nu": 140_000, "meuble": 200_000, "nuit": 28_000},
}

# ---------------------------------------------------------------------------
# Lignes d'amenagement, VRD, equipements et plus-values.
# (libelle, unite, PU, source, {A: qte, B: qte, L: qte}, divise)
# divise = True  : ratio de la base Eco-donnees, soumis au coefficient diviseur
# divise = False : prix de marche direct (hypothese), non divise
# ---------------------------------------------------------------------------
EXTERIEURS = [
    ("Parking, allées et cour de service pavés (pavés drainants)", "m2", 85_000,
     "Villa Cacao 6 - patio (assimilé)", {"A": 62, "B": 62, "L": 75}, True),
    ("Jardins plantés (terre végétale, gazon, arbres)", "m2", 20_000, "Les Flamboyants - jardins",
     {"A": 115, "B": 145, "L": 45}, True),
    ("Bâche à eau + surpresseur", "ens", 4_047_076, "Pavillon Akpo 2022 - bâche + surpresseur",
     {"A": 1, "B": 1, "L": 1}, True),
    ("Réfection clôture existante + portail coulissant + portillon", "ens", 3_000_000, "Prix de marché (hypothèse)",
     {"A": 1, "B": 1, "L": 1}, False),
    ("Mur séparatif villa / locatif (h 2,5 m, BTC) + claustras de la cour de service", "ml", 60_000,
     "Prix de marché (hypothèse)", {"A": 28, "B": 28, "L": 0}, False),
    ("Assainissement autonome (fosse + puisard) + branchements CIE / SODECI", "ens", 3_500_000,
     "Prix de marché (hypothèse)", {"A": 1, "B": 1, "L": 1.5}, False),
    ("Traitement anti-termites du sol + remblai de plateforme", "m2", 8_000, "Prix de marché (hypothèse)",
     {"A": 160, "B": 125, "L": 145}, False),
    ("Volets coulissants bois à caisson (amado) + moustiquaires", "m2", 110_000, "Prix de marché (hypothèse)",
     {"A": 30, "B": 34, "L": 0}, False),
    ("Chauffe-eau solaires + attentes climatisation (par logement)", "u", 900_000, "Prix de marché (hypothèse)",
     {"A": 2.5, "B": 2.5, "L": 6}, False),
]

PLUS_VALUES = [
    ("Panneaux coulissants bois massif (fusuma / shoji à lames)", "m2", 125_000, "Prix de marché (hypothèse)",
     {"A": 22, "B": 26, "L": 0}, False),
    ("Claustras en terre cuite / BTC ajourée (dont rive de coursive)", "m2", 30_000, "Prix de marché (hypothèse)",
     {"A": 30, "B": 30, "L": 60}, False),
    ("Mur d'accent en pisé (terre crue stabilisée, sous abri)", "m2", 45_000, "Prix de marché (hypothèse)",
     {"A": 20, "B": 18, "L": 0}, False),
    ("Brise-soleil à lames bois (façades Ouest)", "m2", 60_000, "Prix de marché (hypothèse)",
     {"A": 14, "B": 18, "L": 12}, False),
    ("Grande toiture débordante : charpente + couverture hors clos", "m2", 60_000, "Prix de marché (hypothèse)",
     {"A": 0, "B": 100, "L": 0}, False),
    ("Toiture végétalisée extensive (aile parentale)", "m2", 45_000, "Prix de marché (hypothèse)",
     {"A": 35, "B": 0, "L": 0}, False),
    ("Moins-value murs BTC apparents (vs agglos enduits 2 faces)", "m2", -5_000, "Prix de marché (hypothèse)",
     {"A": 260, "B": 240, "L": 320}, False),
]

FRAIS = [  # % du montant travaux HT (base Eco-donnees, recap Pavillon Akpo)
    ("Honoraires architecte (conception + suivi)", 0.08),
    ("BET structure / fluides", 0.02),
    ("Étude géotechnique", 0.015),
    ("Bureau de contrôle", 0.0135),
    ("Assurances (TRC / dommages)", 0.012),
]
IMPREVUS = 0.10  # porte a 10 % au stade esquisse (revue)
TVA = 0.18


def surfaces(opt):
    p = opt["pieces"]
    out = {}
    for niv in ("RDC", "R+1"):
        out[niv] = round(sum(r["surface"] for r in p if r["niveau"] == niv and r["clos"]), 2)
    out["clos"] = round(out["RDC"] + out["R+1"], 2)
    out["ext_couvert"] = round(sum(r["surface"] for r in p if not r["clos"] and r["code"] in
                                   ("terrasse", "balcon", "l_coursive")), 2)
    out["emprise"] = round(sum(r["surface"] for r in p if r["niveau"] == "RDC"
                               and r["nom"] not in ("Engawa", "Arrière-cuisine (préau)",
                                                    "Cour de service / séchoir")
                               and not r["nom"].startswith("Patios privés")), 2)
    return out


def cout_pieces(opt, div=None):
    return round(sum(r["surface"] * pu(r["code"], div) for r in opt["pieces"]))


def pu_ligne(ligne, div=None):
    d = DIVISEUR if div is None else div
    return ligne[2] / d if ligne[5] else ligne[2]


def cout_lignes(liste, key, div=None):
    return round(sum(lg[4].get(key, 0) * pu_ligne(lg, div) for lg in liste))


def budget(opt, div=None):
    k = opt["code"]
    travaux = cout_pieces(opt, div) + cout_lignes(EXTERIEURS, k, div) + cout_lignes(PLUS_VALUES, k, div)
    frais = round(sum(t for _, t in FRAIS) * travaux)
    imprevus = round(IMPREVUS * travaux)
    ht = travaux + frais + imprevus
    return {"travaux": travaux, "frais": frais, "imprevus": imprevus, "total_ht": ht,
            "tva": round(ht * TVA), "total_ttc": round(ht * (1 + TVA))}


if __name__ == "__main__":
    for o in (OPTION_A, OPTION_B, LOCATIF):
        s = surfaces(o)
        b = budget(o)
        print(o["nom"])
        print("  surfaces", s)
        print("  pieces", cout_pieces(o), "budget", b, "PU moyen travaux/m2 clos",
              round(b["travaux"] / s["clos"]))
