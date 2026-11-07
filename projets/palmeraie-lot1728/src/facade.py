"""Facades, patio et toit-terrasse de l'option C (markup du client du 07-11-2026) et du locatif en duplex.

Ecriture : Palinda Kannangara Architects (Capitude : Casa Lineal, Casa Estudio) pour la matiere ;
double peau Nord en deux variantes tirees de Capitude :
  V1 - brique de terre cuite semi-perforee (Casa Estudio : « brique a perforations aleatoires a l'exterieur,
       lames de verre reglables a l'interieur ») ;
  V2 - resille de beton triangulee (Typologie urbaine 8 : « claustra en resille triangulee en nu exterieur,
       devant une loggia filante »).
Limite : les images des planches ne sont pas consultees (bucket prive « plans ») ; la lecture repose sur les
donnees textuelles et les legendes des details de la base.

Cotes en metres, repere du plan (x vers l'Est, y vers le Sud) ; z depuis le plancher du niveau
(RDC +0,45 ; R+1 +3,75 ; toit +6,85).
"""

REFERENCE = {
    "cle": "ref-casa-lineal, ref-casa-estudio, it8-typologie-urbaine-8",
    "nom": "Palinda Kannangara Architects : Casa Lineal et Casa Estudio (Sri Lanka)",
    "pourquoi": ("Deux maisons tropicales humides sur petites parcelles, organisées autour d’un patio planté, comme "
                 "l’option C. Leur matière (béton brut coffré planches, moellons, brique ajourée, bois, ciment poli) se "
                 "trouve à Abidjan et vieillit bien sous la pluie. Climat proche : Colombo est à 7° N, Abidjan à 5° N, "
                 "mêmes moussons et mêmes pluies d’orage."),
    "repris": [
        ("Double peau Nord semi-perforée", "Devant la loggia-rangement de 1,2 m de l’étage, sur toute la façade sur rue ; deux variantes (brique, résille béton)"),
        ("Béton brut coffré planches", "Nez de dalle, corniches à goutte d’eau, édicule d’escalier"),
        ("Moellons de pierre", "Rez-de-chaussée sur les deux rues, guérite, socle de la clôture (Casa Lineal)"),
        ("Toit habité", "Toit-terrasse sous pergola bois, jardinière continue de firecracker plants sur la façade Nord (Casa Estudio : toiture-jardin habitée)"),
        ("Patio et galerie", "Galerie vitrée de l’étage sur le patio, écrans en lattes de bois, bio-bassin au pied de l’arbre (Casa Lineal)"),
        ("Jardin d’entrée, bassin, séjour", "Bio-bassin devant le coulissant du salon dans la bande Ouest (séquence de Casa Lineal)"),
        ("Limites végétales", "Mur végétalisé en fond de parcelle, clôture en brique ajourée : la maison plonge dans la verdure"),
    ],
    "complements": [
        ("Typologie urbaine 8", "Résille de béton triangulée devant une loggia filante (variante 2 de la double peau)"),
        ("CDD Cotonou", "Claustra devant la cage d’escalier : la lanterne de l’angle des deux rues"),
    ],
}

