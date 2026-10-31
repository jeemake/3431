# LE ONZE — hôtel-jardin à Jacqueville (esquisse)

Projet personnel : proposition d'aménagement d'un hôtel de 15 clés sur le lot 2511, îlot 225, à Jacqueville (Côte d'Ivoire). Le terrain fait 1 120 m² et se trouve à environ 300 m de la plage. Le client est footballeur.

- **Dossier final** : `LE_ONZE_Jacqueville_esquisse.pdf` (A3 paysage).
- **Propositions** : A « Le Toit-Stade » et B « Le Village-Canopée ».
- **Référence** : Djondji Resort (Bénin), tirée de la base de projets Supabase, plans et images compris.
- **Coûts** : ratios de la base Supabase « Eco-données », divisés par deux à la demande du client.

## Régénérer le dossier

```bash
cd src
python3 geo.py          # contrôle de la géométrie du terrain
python3 design.py       # surfaces, biotope, estimatif
python3 drawings.py     # planches SVG
python3 scene3d.py && node render3d.js ../build/png   # maquettes 3D (Three.js, Chromium headless)
python3 build.py && node topdf.js ../build/dossier.html ../LE_ONZE_Jacqueville_esquisse.pdf
```

Dépendances : Python 3 avec `shapely` et `Pillow`, Node avec `playwright` (Chromium).
Les images d'ambiance de `img/` (A_*, B_*, chambre) ont été générées par IA avec `src/renders.py` (fal.ai). Elles ne sont pas contractuelles.
