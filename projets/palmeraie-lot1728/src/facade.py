"""Facades, patio et toit-terrasse de l'option C (markup du client du 10-11-2026) et du locatif en 2 duplex.

Facade Nord en deux types, d'apres les deux images de reference fournies par le client (references de style,
pas des projets a copier) :
  V1 - claustra de lames de bois verticales posees en damier (double peau semi-ouverte devant la loggia), dalle
       de plancher a nez mince, toiture plate tres mince a grand debord au-dessus du toit-terrasse ;
  V2 - bardage bois a lames verticales et brise-soleil pivotants dans l'axe des baies, debords profonds a sous-face
       en lames de bois (auvent bas sur la rue et toit en croupe a faible pente au-dessus du toit-terrasse),
       cloture en moellons, claustra de blocs de beton ajoures et portail en lames de bois.
Le patio, le plan en L, les axes des baies et les niveaux sont communs aux deux types.

Cotes en metres, repere du plan (x vers l'Est, y vers le Sud) ; z depuis le plancher du niveau
(RDC +-0,00 ; R+1 +3,30 ; toit +6,60 ; couverture du toit-terrasse +9,00, cotes du client).
"""

REFERENCE = {
    "cle": "images de reference du client, ref-casa-lineal (patio)",
    "nom": "Deux images de référence du client, patio d'après Palinda Kannangara (Casa Lineal)",
    "pourquoi": ("Le client a fourni deux images de référence pour la façade : un claustra de lames de bois en damier "
                 "sous une toiture mince à grand débord, et une maison à bardage bois, débords profonds, claustra de béton "
                 "et moellons. Ce sont des références de style. Le patio planté reste celui de Casa Lineal."),
    "repris": [
        ("V1 · lames de bois en damier", "Double peau devant la loggia de l'étage, panneaux de lames verticales décalés d'un rang à l'autre ; toiture plate mince à grand débord à +9,00"),
        ("V2 · bardage bois et grands débords", "Bardage à lames verticales, brise-soleil pivotants dans l'axe des baies, auvent bas sur la rue et toit en croupe à sous-face bois"),
        ("Moellons et claustra béton", "Rez-de-chaussée sur rue, guérite et socle de clôture en moellons ; claustra de blocs de béton ajourés sur la clôture"),
        ("Toit habité", "Toit-terrasse couvert, jardinière continue de firecracker plants sur la façade Nord"),
        ("Patio", "Patio planté autour d'un frangipanier, galerie vitrée de l'étage, écrans en lattes de bois (Casa Lineal)"),
        ("Limites végétales", "Mur végétalisé en fond de parcelle, massifs tropicaux le long de la clôture : la maison plonge dans la verdure"),
    ],
    "complements": [],
}