# Ouvertures explicites par facade : (niveau, sens, ligne, a, b, z0, z1, type) ; type : baie | fenetre | porte | jour | claustra
# Regles : axes verticaux communs RDC / R+1 (Nord : 7,5 / 11,75 / 14,5 / 17,25 ; Ouest : 7,8 / 12,5 / 15,4) ;
# linteaux a 2,40 m ; alleges 1,00 m (fenetres), 1,80 m (jours hauts), 0 (portes et baies).
OUVERTURES = [
    # --- Nord (rue, y = 5,7, derriere le passage couvert et la loggia) ---
    ("RDC", "h", 5.7, 6.9, 8.1, 0.0, 2.4, "porte"),        # entree pivotante, axe 7,5
    ("RDC", "h", 5.7, 11.05, 12.45, 1.0, 2.4, "fenetre"),  # SAM, axe 11,75
    ("RDC", "h", 5.7, 13.75, 15.25, 1.0, 2.4, "fenetre"),  # cuisine, axe 14,5
    ("RDC", "h", 5.7, 16.65, 17.85, 0.0, 2.4, "porte"),    # cuisine africaine -> preau, axe 17,25
    ("R+1", "h", 5.7, 6.7, 8.3, 0.0, 2.4, "baie"),         # salon familial -> loggia, axe 7,5
    ("R+1", "h", 5.7, 11.05, 12.45, 0.0, 2.4, "baie"),     # chambre 1 -> loggia, axe 11,75
    ("R+1", "h", 5.7, 14.15, 14.85, 1.8, 2.4, "jour"),     # SE ch.1, axe 14,5
    ("R+1", "h", 5.7, 16.55, 17.95, 0.0, 2.4, "baie"),     # chambre 2 -> loggia, axe 17,25
    # --- Ouest (rue, x = 3,5) ---
    ("RDC", "v", 3.5, 6.0, 9.6, 0.3, 3.0, "claustra"),     # escalier : lanterne en brique ajouree
    ("RDC", "v", 3.5, 10.2, 10.9, 1.8, 2.4, "jour"),       # WC visiteurs
    ("RDC", "v", 3.5, 11.8, 13.2, 1.0, 2.4, "fenetre"),    # salon, axe 12,5
    ("RDC", "v", 3.5, 14.2, 16.6, 0.0, 2.4, "baie"),       # salon -> bio-bassin, axe 15,4
    ("R+1", "v", 3.5, 6.0, 9.6, 0.3, 2.8, "claustra"),
    ("R+1", "v", 3.5, 10.2, 10.9, 1.8, 2.4, "jour"),       # lingerie
    ("R+1", "v", 3.5, 11.8, 13.2, 1.8, 2.4, "jour"),       # SdB parentale, axe 12,5
    ("R+1", "v", 3.5, 14.2, 16.6, 0.0, 2.4, "baie"),       # chambre principale -> jardiniere Ouest, axe 15,4
    ("TOIT", "v", 3.5, 6.0, 9.6, 0.3, 2.4, "claustra"),    # edicule d'escalier
    # --- Sud (passage de 1 m et mur vegetalise, y = 17,0) ---
    ("RDC", "h", 17.0, 5.0, 7.4, 1.0, 2.4, "fenetre"),     # salon, vue sur le mur vegetalise
    ("RDC", "h", 17.0, 16.5, 18.0, 1.0, 2.4, "fenetre"),   # chambre nounou
    ("R+1", "h", 17.0, 5.0, 7.4, 1.8, 2.4, "jour"),        # chambre principale (tete de lit), jour haut
    # --- Est (limite a 1 m, x = 19,0) : jours hauts ---
    ("RDC", "v", 19.0, 6.5, 8.0, 1.8, 2.4, "jour"),        # cuisine africaine (fumees)
    ("RDC", "v", 19.0, 10.0, 10.8, 0.0, 2.4, "porte"),     # buanderie -> passage Est
    ("RDC", "v", 19.0, 11.8, 12.6, 1.8, 2.4, "jour"),      # bureau
    ("RDC", "v", 19.0, 13.5, 14.3, 1.8, 2.4, "jour"),      # SE nounou
    ("RDC", "v", 19.0, 15.4, 16.2, 0.0, 2.4, "porte"),     # nounou -> passage Est
    ("R+1", "v", 19.0, 6.5, 8.0, 1.8, 2.4, "jour"),        # chambre 2, axe de la cuisine africaine
    # --- Patio ---
    ("RDC", "v", 10.0, 12.1, 16.1, 0.0, 2.6, "baie"),      # salon -> terrasse et patio
    ("RDC", "h", 11.2, 10.55, 12.95, 0.0, 2.6, "baie"),    # SAM -> terrasse, axe 11,75
    ("RDC", "h", 11.2, 14.05, 14.95, 0.0, 2.4, "porte"),   # cuisine -> terrasse
    ("RDC", "v", 15.5, 11.75, 12.65, 0.0, 2.4, "porte"),   # bureau -> terrasse
    ("RDC", "v", 15.5, 13.6, 14.2, 1.8, 2.4, "jour"),      # SE nounou
    ("RDC", "v", 15.5, 15.2, 16.6, 1.0, 2.4, "fenetre"),   # chambre nounou sur le patio (ecran)
    ("R+1", "h", 11.2, 10.2, 15.3, 0.0, 2.6, "baie"),      # galerie vitree sur le patio
    ("R+1", "v", 10.0, 14.6, 16.2, 1.0, 2.4, "fenetre"),   # chambre principale sur le patio
    ("R+1", "h", 11.2, 16.5, 18.0, 1.0, 2.4, "fenetre"),   # chambre 2 sur la toiture de l'aile Est
]

# Niveaux
Z = {"RDC": 0.45, "R+1": 3.75, "TOIT": 6.85}
TOIT_Z = 6.85              # dessus de la dalle haute de l'etage (toit-terrasse)
ACROTERE = 1.0             # garde-corps maconne des toits-terrasses
PERGOLA_H = 2.7            # sous-face des poutres de la pergola
# Pergola sur le L (x0, y0, x1, y1) et poteaux sur la trame
PERGOLA = [(6.5, 5.7, 19.0, 11.2), (3.5, 11.2, 10.0, 17.0)]
POTEAUX = [(x, y) for x in (6.5, 10.0, 13.5, 15.5, 19.0) for y in (5.7, 11.2)] + \
          [(x, y) for x in (3.5, 6.5, 10.0) for y in (14.0, 17.0)]
