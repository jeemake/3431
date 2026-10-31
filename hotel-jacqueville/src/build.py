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

S = {c: D.biotope(c) for c in 'ABC'}
E = {c: D.estimatif(c) for c in 'ABC'}
G = {c: D.cout_global(c) for c in 'ABC'}
green = {c: S[c][0]['pleine_terre'] + S[c][0].get('pelouse', 0) for c in 'ABC'}
bati = lambda c: S[c][0]['bati'] + S[c][0].get('tech', 0)

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
      <div><b>2 % → {green['C'] / SITE.area * 100:.0f} %</b><span>de sol végétal : programme initial → proposition C recommandée</span></div>
      <div><b>14–15</b><span>clés, dont 3 à 6 suites familiales modulables</span></div>
      <div><b>3</b><span>propositions : A et B, puis C issue de la revue critique</span></div>
    </div>
    <p class="small"><b>A — Le Toit-Stade</b> · <b>B — Le Village-Canopée</b> · <b>C — Le Jardin du Onze</b> (recommandée).<br>
    Référence : Djondji Resort (Bénin). Coûts : ratios Éco-données divisés par deux. Relu par un architecte senior exerçant en Côte d’Ivoire.</p>
  </div>
</div>''', 'cv', num=False)

# ------------------------------------------------------------------ 2. synthèse
cost = {c: E[c][-1] for c in 'ABC'}
def card(c, cls, txt):
    return (f'<div class="card {cls}"><div class="tag">Proposition {c}' + (' · recommandée' if c == 'C' else '') + f'</div><h3>{D.VARIANTS[c]["nom"]}</h3><p>{txt}</p>'
            f'<table class="kv"><tr><td>Sol végétal</td><td>{green[c]:.0f} m² · {green[c] / SITE.area * 100:.0f} %</td></tr>'
            f'<tr><td>Coef. de biotope</td><td>{S[c][1]:.2f}</td></tr><tr><td>Clés</td><td>{D.CLES[c]}</td></tr>'
            f'<tr><td>Travaux HT (÷2)</td><td><b>{cost[c] / 1e6:,.0f} M FCFA</b></td></tr></table></div>')
page(head('00 · Synthèse', 'L’idée en une page') + f'''
<div class="cols4">
 <div><h3>Le constat</h3>
  <p>Le programme reçu totalise <b>1 851 m² de surfaces</b>, dont <b>1 345 m² posés au sol</b> pour un terrain de <b>1 120 m²</b>. Il ne tient pas. Le jardin y est réduit à <b>20 m²</b> (1,8 %) et le parking en consomme 400.</p>
  <h3>La stratégie</h3>
  <ol class="tight">
   <li><b>Empiler plutôt qu’étaler</b> : hébergement en R+2.</li>
   <li><b>Sortir la voiture</b> de la parcelle, sur un terrain voisin sécurisé.</li>
   <li><b>Mutualiser</b> : suites familiales par portes communicantes, lounge = salle de projection des matchs.</li>
   <li><b>Donner au foot sa place</b> : sur le toit (A) ou sur une pelouse (B, C).</li>
   <li><b>Climatiser par le dessin</b> : une pièce d’épaisseur, nord/sud, brise SO, débords.</li>
  </ol>
  <h3>La méthode</h3>
  <p class="small">A et B ont été soumises à un architecte senior exerçant en Côte d’Ivoire. Sa revue (14 observations, dont 7 graves) a produit <b>C</b>, qui garde le meilleur des deux et lève les risques.</p>
 </div>
 {card('A', 'a', 'Une barre R+2 coiffée d’un restaurant sous chaume et d’une cage de foot en toiture ; tout le sud en jardin.')}
 {card('B', 'b', 'Trois cases-tours sous chaume, une case commune ouverte et une pelouse-terrain au cœur du jardin.')}
 {card('C', 'c', 'La barre de A pour dormir, une case-restaurant et une pelouse-terrain au sol pour vivre, un toit solaire et végétal.')}
