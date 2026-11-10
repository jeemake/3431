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
    "cuis_afr":   ("Cuisine africaine (carrelée, ventilée)", 850_000, "Pavillon Akpo 2022 - cuisine"),
    "dressing":   ("Dressing / placards", 850_000, "Résidences Anthurium 2021 - dressing"),
    "service":    ("Réserve / buanderie / cellier", 500_000, "Pavillon Akpo 2022 - réserve"),
    "circ":       ("Circulations (hall, dégagements, palier)", 550_000, "Résidence Les Flamboyants - dégagements"),
    "escalier":   ("Escalier", 600_000, "Résidences Anthurium 2021 - circulations (haut de fourchette)"),
    "terrasse":   ("Terrasse couverte / galerie", 350_000, "Pavillon Akpo 2022 - terrasse"),
    "balcon":     ("Balcon d'étage", 450_000, "Résidences Anthurium 2021 - balcons"),
    "toit_jard":  ("Toit-jardin accessible", 350_000, "Assimilé terrasse (Akpo 2022)"),
    "patio":      ("Cour de service / séchoir / patio", 85_000, "Villa Cacao 6 2023 - patio"),
    "parvis":     ("Parking et allées pavés", 85_000, "Villa Cacao 6 2023 - patio (assimilé)"),
    "jardin":     ("Espaces verts (aménagement)", 20_000, "Résidence Les Flamboyants - jardins et patios"),
    # Locatif (standard appartement)
    "l_sejour":   ("Séjour-cuisine (locatif)", 550_000, "Résidences Anthurium 2021 - sejour"),
    "l_chambre":  ("Chambre / alcôve (locatif)", 500_000, "Résidences Anthurium 2021 - chambres"),
    "l_eau":      ("Salle d'eau (locatif)", 1_000_000, "Résidence Les Flamboyants - salles de bain"),
    "l_kitch":    ("Kitchenette / bande humide", 850_000, "Pavillon Akpo 2022 - cuisine"),
    "l_circ":     ("Dégagement / placard / bureau", 400_000, "Résidences Anthurium 2021 - circulations (bas)"),
    "l_coursive": ("Coursive R+1", 400_000, "Résidences Anthurium 2021 - circulations (bas)"),
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


# ---------------------------------------------------------------------------
# Villa. Partie jour commune aux deux options, deduite des plans de la base Capitude :
# salon traversant N/S (maison de ville Anthurium : 7,0 x 6,5 m), SAM entre salon et cuisine,
# hall + escalier + WC visiteurs groupes cote rue, terrasse couverte au Sud.
# ---------------------------------------------------------------------------
def socle_jour():
    return [
        R("Salon", "RDC", (3.2, 5.0, 8.6, 13.4), "sejour"),
        R("WC visiteurs", "RDC", (8.6, 5.0, 10.0, 7.0), "eau"),
        R("Hall d'entrée", "RDC", [(8.6, 7.0, 11.6, 8.6), (10.0, 5.0, 11.6, 7.0)], "circ"),
        R("Salle à manger", "RDC", (8.6, 8.6, 11.6, 13.4), "sejour"),
        R("Escalier", "RDC", (11.6, 5.0, 14.0, 9.5), "escalier"),
        R("Guérite + WC gardien", "RDC", (7.6, 0.3, 10.0, 2.7), "service"),
    ]


def etage_ouest():
    """Etage commun : salon familial a l'arrivee de l'escalier, suite parentale a l'Ouest."""
    return [
        R("Escalier", "R+1", (11.6, 5.0, 14.0, 9.5), "escalier"),
        R("Salon familial", "R+1", (8.6, 5.0, 11.6, 8.6), "sejour"),
        R("Dressing parental", "R+1", (5.6, 5.0, 8.6, 8.6), "dressing"),
        R("SdB parentale", "R+1", (3.2, 5.0, 5.6, 8.6), "eau"),
        R("Chambre parentale", "R+1", (3.2, 8.6, 8.6, 13.4), "chambre"),
    ]


# Portes : (niveau, x, y, sens, largeur)  sens 'h' = dans un mur horizontal, 'v' = vertical
PORTES_JOUR = [
    ("RDC", 10.8, 5.0, "h", 1.2),   # porte d'entree (blindee)
    ("RDC", 8.6, 7.8, "v", 1.4),    # hall -> salon
    ("RDC", 9.3, 7.0, "h", 0.7),    # hall -> WC visiteurs
    ("RDC", 10.1, 8.6, "h", 1.6),   # hall -> salle a manger
    ("RDC", 11.6, 9.05, "v", 0.8),  # SAM / hall -> palier de depart de l'escalier
    ("RDC", 8.6, 11.0, "v", 3.0),   # salon <-> SAM (grande ouverture)
    ("RDC", 5.9, 13.4, "h", 4.0),   # salon -> terrasse
    ("RDC", 10.1, 13.4, "h", 2.4),  # SAM -> terrasse
    ("RDC", 11.6, 10.1, "v", 0.9),  # SAM -> cuisine (cote hall, hors de la table)
    ("RDC", 8.8, 2.7, "h", 0.8),    # guerite
    ("R+1", 11.6, 9.15, "v", 0.6),  # escalier (arrivee) -> degagement
    ("R+1", 8.6, 6.8, "v", 0.9),    # salon familial -> dressing (suite)
    ("R+1", 5.6, 6.8, "v", 0.8),    # dressing -> SdB
    ("R+1", 7.1, 8.6, "h", 0.9),    # dressing -> chambre
    ("R+1", 10.1, 8.6, "h", 1.2),   # salon familial -> degagement
    ("R+1", 5.9, 13.4, "h", 2.4),   # chambre parentale -> balcon
    ("R+1", 10.4, 9.8, "h", 0.9),   # degagement -> chambre 2
    ("R+1", 10.4, 13.4, "h", 1.8),  # chambre 2 -> balcon
]

