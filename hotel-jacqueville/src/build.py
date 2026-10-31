"""Assemble le dossier « LE ONZE — hôtel-jardin à Jacqueville » en HTML puis PDF (A3 paysage)."""
import os, json, html, subprocess
import design as D
from geo import SITE

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
BUILD = os.path.join(ROOT, 'build')
SVG = lambda n: open(os.path.join(BUILD, 'svg', n + '.svg')).read()
IMG = lambda n: f'../img/{n}'
PNG = lambda n: f'png/{n}'
fm = lambda x: f'{x:,.0f}'.replace(',', ' ')
fm1 = lambda x: f'{x:,.1f}'.replace(',', ' ').replace('.', ',')
REVIEW = os.path.join(ROOT, 'src', 'avis_senior.json')

pages = []
def page(body, cls='', num=True):
    pages.append((body, cls, num))

def head(kicker, title, sub=''):
    return f'<header class="ph"><div class="kick">{kicker}</div><h1>{title}</h1>' + (f'<p class="sub">{sub}</p>' if sub else '') + '</header>'

def fig(content, cap='', cls=''):
    return f'<figure class="{cls}">{content}' + (f'<figcaption>{cap}</figcaption>' if cap else '') + '</figure>'

def img(src, cap='', cls='', ia=False):
    tag = '<span class="ia">Image d’ambiance générée par IA — non contractuelle</span>' if ia else ''
    return fig(f'<div class="imgw"><img src="{src}">{tag}</div>', cap, cls)

S = {c: D.biotope(c) for c in 'AB'}
E = {c: D.estimatif(c) for c in 'AB'}
green = {c: S[c][0]['pleine_terre'] + S[c][0].get('pelouse', 0) for c in 'AB'}

# ------------------------------------------------------------------ 1. couverture
page(f'''
<div class="cover">
  <div class="cv-img"><img src="{IMG('A_toit.jpg')}"><span class="ia">Image d’ambiance générée par IA — non contractuelle</span></div>
  <div class="cv-txt">
    <div class="kick">Projet personnel · Esquisse · Octobre 2026</div>
    <h1 class="big">LE ONZE</h1>
    <h2>Un hôtel-jardin de 15 clés à Jacqueville, pensé pour un footballeur</h2>
    <p>Lot 2511 · îlot 225 · 1 120 m² · à 300 m de l’océan Atlantique</p>
    <div class="cv-nums">
      <div><b>{green['A'] / SITE.area * 100:.0f} %</b><span>de pleine terre végétale (A)</span></div>
      <div><b>15</b><span>clés, 3 à 6 suites familiales modulables</span></div>
      <div><b>×{green['A'] / 20:.0f}</b><span>d’espace vert vs le programme initial</span></div>
    </div>
    <p class="small">Deux propositions : <b>A — Le Toit-Stade</b> et <b>B — Le Village-Canopée</b>.<br>
    Référence : Djondji Resort (Bénin) issue de la base de projets Supabase · Coûts : base Éco-données, divisés par deux.</p>
  </div>
</div>''', 'cv', num=False)

# ------------------------------------------------------------------ 2. synthèse
costA, costB = E['A'][3], E['B'][3]
page(head('00 · Synthèse', 'L’idée en une page') + f'''
<div class="cols3">
 <div><h3>Le constat</h3>
  <p>Le programme reçu totalise <b>1 851 m² de surfaces utiles</b>, dont <b>1 345 m² posés au sol</b> (RDC + extérieurs) pour un terrain de <b>1 120 m²</b> : il ne tient pas. Le jardin y est réduit à <b>20 m²</b> (1,8 % du terrain) et le parking de 20 places en consomme 400.</p>
  <h3>La stratégie</h3>
  <ol class="tight">
   <li><b>Empiler plutôt qu’étaler</b> : hébergement en R+2 sur une emprise de 30 à 35 %.</li>
   <li><b>Sortir la voiture</b> du terrain : dépose-minute + 2 places, 18 places mutualisées hors parcelle.</li>
   <li><b>Mutualiser</b> : suites familiales par portes communicantes (lock-off), lounge = salle de projection des matchs, restaurant privatisable = salle polyvalente.</li>
   <li><b>Rendre la toiture ou le jardin utiles au foot</b> : cage sur le toit (A) ou pelouse-terrain naturelle (B).</li>
   <li><b>Climatiser par le dessin</b> : barres d’une pièce d’épaisseur, nord/sud, brise SO, grands débords, chaume ventilé.</li>
  </ol>
 </div>
 <div class="card a"><div class="tag">Proposition A</div><h3>Le Toit-Stade</h3>
  <p>Une seule barre R+2 adossée à la limite nord, coiffée d’un <b>restaurant sous chaume</b> avec vue mer et d’une <b>cage de foot en toiture</b>. Tout le sud devient un jardin-forêt avec bassin de nage et bain froid de récupération.</p>
  <table class="kv"><tr><td>Pleine terre</td><td>{S['A'][0]['pleine_terre']:.0f} m² · {S['A'][0]['pleine_terre'] / SITE.area * 100:.0f} %</td></tr>
  <tr><td>Coefficient de biotope</td><td>{S['A'][1]:.2f}</td></tr><tr><td>Hauteur</td><td>R+2 + toit-terrasse (faîtage ≈ +17 m)</td></tr>
  <tr><td>Estimation travaux</td><td><b>{costA / 1e6:,.0f} M FCFA HT</b></td></tr></table></div>
 <div class="card b"><div class="tag">Proposition B</div><h3>Le Village-Canopée</h3>
  <p>Trois <b>cases-tours</b> R+2 sous hautes toitures de chaume, séparées par des failles plantées qui laissent passer la brise, une <b>case commune</b> ouverte et une <b>pelouse-terrain</b> en gazon naturel au cœur du jardin.</p>
  <table class="kv"><tr><td>Pleine terre + pelouse</td><td>{green['B']:.0f} m² · {green['B'] / SITE.area * 100:.0f} %</td></tr>
  <tr><td>Coefficient de biotope</td><td>{S['B'][1]:.2f}</td></tr><tr><td>Hauteur</td><td>R+2 sous chaume (faîtage ≈ +14,6 m)</td></tr>
  <tr><td>Estimation travaux</td><td><b>{costB / 1e6:,.0f} M FCFA HT</b></td></tr></table></div>
</div>
<div class="note">Montants : ratios Éco-données (FCFA HT/m²) <b>divisés par deux à la demande du maître d’ouvrage</b>, aléas 5 % inclus, hors honoraires, taxes, foncier, mobilier et raccordements concessionnaires.</div>''')

