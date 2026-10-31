"""Single geometry source, metres. X along B1-B2, Y inward-negative.
Design proposals are not surveyed or engineered construction dimensions.
"""
import math
from shapely.geometry import Polygon, box
from geo_source import BORNES

E0,N0=BORNES['B1']
ANGLE=math.atan2(BORNES['B2'][1]-N0,BORNES['B2'][0]-E0)
C,S=math.cos(ANGLE),math.sin(ANGLE)
def local(e,n):
    return ((e-E0)*C+(n-N0)*S,-(e-E0)*S+(n-N0)*C)
SITE=Polygon([local(*BORNES[k]) for k in ['B1','B4','B3','B2']])
BOUNDARY={k:local(*v) for k,v in BORNES.items()}
def rect(u,v,w,d): return box(u,-v-d,u+w,-v)
HOTEL=rect(5.9,4,32.4,9)
PAVILION=rect(8,17,14,7)
POOL=rect(9,25.5,10,2.5)
SOCCER=rect(24.2,18.4,12,7)
FOOTPONG=rect(28.5,14.9,6,3.5)
STAIR2=rect(36.5,14.9,2.8,4.5)
SPACES=[]
DOORS=[]
WINDOWS=[]
WALLS=[]
MARKERS=[]
def room(code,name,level,u,v,w,d,category,unit=None):
    p=rect(u,v,w,d)
    SPACES.append(dict(code=code,name=name,level=level,poly=p,category=category,unit=unit))
    return p
def wall(name,level,x,y,w,d):
    WALLS.append(dict(name=name,level=level,poly=box(x,y,x+w,y+d)))
def door(name,level,x,y,width=.9,axis='x',kind='single'):
    DOORS.append(dict(name=name,level=level,x=x,y=y,width=width,axis=axis,kind=kind))
def marker(name,level,u,v,w,d):
    MARKERS.append(dict(name=name,level=level,poly=rect(u,v,w,d)))

# Nine structural bays; first bay is the vertical circulation core.
for lev in [0,1]:
    wall('Facade jardin',lev,5.9,-13,32.4,.2)
    wall('Facade coursive',lev,5.9,-6,32.4,.2)
    for i in range(10): wall('Refend / pignon',lev,5.9+3.6*i,-12.8,.2,6.8)
    room(f'GAL{lev}','Coursive ouverte 1.80 m',lev,5.9,4,32.4,1.8,'circulation')
    room(f'CORE{lev}','Noyau escalier / palier',lev,6.1,6,3.4,6.8,'circulation')
    marker('E1 : escalier a deux volees - bloc manquant',lev,6.3,7.4,2.8,4.8)
    marker('Reserve elevateur - a etudier',lev,6.3,6.1,1.8,1.2)
    door('Acces noyau',lev,8.4,-6)
    for bay in range(1,9):
        u=5.9+bay*3.6+.2
        is_unit=lev==1 or bay<=4
        code=f'CH{bay if lev==0 else bay+4:02d}' if is_unit else ['ACC','SPORT','REUN','BOH'][bay-5]
        name=code if is_unit else {'ACC':'Accueil / lounge','SPORT':'Salle de sport','REUN':'Salle de reunion','BOH':'Lingerie / office / personnel'}[code]
        if is_unit:
            # Net room footprint excludes internal bathroom partition.
            bathw=2.0
            bath=room(code+'-SDE','Salle eau',lev,u,6,2,2.2,'sde',code)
            main=rect(u,6,3.4,6.8).difference(rect(u,6,2.1,2.3))
            SPACES.append(dict(code=code,name=name,level=lev,poly=main,category='chambre',unit=code))
            wall('Cloison SdE',lev,u,-8.3,2.1,.1)
            wall('Cloison SdE',lev,u+2,-8.3,.1,2.3)
            door(code+' salle eau',lev,u+.45,-8.3,.8)
            marker('LIT - bloc 2D absent',lev,u+.6,9.3,1.8,2.0)
            marker('PL - bloc 2D absent',lev,u+2.65,6.8,.55,1.4)
            marker('SAN - familles IFC',lev,u+.15,6.15,1.7,1.9)
        else:
            room(code,name,lev,u,6,3.4,6.8,'commun')
        door(code+' entree',lev,u+2.35,-6,.9)
        if code=='ACC':
            door('Accueil jardin',lev,u+.55,-13,1.4,kind='double')
        else:
            WINDOWS.append(dict(name=code+' baie',level=lev,x=u+.55,y=-13,width=2.1))