OPTION_A = {
    "code": "A",
    "nom": "Option A — Villa compacte, nounou à l'étage",
    "titre_court": "Villa compacte",
    "ref": "Maison de ville Anthurium (R+1, 4 ch.), villa ABYA 2",
    "parti": ("Un seul volume R+1 de 14,4 × 8,4 m. Au RDC, la bande Est regroupe magasin, buanderie et cuisine "
              "et arrière-cuisine ; la cuisine africaine est un petit pavillon en claustra dans la cour de service, hors "
              "du volume habité. La chambre de la nounou est à l'étage, à côté des chambres d'enfants."),
    "pieces": socle_jour() + [
        R("Cuisine", "RDC", (11.6, 9.5, 14.0, 13.4), "cuisine"),
        R("Magasin / réserve", "RDC", (14.0, 5.0, 17.6, 7.4), "service"),
        R("Buanderie", "RDC", (14.0, 7.4, 17.6, 9.8), "service"),
        R("Arrière-cuisine (préparations)", "RDC", (14.0, 9.8, 17.6, 13.4), "service"),
        # revue V2 : la cuisine africaine sort du volume habite (feu, pilon, fumees)
        R("Cuisine africaine (pavillon claustra)", "RDC", (17.6, 9.8, 20.0, 13.4), "cuis_afr"),
        R("Cour de service / séchoir", "RDC", (17.6, 5.0, 20.0, 9.8), "patio", clos=False),
        R("Terrasse couverte", "RDC", (3.2, 13.4, 17.6, 15.8), "terrasse", clos=False),
    ] + etage_ouest() + [
        R("Dégagement", "R+1", [(8.6, 8.6, 11.6, 9.8), (14.0, 8.6, 17.6, 9.8), (11.6, 9.5, 14.0, 9.8)], "circ"),
        R("Chambre 2", "R+1", (8.6, 9.8, 12.2, 13.4), "chambre"),
        R("SE ch.2", "R+1", (12.2, 9.8, 14.2, 11.6), "eau"),
        R("SE ch.3", "R+1", (12.2, 11.6, 14.2, 13.4), "eau"),
        R("Chambre 3", "R+1", (14.2, 9.8, 17.6, 13.4), "chambre"),
        R("Chambre nounou", "R+1", (14.0, 6.2, 17.6, 8.6), "chambre"),
        R("SE nounou", "R+1", (14.0, 5.0, 17.6, 6.2), "eau"),
        R("Balcon", "R+1", (3.2, 13.4, 17.6, 15.2), "balcon", clos=False),
    ],
    "portes": PORTES_JOUR + [
        ("RDC", 14.0, 12.0, "v", 0.9),  # cuisine -> arriere-cuisine
        ("RDC", 12.8, 13.4, "h", 1.4),  # cuisine -> terrasse (baie + imposte, revue V2)
        ("RDC", 17.6, 6.2, "v", 0.9),   # magasin -> cour
        ("RDC", 17.6, 8.6, "v", 0.9),   # buanderie -> cour / sechoir
        ("RDC", 15.8, 9.8, "h", 0.8),   # buanderie -> arriere-cuisine
        ("RDC", 17.6, 11.6, "v", 1.2),  # arriere-cuisine -> cuisine africaine
        ("RDC", 18.8, 9.8, "h", 1.2),   # cuisine africaine -> cour
        ("RDC", 19.6, 5.0, "h", 0.8),   # porte de service sur la cour
        ("R+1", 12.2, 10.7, "v", 0.7),  # ch2 -> SE
        ("R+1", 14.2, 12.5, "v", 0.7),  # ch3 -> SE
        ("R+1", 15.9, 9.8, "h", 0.9),   # degagement -> chambre 3
        ("R+1", 15.9, 13.4, "h", 1.8),  # chambre 3 -> balcon
        ("R+1", 15.8, 8.6, "h", 0.9),   # degagement -> chambre nounou
        ("R+1", 15.8, 6.2, "h", 0.7),   # chambre nounou -> SE
    ],
    "toiture": ("Toiture bac acier isolé à faible pente sur charpente, cachée par un acrotère, débords de 1,2 m ; "
                "la terrasse et le balcon Sud forment une casquette de 2,4 m ; conduit de la cuisine africaine "
                "remonté au-dessus de la toiture de l'étage"),
}