</div>
<div class="note">Montants : ratios Éco-données (FCFA HT/m²) <b>divisés par deux à la demande du maître d’ouvrage</b> (hypothèse de prix cible), provisions techniques et aléas 5 % inclus ; hors honoraires, TVA, foncier, mobilier (voir le coût global, section 12).</div>''')

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
 ('Restaurant 100 pers. + cuisine', '130 m²', '80 couv. en toiture + cuisine', '60 couv. sous chaume + 20', 'Le complément de couverts se fait en jardin / sur la pelouse lors des événements.'),
 ('Salle polyvalente & bureaux', '100 m²', 'supprimée', 'supprimée', 'Fusion : lounge, restaurant privatisable, toit (A) ou pelouse (B) pour les événements.'),
 ('Spa + salle de sport', '140 m²', '30 m² + fitness plein air', '54 m² (R+1, élévateur)', 'Le sport du client se fait dehors : cage, bassin de nage, bain froid de récupération.'),
 ('Supérette', '60 m²', 'boutique 18 m²', 'intégrée à l’accueil', 'Ouverte sur la rue pour la clientèle de passage.'),
 ('Zone technique & services', '200 m²', '17,5 + 24 m²', '17,5 + 14 m²', 'Technique compacte mais réelle : GE, bâche, micro-station, TGBT ; le back-of-house du personnel est indispensable (C).'),
 ('Piscine et plage', '100 m²', 'bassin 2,5 × 16 + bain froid', 'bassin 2,5 × 12', 'Un couloir de nage plutôt qu’un bassin d’agrément : moins de surface, plus d’usage sportif.'),
 ('Soccer cage', '150 m² au sol', 'cage 3c3 en toiture', '111 m² paspalum', 'A : surface gagnée au sol. B : la pelouse est le jardin.'),
 ('Parking 20 places', '400 m²', 'dépose + 2 places', 'dépose + 2 places', 'Places sur un terrain voisin sécurisé par bail ou achat : c’est le principal gisement d’espace vert (voir section 10).'),
 ('Jardin & cheminement', '20 m²', f'{S["A"][0]["pleine_terre"]:.0f} m²', f'{green["B"]:.0f} m²', 'Jardin-forêt d’essences locales : badamier, fromager, cocotier, filao, vétiver.'),
]
CCOL = ['8 × 25,2 m²', '4 × 37,8 m²', '3 lock-off', '2 × 50,4 m²', 'coursives ouvertes', '62 + 14 m²', '60 + 20 couv. au sol', 'supprimée', 'cabane de massage + plein air', 'dans le lobby', '20 m² + 98 m² BOH', 'bassin 2,5 × 11 + bain froid', '99 m² paspalum au sol', 'dépose + 2 pl. + voie de service', None]
CCOL[-1] = f'{green["C"]:.0f} m²'
rows = ''.join(f'<tr><td><b>{a}</b></td><td>{b}</td><td class="ca">{c}</td><td class="cb">{d}</td><td class="cc">{cc}</td><td class="cm">{e}</td></tr>' for (a, b, c, d, e), cc in zip(CH, CCOL))
page(head('02 · Challenger le programme', 'Le programme ne tient pas : on le resserre pour libérer le sol',
          'Chaque ligne du programme initial a été questionnée : garder, fusionner, déplacer (toit, hors parcelle) ou supprimer.') + f'''
<div class="g-ch">
 <table class="data ch"><tr><th>Intitulé initial</th><th>Initial</th><th class="ca">A · Toit-Stade</th><th class="cb">B · Village-Canopée</th><th class="cc">C · Jardin du Onze</th><th>Pourquoi</th></tr>{rows}</table>
 <div>
  {fig(SVG('chart_sols'), 'Occupation du sol (m² et % du terrain). Les valeurs détaillées figurent dans le tableau ci-contre et en annexe.')}
  <table class="data"><tr><th></th><th>Initial</th><th>A</th><th>B</th><th>C</th></tr>
   <tr><td>Surfaces closes (SU)</td><td>1 101 m²</td>{''.join(f"<td>{D.prog_total(c, {'heb','com','spa','rest','boh'}):.0f} m²</td>" for c in 'ABC')}</tr>
   <tr><td>Extérieurs couverts</td><td>—</td>{''.join(f"<td>{D.prog_total(c, {'ext'}):.0f} m²</td>" for c in 'ABC')}</tr>
   <tr><td>Clés / chambres</td><td>15 / 18</td><td>15 / 15</td><td>15 / 15</td><td>14 / 14</td></tr>
   <tr><td>Emprise bâtie</td><td>≈ 695 m²</td>{''.join(f'<td>{bati(c):.0f} m²</td>' for c in 'ABC')}</tr>
   <tr><td>Sol végétal (pleine terre + pelouse)</td><td>20 m²</td>{''.join(f'<td><b>{green[c]:.0f} m²</b></td>' for c in 'ABC')}</tr></table>
  <p class="small">Les chambres proposées sont plus grandes que l’initial, qui annonçait des surfaces sans salle d’eau. Les chambres en moins sont compensées par le lock-off : une junior et une deluxe communicantes forment une suite familiale.</p>
 </div>
</div>''')

# ------------------------------------------------------------------ 5. référence
page(head('03 · Référence', 'Djondji Resort, Ouidah (Bénin) — ce qu’on lui emprunte',
          'Seul resort balnéaire de ma base de références : même cordon dunaire entre océan et lagune, même climat, même clientèle de week-end.') + f'''
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
  <p class="src">Source : présentation d’appel d’offres, janvier 2025 (base de références personnelle).</p>
 </div>
