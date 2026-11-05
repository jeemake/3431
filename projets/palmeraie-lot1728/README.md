# Lot 1728 – Riviera Palmeraie (Cocody, Abidjan)

Étude de faisabilité d'un projet personnel sur une parcelle d'angle de 660 m² (20 × 33 m) : une villa duplex de 4 chambres
dont une chambre de nounou, avec cuisine africaine, sur 360 m², et un bâtiment locatif R+1 de 6 logements sur 300 m².
Trois options de villa, conçues à partir de l'étude des plans de la base Capitude et relues par un architecte senior :
A (villa compacte, nounou à l'étage), B (villa avec aile de service, recommandée), C (maison à patio central).

## Livrables (`out/`)

| Document | Fichiers |
|---|---|
| 1. Analyse de site, étude Capitude, trois options de villa, locatif, revues senior | `01_Esquisse_Lot1728_Palmeraie.pdf` |
| 2. Estimatif sommaire (ratios Éco-données ÷ 2) | `02_Estimatif_Lot1728_Palmeraie.pdf`, `.xlsx` (formules actives) |
| 3. Business plan de l'investissement locatif | `03_Business_Plan_Lot1728_Palmeraie.pdf`, `.xlsx` (hypothèses modifiables) |
| 4. Option C, dossier de présentation : plans, coupes, élévations, vues 3D (maquette), surfaces, estimatif | `04_Dossier_Option_C_Lot1728.pdf` |
| Option C, façades et patio (références Capitude Palinda Kannangara : Casa Lineal, Casa Estudio) : élévations annotées, vues | `C_Facades_Lot1728.pdf` |

Les plans sont aussi fournis en SVG et PNG (`out/svg`, `out/png`).

## Sources de données

- Plan cadastral du lot 1728, îlot 174, Djorogobité 1 (CGE Coco Habib, 04-11-2025).
- Base Supabase **Capitude** : plans vectorisés (pièces, dimensions, portes, liaisons) des villas Anthurium, ABYA 2,
  EMIIKA et JIK ; surfaces médianes par type de pièce et motifs de conception.
- Base Supabase **Éco-données** : ratios d'estimation sommaire par pièce (Pavillon Akpo 2022, Résidences
  Anthurium 2021, Résidence Les Flamboyants, Villa Cacao 6 2023), divisés par 2 sur consigne du client.
- Loyers de marché Riviera Palmeraie (début 2026), relevés dans des annonces et des guides en ligne.

## Régénérer

Tout part du modèle `src/projet.py` : géométrie des pièces, ratios, quantités.

```bash
cd src
python3 plans.py      # plans SVG
python3 estimatif.py  # classeur estimatif
python3 bp.py         # classeur business plan
python3 doc.py        # 3 PDF (Chromium / Playwright)
python3 rendu/scene.py  # maquette 3D de l'option C (facades : facade.py)
python3 doc_dossier_C.py  # dossier de presentation de l'option C
python3 doc_facade.py   # planches facades (apres rendu des vues clay, voir rendu/render_clay.js)
```
