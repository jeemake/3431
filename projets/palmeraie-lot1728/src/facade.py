"""Ecriture des facades de l'option C, d'apres la reference Capitude ABYA 2 (Assinie, villa R+1).

Ce que l'on reprend d'ABYA 2 (fiche projet, planches 26-29 « Coupes », « Facades », « Vue depuis le jardin ») :
  - une toiture-ombriere : dalle plate mince qui deborde largement des parois (ABYA : 2 a 5 m, toiture +6,60) ;
  - des persiennes bois devant les baies de l'etage et des garde-corps a barreaudage ;
  - un claustra de briques ajourees pour tout ce qui est service (pavillon de service d'ABYA) ;
  - des sejours vitres toute hauteur sous les debords.
Complements tires de Capitude :
  - claustra devant la cage d'escalier (CDD Cotonou : « claustras devant les cages d'escalier et le hall ») ;
  - double peau sur la facade exposee a l'Ouest (Typologie urbaine 8 : loggia derriere claustra) ;
  - cloture sur rue en lames bois et portail en planches (House on Pali Hill : « ecran de lattes, portail en planches »).
Adaptation au lot 1728 : le rez-de-chaussee est en BTC apparents (terre du brief initial), l'etage en enduit
blanc casse, la toiture-ombriere en beton blanc ; bois = iroko ou teck local.

Toutes les cotes sont en metres, repere du plan (x vers l'Est, y vers le Sud) ; z depuis le niveau du plancher
du niveau concerne (RDC +0,45 ; R+1 +3,75).
"""

REFERENCE = {
    "cle": "abya-assinie",
    "nom": "ABYA 2, villa R+1, Assinie",
    "pourquoi": ("Seule villa R+1 ivoirienne de la base dont les façades sont documentées (4 élévations, coupes, "
                 "axonométrie, vues) ; même climat lagunaire ; mêmes hauteurs (étage +3,50 et toiture +6,60, contre "
                 "+3,75 et +6,85 ici) ; vocabulaire simple et économique : une dalle, des poteaux, des persiennes, "
                 "un claustra."),
    "repris": [
        ("Toiture-ombriere debordante", "Dalle plate mince, debord 1,4 m a l'Ouest, 1,2 m au Nord, 0,8 m a l'Est"),
        ("Persiennes bois coulissantes", "Devant les baies de l'etage au Nord et a l'Est (chambres 2 et 3, salon familial)"),
        ("Garde-corps a barreaudage", "Portes-fenetres de l'etage (chambre 2, salon familial)"),
        ("Claustra de briques ajourees", "Cage d'escalier (lanterne d'angle), aile de service, cloture sur rue"),
        ("Sejour vitre sous debord", "Baie coulissante 4,4 m du salon a l'Ouest sous la dalle du balcon"),
    ],
    "complements": [
        ("cdd", "Claustra devant la cage d'escalier"),
        ("it8-typologie-urbaine-8", "Double peau sur la facade Ouest : balcon de la suite derriere un claustra"),
        ("ref-pali-hill", "Portail et portillons en lames de bois, socle mineral sombre"),
    ],
}