</div>''')

# ------------------------------------------------------------------ 6. bioclimatique
page(head('04 · Principes bioclimatiques', 'Climatiser par l’architecture avant la machine') + f'''
<div class="g-bio">
 <div class="bio-list">
  <div><h4>1 · Orientation</h4><p>Barres et tours d’une seule pièce d’épaisseur, façades longues au nord et au sud (écart 4,5°). Pignons est/ouest aveugles et végétalisés (A) ou en claustra de brique de terre (B).</p></div>
  <div><h4>2 · Ventilation traversante</h4><p>Chaque chambre s’ouvre sur une loggia au sud et sur une coursive au nord par impostes à jalousies : la brise SO traverse la chambre. <b>Double mode</b> : ouvert ventilé (jalousies à moustiquaire, ventilateur) ou fermé climatisé (menuiserie étanche, split inverter coupé à l’ouverture).</p></div>
  <div><h4>3 · Protection solaire</h4><p>À 5,2° N, le soleil de midi culmine à 61° au sud (décembre) et 72° au nord (juin) : une loggia de 1,8 m et une coursive de 1,8 m suffisent. Persiennes coulissantes en iroko sur toute la façade sud.</p></div>
  <div><h4>4 · Toiture ventilée</h4><p>Chaume synthétique Palmex sur charpente bois, lame d’air, faîtage ventilé : l’air chaud s’évacue au-dessus du restaurant (A) et des suites premium (B). Dalle de toit isolée sous la cage de foot.</p></div>
  <div><h4>5 · Eau</h4><p>Récupération des eaux de pluie (≈ 340 m² de toiture × 1 900 mm ≈ 500 m³/an) en cuves pour arrosage et chasses ; phyto-épuration des eaux grises en jardin filtrant ; sol perméable partout ailleurs.</p></div>
  <div><h4>6 · Végétation</h4><p>Jardin-forêt sur 45 à 55 % du terrain : canopée de badamiers et fromagers, cocotiers, filaos en lisière, couvre-sols dunaires (ipomée, vétiver). L’ombre portée et l’évapotranspiration rafraîchissent l’air qui entre dans les chambres (gain à quantifier par simulation en APS).</p></div>
  <div><h4>7 · Énergie</h4><p>Pergola photovoltaïque possible sur la toiture de cuisine et les locaux techniques (≈ 15–20 kWc), eau chaude solaire, LED, groupe électrogène en secours.</p></div>
  <div><h4>8 · Matériaux</h4><p>Bois dur local, brique de terre stabilisée (claustras), enduits à la chaux, sols en grès cérame effet pierre comme à Djondji. Peu d’inertie en climat humide : on cherche la ventilation, pas le stockage de chaleur.</p></div>
 </div>
 {fig(SVG('coupe_A'), 'Coupe bioclimatique de la proposition A : brise SO rafraîchie par le jardin, protection solaire par loggias, air chaud évacué sous le chaume, eaux de pluie vers cuves.')}
</div>''')

# ------------------------------------------------------------------ 7-9. Variante A
sA, sB, sC = S['A'][0], S['B'][0], S['C'][0]
def kpis(c):
    return (f'<div class="kpis"><div><b>{green[c]:.0f} m²</b><span>sol végétal ({green[c] / SITE.area * 100:.0f} %)</span></div>'
            f'<div><b>{bati(c):.0f} m²</b><span>emprise bâtie ({bati(c) / SITE.area * 100:.0f} %)</span></div>'
            f'<div><b>{S[c][1]:.2f}</b><span>coefficient de biotope</span></div><div><b>{D.CLES[c]}</b><span>clés</span></div></div>')
page(head('05 · Proposition A', 'Le Toit-Stade', 'Une barre, un toit qui joue au football, un jardin entier au sud.') + f'''
<div class="g-var">
 {fig(SVG('masse_A'), 'Plan masse A — la barre s’adosse à la limite nord (recul 4 m planté), tout le sud est jardin.')}
 <div>
  {img(PNG('axo3d_A_sw.png'), 'Maquette 3D — vue depuis le sud-ouest : restaurant sous chaume et cage de foot en toiture.')}
  {kpis('A')}
  <p><b>Le parti.</b> Toute la construction tient dans une barre de 32,4 × 10,6 m sur trois niveaux, posée le long de la seule limite bien orientée. Le footballeur retrouve son terrain sur le toit (cage 3 contre 3), à côté d’un restaurant-bar sous une grande toiture de chaume ; la vue vers l’océan, au-dessus des cocotiers, reste à vérifier par une prise de vue drone à +11 m. Au sol, il ne reste qu’un jardin, un couloir de nage et un bain froid pour la récupération.</p>
  <p class="small">7 deluxe · 6 suites junior · 2 suites premium (R+2 ouest, hors aplomb de la cage) · 3 suites familiales en lock-off.</p>
 </div>
</div>''')
page(head('05 · Proposition A', 'Plans de niveaux — trame 3,60 m, 9 travées') + f'''
<div class="g-plans">
 {fig(SVG('A_R0'))}{fig(SVG('A_R1'))}{fig(SVG('A_R2'))}{fig(SVG('A_toit'))}
</div>
<p class="small">Noyau central escalier + ascenseur 8 personnes, qui sert aussi de monte-charge pour la cuisine de toit. Second dégagement par l’escalier extérieur du pignon ouest : il tombe dans le recul, et c’est l’un des points qui ont conduit à la proposition C.</p>''')
page(head('05 · Proposition A', 'Ambiances, forces et risques') + f'''
<div class="g-amb">
 {img(IMG('A_toit.jpg'), 'Le toit au coucher du soleil : cage de foot et restaurant-bar sous chaume.', ia=True)}
 {img(IMG('A_jardin.jpg'), 'Le jardin-forêt et le couloir de nage au pied des loggias.', ia=True)}
 {img(PNG('axo3d_A_se.png'), 'Maquette 3D — vue depuis le sud-est : pignon est végétalisé, filets de la cage.')}
 <div class="pc"><h3>Forces</h3><ul class="tight"><li>Le maximum de pleine terre ({sA['pleine_terre'] / SITE.area * 100:.0f} %) et un jardin d’un seul tenant.</li><li>Un produit unique : le toit-stade et son restaurant, ouverts aux clients extérieurs.</li><li>Ascenseur : toutes les chambres accessibles PMR.</li></ul>
 <h3>Risques relevés par la revue</h3><ul class="tight"><li><b>Sécurité incendie</b> : environ 100 personnes à +9,80 m, une cuisine sous chaume au-dessus de chambres et un 2e escalier dans le recul. Risque de refus.</li><li><b>Structure, étanchéité, acoustique</b> de la cage au-dessus des chambres (provision de 45 M FCFA avant ÷2).</li><li><b>R+3 de fait</b> (faîtage ≈ +17 m) avec un recul nord de 4 m : prospect H/2 non respecté.</li><li>Back-of-house, technique et stationnement insuffisants sur la parcelle.</li></ul></div>