# ------------------------------------------------------------------ 3. site
page(head('01 · Le site', 'Un trapèze rectangle de 1 120 m², presque parfaitement orienté',
          'Jacqueville, cordon littoral entre la lagune Ébrié (nord) et l’océan Atlantique (sud), à ~300 m de la plage.') + f'''
<div class="g-site">
 {fig(SVG('site'), 'Analyse du terrain — coordonnées des bornes B1–B4 (levé N’GUESSAN, 27-01-2026), reculs retenus en hypothèse.')}
 <div>
  <h3>Ce que dit le plan cadastral</h3>
  <table class="data"><tr><th>Borne</th><th>X</th><th>Y</th><th>Angle</th><th>Côté</th></tr>
  <tr><td>B1</td><td>351 038,835</td><td>575 741,923</td><td>87,756 gr</td><td>B1–B2 · 40,751 m</td></tr>
  <tr><td>B2</td><td>351 079,462</td><td>575 738,749</td><td>112,244 gr</td><td>B2–B3 · 24,112 m</td></tr>
  <tr><td>B3</td><td>351 082,214</td><td>575 714,794</td><td>100,000 gr</td><td>B3–B4 · 40,000 m</td></tr>
  <tr><td>B4</td><td>351 042,475</td><td>575 710,230</td><td>100,000 gr</td><td>B4–B1 · 31,902 m</td></tr></table>
  <p>Contenance <b>11 a 20 ca</b> (vérifiée : 1 120,3 m² par calcul des coordonnées). Voisins : lot 2513 au sud, lots 2512/2514 à l’est. Une emprise en tireté à l’ouest est lue comme la <b>voie d’accès</b> (à confirmer).</p>
  <h3>Les atouts bioclimatiques</h3>
  <ul class="tight">
   <li><b>Limite nord à l’azimut 94,5°</b> : un bâtiment qui s’y adosse a ses longues façades à 4,5° du nord/sud vrais — l’orientation idéale à 5° de latitude.</li>
   <li><b>Brise de mer SO</b> (mousson, 3–5 m/s) : le jardin placé au sud la rafraîchit avant qu’elle traverse les chambres.</li>
   <li>Climat équatorial humide : 24–31 °C, HR 80–90 %, ≈ 1 800–2 000 mm/an en deux saisons des pluies (avril–juillet, octobre–novembre).</li>
   <li>Sol sableux, <b>nappe haute</b> : pas de sous-sol, fondations superficielles sur sable compacté ou micro-pieux selon étude G2, cuves d’eau de pluie semi-enterrées.</li>
   <li>Air salin : béton à enrobage renforcé, bois durs (iroko, tali) traités, quincaillerie inox A4, aluminium anodisé.</li>
  </ul>
  <div class="g-sit">{fig(SVG('situation'), 'Situation schématique sur le cordon littoral.')}{img(IMG('cadastre.png'), 'Plan cadastral fourni (redressé).', 'small-fig')}</div>
 </div>
</div>''')

