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

OPTION_C = {
    "code": "C",
    "nom": "Option C — Maison à patio central",
    "titre_court": "Maison à patio",
    "ref": "ABYA 3 (maison-patio à galerie), EMIIKA (patios et lanière de services)",
    "parti": ("Les pièces s'organisent en U autour d'un patio planté, ouvert au Sud vers la brise. Salon à l'Ouest, "
              "salle à manger et cuisine au Nord, service et nounou à l'Est. Un passage de 1,50 m fait le tour de la "
              "maison pour circuler et ouvrir des fenêtres sur toutes les faces."),
    "pieces": [
        R("Guérite + WC gardien", "RDC", (4.4, 0.3, 6.8, 2.7), "service"),
        R("Escalier", "RDC", (3.2, 5.0, 5.6, 9.5), "escalier"),
        R("WC visiteurs", "RDC", (5.6, 5.0, 7.0, 7.0), "eau"),
        R("Hall d'entrée", "RDC", [(5.6, 7.0, 8.0, 9.2), (7.0, 5.0, 8.0, 7.0)], "circ"),
        R("Salle à manger", "RDC", (8.0, 5.0, 11.6, 9.2), "sejour"),
        R("Cuisine", "RDC", (11.6, 5.0, 14.9, 9.2), "cuisine"),
        R("Salon", "RDC", [(5.6, 9.2, 9.2, 16.5), (3.2, 9.5, 5.6, 16.5)], "sejour"),
        R("Cuisine africaine", "RDC", (14.9, 5.0, 18.5, 8.6), "cuis_afr"),
        R("Buanderie / magasin", "RDC", (14.9, 8.6, 18.5, 11.6), "service"),
        R("Chambre nounou", "RDC", (14.9, 11.6, 18.5, 14.9), "chambre"),
        R("SE nounou", "RDC", (14.9, 14.9, 18.5, 16.5), "eau"),
        R("Galerie sur patio", "RDC", (9.2, 9.2, 14.9, 10.4), "terrasse", clos=False),
        R("Patio planté", "RDC", (9.2, 10.4, 14.9, 18.0), "patio", clos=False),
        R("Séchoir couvert (passage Est)", "RDC", (18.5, 8.6, 20.0, 12.0), "terrasse", clos=False),
        R("Préau cuisine africaine", "RDC", (15.9, 2.6, 18.5, 5.0), "terrasse", clos=False),
        R("Escalier", "R+1", (3.2, 5.0, 5.6, 9.5), "escalier"),
        R("Palier", "R+1", (5.6, 5.0, 8.0, 9.2), "circ"),
        R("Salon familial", "R+1", (8.0, 5.0, 11.6, 9.2), "sejour"),
        R("Chambre 2", "R+1", [(11.6, 5.0, 13.4, 9.2), (13.4, 7.4, 14.9, 9.2)], "chambre"),
        R("SE ch.2", "R+1", (13.4, 5.0, 14.9, 7.4), "eau"),
        R("Dressing parental", "R+1", (6.2, 9.2, 9.2, 12.2), "dressing"),
        R("SdB parentale", "R+1", (3.2, 9.5, 6.2, 12.2), "eau"),
        R("Chambre parentale", "R+1", (3.2, 12.2, 9.2, 16.5), "chambre"),
        R("Chambre 3", "R+1", (14.9, 8.6, 18.5, 12.2), "chambre"),
        R("SE ch.3", "R+1", (14.9, 12.2, 18.5, 13.7), "eau"),
        R("Coursive sur patio", "R+1", [(9.2, 9.2, 14.9, 10.4), (9.2, 10.4, 10.4, 16.5)], "balcon", clos=False),
    ],
    "portes": [
        ("RDC", 7.5, 5.0, "h", 0.9),    # porte d'entree (blindee)
        ("RDC", 6.3, 7.0, "h", 0.7),    # hall -> WC visiteurs
        ("RDC", 5.6, 8.8, "v", 0.7),    # hall -> palier de depart de l'escalier
        ("RDC", 6.8, 9.2, "h", 1.6),    # hall -> salon
        ("RDC", 8.0, 7.8, "v", 1.2),    # hall -> salle a manger
        ("RDC", 8.6, 9.2, "h", 1.0),    # salle a manger <-> salon
        ("RDC", 10.4, 9.2, "h", 2.0),   # salle a manger -> galerie / patio
        ("RDC", 11.6, 7.0, "v", 0.9),   # salle a manger -> cuisine
        ("RDC", 13.2, 9.2, "h", 0.9),   # cuisine -> galerie
        ("RDC", 14.9, 7.0, "v", 0.9),   # cuisine -> cuisine africaine
        ("RDC", 17.2, 5.0, "h", 1.2),   # cuisine africaine -> preau / livraisons (Nord)
        ("RDC", 16.7, 8.6, "h", 0.8),   # cuisine africaine -> buanderie
        ("RDC", 18.5, 10.1, "v", 0.9),  # buanderie -> sechoir (passage Est)
        ("RDC", 18.5, 13.2, "v", 0.8),  # chambre nounou -> passage Est (porte independante)
        ("RDC", 16.7, 14.9, "h", 0.7),  # chambre nounou -> SE
        ("RDC", 9.2, 13.0, "v", 4.0),   # salon -> galerie / patio (baies)
        ("RDC", 6.2, 16.5, "h", 2.4),   # salon -> passage Sud
        ("RDC", 3.2, 13.0, "v", 2.4),   # salon -> jardin Ouest
        ("RDC", 5.6, 2.7, "h", 0.8),    # guerite
        ("R+1", 5.6, 8.8, "v", 0.7),    # escalier (arrivee) -> palier
        ("R+1", 8.0, 7.8, "v", 1.2),    # palier -> salon familial
        ("R+1", 10.4, 9.2, "h", 1.8),   # salon familial -> coursive
        ("R+1", 7.1, 9.2, "h", 0.9),    # palier -> dressing (suite)
        ("R+1", 6.2, 10.7, "v", 0.8),   # dressing -> SdB
        ("R+1", 7.7, 12.2, "h", 0.9),   # dressing -> chambre
        ("R+1", 9.2, 14.3, "v", 1.8),   # chambre parentale -> coursive
        ("R+1", 12.5, 9.2, "h", 0.9),   # coursive -> chambre 2
        ("R+1", 13.4, 6.2, "v", 0.7),   # chambre 2 -> SE
        ("R+1", 14.9, 9.8, "v", 0.9),   # coursive -> chambre 3
        ("R+1", 16.7, 12.2, "h", 0.7),  # chambre 3 -> SE
    ],
    "toiture": ("Toiture bac acier isolé à faible pente vers le patio, débords de 1,2 m sur la coursive ; "
                "aile de service sous toiture basse, conduit d'extraction de la cuisine africaine en toiture"),
}

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
    ("Parking, allée et aire de livraison pavés (pavés drainants)", "m2", 85_000,
     "Villa Cacao 6 - patio (assimilé)", {"A": 65, "B": 65, "C": 60, "L": 75}, True),
    ("Jardins plantés (terre végétale, gazon, arbres d'ombrage)", "m2", 20_000, "Les Flamboyants - jardins",
     {"A": 100, "B": 85, "C": 60, "L": 45}, True),
    ("Bâche à eau + surpresseur", "ens", 4_047_076, "Pavillon Akpo 2022 - bâche + surpresseur",
     {"A": 1, "B": 1, "C": 1, "L": 1}, True),
    ("Réfection clôture existante + portail coulissant + portillon", "ens", 3_000_000, "Prix de marché (hypothèse)",
     {"A": 1, "B": 1, "C": 1, "L": 1}, False),
    ("Mur séparatif villa / locatif (h 2,5 m) + claustras de la cour de service", "ml", 60_000,
     "Prix de marché (hypothèse)", {"A": 28, "B": 28, "C": 32, "L": 0}, False),
    ("Assainissement autonome (fosse + puisard) + branchements CIE / SODECI", "ens", 3_500_000,
     "Prix de marché (hypothèse)", {"A": 1, "B": 1, "C": 1, "L": 1.5}, False),
    ("Traitement anti-termites du sol + remblai de plateforme", "m2", 8_000, "Prix de marché (hypothèse)",
     {"A": 125, "B": 150, "C": 150, "L": 145}, False),
    ("Grilles de défense RDC et étage + moustiquaires", "m2", 45_000, "Prix de marché (hypothèse)",
     {"A": 70, "B": 70, "C": 70, "L": 30}, False),
    ("Chauffe-eau solaires + attentes climatisation (par logement)", "u", 900_000, "Prix de marché (hypothèse)",
     {"A": 2.5, "B": 2.5, "C": 2.5, "L": 6}, False),
    ("Cuisine africaine : hotte d'extraction, évier double bac, cage à bouteilles de gaz", "ens", 900_000,
     "Prix de marché (hypothèse)", {"A": 1, "B": 1, "C": 1, "L": 0}, False),
]