</div>''')

# ------------------------------------------------------------------ 10-12. Variante B
page(head('06 · Proposition B', 'Le Village-Canopée', 'Trois cases-tours, une case commune, une pelouse où l’on joue pieds nus.') + f'''
<div class="g-var">
 {fig(SVG('masse_B'), 'Plan masse B — trois cases-tours au nord séparées par des failles plantées, case commune et pelouse-terrain au sud.')}
 <div>
  {img(PNG('axo3d_B_sw.png'), 'Maquette 3D — vue depuis le sud-ouest.')}
  {kpis('B')}
  <p><b>Le parti.</b> Le vocabulaire de Djondji (poteaux bois, chaume, claustras, halles ouvertes) passe à la verticale. Entre les trois tours, des failles de 2,7 m accueillent les escaliers extérieurs : un pour T1, un partagé par T2 et T3 grâce à des passerelles. Les palmiers y poussent et la brise y passe. La pelouse de paspalum de 12,6 × 8,8 m sert de terrain le matin et de jardin d’événements le soir, dans le prolongement du restaurant.</p>
  <p class="small">6 deluxe · 6 suites junior · 3 suites premium sous chaume · jusqu’à 6 suites familiales · 6 clés au RDC, dont 2 adaptées PMR.</p>
 </div>
</div>''')
page(head('06 · Proposition B', 'Plans — case-tour (×3) et case commune') + f'''
<div class="g-plansB">
 {fig(SVG('B_tour_R0R1'))}{fig(SVG('B_tour_R2'))}{fig(SVG('B_case_commune'), '', 'wide')}
</div>
<div class="g-plansB2">
 {fig(SVG('coupe_B'), 'Coupe bioclimatique B : tour d’une pièce d’épaisseur, suite premium sous chaume avec lanterne de ventilation, case commune ouverte.')}
 <div><h3>Comment ça se construit</h3><ul class="tight">
  <li>Ossature poteaux-poutres béton (trame 3,60 / 5,40 m), poteaux de façade habillés de bois dur ; dalles BA.</li>
  <li>Charpente bois traitée (classe 4, anti-termites), chaume synthétique ignifugé et fixé contre l’arrachement, pente ≥ 45°.</li>
  <li>Pignons ouest en claustra de briques de terre comprimée (BTC).</li>
  <li>Deux escaliers extérieurs béton à marches bois, abrités par les débords ; passerelles T2/T3.</li>
  <li>Case commune : poteaux bois massif 30 × 30 sur plots béton ; R+1 desservi par un élévateur PMR et un monte-linge.</li>
 </ul></div>
</div>''')
page(head('06 · Proposition B', 'Ambiances, forces et risques') + f'''
<div class="g-amb">
 {img(IMG('B_village.jpg'), 'Les cases-tours depuis la pelouse-terrain : escaliers et palmiers dans les failles.', ia=True)}
 {img(IMG('B_case.jpg'), 'La case commune : restaurant ouvert sous double toiture de chaume.', ia=True)}
 {img(PNG('axo3d_B_se.png'), 'Maquette 3D — vue depuis le sud-est : pelouse-terrain et cages.')}
 <div class="pc"><h3>Forces</h3><ul class="tight"><li>Échelle domestique, identité forte, filiation directe avec Djondji.</li><li>Porosité au vent : les failles ventilent aussi le jardin.</li><li>Foot sur gazon, au sol, sans risque pour les chambres.</li><li>Chantier phasable tour par tour.</li></ul>
 <h3>Risques relevés par la revue</h3><ul class="tight"><li>Pas d’ascenseur : seules les 6 clés du RDC sont accessibles.</li><li>Trois toitures de chaume sur R+2 : risque feu et vent, entretien tous les 15 à 20 ans ; coût au m² plus élevé (coefficient de forme 1,10).</li><li>Case commune contrainte par les reculs ; back-of-house du personnel insuffisant.</li><li>Pelouse naturelle à arroser en saison sèche (eau de pluie stockée).</li></ul></div>
</div>''')

# ------------------------------------------------------------------ revue senior
R = json.load(open(REVIEW))
obs = ''.join(f'<tr><td><b>{html.escape(o["theme"])}</b></td><td>{html.escape(o["avis"])}</td><td class="crit-{o["gravite"].lower()}">{o["gravite"]}</td><td>{html.escape(o["suite"])}</td></tr>' for o in R['observations'])
page(head('07 · Revue critique', 'L’avis d’un architecte senior exerçant en Côte d’Ivoire', R['profil']) + f'''
<div class="g-rev">
 <div class="verdict"><h3>Verdict</h3><p>{html.escape(R['verdict'])}</p><h3>Préférence</h3><p>{html.escape(R['preference'])}</p>
 <p class="small">Revue menée par un agent IA chargé de raisonner comme un architecte senior (25 ans de pratique en Côte d’Ivoire). Elle ne remplace pas l’avis d’un architecte inscrit à l’Ordre, obligatoire pour le permis de construire.</p></div>
 <table class="data rev"><tr><th>Thème</th><th>Observation</th><th>Gravité</th><th>Suite donnée dans ce dossier</th></tr>{obs}</table>