# Ouvertures explicites par facade : (niveau, sens, ligne, a, b, z0, z1, type) ; type : baie | fenetre | porte | jour | claustra
# Regles : axes verticaux communs RDC / R+1 (Nord : 6,5 / 10,75 / 13,5 / 16,25 ; Ouest : 7,6 / 12,3 / 15,2) ;
# linteaux a 2,40 m ; alleges 1,00 m (fenetres), 1,80 m (jours hauts), 0 (portes et baies).
OUVERTURES = [
    # --- Nord (rue, y = 5,5, derriere le passage couvert et la loggia) ---
    ("RDC", "h", 5.5, 5.9, 7.1, 0.0, 2.4, "porte"),        # entree pivotante, axe 6,5
    ("RDC", "h", 5.5, 10.05, 11.45, 1.0, 2.4, "fenetre"),  # SAM, axe 10,75
    ("RDC", "h", 5.5, 12.9, 14.1, 1.0, 2.4, "fenetre"),    # cuisine, axe 13,5
    ("RDC", "h", 5.5, 15.65, 16.85, 0.0, 2.4, "porte"),    # cuisine africaine -> preau, axe 16,25
    ("R+1", "h", 5.5, 5.7, 7.3, 0.0, 2.4, "baie"),         # salon familial -> loggia, axe 6,5
    ("R+1", "h", 5.5, 10.05, 11.45, 0.0, 2.4, "baie"),     # chambre 1 -> loggia, axe 10,75
    ("R+1", "h", 5.5, 13.15, 13.85, 1.8, 2.4, "jour"),     # SE ch.1, axe 13,5
    ("R+1", "h", 5.5, 15.55, 16.95, 0.0, 2.4, "baie"),     # chambre 2 -> loggia, axe 16,25
    # --- Ouest (rue, x = 2,5) ---
    ("RDC", "v", 2.5, 5.8, 9.4, 0.3, 3.0, "claustra"),     # escalier : lanterne en claustra
    ("RDC", "v", 2.5, 10.0, 10.7, 1.8, 2.4, "jour"),       # WC visiteurs
    ("RDC", "v", 2.5, 11.6, 13.0, 1.0, 2.4, "fenetre"),    # salon, axe 12,3
    ("RDC", "v", 2.5, 14.0, 16.4, 0.0, 2.4, "baie"),       # salon -> jardin Ouest, axe 15,2
    ("R+1", "v", 2.5, 5.8, 9.4, 0.3, 2.8, "claustra"),
    ("R+1", "v", 2.5, 10.0, 10.7, 1.8, 2.4, "jour"),       # lingerie
    ("R+1", "v", 2.5, 11.6, 13.0, 1.8, 2.4, "jour"),       # SdB parentale, axe 12,3
    ("R+1", "v", 2.5, 14.0, 16.4, 0.0, 2.4, "baie"),       # chambre principale -> jardiniere Ouest, axe 15,2
    ("TOIT", "v", 2.5, 5.8, 9.4, 0.3, 2.0, "claustra"),    # edicule d'escalier
    # --- Sud (passage de 1,2 m et mur vegetalise, y = 16,8) ---
    ("RDC", "h", 16.8, 4.0, 6.4, 1.0, 2.4, "fenetre"),     # salon, vue sur le mur vegetalise
    ("RDC", "h", 16.8, 15.5, 17.0, 1.0, 2.4, "fenetre"),   # chambre nounou
    ("R+1", "h", 16.8, 4.0, 6.4, 1.8, 2.4, "jour"),        # chambre principale (tete de lit), jour haut
    # --- Est (passage de service de 2 m, x = 18,0) : jours hauts ---
    ("RDC", "v", 18.0, 6.3, 7.8, 1.8, 2.4, "jour"),        # cuisine africaine (fumees)
    ("RDC", "v", 18.0, 9.8, 10.6, 0.0, 2.4, "porte"),      # buanderie -> passage Est
    ("RDC", "v", 18.0, 11.6, 12.4, 1.8, 2.4, "jour"),      # bureau
    ("RDC", "v", 18.0, 13.3, 14.1, 1.8, 2.4, "jour"),      # SE nounou
    ("RDC", "v", 18.0, 15.2, 16.0, 0.0, 2.4, "porte"),     # nounou -> passage Est
    ("R+1", "v", 18.0, 6.3, 7.8, 1.8, 2.4, "jour"),        # chambre 2, axe de la cuisine africaine
    # --- Patio ---
    ("RDC", "v", 9.0, 11.9, 15.9, 0.0, 2.6, "baie"),       # salon -> terrasse et patio
    ("RDC", "h", 11.0, 9.55, 11.95, 0.0, 2.6, "baie"),     # SAM -> terrasse, axe 10,75
    ("RDC", "v", 14.5, 11.55, 12.45, 0.0, 2.4, "porte"),   # bureau -> terrasse
    ("RDC", "v", 14.5, 13.4, 14.0, 1.8, 2.4, "jour"),      # SE nounou
    ("RDC", "v", 14.5, 15.0, 16.4, 1.0, 2.4, "fenetre"),   # chambre nounou sur le patio (ecran)
    ("R+1", "h", 11.0, 9.2, 14.3, 0.0, 2.6, "baie"),       # galerie vitree sur le patio
    ("R+1", "v", 9.0, 14.4, 16.0, 1.0, 2.4, "fenetre"),    # chambre principale sur le patio
    ("R+1", "h", 11.0, 15.5, 17.0, 1.0, 2.4, "fenetre"),   # chambre 2 sur la toiture de l'aile Est
]