OPTION_B = {
    "code": "B",
    "nom": "Option B — Villa avec aile de service",
    "titre_court": "Villa et aile de service",
    "ref": "Résidence EMIIKA, villa JIK",
    "parti": ("Un volume R+1 de 12,6 × 8,4 m et, le long de la limite Est, une aile de service de plain-pied reliée par "
              "une galerie couverte : cuisine africaine, buanderie, séchoir et studio de la nounou avec sa salle d'eau. "
              "Grande cuisine moderne avec îlot."),
    "pieces": socle_jour() + [
        R("Cuisine (avec îlot)", "RDC", [(11.6, 9.5, 14.0, 13.4), (14.0, 8.6, 15.8, 13.4)], "cuisine"),
        R("Office / cellier", "RDC", (14.0, 5.0, 15.8, 8.6), "service"),
        R("Galerie de service", "RDC", (15.8, 5.0, 17.0, 16.0), "terrasse", clos=False),
        R("Préau cuisine africaine", "RDC", (17.0, 2.6, 20.0, 5.0), "terrasse", clos=False),
        R("Cuisine africaine", "RDC", (17.0, 5.0, 20.0, 9.0), "cuis_afr"),
        R("Buanderie / magasin", "RDC", (17.0, 9.0, 20.0, 11.4), "service"),
        R("Séchoir couvert (claustra)", "RDC", (17.0, 11.4, 20.0, 13.6), "terrasse", clos=False),
        R("Chambre nounou", "RDC", (17.0, 13.6, 20.0, 16.6), "chambre"),
        R("SE nounou", "RDC", (17.0, 16.6, 20.0, 18.0), "eau"),
        R("Terrasse couverte", "RDC", (3.2, 13.4, 15.8, 15.8), "terrasse", clos=False),
    ] + etage_ouest() + [
        R("Dégagement", "R+1", [(8.6, 8.6, 11.6, 9.8), (14.0, 8.6, 15.8, 9.8), (11.6, 9.5, 14.0, 9.8)], "circ"),
        R("Chambre 2", "R+1", (8.6, 9.8, 12.2, 13.4), "chambre"),
        R("Chambre 3", "R+1", (12.2, 9.8, 15.8, 13.4), "chambre"),
        R("SE partagée ch.2 / ch.3", "R+1", (14.0, 5.0, 15.8, 8.6), "eau"),
        R("Balcon", "R+1", (3.2, 13.4, 15.8, 15.2), "balcon", clos=False),
    ],
    "portes": PORTES_JOUR + [
        ("RDC", 15.8, 11.0, "v", 0.9),  # cuisine -> galerie de service
        ("RDC", 13.7, 13.4, "h", 1.2),  # cuisine -> terrasse
        ("RDC", 14.9, 8.6, "h", 0.8),   # cuisine -> office
        ("RDC", 14.0, 9.05, "v", 0.6),  # office -> palier de depart de l'escalier (revue V2)
        ("RDC", 15.8, 6.8, "v", 0.8),   # office -> galerie
        ("RDC", 17.0, 7.0, "v", 1.2),   # galerie -> cuisine africaine
        ("RDC", 18.5, 5.0, "h", 1.2),   # cuisine africaine -> preau / aire de livraison (Nord)
        ("RDC", 17.0, 10.2, "v", 0.9),  # galerie -> buanderie
        ("RDC", 18.5, 11.4, "h", 0.9),  # buanderie -> sechoir
        ("RDC", 17.0, 15.1, "v", 0.8),  # galerie couverte -> chambre nounou
        ("RDC", 18.5, 16.6, "h", 0.7),  # chambre nounou -> SE
        ("R+1", 14.0, 9.8, "h", 0.9),   # degagement -> chambre 3
        ("R+1", 14.0, 13.4, "h", 1.8),  # chambre 3 -> balcon
        ("R+1", 14.9, 8.6, "h", 0.8),   # degagement -> SE partagee
    ],
    "toiture": ("Toiture bac acier isolé sur charpente, débords de 1,2 m ; aile de service sous toiture monopente "
                "vers l'Ouest, acrotère sur la limite Est (aucune eau chez le voisin) ; conduit de la cuisine africaine "
                "remonté au-dessus de l'égout de l'étage"),
}

