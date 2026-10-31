"""Exterior composition, metres; proposed planting functions, not a species schedule."""
from shapely.geometry import Point, LineString, Polygon
from shapely.ops import unary_union
from project import *

# Continuous primary routes; stepping stones are deliberately not used here.
ROUTES = [
 ('P1','Entrée ouest / coursive',rect(.5,4,5.4,1.8)),
 ('P2','Entrée jardin / accueil / restaurant',rect(2.6,14.5,24.2,1.8)),
 ('P3','Seuil accueil',rect(24.65,13,1.4,1.5)),
 ('P4','Sortie noyau E1',rect(7,13,1.4,1.5)),
 ('P5','Restaurant / terrasse',rect(10,16.3,1.4,.7)),
 ('P6','Circuit service / massage / piscine',rect(22,16.3,1.8,9.2)),
 ('P7','Accès cuisine et réserve',rect(16.4,16.3,5.6,.7)),
 ('P8','Sortie E2 / aire de jeux',unary_union([rect(39.3,13,1.5,8),rect(36.2,19.4,4.6,1.5),rect(36.2,20.9,1.5,4.1)])),
 ('P9','Terrasse sud / piscine',rect(8,24,15.8,1.5)),
 ('P10','Plage piscine',POOL.buffer(1.0,join_style=2).difference(POOL)),
 ('P11','Jonction accueil / jeux',unary_union([rect(26.05,13,14.75,1.9),rect(26.05,14.8,1.8,1.5)])),
 ('P12','Accès soccer',rect(23.8,18.4,0.4,1.8)),
 ('P13','Dépose / entrée jardin',rect(5,16.3,2.5,.7)),
]
OBSTACLES=unary_union([HOTEL,PAVILION,POOL,SOCCER,FOOTPONG,STAIR2]+[p for n,p,c in EXTERIOR if c=='tech'])
ROUTES=[(i,n,p.intersection(SITE).difference(OBSTACLES)) for i,n,p in ROUTES]
PATHS=unary_union([p for i,n,p in ROUTES])
FREE=SITE.difference(unary_union([OBSTACLES,PATHS]+[p for n,p,c in EXTERIOR if c=='acces']))

ZONE_DEFS=[
 ('J1','Seuil ouest',Polygon([(0,0),(7,0),(6.5,-3.4),(.8,-3.4)]),'texture_couvre_sol','P01','Couvre-sol bas, vues d’entrée dégagées','Soleil présumé / passage exposé'),
 ('J2','Lisière de coursive',rect(9,.7,28,2.6),'texture_massif_tropical','P02','Massifs bas discontinus ; pas de haie opaque','Soleil / mi-ombre à vérifier'),
 ('J3','Jardin entre hôtel et restaurant',rect(8.8,13.2,13.6,1.15),'texture_couvre_sol','P03','Sous-strate basse face aux chambres','Ombre portée du R+1 à simuler'),
 ('J4','Lisière est',Polygon([(40,-4),(42,-4),(44,-22),(39.8,-22)]),'texture_massif_tropical','P04','Écran discontinu, ventilation et entretien','Exposition au vent à mesurer'),
 ('J5','Jardin de repos au sud',Polygon([(7,-29.1),(19.5,-29.1),(22.5,-27.2),(24,-29),(6.2,-31.2)]),'texture_couvre_sol','P05','Couvre-sol et clairières, surveillance du bassin','Ensoleillement / embruns à vérifier'),
 ('J6','Lisière des jeux',Polygon([(25,-26),(36,-26),(39,-25),(40,-25.8),(24,-28.3)]),'texture_massif_tropical','P06','Massif bas, aucune plante épineuse prescrite','Soleil présumé / usage actif'),
]
ZONES=[]
for zid,name,p,texture,pid,role,micro in ZONE_DEFS:
 p=p.intersection(FREE)
 # Leave alternating open soil at the long north edge, instead of a continuous fill.
 if zid=='J2':p=p.difference(unary_union([rect(16,0,2,4),rect(27,0,2.5,4)]))
 ZONES.append(dict(id=zid,name=name,poly=p,texture=texture,plant_id=pid,role=role,microclimate=micro))

# One repeated pair has the same shading role along the eastern edge. Symbols
# describe canopy envelopes only; no botanical variety is claimed from rotation.
CANOPIES=[dict(id='A01',zone='J1',x=3.2,y=-2.0,scale=.4,rotation=15,opacity=.9),
 dict(id='A02',zone='J4',x=41.0,y=-9.5,scale=.4,rotation=0,opacity=.55),
 dict(id='A03',zone='J4',x=42.3,y=-19.4,scale=.4,rotation=33,opacity=.60)]

def landscape_checks():
 errors=[]
 main=next(p for p in (PATHS.geoms if hasattr(PATHS,'geoms') else [PATHS]) if p.covers(Point(15,-15.4)))
 destinations={'accueil':(25.3,-13.4),'restaurant':(10.7,-16.8),'cuisine':(17.5,-16.8),'massage':(17.55,-24.5),'WC':(20.25,-24.5),'piscine':(8.5,-26.5),'foot_pong':(31.5,-14),'soccer':(23.95,-19),'E2_nord':(37.8,-14.4),'E2_sud':(37.5,-20)}
 for name,xy in destinations.items():
  if not main.covers(Point(*xy)):errors.append('Destination non reliée : '+name)
 for z in ZONES:
  if not SITE.buffer(1e-8).covers(z['poly']):errors.append(z['id']+' hors parcelle')
  if z['poly'].intersection(OBSTACLES.union(PATHS)).area>1e-7:errors.append(z['id']+' conflit emprise')
 for a in CANOPIES:
  # Conservative 3.02 m source-symbol radius; mature biological size remains unknown.
  envelope=Point(a['x'],a['y']).buffer(3.02*a['scale'])
  if not SITE.covers(envelope):errors.append(a['id']+' couronne hors parcelle')
  if envelope.intersection(PATHS.union(OBSTACLES)).area>1e-7:errors.append(a['id']+' conflit couronne dessinée')
 return dict(errors=errors,path_area_m2=round(PATHS.area,2),planting_area_m2=round(sum(z['poly'].area for z in ZONES),2),connected_destinations=list(destinations),mature_botanical_dimensions_validated=False)
