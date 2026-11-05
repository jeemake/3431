"""Ecriture des facades et du patio de l'option C, d'apres les references Capitude de Palinda Kannangara
Architects (Sri Lanka) : Casa Lineal (Battaramulla) et Casa Estudio.

Le concept du patio central de l'option C est conserve tel quel (patio plante a ciel ouvert, terrasse couverte,
passerelle bois a l'etage, claustra haute au Sud). La reference change son traitement et l'aspect du batiment.

Ce que disent les fiches Capitude (projets, motifs, pieces, liaisons, legendes des planches) :
  Casa Lineal : beton, murs en moellons de pierre, ciment poli, bois de jacquier de recuperation ; patio central
    plante sous lanterneau, franchi a l'etage par des passerelles bois ; bio-bassin entre le jardin d'entree et le
    sejour vitre ; ecrans bois et stores bambou ; toiture vegetalisee, jardinieres engazonnees en rive.
    Sequence : jardin d'entree -> bio-bassin -> sejour -> escalier -> SAM -> patio ; SAM -> cuisine -> cour de
    cuisine -> chambre de service ; etage : escalier -> salon TV -> chambre parentale ; salon TV -> passerelles.
  Casa Estudio : facade sur rue en double peau, brique a perforations aleatoires a l'exterieur, lames de verre
    reglables a l'interieur ; beton apparent coffre en planches de bois local ; corniches beton a goutte d'eau ;
    jardinieres de toiture ; parking en sol drainant prolongeant un jardin de pluie.
Limite : les images des planches ne sont pas consultees (stockage prive) ; la lecture repose sur les donnees
textuelles et les legendes de details de la base.

Toutes les cotes sont en metres, repere du plan (x vers l'Est, y vers le Sud) ; z depuis le niveau du plancher
du niveau concerne (RDC +0,45 ; R+1 +3,75).
"""

REFERENCE = {
    "cle": "ref-casa-lineal, ref-casa-estudio",
    "nom": "Palinda Kannangara Architects : Casa Lineal et Casa Estudio (Sri Lanka)",
    "pourquoi": ("Deux maisons tropicales humides sur petites parcelles, organisées autour d’un patio planté et "
                 "d’une passerelle bois, comme l’option C. Leur matière (béton brut coffré planches, moellons, brique "
                 "ajourée, bois, ciment poli) se trouve à Abidjan et vieillit bien sous la pluie. Climat proche : "
                 "Colombo est à 7° N, Abidjan à 5° N, mêmes moussons et mêmes pluies d’orage."),
    "repris": [
        ("Double peau en brique ajourée", "Loggia filante de 0,9 m à l’étage Nord derrière un mur de brique à perforations aléatoires (Casa Estudio), lanterne d’escalier et balcon Ouest dans la même brique"),
        ("Béton brut coffré planches", "Nez de dalle, corniches à goutte d’eau, porche et casquettes"),
        ("Moellons de pierre", "Rez-de-chaussée sur les deux rues et socle de la clôture (Casa Lineal)"),
        ("Patio : passerelle sous lanterneau", "Lanterneau vitré ventilé au-dessus de la passerelle, écrans en lattes de bois, bio-bassin agrandi au pied de l’arbre"),
        ("Jardin d’entrée, bassin, séjour", "Bio-bassin devant le coulissant du salon dans la bande Ouest, comme la séquence d’arrivée de Casa Lineal"),
        ("Toiture végétalisée", "Toiture extensive sur l’étage, jardinières engazonnées en rive (Casa Lineal, Casa Estudio)"),
        ("Écrans bois et stores bambou", "Écrans coulissants en lattes devant les fenêtres Est et Sud, stores bambou sous les débords Ouest"),
    ],
    "complements": [
        ("ABYA 2 (Assinie)", "Débords de dalle généreux pour l’ombre et la pluie, conservés de la version précédente"),
        ("CDD Cotonou", "Claustra devant la cage d’escalier, qui devient la lanterne de l’angle des deux rues"),
    ],
}