</div>''', 'rev')

# ------------------------------------------------------------------ C recommandée
page(head('08 · Proposition C — recommandée', 'Le Jardin du Onze', 'Dormir dans la barre, vivre dans le jardin, jouer sur l’herbe.') + f'''
<div class="g-var">
 {fig(SVG('masse_C'), 'Plan masse C — barre R+2 en recul de 5 m au nord, case-restaurant et pelouse-terrain au sud, voie de service séparée.')}
 <div>
  {img(PNG('axo3d_C_sw.png'), 'Maquette 3D — vue depuis le sud-ouest : pergola photovoltaïque et toiture végétalisée, case-restaurant sous chaume au sol.')}
  {kpis('C')}
  <p><b>Le parti.</b> C reprend ce qui fonctionne. De A : la barre d’une pièce d’épaisseur, son ascenseur et son jardin au sud. De B : la case ouverte sous chaume et le foot sur l’herbe. Elle enlève tout ce qui faisait peur : plus de public ni de cuisine en toiture, plus de chaume au-dessus des chambres, plus de cage sur l’étanchéité. Le toit produit l’électricité (≈ 25 kWc) et retient la pluie. Le prix à payer est de 7 points de sol végétal par rapport à A, pour un hôtel qui fonctionne vraiment : cuisine, personnel, livraisons et technique sont dessinés.</p>
  <p class="small">8 deluxe (dont 1 PMR) · 4 suites junior · 2 suites premium · 3 suites familiales en lock-off · restaurant de 60 couverts + 20 en terrasse.</p>
 </div>
</div>''', 'c')
page(head('08 · Proposition C — recommandée', 'Plans et coupe') + f'''
<div class="g-plans">
 {fig(SVG('C_R0'))}{fig(SVG('A_R1'), 'R+1 identique à A : 4 suites junior + 2 deluxe, 2 lock-off.')}{fig(SVG('C_R2'))}{fig(SVG('C_toit'))}
</div>''', 'c')
CHG = [('Restaurant', 'en toiture, sous chaume, 80 couverts', 'au sol, case ouverte 60 + 20 couverts'),
       ('Cuisine', '30 m² en toiture, 1 ascenseur', '40 m² tout électrique au RDC + 22 m² d’économat/CF'),
       ('Foot', 'cage 3c3 synthétique au-dessus des chambres', 'pelouse paspalum 12,4 × 8 au sol, buts amovibles'),
       ('Toiture', 'lieu public ≈ 100 pers.', 'terrasse ≤ 19 pers., PV 25 kWc, toiture végétalisée'),
       ('Recul nord / hauteur', '4 m · faîtage ≈ +17 m', '5 m · acrotère +9,80 m (H/2 = 4,9 m)'),
       ('Back-of-house', 'absent', '98 m² : vestiaires, réfectoire, lingerie, déchets'),
       ('Technique', '17,5 m² dans le recul', 'bloc 20 m² + bâche enterrée, en zone constructible'),
       ('Livraisons', 'mêlées à la dépose clients', 'voie de service nord séparée'),
       ('Clés', '15', '14 (2 deluxe au RDC ont cédé la place au personnel)')]
page(head('08 · Proposition C — recommandée', 'Ce qui change par rapport à A') + f'''
<div class="g-cC">
 <div>{fig(SVG('coupe_C'), 'Coupe C : prospect nord respecté, toit ventilé et végétalisé, case-restaurant isolée des chambres.')}
 {img(PNG('axo3d_C_se.png'), 'Maquette 3D — vue depuis le sud-est.')}</div>
 <div><table class="data cmp"><tr><th></th><th class="ca">A</th><th class="cc">C</th></tr>{''.join(f'<tr><td><b>{a}</b></td><td>{x}</td><td>{y}</td></tr>' for a, x, y in CHG)}</table>
 <h3>Pourquoi C est la bonne base pour l’APS</h3>
 <ul class="tight"><li>Elle reste réglementairement simple : un ERP de petite taille au RDC et un hôtel de 14 chambres.</li>
 <li>L’exploitation tient : flux client, personnel, livraisons et déchets sont séparés.</li>
 <li>Elle garde le récit pour le client footballeur : un terrain au milieu du jardin, avec bain froid et bassin de nage pour la récupération.</li>
 <li>Elle conserve près de la moitié du terrain en sol vivant ({green['C'] / SITE.area * 100:.0f} %).</li></ul></div>
</div>''', 'c')

# ------------------------------------------------------------------ typologies
page(head('09 · Les chambres', 'Un module unique, trois produits, une suite familiale sans m² en plus') + f'''
<div class="g-typo">
 {img(IMG('chambre.jpg'), 'Chambre : persiennes coulissantes ouvertes sur la loggia, ventilateur de plafond, imposte haute pour la ventilation traversante.', ia=True)}
 <div>
  <table class="data"><tr><th>Produit</th><th>Largeur</th><th>Surface (SdE incl.)</th><th>Loggia</th><th>A</th><th>B</th><th>C</th></tr>
  <tr><td>Deluxe</td><td>3,60 m · 1 trame</td><td>25,2 m²</td><td>6,5 m²</td><td>7</td><td>6</td><td>8</td></tr>
  <tr><td>Suite junior</td><td>5,40 m · 1,5 trame</td><td>37,8 m²</td><td>9,7 m²</td><td>6</td><td>6</td><td>4</td></tr>
  <tr><td>Suite premium</td><td>7,20 m (A, C) · 9,00 m (B)</td><td>50,4 / 63,0 m²</td><td>13–16 m²</td><td>2</td><td>3</td><td>2</td></tr>
  <tr><td><b>Suite familiale</b></td><td colspan="3">junior (canapé-lit) + deluxe par porte communicante : 63 m², 2 SdE, 2 loggias</td><td>3</td><td>6</td><td>3</td></tr></table>
  <h3>Anatomie d’une chambre, de la coursive à la loggia</h3>
  <ol class="tight">
   <li><b>Coursive nord 1,80 m</b> : ouverte et ombragée, avec un écran planté côté voisin.</li>
   <li><b>Bande humide 2,00 m</b> : niche d’entrée avec penderie, WC, douche à l’italienne, simple vasque dans les deluxe (double dans les suites).</li>
   <li><b>Chambre 5,00 m</b> : lit face à la vue, imposte haute acoustique, ventilateur, split inverter.</li>
   <li><b>Loggia 1,80 m</b> : persiennes coulissantes en iroko, moustiquaires, bacs plantés.</li>
  </ol>
  {fig(SVG('typo_module'), 'Paire lock-off junior + deluxe : 2 clés ou 1 suite familiale de 63 m².')}
 </div>