# ------------------------------------------------------------------ 4. challenge programme
CH = [
 ('Chambres deluxe', '4 × 15 m²', '7 × 25,2 m²', '6 × 25,2 m²', '15 m² est sous le standard d’un 4* (≥ 24 m² SdE comprise). Module 3,6 × 7,0 m, SdE incluse.'),
 ('Suites junior', '6 × 20 m²', '6 × 37,8 m²', '6 × 37,8 m²', '1,5 trame : coin salon + loggia de 9,7 m².'),
 ('Suites familiales 2 ch.', '3 × 45 m²', '3 lock-off', '6 lock-off', 'Junior + deluxe reliées par porte communicante : vendues en 2 clés en semaine, en 1 suite le week-end — 0 m² en plus.'),
 ('Suites premium', '2 × 45 m²', '2 × 50,4 m²', '3 × 63 m²', 'B : sous la toiture de chaume, avec mezzanine.'),
 ('Circulations 20 %', '81 m² clos', 'coursives ouvertes', 'galeries + esc. ext.', 'Ouvertes au nord : elles ventilent au lieu d’être climatisées.'),
 ('Accueil + administration', '65 m²', '52 + 15 m²', '28 + 20 m²', 'Le lobby-lounge sert aussi de salle de projection des matchs.'),
 ('Restaurant 100 pers. + cuisine', '130 m²', '80 couv. en toiture + cuisine', '50 + 30 couv. sous chaume', 'Le complément de couverts se fait en jardin / sur la pelouse lors des événements.'),
 ('Salle polyvalente & bureaux', '100 m²', 'supprimée', 'supprimée', 'Fusion : lounge, restaurant privatisable, toit (A) ou pelouse (B) pour les événements.'),
 ('Spa + salle de sport', '140 m²', '30 m² + fitness plein air', '56 m² (R+1)', 'Le sport du client se fait dehors : cage, bassin de nage, bain froid de récupération.'),
 ('Supérette', '60 m²', 'boutique 18 m²', 'intégrée à l’accueil', 'Ouverte sur la rue pour la clientèle de passage.'),
 ('Zone technique & services', '200 m²', '17,5 + 24 m²', '17,5 + 12 m²', '200 m² est surdimensionné pour 15 clés : locaux concessionnaires + GE en limite, lingerie, PV en toiture.'),
 ('Piscine et plage', '100 m²', 'bassin 2,5 × 16 + bain froid', 'bassin 2,5 × 12', 'Un couloir de nage plutôt qu’un bassin d’agrément : moins de surface, plus d’usage sportif.'),
 ('Soccer cage', '150 m² au sol', '153 m² en toiture', '117 m² gazon naturel', 'A : surface gagnée au sol. B : la pelouse est le jardin.'),
 ('Parking 20 places', '400 m²', 'dépose + 2 places', 'dépose + 2 places', '18 places mutualisées hors parcelle (convention / voiturier). C’est le principal gisement d’espace vert.'),
 ('Jardin & cheminement', '20 m²', f'{S["A"][0]["pleine_terre"]:.0f} m²', f'{green["B"]:.0f} m²', 'Jardin-forêt d’essences locales : badamier, fromager, cocotier, filao, vétiver.'),
]
rows = ''.join(f'<tr><td><b>{a}</b></td><td>{b}</td><td class="ca">{c}</td><td class="cb">{d}</td><td class="cm">{e}</td></tr>' for a, b, c, d, e in CH)
page(head('02 · Challenger le programme', 'Le programme ne tient pas : on le resserre pour libérer le sol',
          'Chaque ligne du programme initial a été questionnée : garder, fusionner, déplacer (toit, hors parcelle) ou supprimer.') + f'''
<div class="g-ch">
 <table class="data ch"><tr><th>Intitulé initial</th><th>Initial</th><th class="ca">A · Toit-Stade</th><th class="cb">B · Village-Canopée</th><th>Pourquoi</th></tr>{rows}</table>
 <div>
  {fig(SVG('chart_sols'), 'Occupation du sol (m² et % du terrain). Les valeurs détaillées figurent dans le tableau ci-contre et en annexe.')}
  <table class="data"><tr><th></th><th>Initial</th><th>A</th><th>B</th></tr>
   <tr><td>Surfaces closes (SU)</td><td>1 101 m²</td><td>{D.prog_total('A', {'heb','com','spa','rest'}):.0f} m²</td><td>{D.prog_total('B', {'heb','com','spa','rest'}):.0f} m²</td></tr>
   <tr><td>Extérieurs couverts</td><td>—</td><td>{D.prog_total('A', {'ext'}):.0f} m²</td><td>{D.prog_total('B', {'ext'}):.0f} m²</td></tr>
   <tr><td>Clés / chambres</td><td>15 / 18</td><td>15 / 15 (12 si 3 familles)</td><td>15 / 15 (9 si 6 familles)</td></tr>
   <tr><td>Emprise bâtie</td><td>≈ 695 m²</td><td>{S['A'][0]['bati'] + S['A'][0]['tech']:.0f} m²</td><td>{S['B'][0]['bati'] + S['B'][0]['tech']:.0f} m²</td></tr>
   <tr><td>Végétal en pleine terre</td><td>20 m²</td><td><b>{S['A'][0]['pleine_terre']:.0f} m²</b></td><td><b>{green['B']:.0f} m²</b></td></tr></table>
  <p class="small">Les chambres proposées sont plus grandes que l’initial, car celui-ci annonçait des surfaces sans salle d’eau. Les 3 chambres du nombre initial de 18 sont récupérées en souplesse par le lock-off.</p>
 </div>
</div>''')