# Ouvertures explicites par facade exterieure. Elles remplacent la regle automatique des rendus.
# (niveau, sens, ligne, a, b, z0, z1, type)   type : baie | fenetre | porte | jour | claustra
OUVERTURES = [
    # Regles d'alignement : axes verticaux communs RDC / R+1 ; linteaux a 2,40 m partout (porte, fenetre, baie, jour) ;
    # alleges a 1,00 m (fenetres), 1,80 m (jours hauts), 0,00 (baies et portes).
    # --- Facade Nord (rue, y = 5,0) : axes A 3,4-5,4 (claustra) | B 8,3-10,1 | C 11,8-13,2 ---
    ("RDC", "h", 5.0, 3.4, 5.4, 0.3, 3.0, "claustra"),     # A : escalier, lanterne en claustra BTC
    ("RDC", "h", 5.0, 5.95, 6.65, 1.8, 2.4, "jour"),       # WC visiteurs
    ("RDC", "h", 5.0, 7.05, 7.95, 0.0, 2.4, "porte"),      # entree (porte pivotante bois)
    ("RDC", "h", 5.0, 8.3, 10.1, 1.0, 2.4, "fenetre"),     # B : SAM
    ("RDC", "h", 5.0, 11.8, 13.2, 1.0, 2.4, "fenetre"),    # C : cuisine (plan de travail sous la fenetre)
    ("RDC", "h", 5.0, 13.8, 14.5, 1.8, 2.4, "jour"),       # cuisine, sous le jour de la SE ch.2 (ventilation)
    ("RDC", "h", 5.0, 15.4, 16.2, 1.8, 2.4, "jour"),       # cuisine africaine (sous le preau)
    ("RDC", "h", 5.0, 16.6, 17.8, 0.0, 2.4, "porte"),      # cuisine africaine -> preau
    ("R+1", "h", 5.0, 3.4, 5.4, 0.3, 2.8, "claustra"),     # A
    ("R+1", "h", 5.0, 5.95, 6.65, 1.8, 2.4, "jour"),       # salon familial, au-dessus du jour du WC
    ("R+1", "h", 5.0, 8.3, 10.1, 0.0, 2.4, "baie"),        # B : salon familial, persiennes + barreaudage
    ("R+1", "h", 5.0, 11.8, 13.2, 0.0, 2.4, "baie"),       # C : chambre 2, persiennes + barreaudage
    ("R+1", "h", 5.0, 13.8, 14.5, 1.8, 2.4, "jour"),       # SE chambre 2
    ("R+1", "h", 8.6, 16.6, 17.8, 1.0, 2.4, "fenetre"),    # chambre 3 au Nord, axe de la porte de la cuisine africaine
    # --- Facade Ouest (rue, x = 3,2) : axes A 5,3-9,2 (claustra) | B 10,2-11,5 | C 12,6-15,8 ---
    ("RDC", "v", 3.2, 5.3, 9.2, 0.3, 3.0, "claustra"),     # A : escalier
    ("RDC", "v", 3.2, 10.2, 11.5, 1.0, 2.4, "fenetre"),    # B : salon
    ("RDC", "v", 3.2, 12.6, 15.8, 0.0, 2.4, "baie"),       # C : salon, coulissant 3,2 m sous le balcon
    ("R+1", "v", 3.2, 5.3, 9.2, 0.3, 2.8, "claustra"),     # A
    ("R+1", "v", 3.2, 10.2, 11.5, 1.8, 2.4, "jour"),       # B : SdB parentale
    ("R+1", "v", 3.2, 12.6, 15.8, 0.0, 2.4, "baie"),       # C : chambre parentale -> balcon (derriere claustra)
    # --- Facade Est (limite a 1,5 m, x = 18,5) : jours hauts a l'etage dans l'axe des ouvertures du RDC ---
    ("RDC", "v", 18.5, 6.0, 7.2, 1.8, 2.4, "jour"),        # cuisine africaine (fumees)
    ("RDC", "v", 18.5, 9.65, 10.55, 0.0, 2.4, "porte"),    # buanderie -> sechoir
    ("RDC", "v", 18.5, 12.0, 12.8, 1.8, 2.4, "jour"),      # SE nounou
    ("RDC", "v", 18.5, 14.4, 15.2, 0.0, 2.4, "porte"),     # nounou -> passage Est
    ("R+1", "v", 18.5, 9.65, 10.55, 1.8, 2.4, "jour"),     # chambre 3, axe de la porte de la buanderie
    ("R+1", "v", 18.5, 12.0, 12.8, 1.8, 2.4, "jour"),      # chambre 3, axe du jour de la SE nounou
    # --- Facade Sud (jardin arriere, y = 16,5) : axe 4,4-8,4 commun salon / chambre parentale ---
    ("RDC", "h", 16.5, 4.4, 8.4, 0.0, 2.4, "baie"),        # salon -> jardin Sud-Ouest
    ("RDC", "h", 16.5, 15.9, 17.5, 1.0, 2.4, "fenetre"),   # chambre nounou
    ("R+1", "h", 16.5, 4.4, 8.4, 1.0, 2.4, "fenetre"),     # chambre parentale, persiennes
    ("R+1", "h", 13.6, 16.6, 17.8, 1.8, 2.4, "jour"),      # SE chambre 3, axe de la fenetre de la chambre 3
]