</div>''')

# ------------------------------------------------------------------ points techniques
pt_c = sC['pleine_terre']
page(head('10 · Points techniques', 'Ce qui fait tourner l’hôtel : stationnement, réseaux, littoral') + f'''
<div class="cols3">
 <div><h3>Stationnement</h3>
  <p>Au pic du samedi, il faut compter <b>35 à 45 véhicules</b> (clients de l’hôtel, du restaurant et des événements, personnel). La parcelle n’accueille que la dépose-minute et 2 places (PMR, livraison).</p>
  <ul class="tight"><li><b>Solution retenue</b> : un terrain de 600 à 900 m² à moins de 150 m, sécurisé par achat ou bail notarié et <b>joint au permis</b>, planté en evergreen et gardienné.</li>
  <li><b>Repli</b> : 8 places evergreen sur la parcelle (≈ 200 m²). La pleine terre de C passe alors de {pt_c:.0f} m² à {pt_c - 200:.0f} m² ({(pt_c - 200) / SITE.area * 100:.0f} %).</li>
  <li>Foncier non chiffré dans l’estimatif.</li></ul>
 </div>
 <div><h3>Réseaux autonomes</h3><ul class="tight">
  <li><b>Assainissement</b> : pas d’égout à Jacqueville. Micro-station d’environ 70 EH + bac à graisse, rejet en tranchée d’infiltration sous le jardin, à valider par l’étude de sol.</li>
  <li><b>Eau</b> : alimentation SODECI intermittente. Bâche de 40 m³ enterrée et lestée, surpresseur, réserve incendie ; forage à éviter (risque d’eau saumâtre).</li>
  <li><b>Énergie</b> : GE de 160 kVA capoté avec cuve et dépotage depuis la voie ; PV de 25 kWc en toiture (C) ; eau chaude solaire.</li>
  <li><b>Eaux pluviales</b> : environ 340 m² de toiture × 1 900 mm ≈ 500 m³/an, stockés en cuves pour l’arrosage de la pelouse et les chasses d’eau.</li></ul>
 </div>
 <div><h3>Durabilité en bord de mer</h3><ul class="tight">
  <li>Béton : enrobage ≥ 4 à 5 cm, ciment adapté à l’ambiance saline, aciers galvanisés à chaud, quincaillerie inox A4.</li>
  <li>Bois : poteaux sur socles béton hors sol, traitement classe 4 et barrière anti-termites.</li>
  <li>Chaume synthétique : procès-verbal de réaction au feu, fixation testée au vent, remplacement tous les 15 à 20 ans.</li>
  <li>Climatisation et ascenseur : modèles traités bord de mer ; contrat de maintenance avec une société d’Abidjan.</li>
  <li>Étude géotechnique G2 avant l’APS : radier ou micro-pieux selon les résultats.</li>
  <li>Plage : partenariat avec une paillote sur la plage, cheminement balisé ou navette.</li></ul>
 </div>
</div>''')

# ------------------------------------------------------------------ comparatif
def tri(f):
    return ''.join(f'<td>{f(c)}</td>' for c in 'ABC')
cmp_rows = [
 ('Sol végétal (pleine terre + pelouse)', tri(lambda c: f"{green[c]:.0f} m² · {green[c] / SITE.area * 100:.0f} %")),
 ('Coefficient de biotope', tri(lambda c: f"{S[c][1]:.2f}")),
 ('Emprise bâtie', tri(lambda c: f"{bati(c):.0f} m²")),
 ('Surfaces closes (SU)', tri(lambda c: f"{D.prog_total(c, {'heb','com','spa','rest','boh'}):.0f} m²")),
 ('Clés / suites familiales', '<td>15 / 3</td><td>15 / 6</td><td>14 / 3</td>'),
 ('Restaurant', '<td>80 couv. en toiture</td><td>60 couv. + 20 sur pelouse</td><td>60 couv. + 20 en terrasse, au sol</td>'),
 ('Football', '<td>cage 3c3 en toiture</td><td>pelouse 12,6 × 8,8</td><td>pelouse 12,4 × 8</td>'),
 ('Hauteur / recul nord', '<td>≈ +17 m · 4 m</td><td>≈ +14,6 m · 4 m</td><td>+9,80 m + pergola · 5 m</td>'),
 ('Accessibilité PMR', '<td>totale</td><td>RDC seulement</td><td>totale</td>'),
 ('Back-of-house dessiné', '<td>non</td><td>partiel</td><td>oui</td>'),
 ('Risque réglementaire', '<td class="crit-haute">élevé</td><td class="crit-moyenne">moyen</td><td class="crit-faible">faible</td>'),
 ('Travaux HT (÷2, provisions incluses)', tri(lambda c: f"<b>{E[c][-1] / 1e6:,.0f} M FCFA</b>")),
 ('Coût global par clé (voir section 12)', tri(lambda c: f"{G[c]['total'] / D.CLES[c] / 1e6:,.1f} M FCFA".replace('.', ','))),
]
page(head('11 · Comparaison', 'A, B ou C ?') + f'''
<div class="g-cmp">
 <table class="data cmp"><tr><th></th><th class="ca">A · Toit-Stade</th><th class="cb">B · Village-Canopée</th><th class="cc">C · Jardin du Onze</th></tr>
 {''.join(f'<tr><td><b>{a}</b></td>{r}</tr>' for a, r in cmp_rows)}</table>
 <div>
  <h3>Recommandation</h3>
  <p><b>Partir de C pour l’APS.</b> C’est la proposition qui tient à la fois la réglementation, l’exploitation et le budget, tout en gardant près de la moitié du terrain en sol vivant.</p>
  <p><b>A</b> reste l’image la plus forte. Si le client tient au toit-stade, il faut le traiter comme un ouvrage à part : structure, étanchéité, acoustique, dégagements et étude de sécurité incendie dès l’APS, avec un surcoût assumé.</p>
  <p><b>B</b> a le plus de charme, mais son exploitation est la plus difficile : pas d’ascenseur, trois toitures de chaume en hauteur.</p>
  {fig(SVG('chart_sols'))}
 </div>