# Niveaux (cotes du client, markup de la coupe BB)
Z = {"RDC": 0.0, "R+1": 3.30, "TOIT": 6.60}
TOIT_Z = 6.60              # dessus de la dalle haute de l'etage (toit-terrasse)
COUV_Z = 9.00              # dessus de la couverture du toit-terrasse
ACROTERE = 1.0             # garde-corps maconne des toits-terrasses
PERGOLA_H = 2.4            # couverture a +9,00
# Emprise couverte du niveau haut (x0, y0, x1, y1) et poteaux sur la trame
PERGOLA = [(5.5, 5.5, 18.0, 11.0), (2.5, 11.0, 9.0, 16.8)]
POTEAUX = [(x, y) for x in (5.5, 9.0, 12.5, 14.5, 18.0) for y in (5.5, 11.0)] + \
          [(x, y) for x in (2.5, 5.5, 9.0) for y in (13.8, 16.8)]
EDICULE = (2.5, 5.5, 5.5, 9.7, 2.15)       # cage d'escalier au niveau toit, fermee sous la couverture
JARDINIERE = (2.5, 4.5, 18.0, 5.1, 0.6)    # jardiniere continue sur la loggia (firecracker plants)
# Double peau Nord : plan exterieur, de l'allege du R+1 au sommet de la jardiniere
DOUBLE_PEAU = (2.5, 4.36, 18.0, 4.5, 3.30, 7.20)
DP_ALLEGE = 1.1                             # partie pleine (garde-corps, intimite) au-dessus du plancher
DP_AXES = [6.5, 10.75, 13.5, 16.25]         # panneaux ouverts / brise-soleil dans l'axe des baies
# Couvertures du niveau haut : rectangles avec debords (x0, y0, x1, y1)
COUV_V1 = [(1.5, 3.5, 19.0, 12.0), (1.5, 12.0, 10.0, 17.6)]          # dalle mince, rive de 0,18 m
COUV_V2 = [(1.3, 3.3, 19.2, 12.2), (1.3, 12.2, 10.2, 17.7)]          # croupes a 15 degres, sous-face bois
AUVENT_V2 = (1.5, 2.9, 19.0, 4.5, 3.30)                              # auvent bas sur la rue (V2), sous-face bois
VARIANTES = {
    "V1": ("Claustra de lames de bois en damier", "image de référence 1 du client",
           "Panneaux de lames de bois dur verticales, décalés d’un rang à l’autre comme un damier, devant la loggia "
           "de l’étage ; nez de dalle mince ; toiture plate mince à grand débord au-dessus du toit-terrasse. La nuit, "
           "la façade devient une lanterne."),
    "V2": ("Bardage bois et grands débords", "image de référence 2 du client",
           "Bardage à lames verticales, brise-soleil pivotants dans l’axe des baies ; auvent bas et toit en croupe à "
           "sous-face en lames de bois ; clôture en moellons, claustra de blocs de béton ajourés et portail en lames."),
}
# Ecrans en lattes de bois (niveau, sens, ligne, a, b, z0, z1)
ECRANS = [
    ("R+1", "h", 16.8, 3.6, 6.8, 0.0, 2.6),     # chambre principale (Sud)
    ("RDC", "v", 14.5, 14.8, 16.6, 0.0, 2.6),   # chambre nounou sur le patio
]
ECRANS_GALERIE = [(9.2, 10.8), (12.7, 14.3)]    # galerie de l'etage, cote patio
BIO_BASSINS = []                                 # supprimes (markup du 10-11-2026)
ARBRE_PATIO = (12.6, 15.8)
MUR_VEGETAL = (0.0, 17.82, 20.0, 18.0, 3.5)      # en limite villa / locatif, h 3,50 m (vis-a-vis, demande du client)
TOITURE_VEGETALE = [(14.5, 11.0, 18.0, 16.8), (9.0, 11.0, 14.5, 13.4)]   # aile Est et terrasse couverte
CLAUSTRAS = [(14.5, 0.2, 18.0, 0.34, 0.0, 2.2)]   # sechoir, face Nord
CLOTURE_SOCLE = 1.0
CLOTURE_H = 2.2
RUES = [("h", 5.5), ("v", 2.5)]
STATIONNEMENT = (7.0, 0.2, 12.5, 4.5)            # 2 places (markup), portail coulissant de 5,5 m
PORTILLON = (6.0, 7.0)                           # portillon d'entree, dans l'axe de la porte (6,5)