# ------------------------------------------------------------------ 5. référence
page(head('03 · Référence', 'Djondji Resort, Ouidah (Bénin) — ce qu’on lui emprunte',
          'Projet retenu dans la base Supabase (12 projets, 162 patterns) : seul resort balnéaire du corpus, même cordon dunaire entre océan et lagune, même climat.') + f'''
<div class="g-ref">
 {img(IMG('ref_djondji_p01.jpg'), 'Vue aérienne — 13,14 ha entre océan et lac Djegba.')}
 {img(IMG('ref_djondji_p12.jpg'), 'Pavillon Plage, plan RDC — 5 travées de 4 m, bande humide côté allée, façade mer vitrée, lock-off 2 clés.')}
 {img(IMG('ref_djondji_p13.jpg'), 'Structure : poteaux bois massif 30 × 30, charpente apparente, chaume synthétique Palmex.')}
 {img(IMG('ref_djondji_p18.jpg'), 'Salle d’eau ouverte sur une douche extérieure en patio claustra.')}
 {img(IMG('ref_djondji_p23.jpg'), 'Restaurant ouvert sous charpente, ventilé naturellement.')}
 {img(IMG('ref_djondji_p26.jpg'), 'Bungalow sur butte plantée, accès en impasse.')}
 <div class="refl">
  <h3>Patterns repris (lus sur les plans)</h3>
  <ul class="tight">
   <li><b>Bande humide côté accès, pièces de vie côté vue</b> (p12) : SdE de 2,0 m le long de la coursive nord, chambre et loggia au sud.</li>
   <li><b>Lock-off</b> : le Pavillon Plage se loue en 2 clés (56,6 + 75,4 m²) ou en suite de 132 m² → nos suites familiales.</li>
   <li><b>Trame régulière</b> (4,00 m chez Djondji) → trame 3,60 m imposée par la longueur constructible (32,4 m).</li>
   <li><b>Poteaux bois détachés de la façade</b>, loggias en creux, grands débords de chaume.</li>
   <li><b>Douche extérieure en patio claustra</b> pour les chambres du RDC.</li>
   <li><b>Équipements communs en halles ouvertes</b> ventilées (restaurant, accueil) — case commune de B, restaurant de toit de A.</li>
   <li><b>Voiture cantonnée à l’entrée</b>, desserte piétonne, unités sur buttes plantées (B).</li>
  </ul>
  <h3>Ce qu’on ne reprend pas</h3>
  <p>L’étalement (1 unité pour ≈ 3 500 m² de terrain chez Djondji) : à Jacqueville on dispose de 75 m² de terrain par clé. D’où la verticalité.</p>
  <p class="src">Planches : présentation AO janvier 2025, base Supabase « capitude », projet <i>djondji-resort</i>.</p>
 </div>
</div>''')

# ------------------------------------------------------------------ 6. bioclimatique
page(head('04 · Principes bioclimatiques', 'Climatiser par l’architecture avant la machine') + f'''
<div class="g-bio">
 <div class="bio-list">
  <div><h4>1 · Orientation</h4><p>Barres et tours d’une seule pièce d’épaisseur, façades longues au nord et au sud (écart 4,5°). Pignons est/ouest aveugles et végétalisés (A) ou en claustra de brique de terre (B).</p></div>
  <div><h4>2 · Ventilation traversante</h4><p>Chaque chambre s’ouvre sur une loggia au sud et sur une coursive au nord par impostes à jalousies : la brise SO traverse sans climatiseur la majorité de l’année. Ventilateurs de plafond partout, clim d’appoint inverter en chambre.</p></div>
  <div><h4>3 · Protection solaire</h4><p>À 5,2° N, le soleil de midi culmine à 61° au sud (décembre) et 72° au nord (juin) : une loggia de 1,8 m et une coursive de 1,8 m suffisent. Persiennes coulissantes en iroko sur toute la façade sud.</p></div>
  <div><h4>4 · Toiture ventilée</h4><p>Chaume synthétique Palmex sur charpente bois, lame d’air, faîtage ventilé : l’air chaud s’évacue au-dessus du restaurant (A) et des suites premium (B). Dalle de toit isolée sous la cage de foot.</p></div>
  <div><h4>5 · Eau</h4><p>Récupération des eaux de pluie (≈ 340 m² de toiture × 1 900 mm ≈ 500 m³/an) en cuves pour arrosage et chasses ; phyto-épuration des eaux grises en jardin filtrant ; sol perméable partout ailleurs.</p></div>
  <div><h4>6 · Végétation</h4><p>Jardin-forêt sur 45 à 55 % du terrain : canopée de badamiers et fromagers, cocotiers, filaos en lisière, couvre-sols dunaires (ipomée, vétiver). L’ombre au sol abaisse de 2 à 4 °C la température de l’air qui entre dans les chambres.</p></div>
  <div><h4>7 · Énergie</h4><p>Pergola photovoltaïque possible sur la toiture de cuisine et les locaux techniques (≈ 15–20 kWc), eau chaude solaire, LED, groupe électrogène en secours.</p></div>
  <div><h4>8 · Matériaux</h4><p>Bois dur local, brique de terre stabilisée (claustras), enduits à la chaux, sols en grès cérame effet pierre comme à Djondji. Peu d’inertie en climat humide : on cherche la ventilation, pas le stockage de chaleur.</p></div>
 </div>
 {fig(SVG('coupe_A'), 'Coupe bioclimatique de la proposition A : brise SO rafraîchie par le jardin, protection solaire par loggias, air chaud évacué sous le chaume, eaux de pluie vers cuves.')}
</div>''')

