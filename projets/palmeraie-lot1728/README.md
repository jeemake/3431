# Lot 1728 – Riviera Palmeraie (Cocody, Abidjan)

Étude de faisabilité d'un projet personnel sur une parcelle d'angle de 660 m² (20 × 33 m). On y prévoit une villa duplex de
4 chambres sur 360 m², d'inspiration japonaise, et un bâtiment locatif R+1 de 6 logements sur 300 m².

## Livrables (`out/`)

| Document | Fichiers |
|---|---|
| 1. Analyse de site, deux options de villa, locatif, revue senior | `01_Esquisse_Lot1728_Palmeraie.pdf` |
| 2. Estimatif sommaire (ratios Éco-données ÷ 2) | `02_Estimatif_Lot1728_Palmeraie.pdf`, `.xlsx` (formules actives) |
| 3. Business plan de l'investissement locatif | `03_Business_Plan_Lot1728_Palmeraie.pdf`, `.xlsx` (hypothèses modifiables) |

Les plans sont aussi fournis en SVG et PNG (`out/svg`, `out/png`).

## Sources de données

- Plan cadastral du lot 1728, îlot 174, Djorogobité 1 (CGE Coco Habib, 04-11-2025).
- Base Supabase **Capitude** : surfaces médianes par type de pièce et motifs de conception de 12 projets.
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
```