</div>''')

# ------------------------------------------------------------------ estimatif
dj = D.CHECK_DJONDJI
def est_table(c, compact=False):
    rows, prov, hr, ht, al, tot = E[c]
    tr = ''.join(f'<tr><td>{D.LIB_CAT[k]}</td><td class="r">{fm1(s)}</td><td class="src">{lib}</td><td class="r">{fm(r)}</td><td class="r">{fm(r2)}</td><td class="r"><b>{fm(m)}</b></td></tr>'
                 for k, lib, s, r, r2, m in rows)
    tp = ''.join(f'<tr><td colspan="3" class="src">{lib}</td><td class="r">{fm(m)}</td><td class="r">÷ 2</td><td class="r"><b>{fm(m2)}</b></td></tr>' for lib, m, m2 in prov)
    return (f'<table class="data est"><tr><th>Poste</th><th>m²</th><th>Ratio source</th><th>FCFA/m²</th><th>÷ 2</th><th>Montant HT</th></tr>{tr}'
            f'<tr class="tot"><td colspan="5">Sous-total ratios</td><td class="r">{fm(hr)}</td></tr>'
            f'<tr><th colspan="6">Provisions hors ratios (revue critique)</th></tr>{tp}'
            f'<tr><td colspan="5">Aléas et imprévus 5 %</td><td class="r">{fm(al)}</td></tr>'
            f'<tr class="tot2"><td colspan="5">TOTAL TRAVAUX HT — {c}</td><td class="r">{fm(tot)} FCFA</td></tr></table>')
page(head('12 · Estimation', 'Proposition C — estimation sommaire des travaux') + f'''
<div class="g-estC">
 <div>{est_table('C')}</div>
 <div>
  <h3>Coût global d’opération (hors foncier)</h3>
  <table class="data"><tr><th></th><th class="ca">A</th><th class="cb">B</th><th class="cc">C</th></tr>
   <tr><td>Travaux HT (÷2)</td>{tri(lambda c: fm(G[c]['travaux'] / 1e6) + ' M')}</tr>
   <tr><td>Honoraires et études 10 %</td>{tri(lambda c: fm(G[c]['honoraires'] / 1e6) + ' M')}</tr>
   <tr><td>TVA 18 %</td>{tri(lambda c: fm(G[c]['tva'] / 1e6) + ' M')}</tr>
   <tr><td>Mobilier et équipements hôteliers (8 M FCFA/clé, non divisé)</td>{tri(lambda c: fm(G[c]['ffe'] / 1e6) + ' M')}</tr>
   <tr class="tot2"><td>Total TTC (FCFA)</td>{tri(lambda c: fm(G[c]['total'] / 1e6) + ' M')}</tr>
   <tr class="tot"><td>Par clé</td>{tri(lambda c: fm1(G[c]['total'] / D.CLES[c] / 1e6) + ' M')}</tr>
   <tr><td>Pour information, en euros par clé</td>{tri(lambda c: fm(G[c]['total'] / D.CLES[c] / 655.957) + ' €')}</tr></table>
  <div class="note2"><b>Méthode.</b> Ratios extraits de la base « Eco-données » (classeur <i>BASE DE DONNEES DES COUTS DES PROJETS 5</i> ; fiches d’esquisse non validées économiquement). Ils sont appliqués aux surfaces de chaque poste puis <b>divisés par deux selon la consigne</b> : il s’agit d’une <b>hypothèse de prix cible</b>, pas d’une précision. Les provisions hors ratios sont des hypothèses de l’auteur, elles aussi divisées par deux pour rester cohérentes. B porte un coefficient de forme de 1,10. Contrôle : le ratio tout compris de Djondji Resort ({fm(dj[1])} FCFA/m², ÷2 = {fm(dj[1] / 2)}) donnerait {fm(D.prog_total('C', {'heb','com','spa','rest','boh'}) * dj[1] / 2 / 1e6)} M FCFA pour C, contre {fm(E['C'][-1] / 1e6)} M ici. L’écart de {(D.prog_total('C', {'heb','com','spa','rest','boh'}) * dj[1] / 2 / E['C'][-1] - 1) * 100:.0f} % correspond au niveau de gamme supérieur de Djondji ; c’est la marge d’incertitude à garder en tête. <b>Exclus</b> : foncier (parcelle et parking), raccordements CIE/SODECI, études de sol, frais financiers.</div>
 </div>