# ------------------------------------------------------------------ 7-9. Variante A
sA = S['A'][0]
page(head('05 · Proposition A', 'Le Toit-Stade', 'Une barre, un toit qui joue au football, un jardin entier au sud.') + f'''
<div class="g-var">
 {fig(SVG('masse_A'), 'Plan masse A — la barre s’adosse à la limite nord (recul 4 m planté), tout le sud est jardin.')}
 <div>
  {img(PNG('axo3d_A_sw.png'), 'Maquette 3D — vue depuis le sud-ouest : restaurant sous chaume et cage de foot en toiture.')}
  <div class="kpis">
   <div><b>{sA['pleine_terre']:.0f} m²</b><span>pleine terre ({sA['pleine_terre'] / SITE.area * 100:.0f} %)</span></div>
   <div><b>{sA['bati'] + sA['tech']:.0f} m²</b><span>emprise bâtie ({(sA['bati'] + sA['tech']) / SITE.area * 100:.0f} %)</span></div>
   <div><b>{S['A'][1]:.2f}</b><span>coefficient de biotope</span></div>
   <div><b>15</b><span>clés · 7 D · 6 J · 2 P</span></div>
  </div>
  <p><b>Le parti.</b> Toute la construction est ramassée en une barre de 32,4 × 10,6 m sur trois niveaux, posée sur la seule limite parfaitement orientée. Le footballeur retrouve son terrain sur le toit, à côté d’un restaurant-bar sous une grande toiture de chaume d’où l’on voit l’océan au-dessus des cocotiers. Au sol, il ne reste qu’un jardin, un couloir de nage et un bain froid pour la récupération.</p>
 </div>
</div>''')
page(head('05 · Proposition A', 'Plans de niveaux — trame 3,60 m, 9 travées') + f'''
<div class="g-plans">
 {fig(SVG('A_R0'))}{fig(SVG('A_R1'))}{fig(SVG('A_R2'))}{fig(SVG('A_toit'))}
</div>
<p class="small">Noyau central escalier + ascenseur (8 pers., sert aussi de monte-charge pour la cuisine de toit). Second dégagement par escalier extérieur ouvert au pignon ouest (exigé pour un restaurant de 80 personnes en toiture). Coursives nord ouvertes, garde-corps bois.</p>''')
page(head('05 · Proposition A', 'Ambiances') + f'''
<div class="g-amb">
 {img(IMG('A_toit.jpg'), 'Le toit au coucher du soleil : cage de foot et restaurant-bar sous chaume face à l’océan.', ia=True)}
 {img(IMG('A_jardin.jpg'), 'Le jardin-forêt et le couloir de nage au pied des loggias.', ia=True)}
 {img(PNG('axo3d_A_se.png'), 'Maquette 3D — vue depuis le sud-est : pignon est végétalisé, filets de la cage.')}
 <div class="pc"><h3>Forces</h3><ul class="tight"><li>Le maximum de pleine terre ({sA['pleine_terre'] / SITE.area * 100:.0f} %) et un jardin d’un seul tenant.</li><li>Un « produit » unique : le toit-stade et son restaurant avec vue mer, ouvert aux clients extérieurs.</li><li>Ascenseur : toutes les chambres accessibles PMR.</li><li>Construction compacte et rationnelle (une seule cage, gaines superposées).</li></ul>
 <h3>Points de vigilance</h3><ul class="tight"><li>Acoustique du terrain au-dessus des chambres : dalle flottante, horaires encadrés.</li><li>Charges en toiture (public + gazon + filets au vent) : structure béton plus coûteuse.</li><li>Second escalier et sécurité incendie du restaurant en toiture.</li><li>Hauteur (faîtage ≈ +17 m) à valider au règlement.</li></ul></div>
</div>''')

# ------------------------------------------------------------------ 10-12. Variante B
sB = S['B'][0]
page(head('06 · Proposition B', 'Le Village-Canopée', 'Trois cases-tours, une case commune, une pelouse où l’on joue pieds nus.') + f'''
<div class="g-var">
 {fig(SVG('masse_B'), 'Plan masse B — trois cases-tours au nord séparées par des failles plantées, case commune et pelouse-terrain au sud.')}
 <div>
  {img(PNG('axo3d_B_sw.png'), 'Maquette 3D — vue depuis le sud-ouest.')}
  <div class="kpis">
   <div><b>{green['B']:.0f} m²</b><span>pleine terre + pelouse ({green['B'] / SITE.area * 100:.0f} %)</span></div>
   <div><b>{sB['bati'] + sB['tech']:.0f} m²</b><span>emprise bâtie ({(sB['bati'] + sB['tech']) / SITE.area * 100:.0f} %)</span></div>
   <div><b>{S['B'][1]:.2f}</b><span>coefficient de biotope</span></div>
   <div><b>15</b><span>clés · 6 D · 6 J · 3 P</span></div>
  </div>
  <p><b>Le parti.</b> On transpose le vocabulaire de Djondji (poteaux bois, chaume, claustras, halles ouvertes) à la verticale. Les trois tours laissent entre elles des failles de 2,7 m où montent les escaliers extérieurs et les palmiers : la brise passe, les vues aussi. La pelouse naturelle de 13 × 9 m sert de terrain le matin et de jardin d’événements le soir, en continuité avec le restaurant.</p>
 </div>
</div>''')
page(head('06 · Proposition B', 'Plans — case-tour (×3) et case commune') + f'''
<div class="g-plansB">
 {fig(SVG('B_tour_R0R1'))}{fig(SVG('B_tour_R2'))}{fig(SVG('B_case_commune'), '', 'wide')}
</div>
<div class="g-plansB2">
 {fig(SVG('coupe_B'), 'Coupe bioclimatique B : tour d’une pièce d’épaisseur, suite premium sous chaume avec lanterne de ventilation, case commune ouverte.')}
 <div><h3>Comment ça se construit</h3><ul class="tight">
  <li>Ossature poteaux-poutres béton (trame 3,60 / 5,40 m), habillage des poteaux de façade en bois dur ; dalles BA.</li>
  <li>Charpente bois traitée (classe 4, anti-termites) et chaume synthétique ignifugé sur liteaux, pente ≥ 45°.</li>
  <li>Pignons en claustra de brique de terre stabilisée (BTC) sur l’ouest de chaque tour, végétalisés.</li>
  <li>Escaliers extérieurs béton à marches bois dans les failles, abrités par les débords de 1,50 m.</li>
  <li>Case commune : poteaux bois massif 30 × 30 sur plots béton, comme Djondji ; mezzanine bois.</li>
 </ul></div>
</div>''')
page(head('06 · Proposition B', 'Ambiances') + f'''
<div class="g-amb">
 {img(IMG('B_village.jpg'), 'Les cases-tours depuis la pelouse-terrain : escaliers et palmiers dans les failles.', ia=True)}
 {img(IMG('B_case.jpg'), 'La case commune : restaurant ouvert sous double toiture de chaume.', ia=True)}
 {img(PNG('axo3d_B_se.png'), 'Maquette 3D — vue depuis le sud-est : pelouse-terrain et cages.')}
 <div class="pc"><h3>Forces</h3><ul class="tight"><li>Coefficient de biotope le plus élevé ({S['B'][1]:.2f}) grâce à la pelouse et aux claustras plantés.</li><li>Porosité au vent : les failles entre tours ventilent aussi le jardin.</li><li>Échelle domestique, identité forte, filiation directe avec Djondji.</li><li>Moins de béton, coût plus bas, chantier phasable tour par tour.</li></ul>
 <h3>Points de vigilance</h3><ul class="tight"><li>Pas d’ascenseur : 3 clés PMR au RDC seulement.</li><li>Chaume sur 3 niveaux : produit ignifugé (classement à justifier), entretien tous les 15–20 ans.</li><li>Trois cages d’escalier extérieures exposées à la pluie battante.</li><li>Pelouse naturelle : arrosage en saison sèche (eau de pluie stockée).</li></ul></div>
</div>''')