PLUS_VALUES = [
    ("Menuiseries bois persiennées (jalousies) sur séjour et chambres", "m2", 120_000, "Prix de marché (hypothèse)",
     {"A": 30, "B": 28, "C": 34, "L": 0}, False),
    ("Claustras en terre cuite / BTC ajourée (cour de service, façades Ouest, coursive)", "m2", 30_000,
     "Prix de marché (hypothèse)", {"A": 35, "B": 35, "C": 40, "L": 60}, False),
    ("Brise-soleil à lames (façades Ouest)", "m2", 60_000, "Prix de marché (hypothèse)",
     {"A": 14, "B": 14, "C": 10, "L": 12}, False),
    ("Débords de toiture et casquettes (hors clos)", "m2", 60_000, "Prix de marché (hypothèse)",
     {"A": 50, "B": 55, "C": 45, "L": 0}, False),
    ("Patio : arbre d'ombrage, massifs, bassin et éclairage", "ens", 3_000_000, "Prix de marché (hypothèse)",
     {"A": 0, "B": 0, "C": 1, "L": 0}, False),
    ("Moins-value murs BTC (vs agglos enduits 2 faces)", "m2", -5_000, "Prix de marché (hypothèse)",
     {"A": 250, "B": 270, "C": 290, "L": 320}, False),
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
                               and r["nom"] != "Guérite + WC gardien"), 2) + round(sum(
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