</div>''', 'c')
page(head('12 · Estimation', 'Propositions A et B — estimation sommaire des travaux') + f'''
<div class="g-est">
 <div><h3 class="ca-t">A — Le Toit-Stade</h3>{est_table('A')}</div>
 <div><h3 class="cb-t">B — Le Village-Canopée</h3>{est_table('B')}</div>
</div>''')

# ------------------------------------------------------------------ références externes
REFS = [
 ('Hotel Football', 'Manchester (R.-U.), 2015', 'Hôtel fondé par d’anciens joueurs face à Old Trafford, avec un terrain en toiture. Il montre qu’un terrain sur le toit peut être un produit hôtelier (A).'),
 ('Parkroyal on Pickering — WOHA', 'Singapour, 2013', '« Hôtel dans un jardin » : la surface végétalisée totale dépasse celle du terrain grâce aux jardins suspendus. C’est le principe du coefficient de biotope (A, C).'),
 ('Lycée Schorge — Kéré Architecture', 'Koudougou (Burkina Faso), 2016', 'Double toiture ventilée, claustras en terre : le climat traité par le dessin en Afrique de l’Ouest (B, C).'),
 ('Heritance Kandalama — Geoffrey Bawa', 'Sri Lanka, 1994', 'Un hôtel envahi par la végétation, avec des coursives ouvertes et des ailes d’une pièce d’épaisseur (A, C).'),
 ('Naman Retreat — Vo Trong Nghia', 'Da Nang (Vietnam), 2015', 'Pavillons hôteliers à toitures ventilées en climat tropical humide (B).'),
 ('Djondji Resort & ABYA Assinie', 'Bénin / Côte d’Ivoire', 'Mes références : lock-off, bande humide, halles ouvertes, appatam de 8 m de diamètre, ceinture végétale (A, B, C).'),
]
page(head('13 · Références', 'D’autres projets qui nourrissent les propositions') + '<div class="g-refs">' +
     ''.join(f'<div class="ref"><h4>{a}</h4><div class="where">{b}</div><p>{c}</p></div>' for a, b, c in REFS) + '''</div>
<div class="g-ref2">''' + img(IMG('ref_djondji_p14.jpg'), 'Djondji — finitions : claustra brique de terre, deck bois, grès cérame effet pierre.') +
     img(IMG('ref_djondji_p24.jpg'), 'Djondji — bar de piscine circulaire en chaume.') +
     img(IMG('ref_djondji_p30.jpg'), 'Djondji — snack sous deux toitures pyramidales : modèle de la case commune (B) et de la case-restaurant (C).') + '</div>')

# ------------------------------------------------------------------ hypothèses
page(head('14 · Hypothèses et suite', 'Ce qu’il faut vérifier avant l’APS') + '''
<div class="cols2">
 <div><h3>Hypothèses de ce dossier</h3><ul class="tight">
  <li>Destination hôtelière et ERP admise sur le lot 2511 (lotissement à vocation probablement résidentielle) : <b>à confirmer en premier</b>.</li>
  <li>Reculs : 4 m au nord (A, B), 5 m (C, prospect H/2), 3 m ailleurs ; hauteur admissible ≥ R+2.</li>
  <li>Voie d’accès à l’ouest, lue sur l’emprise en tireté du plan cadastral.</li>
  <li>Stationnement sur un terrain voisin, à sécuriser (voir section 10).</li>
  <li>Sol sableux, nappe haute, terrain plat (aucun levé topographique fourni).</li>
  <li>Estimation : ratios d’esquisse divisés par deux = prix cible ; marge d’incertitude d’environ −20 % / +50 %.</li>
 </ul></div>
 <div><h3>Prochaines étapes</h3><ol class="tight">
  <li>Certificat d’urbanisme et cahier des charges du lotissement ; validation de la destination.</li>
  <li>Levé topographique, étude géotechnique G2, prise de vue par drone à +11 et +14 m (vue mer).</li>
  <li>Sécurisation du terrain de stationnement ; partenariat avec une paillote de plage.</li>
  <li>Business case simplifié : prix moyen et taux d’occupation semaine / week-end à Jacqueville, recettes du restaurant, du terrain et des événements.</li>
  <li>APS sur la base de C : note de sécurité incendie (types O / N), plan des réseaux, simulation aéraulique, salles d’eau au 1/50, plan de plantation avec un paysagiste.</li>
 </ol></div>
</div>''')

# ------------------------------------------------------------------ assemblage
CSS = open(os.path.join(ROOT, 'src', 'style.css')).read()
body = ''
n = 0
for b, cls, num in pages:
    n += 1
    foot = f'<footer><span>LE ONZE · hôtel-jardin · Jacqueville</span><span>Esquisse révisée après revue critique · octobre 2026</span><span>{n:02d}</span></footer>' if num else ''
    body += f'<section class="page {cls}">{b}{foot}</section>\n'
out = os.path.join(BUILD, 'dossier.html')
open(out, 'w').write(f'<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>LE ONZE — Hôtel-jardin à Jacqueville</title><style>{CSS}</style></head><body>{body}</body></html>')
print('pages:', n, '->', out)