# ------------------------------------------------------------------ 13. typologies
page(head('07 · Les chambres', 'Un module unique, trois produits, une suite familiale sans m² en plus') + f'''
<div class="g-typo">
 {img(IMG('chambre.jpg'), 'Chambre : persiennes coulissantes ouvertes sur la loggia, ventilateur de plafond, imposte haute pour la ventilation traversante.', ia=True)}
 <div>
  <table class="data"><tr><th>Produit</th><th>Largeur</th><th>Surface (SdE incl.)</th><th>Loggia</th><th>A</th><th>B</th></tr>
  <tr><td>Deluxe</td><td>3,60 m · 1 trame</td><td>25,2 m²</td><td>6,5 m²</td><td>7</td><td>6</td></tr>
  <tr><td>Suite junior</td><td>5,40 m · 1,5 trame</td><td>37,8 m²</td><td>9,7 m²</td><td>6</td><td>6</td></tr>
  <tr><td>Suite premium</td><td>7,20 m (A) · 9,00 m (B)</td><td>50,4 / 63,0 m²</td><td>13–16 m²</td><td>2</td><td>3</td></tr>
  <tr><td><b>Suite familiale</b></td><td colspan="3">junior + deluxe par porte communicante : 63 m², 2 chambres, 2 SdE, 2 loggias</td><td>3</td><td>6</td></tr></table>
  <h3>Anatomie d’une chambre (de la coursive à la loggia)</h3>
  <ol class="tight">
   <li><b>Coursive nord 1,80 m</b> — ouverte, ombragée, l’air y est plus frais.</li>
   <li><b>Bande humide 2,00 m</b> — niche d’entrée, WC, douche à l’italienne, double vasque ; impostes à jalousies sur la coursive (pattern Djondji).</li>
   <li><b>Chambre 5,00 m</b> — lit face à la vue, plafond bois, ventilateur.</li>
   <li><b>Loggia 1,80 m</b> — persiennes coulissantes en iroko, bacs plantés, hamac.</li>
  </ol>
  <p>Au RDC, la loggia se prolonge par une terrasse jardin et une douche extérieure en patio claustra.</p>
  {fig(SVG('typo_module'), 'Paire lock-off junior + deluxe : 2 clés ou 1 suite familiale de 63 m².')}
 </div>
</div>''')

