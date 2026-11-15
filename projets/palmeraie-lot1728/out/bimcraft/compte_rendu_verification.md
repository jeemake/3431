# Compte rendu de vérification — dossier 07 (maquette BIMCraft), 15-11-2026

Règles Capitude lues dans Supabase (`regles_agents`, projet `capitude`) : PRESENTATION-PROJETS-ARCHI v4,
GABARIT-VISUEL-PLANS v4 (11-11-2026, pièces numérotées et légende en C10-12), BLOCS-ARCHIBOOKS v13,
CAPITUDE-SUPABASE-ONLY v1. Bibliothèque et blocs téléchargés par `/functions/v1/blocs/lib` et `/blocs/batch`
(38 fichiers de `lib/`, 53 DXF), empreintes SHA-256 toutes conformes.

## Source des dessins

Maquette BIMCraft `Lot1728_v5.bimc` (558 commandes générées depuis `projet.py` et `facade.py`). Plans, coupes et
élévations sont les vues de BIMCraft ; la mise en page y pose, à l'échelle vraie (1:100, plan masse 1:200) :
textures Archibooks, canopées El Croquis (`vegetation-elcroquis-v1`), numéros de pièces et légende, repères de coupe,
nord et échelle graphique, trait de sol, végétation `veg_coupe_*` et personnages `pers_*` en coupe et élévation,
calepinage de la peau de lames. Calibrage pixels → mètres sur des axes temporaires posés sur les limites de la parcelle.

## Passes

1. Premier export : pages lues en entier et zones denses agrandies. Défauts trouvés :
   - arbre du patio visible au travers de la façade Nord (élévation) → arbres cachés par le bâti retirés par vue ;
   - titre de vue de BIMCraft visible sous le plan → contenu BIMCraft recadré à son cadrage ;
   - en-têtes « MAISON » répétés dans la légende des duplex → identifiant et surface de chaque maison posés une fois
     hors des pièces (section 4) ;
   - rive de la couverture de la villa tranchée par le cadre du plan haut des duplex → cadrage remonté ;
   - vues caméra du toit et du patio peu lisibles → remplacées par l'axonométrie Sud-Est et la vue d'ambiance V2 ;
   - export .pptx de 38 Mo → photos en JPEG (8,9 Mo).
2. Second export : aucun défaut bloquant relevé sur les pages relues.

## Contrôles

- Police : `pdffonts` sur le PDF ne liste que URWGothic-Book et URWGothic-Demi (repli de Century Gothic, chaîne de la
  section 7). Les mentions MONTE / DESCEND des escaliers sont dessinées par BIMCraft en traits (pas une police).
- Surfaces : nomenclature BIMCraft aux axes = `projet.py` (villa 275,0 m², maison 153,0 m²) ; mêmes valeurs dans les
  légendes, le tableau des surfaces et l'estimatif.
- Noir et gris sur les plans, coupes et élévations ; couleur réservée aux axonométries (aplats par matériau) et aux vues
  d'ambiance.

## Non réalisé

- Planches de référence El Croquis (`/functions/v1/sheet-url`) : refus 401, l'en-tête `x-agent-key` des plans n'est pas
  configuré dans cette session. Comparaison faite avec les plans du dossier 05, déjà au gabarit.
- Débattements de portes contrôlés à l'œil seulement (pas de test géométrique quart de cercle / mobilier).
- Arbres DWG `tree_pmd_*` (priorité du 31-10) : fichiers DWG sans DXF normalisé, non insérés ; blocs `veg_coupe_*` utilisés.
- Catalogue des éléments, planche matériaux et collage d'intention (section 4 de PRESENTATION-PROJETS-ARCHI) : non produits.