# Option C v5 : trame du client (markup du 10-11-2026). X : recul Ouest 2,5 | 3 | 3,5 | 3,5 | 2 | 3,5 | passage Est 2 ;
# Y : parking 4,5 | loggia / passage couvert 1,0 | bande Nord 5,5 | bande Sud 5,8 | passage 1,2 | mur vegetalise en limite.
# Cloison cuisine / cuisine africaine alignee sur l'axe 5 (x = 14,5), comme le bureau ; porte cuisine -> terrasse supprimee.
CX = (2.5, 5.5, 9.0, 12.5, 14.5, 18.0)
CY = (4.5, 5.5, 11.0, 16.8, 18.0)
NIVEAUX = {"RDC": 0.0, "R+1": 3.30, "TOIT": 6.60, "PERGOLA": 9.00}   # cotes du client (markup coupe BB)
OPTION_C = {
    "code": "C",
    "nom": "Option C — Maison à patio",
    "titre_court": "Maison à patio",
    "ref": ("Images de référence du client (claustra de lames de bois ; bardage bois, claustra béton, moellons, grand "
            "débord), Palinda Kannangara (Casa Lineal, Casa Estudio) pour le patio, Anthurium MV, EMIIKA, JIK"),
    "parti": ("Les pièces s'organisent autour d'un patio planté à ciel ouvert, bordé au Nord par une terrasse couverte "
              "et ouvert au Sud sur un mur végétalisé en limite. Au rez-de-chaussée : salon à l'Ouest, salle à manger "
              "et cuisine au Nord, bureau et nounou à l'Est. À l'étage, un plan en L : salon familial et deux chambres "
              "le long de la rue, chambre principale au fond. L'escalier monte jusqu'à un toit-terrasse couvert."),
    "pieces": [
        R("Guérite + WC gardien", "RDC", (3.3, 0.3, 5.7, 2.7), "service"),
        R("Local GE + niche compteurs", "RDC", (0.3, 0.3, 3.0, 2.5), "service", clos=False),
        R("Passage couvert d'entrée", "RDC", (2.5, 4.5, 15.5, 5.5), "terrasse", clos=False),
        R("Escalier", "RDC", (2.5, 5.5, 5.5, 9.7), "escalier"),
        R("WC visiteurs", "RDC", (2.5, 9.7, 5.5, 11.0), "eau"),
        R("Hall d'entrée", "RDC", (5.5, 5.5, 7.5, 11.0), "circ"),
        R("Salle à manger", "RDC", (7.5, 5.5, 12.5, 11.0), "sejour"),
        R("Cuisine", "RDC", (12.5, 5.5, 14.5, 11.0), "cuisine"),
        R("Cuisine africaine", "RDC", (14.5, 5.5, 18.0, 9.4), "cuis_afr"),
        R("Buanderie (sas)", "RDC", (14.5, 9.4, 18.0, 11.0), "service"),
        R("Salon", "RDC", (2.5, 11.0, 9.0, 16.8), "sejour"),
        R("Terrasse couverte sur patio", "RDC", (9.0, 11.0, 14.5, 13.4), "terrasse", clos=False),
        R("Patio planté", "RDC", (9.0, 13.4, 14.5, 18.0), "patio", clos=False),
        R("Bureau", "RDC", (14.5, 11.0, 18.0, 13.0), "chambre"),
        R("SE nounou", "RDC", (14.5, 13.0, 18.0, 14.4), "eau"),
        R("Chambre nounou", "RDC", (14.5, 14.4, 18.0, 16.8), "chambre"),
        R("Préau cuisine africaine", "RDC", (15.5, 2.6, 18.0, 5.5), "terrasse", clos=False),
        R("Séchoir à ciel ouvert", "RDC", (14.5, 0.2, 18.0, 2.6), "patio", clos=False),
        # etage en L
        R("Rangement", "R+1", (2.5, 4.5, 5.5, 5.5), "dressing"),
        R("Loggia Nord (rangements)", "R+1", (5.5, 4.5, 18.0, 5.5), "balcon", clos=False),
        R("Escalier", "R+1", (2.5, 5.5, 5.5, 9.7), "escalier"),
        R("Lingerie", "R+1", (2.5, 9.7, 5.5, 11.0), "dressing"),
        R("Salon familial", "R+1", (5.5, 5.5, 9.0, 11.0), "sejour"),
        R("Chambre 1", "R+1", (9.0, 5.5, 12.5, 9.8), "chambre"),
        R("SE ch.1", "R+1", (12.5, 5.5, 14.5, 7.65), "eau"),
        R("SE ch.2", "R+1", (12.5, 7.65, 14.5, 9.8), "eau"),
        R("Galerie sur patio", "R+1", (9.0, 9.8, 14.5, 11.0), "circ"),
        R("Chambre 2", "R+1", (14.5, 5.5, 18.0, 11.0), "chambre"),
        R("SdB parentale", "R+1", (2.5, 11.0, 5.5, 13.6), "eau"),
        R("Dressing parental", "R+1", (5.5, 11.0, 9.0, 13.6), "dressing"),
        R("Chambre principale", "R+1", (2.5, 13.6, 9.0, 16.8), "chambre"),
        R("Jardinière Ouest", "R+1", (1.7, 13.6, 2.5, 16.8), "balcon", clos=False),
        # niveau haut : toit-terrasse couvert (pergola V1 sous toiture plate, V2 sous toit en croupe)
        R("Édicule d'escalier", "TOIT", (2.5, 5.5, 5.5, 9.7), "escalier"),
        R("Toit-terrasse couvert", "TOIT", [(5.5, 5.5, 18.0, 11.0), (2.5, 9.7, 5.5, 11.0), (2.5, 11.0, 9.0, 16.8)],
          "toit_jard", clos=False),
        R("Jardinière (firecracker plants)", "TOIT", (2.5, 4.5, 18.0, 5.5), "jardin", clos=False),
    ],
    "portes": [
        ("RDC", 6.5, 5.5, "h", 1.2),    # porte d'entree pivotante (axe 6,5)
        ("RDC", 5.5, 8.4, "v", 0.9),    # hall -> escalier
        ("RDC", 5.5, 10.35, "v", 0.7),  # hall -> WC visiteurs
        ("RDC", 7.5, 7.4, "v", 1.2),    # hall -> salle a manger
        ("RDC", 6.6, 11.0, "h", 1.6),   # hall -> salon
        ("RDC", 8.25, 11.0, "h", 1.2),  # salle a manger <-> salon (ouverture)
        ("RDC", 10.75, 11.0, "h", 2.4), # salle a manger -> terrasse (baie)
        ("RDC", 12.5, 6.4, "v", 0.9),   # salle a manger -> cuisine
        ("RDC", 14.5, 10.2, "v", 0.8),  # cuisine -> buanderie (sas)
        ("RDC", 16.25, 9.4, "h", 0.8),  # buanderie -> cuisine africaine
        ("RDC", 18.0, 10.2, "v", 0.8),  # buanderie -> passage Est
        ("RDC", 16.25, 5.5, "h", 1.2),  # cuisine africaine -> preau / livraisons
        ("RDC", 9.0, 13.9, "v", 4.0),   # salon -> terrasse et patio (baies)
        ("RDC", 2.5, 15.2, "v", 2.4),   # salon -> jardin Ouest
        ("RDC", 14.5, 12.0, "v", 0.9),  # bureau -> terrasse
        ("RDC", 16.25, 14.4, "h", 0.7), # chambre nounou -> SE
        ("RDC", 18.0, 15.6, "v", 0.8),  # chambre nounou -> passage Est (porte independante)
        ("RDC", 4.5, 2.7, "h", 0.8),    # guerite
        ("R+1", 5.5, 8.4, "v", 0.9),    # escalier -> salon familial
        ("R+1", 5.5, 10.35, "v", 0.7),  # salon familial -> lingerie
        ("R+1", 4.0, 5.5, "h", 0.8),    # escalier -> rangement
        ("R+1", 7.3, 11.0, "h", 0.9),   # salon familial -> dressing (suite)
        ("R+1", 5.5, 12.3, "v", 0.8),   # dressing -> SdB
        ("R+1", 7.3, 13.6, "h", 0.9),   # dressing -> chambre principale
        ("R+1", 2.5, 15.2, "v", 2.4),   # chambre principale -> jardiniere Ouest (baie)
        ("R+1", 9.0, 10.4, "v", 0.9),   # salon familial -> galerie
        ("R+1", 10.75, 9.8, "h", 0.9),  # galerie -> chambre 1
        ("R+1", 12.5, 6.6, "v", 0.8),   # chambre 1 -> SE ch.1
        ("R+1", 14.5, 10.4, "v", 0.9),  # galerie -> chambre 2
        ("R+1", 14.5, 8.7, "v", 0.8),   # chambre 2 -> SE ch.2
        ("R+1", 6.5, 5.5, "h", 1.6),    # salon familial -> loggia (axe 6,5)
        ("R+1", 10.75, 5.5, "h", 1.4),  # chambre 1 -> loggia
        ("R+1", 16.25, 5.5, "h", 1.4),  # chambre 2 -> loggia
        ("TOIT", 5.5, 8.4, "v", 0.9),   # edicule -> toit-terrasse
    ],
    "toiture": ("Toit-terrasse accessible en béton, étanché, couvert à +9,00 (V1 : toiture plate mince à grand débord ; "
                "V2 : toit en croupe à faible pente, sous-face en lames de bois), jardinière continue de firecracker "
                "plants sur la façade Nord ; toitures végétalisées sur l'aile Est et la terrasse couverte ; descentes "
                "en façade, aucune eau de toiture dans le patio"),
}
for _r in OPTION_C["pieces"]:
    if (_r["niveau"], _r["nom"]) == ("RDC", "Cuisine"):
        _r["plan"] = "O"     # plan de travail en L le long du mur Ouest et du mur Sud (markup)
    if (_r["niveau"], _r["nom"]) == ("R+1", "Chambre 2"):
        _r["lit"] = "E"

