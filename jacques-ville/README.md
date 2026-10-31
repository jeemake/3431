# Jacques Ville — dossier 3431 — variante C-R1

Révision **B** du 31 octobre 2026, après relecture des sept règles Capitude et demande de couleurs pastel par usage. **Esquisse architecturale à développer, non exécutoire.**

## Livrables

- [Plans PDF A3, six planches, révision B](output/3431_Plans_Capitude_RevB.pdf) : masse au 1:200, RDC et R+1 au 1:100, pavillon au 1:100 et chambre au 1:50, paysage au 1:200, coupe au 1:100. Imprimer à 100 %, sans ajustement.
- [Notice Capitude, quatre pages](output/3431_Notice_Capitude_RevB.pdf) : programme, surfaces, budget, diagnostic paysager, palette fonctionnelle et sources.
- [Maquette IFC4 en mètres](output/3431_JacquesVille_C-R1.ifc).
- Plans éditables DXF R2018 et SVG dans `output/`.
- [Surfaces nettes](output/surfaces.csv), [contrôles](output/verification.json), [provenance des familles IFC](output/familles_utilisees.json).
- [Contrôles des plans et parcours](output/verification_plans_RevB.json), [vérification du cache Capitude](references/cache_verifie_RevB.json).

Le PDF `3431_Plans_C-R1.pdf` et les anciens fichiers `04_Coupe.*` sont conservés comme **première version historique**. Les PDF révision B ci-dessus font foi pour cette livraison. Les aperçus `apercu_01` à `apercu_06` correspondent à la révision B.

## Changements de la révision B

Aplats très pastel limités aux pièces, de couleur constante par usage ; murs, cotes et textes noirs. Cette demande explicite de Jean Marc prévaut sur la préférence monochrome des règles. Paysage gris, opacités différenciées et textures découpées strictement aux limites, bâtiments, parcours et bassin. Les fichiers DXF conservent les définitions des blocs originaux ; les variations graphiques portent sur des copies de présentation.

Deux portes ouvrent l'accueil et le noyau E1 vers le jardin. Foot pong, soccer et réservation E2 sont ajustés pour desservir les activités par un chemin continu. La passerelle et le palier E2 totalisent maintenant 15,24 m². Dix destinations du jardin sont reliées géométriquement au parcours principal ; cette vérification n'est pas une validation réglementaire des largeurs ni des pentes. L'IFC reprend ces changements et les emprises des cheminements et massifs.

Six zones de plantation sont documentées par usage et milieu. Les espèces, quantités de plants, dimensions adultes, sol, salinité, drainage et entretien restent à qualifier localement. Les trois couronnes sont des intentions projetées ; aucun arbre existant n'est inventé.

## Réponse au brief

Terrain déclaré de **1 120 m²**, R+1, **12 clés** (4 au RDC, 8 au R+1). Piscine de 25 m², restaurant de 52,80 m² nets / cible 28 couverts, soccer cage de loisir 84 m², réserve foot pong de 21 m², sport et réunion de 23,12 m² chacun. Supérette supprimée ; spa remplacé par une cabine massage de 8,48 m². Chaque chambre dispose de 22,69 m² nets, dont 4,40 m² de salle d'eau.

La réduction à douze clés limite les surfaces. Les grandes suites et loggias de l'ancienne option ne sont pas conservées ; le standing est une intention de matériaux, confort et service, **pas un niveau hôtelier certifié**. La variante doit être approuvée sur ce point.

## Budget : objectif, pas prix démontré

Le PDF donne une allocation cible de **300 M F CFA, honoraires et études inclus**. Elle n'est pas un devis. Les ratios historiques du dépôt ne démontrent pas que ce programme, ses équipements et la préparation au R+3 puissent entrer dans 250–300 M. Le chiffrage métrique et les consultations de Mr Adicko sont indispensables. Le coût final, la fiscalité et les inclusions doivent être confirmés ; le foncier et la construction future R+2/R+3 ne sont pas compris. Aucune baisse arbitraire des prix n'est présentée comme un résultat acquis.

## Ce que contient l'IFC

Hiérarchie projet / site / bâtiment / niveaux ; murs, cloisons, dalles, poteaux de principe, ouvertures réelles et portes schématiques, espaces avec surfaces, bassin, emprises des activités et passerelle vers E2. Les sanitaires réemploient trois familles Capitude (WC suspendu, vasque, douche), dont les SHA-256 ont été vérifiés. Les maillages sont en mètres et replacés depuis un point d'insertion explicite ; les placements sources sont enregistrés dans le manifeste.

Les poteaux 30 × 30 cm sont des **gabarits non calculés**. Les fondations sont des zones neutres `IfcBuildingElementProxy`, pas des semelles dimensionnées. Aucune capacité R+3 n'est certifiée. Le BET doit déterminer les charges futures, le contreventement, les fondations et la protection en milieu littoral après étude géotechnique. R+2 et R+3 figurent uniquement en intention dans la coupe, pas comme niveaux construits dans l'IFC.