door('Sortie noyau jardin',0,7.0,-13,1.4,kind='double')

# Restaurant, compact massage, kitchen, public facilities.
for x,y,w,d in [(8,-24,14,.2),(8,-17.2,14,.2),(8,-23.8,.2,6.6),(21.8,-23.8,.2,6.6)]:wall('Pavillon',0,x,y,w,d)
for u in [16.2,19.0]:wall('Pavillon refend',0,u,-23.8,.15,6.6)
wall('Pavillon refend',0,16.35,-20.6,5.45,.15)
room('REST','Restaurant 28 couverts',0,8.2,17.2,8,6.6,'restaurant')
room('CUIS','Cuisine / plonge',0,16.35,17.2,2.65,3.25,'service')
room('RES','Reserve / froid',0,19.15,17.2,2.65,3.25,'service')
room('MASS','Massage compact',0,16.35,20.6,2.65,3.2,'massage')
room('WC','Sanitaires publics',0,19.15,20.6,2.65,3.2,'sde')
for name,x,y,width in [('Restaurant',10,-17.2,1.4),('Cuisine',17.1,-17.2,.9),('Reserve',19.8,-17.2,.9),('Massage',17.1,-24,.9),('WC',19.8,-24,.9)]:door(name,0,x,y,width,kind='double' if width>1 else 'single')
marker('Mobilier restaurant - blocs 2D absents',0,9,18.2,6.4,4.3)
marker('Table massage - bloc absent',0,16.9,21.2,1,2)
marker('Equipement cuisine - bloc 2D absent',0,16.7,17.6,1.9,2.4)
marker('WC / lave-mains - detail a completer',0,19.55,21,1.9,2.3)
for lev in [0,1]:MARKERS.append(dict(name='E2 secours - bloc manquant',level=lev,poly=STAIR2))

EXTERIOR=[('Piscine 10 x 2.5 m',POOL,'eau'),('Soccer cage loisir 12 x 7 m',SOCCER,'sport'),('Foot pong - emprise reservee 6 x 3.5 m',FOOTPONG,'sport'),('Local technique',rect(2.3,6,3,4),'tech'),('Depose / livraison',rect(5,17,2.5,8),'acces')]
room('PASS1','Passerelle vers E2',1,38.3,4,1.2,10.9,'circulation')
room('PASS2','Palier E2',1,36.5,13.7,1.8,1.2,'circulation')
TREES=[(3,3,.5),(12,2,.45),(22,2,.45),(32,2,.45),(22.7,27,.4),(5.8,28,.45)]
def schedule():
    return [dict(code=s['code'],name=s['name'],level=s['level'],category=s['category'],unit=s['unit'],area_m2=round(s['poly'].area,2)) for s in SPACES]
def check():
    errors=[]
    for name,p in [('Hotel',HOTEL),('Pavillon',PAVILION),('E2',STAIR2)]+[(n,p) for n,p,c in EXTERIOR]:
        if not SITE.buffer(.001).covers(p):errors.append(name+' outside site')
    for i,a in enumerate(SPACES):
        if not SITE.buffer(.001).covers(a['poly']):errors.append(a['code']+' outside site')
        for b in SPACES[i+1:]:
            if a['level']==b['level'] and a['poly'].intersection(b['poly']).area>1e-7:errors.append(a['code']+' overlap '+b['code'])
    units=sorted({s['unit'] for s in SPACES if s['unit']})
    assert len(units)==12
    return dict(site_declared_m2=1120,site_from_source_coordinates_m2=round(SITE.area,3),hotel_floor_envelope_m2=HOTEL.area,pavilion_envelope_m2=PAVILION.area,total_floor_envelope_m2=2*HOTEL.area+PAVILION.area,units=units,errors=errors)