# ---------------------------------------------------------------------------
# Batiment locatif R+1 : 4 x 2 pieces + 2 x T1 bis
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
    "nom": "Bâtiment locatif R+1 — barrette de 6 logements",
    "pieces": (
        [r for c, t, a, b in LOGEMENTS_X for r in logement(c, t, a, b, "RDC")]
        + [r for c, t, a, b in LOGEMENTS_X for r in logement(c, t, a, b, "R+1")]
        + [
            # escalier droit le long de la facade Nord, garde-corps plein cote villa (revue)
            R("Escalier extérieur", "RDC", (5.6, 19.6, 10.7, 20.8), "escalier"),
            R("Guérite (gardien commun)", "RDC", (0.2, 18.0, 2.6, 20.0), "service"),
            R("Coursive", "R+1", (5.6, 20.8, 20.0, 22.0), "l_coursive", clos=False),
            R("Patios privés / séchoirs", "RDC", (5.6, 31.0, 20.0, 33.0), "patio", clos=False),
        ]
    ),
}

# ---------------------------------------------------------------------------
# Locatif v3 (markup du 10-11-2026) : 2 maisons duplex au lieu de 3, chacune avec toit-terrasse sous pergola.
# Trame X : bande Ouest 3 (allee + stationnement) | 8,5 | 8,5 ; trame Y (depuis la limite villa) :
# jardins 3 | bande jour / nuit 6,5 | bande de service 2,5 | cour d'entree 3.
# ---------------------------------------------------------------------------
MX = (3.0, 11.5, 20.0)
MY = (18.0, 21.0, 27.5, 30.0, 33.0)