# Ouvertures explicites par facade exterieure. Elles remplacent la regle automatique des rendus.
# (niveau, sens, ligne, a, b, z0, z1, type)   type : baie | fenetre | porte | jour | claustra
OUVERTURES = [
    # --- Facade Nord (rue, y = 5,0) ---
    ("RDC", "h", 5.0, 3.4, 5.4, 0.3, 3.0, "claustra"),     # escalier : lanterne en claustra BTC
    ("RDC", "h", 5.0, 5.95, 6.65, 1.8, 2.4, "jour"),       # WC visiteurs
    ("RDC", "h", 5.0, 7.05, 7.95, 0.0, 2.4, "porte"),      # entree (porte pivotante bois)
    ("RDC", "h", 5.0, 8.5, 11.1, 0.5, 2.4, "fenetre"),     # SAM : baie basse sur le jardin de devant
    ("RDC", "h", 5.0, 12.2, 14.3, 1.1, 2.4, "fenetre"),    # cuisine : au-dessus du plan de travail
    ("RDC", "h", 5.0, 15.2, 16.2, 1.8, 2.4, "jour"),       # cuisine africaine (sous le preau)
    ("RDC", "h", 5.0, 16.6, 17.8, 0.0, 2.2, "porte"),      # cuisine africaine -> preau
    ("R+1", "h", 5.0, 3.4, 5.4, 0.3, 2.8, "claustra"),
    ("R+1", "h", 5.0, 6.4, 9.6, 0.0, 2.4, "baie"),         # salon familial, persiennes + barreaudage
    ("R+1", "h", 5.0, 11.1, 12.7, 0.0, 2.4, "baie"),       # chambre 2, persiennes + barreaudage
    ("R+1", "h", 5.0, 13.8, 14.5, 1.8, 2.4, "jour"),       # SE chambre 2
    ("R+1", "h", 8.6, 15.9, 17.5, 0.9, 2.4, "fenetre"),    # chambre 3 au Nord, persiennes
    # --- Facade Ouest (rue, x = 3,2) ---
    ("RDC", "v", 3.2, 5.3, 9.2, 0.3, 3.0, "claustra"),     # escalier
    ("RDC", "v", 3.2, 11.2, 15.6, 0.0, 2.7, "baie"),       # salon : coulissant 4,4 m sous le balcon
    ("R+1", "v", 3.2, 5.3, 9.2, 0.3, 2.8, "claustra"),
    ("R+1", "v", 3.2, 10.2, 11.5, 1.8, 2.4, "jour"),       # SdB parentale
    ("R+1", "v", 3.2, 12.8, 15.9, 0.0, 2.6, "baie"),       # chambre parentale -> balcon (derriere claustra)
    # --- Facade Est (limite a 1,5 m, x = 18,5) : jours hauts seulement (vues droites) ---
    ("RDC", "v", 18.5, 9.65, 10.55, 0.0, 2.2, "porte"),    # buanderie -> sechoir
    ("RDC", "v", 18.5, 14.4, 15.2, 0.0, 2.2, "porte"),     # nounou -> passage Est
    ("RDC", "v", 18.5, 6.0, 7.2, 1.8, 2.4, "jour"),        # cuisine africaine (fumees)
    ("RDC", "v", 18.5, 12.0, 12.8, 1.8, 2.4, "jour"),      # SE nounou
    ("R+1", "v", 18.5, 9.8, 12.4, 1.8, 2.4, "jour"),       # chambre 3
    # --- Facade Sud (jardin arriere, y = 16,5) ---
    ("RDC", "h", 16.5, 4.4, 8.4, 0.0, 2.6, "baie"),        # salon -> jardin Sud-Ouest
    ("RDC", "h", 16.5, 15.9, 17.5, 0.9, 2.3, "fenetre"),   # chambre nounou
    ("R+1", "h", 16.5, 4.4, 8.0, 0.9, 2.4, "fenetre"),     # chambre parentale, persiennes
    ("R+1", "h", 13.6, 16.2, 17.2, 1.8, 2.4, "jour"),      # SE chambre 3
]

# Toiture-ombriere : rectangles des volumes R+1 + debords (N, W, E, S) ; face superieure a +7,07 (sous-face +6,85)
TOIT_Z = 7.07
TOIT_EP = 0.22
TOIT = [
    (3.2, 5.0, 14.9, 9.2, dict(n=1.2, w=1.6, e=0.0, s=0.0)),
    (3.2, 9.2, 9.2, 16.5, dict(n=0.0, w=1.6, e=0.0, s=1.0)),
    (14.9, 8.6, 18.5, 13.6, dict(n=0.6, w=0.0, e=0.8, s=0.6)),
    (9.2, 9.2, 14.9, 10.4, dict(n=0.0, w=0.0, e=0.0, s=0.6)),   # passerelle : debord sur le patio
]
# Casquette du RDC au Nord (dalle +3,75 prolongee) et porche d'entree
CASQUETTES = [
    (5.6, 4.1, 14.9, 5.0, 3.75),     # 0,9 m au-dessus de la SAM et de la cuisine
    (6.2, 3.3, 8.8, 4.1, 3.75),      # porche d'entree, 1,7 m au total
]
# Persiennes coulissantes : panneaux de lames horizontales en applique devant les baies (niveau, sens, ligne, a, b, z0, z1)
PERSIENNES = [
    ("R+1", "h", 5.0, 5.7, 7.3, 0.0, 2.4),     # salon familial : un vantail tire
    ("R+1", "h", 5.0, 10.5, 11.6, 0.0, 2.4),   # chambre 2 : un vantail tire
    ("R+1", "h", 8.6, 17.4, 18.3, 0.9, 2.4),   # chambre 3
    ("R+1", "h", 16.5, 3.4, 4.5, 0.9, 2.4),    # chambre parentale (Sud)
]
# Barreaudage des portes-fenetres de l'etage (h 1,0 m)
BARREAUDAGES = [("R+1", "h", 5.0, 6.4, 9.6), ("R+1", "h", 5.0, 11.1, 12.7)]
# Claustras BTC ajoures autonomes (x0, y0, x1, y1, z0, z1)
CLAUSTRAS = [
    (2.0, 12.2, 2.14, 16.5, 3.75, 6.85),      # double peau du balcon Ouest de la suite (pleine hauteur)
    (18.5, 2.5, 20.0, 2.64, 0.0, 2.9),        # aile de service : face Nord du sechoir
    (19.86, 2.6, 20.0, 8.6, 0.0, 2.9),        # sechoir, en limite Est
]
# Cloture sur rue : socle maconne 1,0 m + claustra BTC 1,2 m ; portail et portillons en lames bois
CLOTURE_SOCLE = 1.0
CLOTURE_H = 2.2


def resume():
    """Texte court pour le dossier."""
    return [f"{a} : {b}" for a, b in REFERENCE["repris"]]