# ------------------------------------------------------------------ 14. comparatif
cmp_rows = [
 ('Pleine terre végétale', f"{sA['pleine_terre']:.0f} m² · {sA['pleine_terre'] / SITE.area * 100:.0f} %", f"{sB['pleine_terre']:.0f} m² + {sB['pelouse']:.0f} m² pelouse · {green['B'] / SITE.area * 100:.0f} %"),
 ('Coefficient de biotope (CBS)', f"{S['A'][1]:.2f}", f"{S['B'][1]:.2f}"),
 ('Emprise bâtie', f"{sA['bati'] + sA['tech']:.0f} m²", f"{sB['bati'] + sB['tech']:.0f} m²"),
 ('Surfaces closes (SU)', f"{D.prog_total('A', {'heb','com','spa','rest'}):.0f} m²", f"{D.prog_total('B', {'heb','com','spa','rest'}):.0f} m²"),
 ('Clés / suites familiales possibles', '15 / 3', '15 / 6'),
 ('Restaurant', '80 couverts en toiture, vue mer', '50 + 30 couverts sur la pelouse'),
 ('Football', 'cage synthétique 14,4 × 10,6 en toiture', 'pelouse naturelle 13 × 9 au sol'),
 ('Hauteur', 'R+2 + toit · faîtage ≈ +17 m', 'R+2 sous chaume · ≈ +14,6 m'),
 ('Accessibilité PMR', 'totale (ascenseur)', 'RDC seulement'),
 ('Estimation travaux HT (÷2)', f"<b>{costA / 1e6:,.0f} M FCFA</b>", f"<b>{costB / 1e6:,.0f} M FCFA</b>"),
 ('Coût par clé', f"{costA / 15 / 1e6:,.1f} M FCFA".replace('.', ','), f"{costB / 15 / 1e6:,.1f} M FCFA".replace('.', ',')),
]
page(head('08 · Comparaison', 'A ou B ?') + f'''
<div class="g-cmp">
 <table class="data cmp"><tr><th></th><th class="ca">A · Le Toit-Stade</th><th class="cb">B · Le Village-Canopée</th></tr>
 {''.join(f'<tr><td><b>{a}</b></td><td>{b}</td><td>{c}</td></tr>' for a, b, c in cmp_rows)}</table>
 <div>
  <h3>Recommandation</h3>
  <p><b>A</b> si le client veut <b>un lieu signature</b> autour de son métier (le toit-stade se raconte, se loue, se filme) et une accessibilité complète. C’est la proposition qui libère le plus de sol.</p>
  <p><b>B</b> si la priorité est <b>l’ambiance de resort</b>, le coût et la souplesse de phasage : c’est la plus végétale au sens du biotope, la plus proche de la référence Djondji, et le football s’y pratique sur de l’herbe.</p>
  <p>Une <b>hybridation</b> est possible : la barre de A avec la pelouse naturelle de B à la place du bassin, le toit étant alors entièrement restaurant + terrasse plantée.</p>
  {fig(SVG('chart_sols'))}
 </div>
</div>''')

# ------------------------------------------------------------------ 15. estimatif
def est_table(c):
    rows, ht, al, tot = E[c]
    tr = ''.join(f'<tr><td>{D.LIB_CAT[k]}</td><td class="r">{fm1(s)}</td><td class="src">{lib}</td><td class="r">{fm(r)}</td><td class="r">{fm(r2)}</td><td class="r"><b>{fm(m)}</b></td></tr>'
                 for k, lib, s, r, r2, m in rows)
    return (f'<table class="data est"><tr><th>Poste</th><th>m²</th><th>Ratio source (Éco-données)</th><th>FCFA/m² source</th><th>÷ 2</th><th>Montant HT</th></tr>{tr}'
            f'<tr class="tot"><td colspan="5">Sous-total travaux</td><td class="r">{fm(ht)}</td></tr>'
            f'<tr><td colspan="5">Aléas et imprévus 5 %</td><td class="r">{fm(al)}</td></tr>'
            f'<tr class="tot2"><td colspan="5">TOTAL TRAVAUX HT — proposition {c}</td><td class="r">{fm(tot)} FCFA</td></tr>'
            f'<tr><td colspan="5">soit, pour information</td><td class="r">{fm(tot / 655.957)} €</td></tr></table>')
dj = D.CHECK_DJONDJI
page(head('09 · Estimation', 'Estimation sommaire des travaux — ratios Éco-données divisés par deux') + f'''
<div class="g-est">
 <div><h3 class="ca-t">Proposition A — Le Toit-Stade</h3>{est_table('A')}</div>
 <div><h3 class="cb-t">Proposition B — Le Village-Canopée</h3>{est_table('B')}</div>
</div>
<div class="note"><b>Méthode.</b> Ratios extraits de la base Supabase « Eco-données » (classeur <i>BASE DE DONNEES DES COUTS DES PROJETS 5</i>, observations non validées économiquement), appliqués aux surfaces de chaque poste puis <b>divisés par deux</b> selon la consigne. Surfaces couvertes ouvertes et toiture-terrain comptées à 50 % du ratio hôtelier ; bassin au ratio hôtelier (hypothèse, pas de ratio piscine dans la base). Contrôle global : le ratio tout compris de Djondji Resort ({fm(dj[1])} FCFA/m² SPL, ÷2 = {fm(dj[1] / 2)}) donnerait {fm(D.prog_total('A', {'heb','com','spa','rest'}) * dj[1] / 2 / 1e6)} M FCFA pour A — l’ordre de grandeur est cohérent pour un produit balnéaire plus luxueux. <b>Exclus</b> : honoraires, TVA, foncier, mobilier/équipements hôteliers, raccordements CIE/SODECI, parking hors parcelle, études de sol.</div>''')