def maison(n, x0):
    y1, y2, y3 = MY[1], MY[2], MY[3]
    m = f"M{n}"
    p = [
        R(f"{m} Séjour-SAM", "RDC", [(x0, y1, x0 + 5.5, y2), (x0 + 5.5, y1, x0 + 8.5, 24.0)], "l_sejour"),
        R(f"{m} Cuisine", "RDC", (x0 + 5.5, 24.0, x0 + 8.5, y2), "l_kitch"),
        R(f"{m} Entrée", "RDC", (x0, y2, x0 + 2.0, y3), "l_circ"),
        R(f"{m} Escalier", "RDC", (x0 + 2.0, y2, x0 + 5.6, y3), "escalier"),
        R(f"{m} WC", "RDC", (x0 + 5.6, y2, x0 + 7.0, y3), "l_eau"),
        R(f"{m} Cellier", "RDC", (x0 + 7.0, y2, x0 + 8.5, y3), "l_circ"),
        R(f"{m} Jardin privé", "RDC", (x0, MY[0], x0 + 8.5, y1), "jardin", clos=False),
        R(f"{m} Cour d'entrée", "RDC", (x0, y3, x0 + 8.5, MY[4]), "parvis", clos=False),
        R(f"{m} Chambre 2", "R+1", (x0, y1, x0 + 3.6, 26.3), "l_chambre"),
        R(f"{m} Chambre principale", "R+1", (x0 + 3.6, y1, x0 + 8.5, 25.0), "l_chambre"),
        R(f"{m} Dressing", "R+1", (x0 + 5.6, 25.0, x0 + 8.5, y2), "dressing"),
        R(f"{m} Dégagement", "R+1", [(x0, 26.3, x0 + 5.6, y2), (x0 + 3.6, 25.0, x0 + 5.6, 26.3)], "l_circ"),
        R(f"{m} Escalier", "R+1", (x0 + 2.0, y2, x0 + 5.6, y3), "escalier"),
        R(f"{m} SE", "R+1", (x0, y2, x0 + 2.0, y3), "l_eau"),
        R(f"{m} SdB parentale", "R+1", (x0 + 5.6, y2, x0 + 8.5, y3), "l_eau"),
        R(f"{m} Édicule d'escalier", "TOIT", (x0 + 2.0, y2, x0 + 5.6, y3), "escalier"),
        R(f"{m} Toit-terrasse sous pergola", "TOIT",
          [(x0, y1, x0 + 8.5, y2), (x0, y2, x0 + 2.0, y3), (x0 + 5.6, y2, x0 + 8.5, y3)], "toit_jard", clos=False),
    ]
    for r in p:
        r["logement"] = m
        r["type_log"] = "MD"
    return p


def portes_maison(x0):
    y1, y2, y3 = MY[1], MY[2], MY[3]
    return [
        ("RDC", x0 + 1.0, y3, "h", 1.0),       # entree depuis la cour d'entree
        ("RDC", x0 + 1.0, y2, "h", 0.9),       # entree -> sejour
        ("RDC", x0 + 2.0, 28.75, "v", 0.9),    # entree -> escalier
        ("RDC", x0 + 5.5, 26.0, "v", 1.2),     # sejour -> cuisine
        ("RDC", x0 + 6.3, y2, "h", 0.7),       # cuisine -> WC
        ("RDC", x0 + 7.75, y2, "h", 0.7),      # cuisine -> cellier
        ("RDC", x0 + 7.75, y3, "h", 0.8),      # cellier -> cour (service)
        ("RDC", x0 + 1.8, y1, "h", 2.8),       # sejour -> jardin prive (baie, axe 1,8 commun avec la chambre 2)
        ("RDC", x0 + 7.0, y1, "h", 2.4),       # coin repas -> jardin (baie)
        ("R+1", x0 + 1.8, 26.3, "h", 0.8),     # degagement -> chambre 2
        ("R+1", x0 + 4.6, 25.0, "h", 0.9),     # degagement -> chambre principale
        ("R+1", x0 + 7.0, 25.0, "h", 0.8),     # chambre principale -> dressing
        ("R+1", x0 + 7.0, y2, "h", 0.8),       # dressing -> SdB parentale
        ("R+1", x0 + 1.0, y2, "h", 0.7),       # degagement -> SE
        ("TOIT", x0 + 3.8, y2, "h", 0.9),      # edicule -> toit-terrasse
    ]