# Toiture : dalle en beton brut debordante (corniche a goutte d'eau), vegetalisee en partie courante
TOIT_Z = 7.07
TOIT_EP = 0.18
TOIT = [
    (3.2, 5.0, 14.9, 9.2, dict(n=1.2, w=1.6, e=0.0, s=0.0)),
    (3.2, 9.2, 9.2, 16.5, dict(n=0.0, w=1.6, e=0.0, s=0.8)),
    (14.9, 8.6, 18.5, 13.6, dict(n=0.6, w=0.0, e=0.6, s=0.6)),
]
TOITURE_VEGETALE = [(3.6, 5.3, 14.6, 8.9), (3.6, 9.2, 8.9, 16.2), (15.2, 8.9, 18.2, 13.3)]   # substrat 15 cm
# Lanterneau vitre ventile au-dessus de la passerelle (Casa Lineal) : verre feuillete sur chassis acier, sur rehausse
LANTERNEAU = (9.2, 9.2, 14.9, 10.4, 7.12)
# Casquette du RDC au Nord = plancher de la loggia de l'etage ; porche d'entree
CASQUETTES = [
    (5.6, 4.1, 14.9, 5.0, 3.75),     # 0,9 m : loggia R+1 au-dessus de la SAM et de la cuisine
    (6.2, 3.3, 8.8, 4.1, 3.75),      # porche d'entree, 1,7 m au total
]
# Double peau en brique a perforations aleatoires (x0, y0, x1, y1, z0, z1) - z absolus
DOUBLE_PEAU = [
    (5.6, 4.1, 14.9, 4.22, 3.75, 6.85),    # loggia Nord de l'etage (Casa Estudio) ; perforations denses au droit des baies
    (2.0, 12.2, 2.12, 16.5, 3.75, 6.85),   # balcon Ouest de la suite
]
# Zones de perforations denses de la loggia Nord (x), dans l'axe des baies B et C et des jours
DENSE_NORD = [(5.95, 6.65), (8.3, 10.1), (11.8, 13.2), (13.8, 14.5)]
# Ecrans coulissants en lattes de bois verticales (niveau, sens, ligne, a, b, z0, z1)
ECRANS = [
    ("R+1", "h", 8.6, 15.4, 16.6, 1.0, 2.4),   # chambre 3 (vantail tire)
    ("R+1", "h", 16.5, 3.3, 4.4, 1.0, 2.4),    # chambre parentale (Sud)
]
# Ecrans bois de la passerelle (x0, x1) sur la rive Sud, au-dessus du garde-corps
ECRANS_PASSERELLE = [(9.3, 10.9), (13.2, 14.8)]
# Bio-bassins (x0, y0, x1, y1)
BIO_BASSINS = [(0.8, 11.6, 2.6, 16.0),       # devant le coulissant du salon, bande Ouest
               (9.6, 11.8, 12.4, 13.2)]      # patio, au pied de l'arbre, alimente par les eaux pluviales
# Claustras en brique ajouree autonomes (x0, y0, x1, y1, z0, z1)
CLAUSTRAS = [
    (18.5, 2.5, 20.0, 2.64, 0.0, 2.9),        # aile de service : face Nord du sechoir
    (19.86, 2.6, 20.0, 8.6, 0.0, 2.9),        # sechoir, en limite Est
]
# Cloture sur rue : socle en moellons 1,0 m + brique ajouree 1,2 m ; portail et portillons en lames bois
CLOTURE_SOCLE = 1.0
CLOTURE_H = 2.2
# Materiaux des murs exterieurs : RDC sur rue en moellons, RDC sur patio et jardins en enduit a la chaux,
# etage en beton brut coffre planches
RUES = [("h", 5.0), ("v", 3.2)]


def resume():
    """Texte court pour le dossier."""
    return [f"{a} : {b}" for a, b in REFERENCE["repris"]]
