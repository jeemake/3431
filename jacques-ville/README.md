# Jacques Ville — dossier 3431 — variante C-R1

Révision du 31 octobre 2026. **Esquisse architecturale à développer, non exécutoire.**

## Livrables

- [Plans PDF A3, six planches](output/3431_Plans_C-R1.pdf) : masse, RDC, R+1, coupe/évolution, surfaces et enveloppe financière.
- [Maquette IFC4 en mètres](output/3431_JacquesVille_C-R1.ifc).
- Plans éditables DXF R2018 et SVG dans `output/`.
- [Surfaces nettes](output/surfaces.csv), [contrôles](output/verification.json), [provenance des familles IFC](output/familles_utilisees.json).

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
- Supabase **capitude**, projet `ysyklinfzlvqkrtrtrmv` : `regles_agents`, règles `BLOCS-ARCHIBOOKS` et `IFC-REUNION-FAMILLES` version 1 ; `rdf_families` et `rdf_family_versions` consultées le 31/10/2026. Aucune donnée distante modifiée.
- Principes adaptés de `design_patterns` : chambres avec salle d'eau privative, services au sol et séparation logistique/jardin issus de Djondji. Ils sont des références de conception, pas des normes.
- Blocs Archibooks récupérés dans le [dossier Drive](https://drive.google.com/drive/folders/1w6APBmrhlfixhxJIzhTPnGhStV84Bcey). Les cinq DWG utilisés sont convertis en DXF avec AutoCAD Core Console 2023 puis insérés avec la bibliothèque `archibooks_blocs.py`. Les originaux Drive restent inchangés. Le contenu original complet de la bibliothèque n'est pas republié dans ce dépôt.
- API IFC et unités : [création géométrique IfcOpenShell](https://docs.ifcopenshell.org/ifcopenshell-python/geometry_creation.html), [traitement des géométries](https://docs.ifcopenshell.org/ifcopenshell-python/geometry_processing.html).

Le fichier `avis_senior_original.json` est un document hérité de l'étude précédente ; son profil déclaré n'a pas été authentifié. Il ne vaut pas validation professionnelle de cette variante.

## Régénérer

Python 3.12 et dépendances épinglées dans `requirements.txt`. Installer dans un environnement isolé.

Configurer `ARCHIBOOKS_BLOCS` vers la bibliothèque autorisée contenant `catalogue.json`, `lib/archibooks_blocs.py`, `dxf/`. Configurer `CAPITUDE_IFC_LIBRARY` vers la bibliothèque Capitude autorisée contenant `catalogue.json` et `ifc/`. Ne pas placer de clé API dans le dépôt.

```text
python src/build_ifc.py
python src/build_plans.py
python src/preview_ifc.py
```

`project.py` constitue la source géométrique commune aux plans et à l'IFC. Le contrôle couvre le nombre de clés, les surfaces sans recouvrement, la présence dans la parcelle des emprises testées, le schéma IFC4 et la tessellation des produits représentés. Il ne remplace ni une détection exhaustive de collisions ni une validation réglementaire ou structurelle.