LOCATIF_M = {
    "code": "M",
    "nom": "Locatif — 2 maisons duplex avec toit-terrasse sous pergola",
    "pieces": [r for n, x0 in enumerate(MX[:2], 1) for r in maison(n, x0)]
              + [R("Stationnement 2 places (rue Ouest)", "RDC", (0.0, 18.0, 3.0, 30.0), "parvis", clos=False),
                 R("Allée piétonne", "RDC", (0.0, 30.0, 3.0, 33.0), "parvis", clos=False)],
    "portes": [d for x0 in MX[:2] for d in portes_maison(x0)],
}
for _r in LOCATIF_M["pieces"]:
    if _r["nom"].endswith("Cuisine"):
        _r["plan"] = "E"

# Logements : surfaces et loyers de marche (Riviera Palmeraie, 2026)
# Fourchettes de marche nu : studio 90-160 k, 2 pieces 160-280 k FCFA / mois
LOYERS = {
    # maison duplex de 150 m² (2 chambres dont une suite, jardin, toit-terrasse) : hypothese a valider avec deux agences
    "MD":    {"nu": 600_000, "meuble": 850_000, "nuit": 95_000},
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
    ("Parking, allée et aire de livraison pavés (pavés drainants)", "m2", 85_000,
     "Villa Cacao 6 - patio (assimilé)", {"A": 65, "B": 65, "C": 55, "L": 75, "M": 75}, True),
    ("Jardins plantés (terre végétale, gazon, arbres d'ombrage)", "m2", 20_000, "Les Flamboyants - jardins",
     {"A": 100, "B": 85, "C": 70, "L": 45, "M": 51}, True),
    ("Bâche à eau + surpresseur", "ens", 4_047_076, "Pavillon Akpo 2022 - bâche + surpresseur",
     {"A": 1, "B": 1, "C": 1, "L": 1, "M": 1}, True),
    ("Réfection clôture existante + portail coulissant + portillon", "ens", 3_000_000, "Prix de marché (hypothèse)",
     {"A": 1, "B": 1, "C": 1, "L": 1, "M": 1}, False),
    ("Mur séparatif villa / locatif (h 2,5 m) + claustras de la cour de service", "ml", 60_000,
     "Prix de marché (hypothèse)", {"A": 28, "B": 28, "C": 8, "L": 0, "M": 0}, False),
    ("Assainissement autonome (fosse + puisard) + branchements CIE / SODECI", "ens", 3_500_000,
     "Prix de marché (hypothèse)", {"A": 1, "B": 1, "C": 1, "L": 1.5, "M": 1.2}, False),
    ("Traitement anti-termites du sol + remblai de plateforme", "m2", 8_000, "Prix de marché (hypothèse)",
     {"A": 125, "B": 150, "C": 160, "L": 145, "M": 160}, False),
    ("Grilles de défense RDC et étage + moustiquaires", "m2", 45_000, "Prix de marché (hypothèse)",
     {"A": 70, "B": 70, "C": 70, "L": 30, "M": 45}, False),
    ("Chauffe-eau solaires + attentes climatisation (par logement)", "u", 900_000, "Prix de marché (hypothèse)",
     {"A": 2.5, "B": 2.5, "C": 2.5, "L": 6, "M": 2}, False),
    ("Cuisine africaine : hotte d'extraction, évier double bac, cage à bouteilles de gaz", "ens", 900_000,
     "Prix de marché (hypothèse)", {"A": 1, "B": 1, "C": 1, "L": 0, "M": 0}, False),
]