EDICULE = (3.5, 5.7, 6.5, 9.9, 2.6)        # cage d'escalier couverte au niveau toit
JARDINIERE = (3.5, 4.5, 19.0, 5.3, 0.6)    # jardiniere continue sur la loggia (firecracker plants)
# Double peau Nord : plan exterieur, de l'allege du R+1 au sommet de la jardiniere
DOUBLE_PEAU = (3.5, 4.36, 19.0, 4.5, 3.75, 7.45)
DP_ALLEGE = 1.1                             # partie pleine (garde-corps, intimite) au-dessus du plancher
DP_AXES = [7.5, 11.75, 14.5, 17.25]         # perforations denses / modules ouverts devant les baies
VARIANTES = {
    "V1": ("Brique de terre cuite semi-perforée", "ref-casa-estudio",
           "Allège pleine de 1,10 m, puis perforations aléatoires plus serrées dans l’axe des baies ; brique locale "
           "de 22 × 10,5 × 6 cm posée en panneresse, joints creux. Laisse passer l’air et la lumière, cache la loggia."),
    "V2": ("Résille de béton triangulée", "it8-typologie-urbaine-8",
           "Allège pleine de 1,10 m en béton brut, puis résille préfabriquée en triangles de 1,0 m sur des montants "
           "alignés sur les axes des baies. Plus ouverte, plus graphique ; ombres portées très dessinées."),
}
# Ecrans en lattes de bois (niveau, sens, ligne, a, b, z0, z1)
ECRANS = [
    ("R+1", "h", 17.0, 4.6, 7.8, 0.0, 2.6),     # chambre principale (Sud)
    ("RDC", "v", 15.5, 15.0, 16.8, 0.0, 2.6),   # chambre nounou sur le patio
]
ECRANS_GALERIE = [(10.2, 11.8), (13.7, 15.3)]   # galerie de l'etage, cote patio
BIO_BASSINS = [(0.9, 11.9, 2.9, 16.7),           # devant le coulissant du salon (bande Ouest)
               (10.6, 14.3, 12.8, 15.6)]         # patio, au pied de l'arbre
ARBRE_PATIO = (13.6, 16.0)
MUR_VEGETAL = (0.0, 17.82, 20.0, 18.0, 3.0)      # en limite villa / locatif
TOITURE_VEGETALE = [(15.5, 11.2, 19.0, 17.0), (10.0, 11.2, 15.5, 13.6)]   # aile Est et terrasse couverte
CLAUSTRAS = [(16.5, 0.2, 19.8, 0.34, 0.0, 2.2)]   # sechoir, face Nord
CLOTURE_SOCLE = 1.0
CLOTURE_H = 2.2
RUES = [("h", 5.7), ("v", 3.5)]

# Locatif : ouvertures par maison (x0 = origine de la maison)
def ouvertures_maison(x0, premiere):
    o = [
        ("RDC", "h", 30.0, x0 + 0.8, x0 + 1.8, 0.0, 2.4, "porte"),
        ("RDC", "h", 30.0, x0 + 3.2, x0 + 4.6, 1.0, 2.4, "fenetre"),    # cuisine
        ("RDC", "h", 30.0, x0 + 4.8, x0 + 5.6, 0.0, 2.4, "porte"),
        ("RDC", "h", 21.0, x0 + 1.2, x0 + 4.8, 0.0, 2.6, "baie"),       # sejour -> jardin
        ("R+1", "h", 21.0, x0 + 0.7, x0 + 2.3, 0.9, 2.4, "fenetre"),    # chambre 1
        ("R+1", "h", 21.0, x0 + 3.7, x0 + 5.3, 0.9, 2.4, "fenetre"),    # chambre 2
        ("R+1", "h", 30.0, x0 + 0.8, x0 + 1.8, 0.9, 2.4, "fenetre"),    # palier
        ("R+1", "h", 30.0, x0 + 4.5, x0 + 5.3, 1.8, 2.4, "jour"),       # SE
    ]
    if premiere:
        o += [("RDC", "v", 2.0, 22.5, 25.0, 1.0, 2.4, "fenetre"), ("R+1", "v", 2.0, 22.8, 24.8, 0.9, 2.4, "fenetre")]
    return o


def resume():
    return [f"{a} : {b}" for a, b in REFERENCE["repris"]]