# ------------------------------------------------------------------ 16. références externes
REFS = [
 ('Hotel Football', 'Manchester (R.-U.), 2015', 'Hôtel fondé par d’anciens joueurs face à Old Trafford, avec un terrain de foot à 5 en toiture. Preuve qu’un terrain sur le toit est un produit hôtelier viable (A).'),
 ('Parkroyal on Pickering — WOHA', 'Singapour, 2013', '« Hôtel-dans-un-jardin » : la surface végétalisée totale dépasse celle du terrain grâce aux jardins suspendus. Principe du coefficient de biotope (A, B).'),
 ('Lycée Schorge — Kéré Architecture', 'Koudougou (Burkina Faso), 2016', 'Double toiture ventilée, claustras en terre, cheminées d’air : climat par le dessin en Afrique de l’Ouest (B).'),
 ('Heritance Kandalama — Geoffrey Bawa', 'Sri Lanka, 1994', 'Un hôtel qui se laisse envahir par la végétation, coursives ouvertes, une pièce d’épaisseur (A).'),
 ('Naman Retreat — Vo Trong Nghia', 'Da Nang (Vietnam), 2015', 'Pavillons hôteliers en bambou et toitures ventilées en climat tropical humide (B).'),
 ('Djondji Resort & ABYA Assinie — base de projets', 'Bénin / Côte d’Ivoire', 'Références internes de la base Supabase : lock-off, bande humide, halles ouvertes, appatam Ø 8 m, ceinture végétale (A, B).'),
]
page(head('10 · Références', 'D’autres projets qui nourrissent les deux propositions') + '<div class="g-refs">' +
     ''.join(f'<div class="ref"><h4>{a}</h4><div class="where">{b}</div><p>{c}</p></div>' for a, b, c in REFS) + '''</div>
<div class="g-ref2">''' + img(IMG('ref_djondji_p14.jpg'), 'Djondji — finitions : claustra brique de terre, deck bois, grès cérame effet pierre.') +
     img(IMG('ref_djondji_p24.jpg'), 'Djondji — bar de piscine circulaire en chaume.') +
     img(IMG('ref_djondji_p30.jpg'), 'Djondji — snack sous deux toitures pyramidales : modèle de la case commune (B).') + '</div>')

# ------------------------------------------------------------------ 17. avis senior
if os.path.exists(REVIEW):
    R = json.load(open(REVIEW))
    obs = ''.join(f'<tr><td><b>{html.escape(o["theme"])}</b></td><td>{html.escape(o["avis"])}</td><td class="crit-{o["gravite"].lower()}">{o["gravite"]}</td><td>{html.escape(o["suite"])}</td></tr>' for o in R['observations'])
    page(head('11 · Revue critique', 'Avis d’un architecte senior exerçant en Côte d’Ivoire', R.get('profil', '')) + f'''
<div class="g-rev">
 <div class="verdict"><h3>Verdict</h3><p>{html.escape(R['verdict'])}</p><h3>Préférence</h3><p>{html.escape(R['preference'])}</p></div>
 <table class="data rev"><tr><th>Thème</th><th>Observation</th><th>Gravité</th><th>Suite donnée dans ce dossier</th></tr>{obs}</table>
</div>
<p class="small">Revue réalisée par un agent IA instruit pour raisonner comme un architecte senior (25 ans de pratique en Côte d’Ivoire) ; elle ne remplace pas l’avis d’un architecte inscrit à l’Ordre des Architectes de Côte d’Ivoire, obligatoire pour le permis de construire.</p>''')

# ------------------------------------------------------------------ 18. hypothèses
page(head('12 · Hypothèses et suite', 'Ce qu’il faut vérifier avant l’APS') + '''
<div class="cols2">
 <div><h3>Hypothèses de ce dossier</h3><ul class="tight">
  <li>Reculs : 4 m au nord (coursives ouvertes), 3 m sur les autres limites — à confirmer avec le règlement du lotissement et la mairie de Jacqueville / MCLU.</li>
  <li>Voie d’accès à l’ouest, lue sur l’emprise en tireté du plan cadastral.</li>
  <li>Hauteur admissible ≥ R+2 + toiture ; 18 places de stationnement pouvant être mutualisées hors parcelle.</li>
  <li>Sol sableux sans sous-sol, nappe haute ; fondations à dimensionner par étude géotechnique G2.</li>
  <li>Altimétrie plane (aucun levé topographique fourni).</li>
  <li>Ratios Éco-données ÷ 2 : l’estimation est une enveloppe d’esquisse (± 25 %).</li>
 </ul></div>
 <div><h3>Prochaines étapes</h3><ol class="tight">
  <li>Choix A / B (ou hybride) avec le client, validation du nombre de clés et du positionnement (3* / 4*).</li>
  <li>Certificat d’urbanisme, levé topographique, étude de sol, étude de marché hôtelier.</li>
  <li>Convention de stationnement (lot voisin, parking communal) ou voiturier.</li>
  <li>APS : descente de charges (toit-stade), étude acoustique, sécurité incendie (ERP type O / N), simulation aéraulique.</li>
  <li>Plan de plantation avec un paysagiste (essences locales résistantes aux embruns).</li>
 </ol></div>
</div>''')

# ------------------------------------------------------------------ assemblage
CSS = open(os.path.join(ROOT, 'src', 'style.css')).read()
body = ''
n = 0
for b, cls, num in pages:
    n += 1
    foot = f'<footer><span>LE ONZE · hôtel-jardin · Jacqueville</span><span>Esquisse · octobre 2026</span><span>{n:02d}</span></footer>' if num else ''
    body += f'<section class="page {cls}">{b}{foot}</section>\n'
out = os.path.join(BUILD, 'dossier.html')
open(out, 'w').write(f'<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>LE ONZE — Hôtel-jardin à Jacqueville</title><style>{CSS}</style></head><body>{body}</body></html>')
print('pages:', n, '->', out)