PLUS_VALUES = [
    ("Menuiseries bois persiennées (jalousies) / écrans coulissants en lattes", "m2", 120_000, "Prix de marché (hypothèse)",
     {"A": 30, "B": 28, "C": 12, "L": 0, "M": 0}, False),
    ("Claustras en terre cuite / BTC ajourée (cour de service, façades Ouest, coursive)", "m2", 30_000,
     "Prix de marché (hypothèse)", {"A": 35, "B": 35, "C": 32, "L": 60, "M": 0}, False),
    ("Brise-soleil à lames (façades Ouest)", "m2", 60_000, "Prix de marché (hypothèse)",
     {"A": 14, "B": 14, "C": 0, "L": 12, "M": 0}, False),
    ("Débords de toiture et casquettes (hors clos)", "m2", 60_000, "Prix de marché (hypothèse)",
     {"A": 50, "B": 55, "C": 15, "L": 0, "M": 0}, False),
    ("Patio : arbre (frangipanier), massifs, éclairage (bassins supprimés, markup)", "ens", 2_200_000, "Prix de marché (hypothèse)",
     {"A": 0, "B": 0, "C": 1, "L": 0, "M": 0}, False),
    ("Patio : claustra haute 4 m + pergola plantée (fermeture Sud)", "ens", 1_500_000, "Prix de marché (hypothèse)",
     {"A": 0, "B": 0, "C": 0, "L": 0, "M": 0}, False),
    ("Patio : caniveau grillé périphérique + exutoire", "ens", 1_200_000, "Prix de marché (hypothèse)",
     {"A": 0, "B": 0, "C": 1, "L": 0, "M": 0}, False),
    ("Moins-value murs BTC (vs agglos enduits 2 faces)", "m2", -5_000, "Prix de marché (hypothèse)",
     {"A": 250, "B": 270, "C": 0, "L": 320, "M": 0}, False),
    # Option C, ecriture Palinda Kannangara (Casa Lineal, Casa Estudio) : postes propres
    ("Peau de l'étage en lames de bois dur traité, sur toutes les faces (V1 damier ; V2 bardage et brise-soleil)",
     "m2", 85_000, "Prix de marché (hypothèse)", {"A": 0, "B": 0, "C": 110, "L": 0, "M": 133}, False),
    ("Claustra en blocs de béton ajourés (clôture sur rue, lanterne d'escalier)", "m2", 32_000,
     "Prix de marché (hypothèse)", {"A": 0, "B": 0, "C": 30, "L": 0, "M": 0}, False),
    ("Plus-value parement en moellons de granite (RDC sur rues, guérite, socle de clôture)", "m2", 28_000,
     "Prix de marché (hypothèse)", {"A": 0, "B": 0, "C": 100, "L": 0, "M": 0}, False),
    ("Plus-value béton brut coffré planches (nez de dalle, corniches à goutte d'eau, porche)", "m2", 15_000,
     "Prix de marché (hypothèse)", {"A": 0, "B": 0, "C": 60, "L": 0, "M": 30}, False),
    ("Toiture végétalisée extensive (substrat 15 cm, drainage, étanchéité anti-racines) + jardinières de rive",
     "m2", 25_000, "Prix de marché (hypothèse)", {"A": 0, "B": 0, "C": 33.5, "L": 0, "M": 0}, False),
    ("Lanterneau vitré ventilé sur la passerelle (verre feuilleté, châssis acier, rehausses)", "m2", 180_000,
     "Prix de marché (hypothèse)", {"A": 0, "B": 0, "C": 0, "L": 0, "M": 0}, False),
    ("Bio-bassin devant le salon (bande Ouest) : supprimé (markup du 10-11-2026)", "ens", 1_600_000,
     "Prix de marché (hypothèse)", {"A": 0, "B": 0, "C": 0, "L": 0, "M": 0}, False),
    ("Écrans en lattes de bois de la passerelle et stores bambou sous débords Ouest", "ens", 900_000,
     "Prix de marché (hypothèse)", {"A": 0, "B": 0, "C": 1, "L": 0, "M": 0}, False),
    # markup du 07-11-2026 : niveau pergola, jardinieres, mur vegetalise, garde-corps des toits-terrasses
    ("Pergola bois sur poteaux acier, niveau toit-terrasse", "m2", 45_000, "Prix de marché (hypothèse)",
     {"A": 0, "B": 0, "C": 0, "L": 0, "M": 0}, False),
    ("Couverture du toit-terrasse à +9,00 sur poteaux acier, sous-face bois (V1 toiture plate mince, V2 croupe)",
     "m2", 70_000, "Prix de marché (hypothèse)", {"A": 0, "B": 0, "C": 150, "L": 0, "M": 178}, False),
    ("Jardinière continue en rive de toiture (plantation basse, sans retombées ; goutte-à-goutte)", "ml", 75_000, "Prix de marché (hypothèse)",
     {"A": 0, "B": 0, "C": 15.5, "L": 0, "M": 17}, False),
    ("Mur végétalisé de 3,50 m en limite villa / locatif (treillis inox, jardinières, arrosage)", "m2", 55_000,
     "Prix de marché (hypothèse)", {"A": 0, "B": 0, "C": 70, "L": 0, "M": 0}, False),
    ("Garde-corps des toits-terrasses (acrotère 1,0 m + lisse)", "ml", 35_000, "Prix de marché (hypothèse)",
     {"A": 0, "B": 0, "C": 45, "L": 0, "M": 52}, False),
    ("Local GE + niche compteurs (dalle, claustra, porte)", "ens", 1_200_000, "Prix de marché (hypothèse)",
     {"A": 0, "B": 0, "C": 1, "L": 0, "M": 0}, False),
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
                               and r["code"] not in ("terrasse", "patio")
                               and r["nom"] != "Guérite + WC gardien" and not r["nom"].startswith("Local GE")
                               and r["clos"]), 2) + round(sum(
        r["surface"] for r in p if r["nom"].startswith("Galerie") and r["niveau"] == "RDC"), 2)
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
    for o in (OPTION_A, OPTION_B, OPTION_C, LOCATIF):
        s = surfaces(o)
        b = budget(o)
        print(o["nom"])
        print("  surfaces", s)
        print("  pieces", cout_pieces(o), "budget", b, "PU moyen travaux/m2 clos",
              round(b["travaux"] / s["clos"]))