Les blocs d'escalier droit, fenêtres adaptées et mobilier 2D manquent à la bibliothèque : E1, E2, EL, F?, LIT?, PL? sont des **réservations neutres**, conformément aux règles Supabase. L'IFC n'a donc pas de volées d'escalier exécutables. Il faut compléter la bibliothèque avec Jean Marc / Stéphanie. L'hélicoïdal disponible n'a pas été employé comme substitut à un escalier hôtelier.

## Points d'APS ouverts

Accessibilité et chambre adaptée, dimensions de l'élévateur, escaliers et évacuation incendie, dégagements des équipements sportifs, protections de piscine, acoustique, ventilation, entretien, assainissement, réserves d'eau, énergie, traitement des déchets et organisation du personnel. La dépose ne constitue pas un parking client complet. Aucun stationnement hors parcelle n'est acquis. Les reculs et la constructibilité future R+3 restent à confirmer avec les documents d'urbanisme. Les réseaux ne sont pas dimensionnés.

## Sources et traçabilité

- Brief du 31/10/2026 et `RETOUR-CLIENT.md` de la branche par défaut.
- Ancienne option C : branche `claude/great-gates-cp292d`, dossier `hotel-jacqueville`. La copie de `geo.py` est conservée dans `src/geo_source.py`. Le contour du lot est repris sans déformation ; les coordonnées donnent **1 120,273 m²**, écart d'arrondi de 0,273 m² par rapport au brief. Original du levé et datum non authentifiés dans cette tâche.
- Supabase **capitude**, projet `ysyklinfzlvqkrtrtrmv` : sept règles relues le 31/10/2026, dont `BLOCS-ARCHIBOOKS` v3 et `GRAPHISME-ELCROQUIS-EXTERIEURS` v2. Versions, dates et empreintes des textes dans `references/regles_capitude_2026-10-31.json` ; textes intégraux conservés uniquement dans le cache local ignoré par Git. Métadonnées consultées via MCP autorisé ; aucune donnée distante modifiée.
- Principes adaptés de `design_patterns` : chambres avec salle d'eau privative, services au sol et séparation logistique/jardin issus de Djondji. Ils sont des références de conception, pas des normes.
- Révision B : cache local contrôlé contre le catalogue Supabase vivant, sans nouvelle connexion externe. Six extensions DXF correspondent exactement aux SHA-256 Supabase ; cinq DXF historiques sont des dérivés AutoCAD 2023 de DWG dont les SHA-256 correspondent aux sources Supabase. Ce statut est explicite dans le manifeste. Les clés des fonctions HTTP ne sont pas configurées dans cette tâche ; aucune clé n'a été recherchée dans Vault et aucun contournement d'accès n'a été utilisé.
- Références Capitude Primaveras p.132/138 et Candela p.152 ouvertes visuellement. SHA-256 locaux contrôlés sur le manifeste ; tailles et ETags comparés aux métadonnées Storage relues dans Supabase. Images sources privées non republiées. Les références guident le graphisme et les relations spatiales ; leurs captures ne servent pas à mesurer le projet.
- API IFC et unités : [création géométrique IfcOpenShell](https://docs.ifcopenshell.org/ifcopenshell-python/geometry_creation.html), [traitement des géométries](https://docs.ifcopenshell.org/ifcopenshell-python/geometry_processing.html).

Le fichier `avis_senior_original.json` est un document hérité de l'étude précédente ; son profil déclaré n'a pas été authentifié. Il ne vaut pas validation professionnelle de cette variante.

## Régénérer

Python 3.12 et dépendances épinglées dans `requirements.txt`. Installer dans un environnement isolé.

Configurer `ARCHIBOOKS_BLOCS` vers le cache vérifié contenant `catalogue.json`, `lib/archibooks_blocs.py`, `lib/archibooks_graphics.py`, `dxf/` et `extensions-exterieurs-v1/`. Configurer `CAPITUDE_IFC_LIBRARY` vers la bibliothèque autorisée contenant `catalogue.json` et `ifc/`. Pour auditer les références, `CAPITUDE_REFERENCE_CACHE` désigne le cache contenant `data/asset_manifest.jsonl` et `media/`. Ne pas placer de clé API dans le dépôt.

```text
python src/build_ifc.py
python src/build_plans.py
python src/preview_ifc.py
```

`project.py` constitue la source géométrique commune aux plans et à l'IFC. Le contrôle couvre le nombre de clés, les surfaces sans recouvrement, la présence dans la parcelle des emprises testées, le schéma IFC4 et la tessellation des produits représentés. Il ne remplace ni une détection exhaustive de collisions ni une validation réglementaire ou structurelle.