# Trame de facade commune a la villa et aux duplex (harmonie demandee par le client) :
#  - horizontales : RDC +-0,00, nez de dalle +3,30 et +6,60, couverture +9,00 ; linteaux a 2,40 ; alleges 1,00 / 1,80 ;
#  - verticales : ouvertures de l'etage alignees sur celles du RDC, sur les axes de chaque batiment ;
#  - matieres : socle en moellons sur rue, etage enveloppe d'une meme peau (V1 lames en damier / V2 bardage et
#    brise-soleil), meme couverture (V1 dalle mince / V2 croupe a sous-face bois), memes poteaux acier noirs.
PEAU_VILLA = [   # (sens, ligne, a, b, cote exterieur, axes des baies)
    ("h", 4.5, 2.5, 18.0, -1, DP_AXES),          # Nord, devant la loggia (double peau)
    ("v", 2.5, 5.5, 13.6, -1, [7.6, 12.3]),      # Ouest, jusqu'a la jardiniere de la chambre principale
    ("h", 16.8, 2.5, 9.0, 1, [5.2]),             # Sud, chambre principale
    ("v", 18.0, 5.5, 11.0, 1, [7.05]),           # Est, chambre 2
]


def peau_maison(x0, premiere):
    p = [("h", 21.0, x0, x0 + 8.5, -1, [x0 + 1.8, x0 + 7.0]),
         ("h", 30.0, x0, x0 + 8.5, 1, [x0 + 1.0, x0 + 3.8, x0 + 7.75])]
    if premiere:
        p.append(("v", 3.0, 21.0, 30.0, -1, [23.4]))
    return p


def couv_maison(x0, premiere):
    a = x0 - 0.4 if premiere else x0 + 0.05
    b = x0 + 8.45 if premiere else min(19.9, x0 + 8.9)
    return (a, 20.4, b, 30.4)


# Locatif : ouvertures par maison (x0 = origine de la maison, largeur 8,5)
def ouvertures_maison(x0, premiere):
    o = [
        ("RDC", "h", 30.0, x0 + 0.5, x0 + 1.5, 0.0, 2.4, "porte"),
        ("RDC", "h", 30.0, x0 + 7.35, x0 + 8.15, 0.0, 2.4, "porte"),
        ("RDC", "h", 30.0, x0 + 2.6, x0 + 5.0, 1.8, 2.4, "jour"),     # escalier
        ("RDC", "h", 21.0, x0 + 0.4, x0 + 3.2, 0.0, 2.4, "baie"),     # sejour -> jardin, axe 1,8
        ("RDC", "h", 21.0, x0 + 5.8, x0 + 8.2, 0.0, 2.4, "baie"),     # coin repas -> jardin, axe 7,0
        ("R+1", "h", 21.0, x0 + 1.0, x0 + 2.6, 0.9, 2.4, "fenetre"),  # chambre 2, axe 1,8
        ("R+1", "h", 21.0, x0 + 5.8, x0 + 8.2, 0.0, 2.4, "baie"),     # chambre principale, axe 7,0
        ("R+1", "h", 30.0, x0 + 0.6, x0 + 1.4, 1.8, 2.4, "jour"),     # SE
        ("R+1", "h", 30.0, x0 + 2.6, x0 + 5.0, 0.9, 2.4, "fenetre"),  # escalier
        ("R+1", "h", 30.0, x0 + 7.2, x0 + 8.3, 1.8, 2.4, "jour"),     # SdB parentale, axe 7,75 (porte du cellier)
    ]
    if premiere:   # pignon sur la rue Ouest : axe 23,4 commun aux deux niveaux
        o += [("RDC", "v", 3.0, 22.6, 24.2, 1.0, 2.4, "fenetre"), ("R+1", "v", 3.0, 22.6, 24.2, 0.9, 2.4, "fenetre")]
    return o


def resume():
    return [f"{a} : {b}" for a, b in REFERENCE["repris"]]
