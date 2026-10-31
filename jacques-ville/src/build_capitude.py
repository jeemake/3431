"""A3 sheets: metric scales, verified Capitude blocks, pastel room overlays."""
import os,sys,json,re,csv,textwrap
from pathlib import Path
import xml.etree.ElementTree as ET
import fitz
from ezdxf.enums import TextEntityAlignment
from ezdxf.addons.drawing import Frontend,RenderContext,layout,svg,config
from ezdxf.math import BoundingBox2d
import ezdxf.path
from shapely.geometry import box,LineString
from shapely.ops import unary_union
from project import *
from landscape import *
LIB=Path(os.environ['ARCHIBOOKS_BLOCS']);sys.path.insert(0,str(LIB/'lib'))
import archibooks_blocs as ab
from archibooks_graphics import fill_texture_clipped,set_instance_opacity
BASE=Path(__file__).resolve().parents[1];OUT=BASE/'output';MM=72/25.4
PALETTE={'chambre':(242,229,216),'sde':(221,237,245),'sport':(224,239,222),'reunion':(232,225,242),'accueil':(246,236,207),'restaurant':(245,222,215),'service':(232,233,232),'massage':(243,224,236),'circulation':(247,246,240)}
LABELS=['Hébergement','Sanitaires','Sport','Réunion','Accueil','Restauration','Services','Massage','Circulations']
AUDIT=[];CLIPS=[];SCALES=[]
def category(s):return {'ACC':'accueil','SPORT':'sport','REUN':'reunion','BOH':'service'}.get(s['code'],s['category'])
def new():
 d=ab.nouveau_plan();d.styles.new('JV',dxfattribs={'font':'arial.ttf'})
 for n,w,g in [('SEEN',20,0),('CUT',40,0),('TEXT',13,0),('DIM',13,0),('RESERVE',13,75),('CONTEXT',13,120),('SITE',25,0)]:
  d.layers.add(n,lineweight=w);d.layers.get(n).rgb=(g,g,g)
 return d,d.modelspace()
def parts(p):return list(p.geoms) if hasattr(p,'geoms') and p.geom_type!='Polygon' else [p]
def poly(m,p,lay='SEEN',fill=None):
 for q in parts(p):
  if q.is_empty or q.geom_type!='Polygon':continue
  if fill is not None:
   color=PALETTE.get(fill,fill);name='FILL_'+str(fill)
   if name not in m.doc.layers:m.doc.layers.add(name)
   m.doc.layers.get(name).rgb=color
   h=m.add_hatch(color=256,dxfattribs={'layer':name});h.paths.add_polyline_path(list(q.exterior.coords),is_closed=True,flags=1)
   for ring in q.interiors:h.paths.add_polyline_path(list(ring.coords),is_closed=True,flags=0)
  if lay:
   m.add_lwpolyline(list(q.exterior.coords),close=True,dxfattribs={'layer':lay})
   for ring in q.interiors:m.add_lwpolyline(list(ring.coords),close=True,dxfattribs={'layer':lay})
def txt(m,s,x,y,h=.25,lay='TEXT'):
 t=m.add_text(s,dxfattribs={'height':h,'style':'JV','layer':lay});t.set_placement((x,y),align=TextEntityAlignment.MIDDLE_CENTER)
def line(m,a,b,lay='SEEN'):m.add_line(a,b,dxfattribs={'layer':lay})
def dim(m,a,b,y,label=None,h=.25):
 line(m,(a,y),(b,y),'DIM')
 for x in [a,b]:line(m,(x-.10,y-.12),(x+.10,y+.12),'DIM')
 txt(m,label or f'{b-a:.2f}',(a+b)/2,y+.32,h,'DIM')
def vdim(m,x,a,b,label=None,h=.25):
 line(m,(x,a),(x,b),'DIM')
 for y in [a,b]:line(m,(x-.12,y-.1),(x+.12,y+.1),'DIM')
 t=m.add_text(label or f'{b-a:.2f}',dxfattribs={'height':h,'style':'JV','layer':'DIM','rotation':90});t.set_placement((x-.3,(a+b)/2),align=TextEntityAlignment.MIDDLE_CENTER)
def reserve(m,p,label,h=.22):
 poly(m,p,'RESERVE');x,y=p.centroid.coords[0]
 if label in ['SAN*','MOB*']:y=p.bounds[3]-.3
 txt(m,label,x,y,h,'RESERVE')
def symbol(m,id,x,y,scale=1,rotation=0,opacity=1,width=13):
 ins=ab.place(m,id,x,y,scale=scale,rotation=rotation);set_instance_opacity(ins,opacity)
 def style(name):
  for e in m.doc.blocks.get(name):
   if e.dxftype()=='INSERT':style(e.dxf.name)
   else:
    g=(65 if opacity>.8 else 135) if id.startswith('arbre') else 0
    e.dxf.true_color=(g<<16)+(g<<8)+g;e.dxf.lineweight=width
 style(ins.dxf.name);return ins
def texture(m,id,p,opacity=.6):
 b=ab.bloc(id)
 for q in parts(p):
  if q.is_empty or q.geom_type!='Polygon':continue
  es=fill_texture_clipped(m,LIB/b['dxf'],b['nom_bloc'],list(q.exterior.coords),holes=[list(r.coords) for r in q.interiors],opacity=opacity)
  for i,e in enumerate(es):
   assert q.buffer(1e-7).covers(LineString(list(e.get_points('xy')))),id+' clip failed'
   e.dxf.true_color=0x606060;e.dxf.lineweight=9
   if i%3==0:m.delete_entity(e)  # lower texture density at 1:200, same module dimensions
  CLIPS.append(dict(texture=id,area_m2=round(q.area,3),segments=len(es),outside=0))
def water(m):
 # Flatten the authenticated source curves in a presentation copy, then clip.
 b=ab.bloc('texture_eau');src=ab.ezdxf.readfile(LIB/b['dxf']);count=0
 for ox in [9,11,13,15,17]:
  for oy in [-28,-26]:
   for e in src.blocks.get(b['nom_bloc']):
    if e.dxf.layer=='BLOC_CONTOUR':continue
    path=ezdxf.path.make_path(e);pts=[(v.x+ox,v.y+oy) for v in path.flattening(.005)]
    if len(pts)<2:continue
    clipped=LineString(pts).intersection(POOL)
    for seg in (clipped.geoms if hasattr(clipped,'geoms') else [clipped]):
     if seg.geom_type!='LineString' or seg.length<1e-7:continue
     assert POOL.buffer(1e-7).covers(seg)
     a=m.add_lwpolyline(list(seg.coords),dxfattribs={'layer':'CONTEXT','lineweight':9});a.transparency=.85;count+=1
 CLIPS.append(dict(texture='texture_eau',segments=count,outside=0,curve_tolerance_m=.005))
def rooms(m,lev,selection,labels=True,detail=False):
 ss=[s for s in SPACES if s['level']==lev and selection.intersection(s['poly']).area>.01]
 for s in ss:poly(m,s['poly'].intersection(selection),None,category(s))
 ds=[d for d in DOORS if d['level']==lev and selection.covers(box(d['x'],d['y'],d['x']+d['width'],d['y']+.2).centroid)]
 ws=[d for d in WINDOWS if d['level']==lev and selection.covers(box(d['x'],d['y'],d['x']+d['width'],d['y']+.2).centroid)]
 cuts=unary_union([box(d['x'],d['y']-.05,d['x']+d['width'],d['y']+.25) for d in ds+ws])
 for w in WALLS:
  if w['level']==lev and selection.intersects(w['poly']):poly(m,w['poly'].intersection(selection).difference(cuts),'CUT',(20,20,20))
 for d in ds:
  bath=d['name'].endswith('salle eau');flip=d['name'].endswith('entree') or d['name']=='Acces noyau' or bath
  symbol(m,'porte_double' if d['kind']=='double' else 'porte_battante_90',d['x']+(d['width'] if flip else 0),d['y']+((.1 if bath else .2) if flip else 0),scale=d['width']/(1.4 if d['kind']=='double' else .9),rotation=180 if flip else 0,opacity=.85,width=15)
 for d in ws:
  line(m,(d['x'],d['y']+.1),(d['x']+d['width'],d['y']+.1),'RESERVE');txt(m,'F*',d['x']+d['width']/2,d['y']-.3,.20,'RESERVE')
 for mk in MARKERS:
  if mk['level']!=lev or selection.intersection(mk['poly']).area<.01:continue
  n=mk['name'];short=next((s for prefix,s in [('E1','E1*'),('E2','E2*'),('Reserve','EL*'),('LIT','LIT*'),('PL','PL*'),('SAN','SAN*')] if n.startswith(prefix)),'MOB*')
  if short=='SAN*' and not detail:continue
  reserve(m,mk['poly'],short,.16 if detail else .22)
 if labels:
  for s in ss:
   code=s['code'];x,y=s['poly'].centroid.coords[0]
   if code.startswith(('CORE','PASS')):continue
   if code.startswith('GAL'):txt(m,'COURSIVE OUVERTE  1,80 m',22,-4.8,.27);continue
   if s['category']=='chambre':y=-11.85
   if '-SDE' in code:
    txt(m,'SDE',x,y+.12,.22);txt(m,'4,40 m²',x,y-.22,.20);continue
   if code=='REST':y=-17.6
   if code in ['CUIS','RES']:y=-19.35
   if code in ['MASS','WC']:y=-22.6
   txt(m,code,x,y+.16,.27);txt(m,f"{s['poly'].area:.2f} m²".replace('.',','),x,y-.22,.21)
def mass_doc(garden=False):
 d,m=new();poly(m,POOL,None,(240,240,240));water(m)
 for z in ZONES:texture(m,z['texture'],z['poly'],.6 if z['texture']=='texture_couvre_sol' else .65)
 texture(m,'texture_pierre_bandes',dict((i,p) for i,n,p in ROUTES)['P9'],.65)
 for i,n,p in ROUTES:poly(m,p,'CONTEXT')
 for a in CANOPIES:symbol(m,'arbre_feuillage_dense',a['x'],a['y'],a['scale'],a['rotation'],a['opacity'],13)
 poly(m,HOTEL,'SEEN','chambre');poly(m,PAVILION,'SEEN','restaurant');poly(m,STAIR2,'RESERVE')
 for n,p,c in EXTERIOR:poly(m,p,'SEEN')
 poly(m,SITE,'SITE')
 for k,(x,y) in BOUNDARY.items():txt(m,k,x+.4,y+.5,.4)
 x,y=43,-1.8;tip=(x+S*2,y+C*2);line(m,(x,y),tip,'DIM')
 line(m,tip,(tip[0]-.18,tip[1]-.4),'DIM');line(m,tip,(tip[0]+.23,tip[1]-.36),'DIM');txt(m,'N',tip[0],tip[1]+.6,.45)
 for s,x,y in [('HÔTEL R+1 / 12 CLÉS',22,-8),('4 au RDC + 8 au R+1',22,-9.2),('RESTAURANT',14.7,-19.4),('Cuisine / massage / WC',14.7,-20.6),('SOCCER CAGE',30.2,-21.4),('12 x 7 m / loisir',30.2,-22.5),('FOOT PONG',31.5,-16.1),('6 x 3,5 m',31.5,-17.2),('PISCINE / 25 m²',14,-26.7),('E2*',37.9,-17.3),('TECH.',3.8,-8),('DÉPOSE',6.2,-20.5)]:txt(m,s,x,y,.43 if len(s)<24 else .38)
 txt(m,'ENTRÉE',1.9,-13.7,.4);txt(m,'ACCUEIL',25.6,-12,.4)
 if garden:
  for z in ZONES:
   x,y=z['poly'].representative_point().coords[0]
   if z['id']=='J1':x,y=5.5,-2
   poly(m,box(x-.45,y-.3,x+.45,y+.3),None,(255,255,255));txt(m,z['id'],x,y,.45)
  for s,x,y in [('P1',3.4,-4.9),('P2',16,-15.4),('P6',22.9,-20.5),('P9',13,-24.7),('P8',38.3,-22.5)]:txt(m,s,x,y,.35)
 dim(m,5.9,38.3,1.4,'32,40 m',.4);txt(m,'1 120 m² déclarés / 1 120,27 m² calculés',24,-32.8,.42)
 return d
def floor_doc(lev):
 d,m=new();rooms(m,lev,HOTEL.buffer(.01))
 if lev==1:
  for s in SPACES:
   if s['code'].startswith('PASS'):poly(m,s['poly'],'SEEN','circulation')
 reserve(m,STAIR2,'E2*');dim(m,5.9,38.3,-1.5,'32,40 m / 9 travées')
 for i in range(9):dim(m,5.9+i*3.6,9.5+i*3.6,-2.7,'3,60')
 vdim(m,4.9,-13,-4,'9,00');vdim(m,40.1,-5.8,-4,'1,80')
 if lev==0:
  for i,n,p in ROUTES:
   if i in ['P3','P4']:poly(m,p,'CONTEXT')
  txt(m,'SORTIE JARDIN',7.7,-14.1,.22);txt(m,'ACCÈS ACCUEIL',25.35,-14.1,.22)
 return d
def pavilion_doc():
 d,m=new();rooms(m,0,PAVILION.buffer(.01));dim(m,8,22,-15.6,'14,00 m');vdim(m,23,-24,-17,'7,00')
 for a,b in [(8.2,16.2),(16.35,19),(19.15,21.8)]:dim(m,a,b,-25)
 return d
def unit_doc():
 d,m=new();rooms(m,0,rect(9.5,4,3.6,9).buffer(.01),False,True)
 txt(m,'CHAMBRE TYPE',11.4,-11.8,.15);txt(m,'22,69 m² nets avec SDE',11.4,-12.05,.13);txt(m,'SDE 4,40 m²',10.7,-7.4,.14)
 dim(m,9.7,13.1,-13.8,'3,40 m',.13);vdim(m,14,-12.8,-6,'6,80 m',.13);dim(m,9.7,11.7,-5.45,'2,00 m',.13)
 return d
def section_doc():
 d,m=new()
 for z in [0,3.3,6.6]:poly(m,box(0,z-.2,32.4,z),'CUT',(20,20,20))
 for x in [i*3.6 for i in range(10)]:poly(m,box(x,0,x+.2,6.4),'CUT',(20,20,20))
 for z in [0,3.3,6.6]:txt(m,f'+{z:.2f}',-1.5,z,.27,'DIM')
 for i in range(9):txt(m,'NOYAU' if i==0 else 'CH'+str(i+4).zfill(2),1.8+i*3.6,4.8,.24)
 for z in [9.9,13.2]:
  for x in range(33):line(m,(x,z),(min(x+.5,32.4),z),'RESERVE')
  txt(m,'R+2 FUTUR' if z==9.9 else 'R+3 FUTUR',16,z-.7,.3,'RESERVE')
 txt(m,'GABARITS FUTURS / NON CONSTRUITS',16,14.15,.3);txt(m,'FONDATIONS À DIMENSIONNER POUR R+3 PAR LE BET',16,-1.1,.27)
 dim(m,0,32.4,-2.1,'32,40 m');return d
def render(d,name,bounds,scale):
 xmin,ymin,xmax,ymax=bounds;wm=(xmax-xmin)*1000/scale;hm=(ymax-ymin)*1000/scale
 audit=d.audit();assert not audit.errors,(name,audit.errors)
 AUDIT.append(dict(name=name,errors=len(audit.errors),fixes=len(audit.fixes)));d.saveas(OUT/(name+'.dxf'))
 backend=svg.SVGBackend();cfg=config.Configuration(background_policy=config.BackgroundPolicy.WHITE,lineweight_policy=config.LineweightPolicy.ABSOLUTE)
 Frontend(RenderContext(d),backend,config=cfg).draw_layout(d.modelspace(),finalize=True)
 s=backend.get_string(layout.Page(wm,hm),settings=layout.Settings(fit_page=False,scale=1000/scale),render_box=BoundingBox2d([(xmin,ymin),(xmax,ymax)]))
 root=ET.fromstring(s);styles={}
 for st in root.iter('{http://www.w3.org/2000/svg}style'):
  for cls,rules in re.findall(r'\.([\w]+)\s*\{([^}]+)\}',st.text or ''):styles[cls]=dict(pair.strip().split(':',1) for pair in rules.split(';') if ':' in pair)
 for el in root.iter():
  for cls in el.attrib.get('class','').split():
   for k,v in styles.get(cls,{}).items():el.set(k,v.strip())
 ET.register_namespace('','http://www.w3.org/2000/svg');path=OUT/(name+'.svg');ET.ElementTree(root).write(path,encoding='utf-8',xml_declaration=True)
 sd=fitz.open(path);pd=fitz.open('pdf',sd.convert_to_pdf());sd.close();assert abs(pd[0].rect.width/MM-wm)<.03
 pd[0].get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(OUT/(name+'.png'))
 SCALES.append(dict(name=name,scale=scale,bounds_m=bounds,width_mm=wm,height_mm=hm,lineweights_mm=[.40,.20,.15,.13,.09]));return pd
def t(p,x,y,s,size=10,color=0,bold=False):p.insert_text((x*MM,y*MM),s,fontsize=size,color=(color,)*3,fontname='hebo' if bold else 'helv')
def para(p,x,y,s,width=90,size=10,leading=4.8):
 for a in textwrap.wrap(s,width=width):t(p,x,y,a,size,.25);y+=leading
 return y+3
def base(pdf,num,title,subtitle,scale=''):
 p=pdf.new_page(width=420*MM,height=297*MM);t(p,14,14,'KOFFI & DIABATE / JACQUES VILLE / DOSSIER 3431',9)
 t(p,14,29,title,22,bold=True);t(p,14,38,subtitle,10,.3)
 for y in [43,277]:p.draw_line((14*MM,y*MM),(406*MM,y*MM),color=(0,)*3,width=.6)
 t(p,14,285,'C-R1 / RÉVISION B / 31.10.2026 / ESQUISSE NON EXÉCUTOIRE',9);t(p,259,285,scale,9);t(p,395,285,f'{num:02}',11)
 return p
def chart(p,d,name,bounds,scale,x,y):
 q=render(d,name,bounds,scale);r=q[0].rect;p.show_pdf_page(fitz.Rect(x*MM,y*MM,x*MM+r.width,y*MM+r.height),q,0);q.close()
def scale_bar(p,x,y,scale,length=5):
 mm=length*1000/scale;p.draw_line((x*MM,y*MM),((x+mm)*MM,y*MM),color=(0,)*3,width=1)
 for k in range(length+1):
  xx=x+k*1000/scale;p.draw_line((xx*MM,y*MM),(xx*MM,(y-1.5)*MM),color=(0,)*3,width=.5)
 t(p,x,y+5,'0',8);t(p,x+mm-4,y+5,f'{length} m',8)
def legend(p,x=17,y=251):
 for i,((key,rgb),label_) in enumerate(zip(PALETTE.items(),LABELS)):
  xx=x+(i%5)*77;yy=y+(i//5)*8;c=tuple(v/255 for v in rgb)
  p.draw_rect(fitz.Rect(xx*MM,(yy-3)*MM,(xx+5)*MM,(yy+1)*MM),color=(.4,)*3,fill=c,width=.3);t(p,xx+8,yy,label_,8.5)
def save(pdf,name,prefix):
 pdf.save(OUT/name,garbage=4,deflate=True)
 for i,p in enumerate(pdf):p.get_pixmap(matrix=fitz.Matrix(1.2,1.2)).save(OUT/f'{prefix}_{i+1:02}.png')
 pdf.close()

pdf=fitz.open()
p=base(pdf,1,'01 / Implantation et programme','Terrain intégralement affecté au projet : 1 120 m². R+1 et 12 unités.','A3 / 1:200 / imprimer à 100 %')
chart(p,mass_doc(),'01_Masse',(-2,-34.5,47,3),200,14,54);y=60
for h,s in [('UN HÔTEL COMPACT','Une barre R+1 de 32,40 x 9,00 m et un pavillon de 14,00 x 7,00 m.'),('PROGRAMME CONSERVÉ','Piscine, restaurant, sport, réunion, soccer cage et foot pong. Massage compact. Supérette et spa complet supprimés.'),('SEUILS CLARIFIÉS','Accueil ouvert sur le jardin ; sortie E1 au sud ; foot pong décalé pour dégager l’arrivée.'),('PRÉPARER LE R+3','Volumes futurs exclus de la phase construite. Structure et fondations à calculer pour les charges futures.'),('ÉTAT DE L’ÉTUDE','Accès ouest repris du dossier source. Reculs, dépose, stationnement, sécurité et accessibilité à confirmer.')]:
 t(p,276,y,h,11,bold=True);y=para(p,276,y+7,s,57,10)+6
scale_bar(p,35,251,200);t(p,100,253,'Nord calculé depuis les coordonnées du dépôt.',9)
for lev in [0,1]:
 p=base(pdf,lev+2,'02 / Rez-de-chaussée - hôtel' if lev==0 else '03 / Premier étage - hôtel','Aplats pastel par usage. Surfaces nettes ; cotes en mètres.','A3 / 1:100 / imprimer à 100 %')
 chart(p,floor_doc(lev),'02_RDC' if lev==0 else '03_R1',(4,-19.5,41,0),100,23,48)
 t(p,23,238,'4 chambres + accueil, sport, réunion et office.' if lev==0 else '8 chambres. Salles d’eau superposées à celles du RDC.',10)
 legend(p);t(p,235,238,'* Réservations : escaliers, élévateur, fenêtres et mobilier à compléter.',8.5)
p=base(pdf,4,'04 / Pavillon et chambre type','Restaurant, cuisine, réserve, massage et sanitaires. Chambre de 22,69 m² nets.','A3 / échelles indiquées')
chart(p,pavilion_doc(),'04_Pavillon',(7,-26,24,-15),100,20,59);t(p,20,180,'PAVILLON / 1:100',11,bold=True);scale_bar(p,20,188,100)
chart(p,unit_doc(),'05_Chambre_type',(9.1,-14.5,14.6,-3.8),50,255,48);t(p,255,267,'CHAMBRE TYPE / 1:50',11,bold=True)
para(p,20,210,'Restaurant : 52,80 m² nets, cible 28 couverts. Cuisine et réserve : 8,61 m² chacune. Massage et WC : 8,48 m² chacun. Implantation du mobilier à développer avec les blocs manquants.',83)
para(p,20,239,'F*, LIT*, PL*, SAN*, MOB* : repères neutres. Aucun équipement absent du catalogue n’est présenté comme une famille validée. Le détail n’est pas une chambre PMR validée.',83)
p=base(pdf,5,'05 / Jardin, seuils et parcours','Arrivée, lisières, jardin calme, terrasse, eau et jeux.','A3 / 1:200 / imprimer à 100 %')
chart(p,mass_doc(True),'06_Paysage',(-2,-34.5,47,3),200,14,54);y=60
for z in ZONES:
 t(p,276,y,z['id']+' / '+z['name'].upper(),10,bold=True);y=para(p,276,y+6,z['role']+'.',58,9.5,4.5)+3
para(p,276,221,'P1 : coursive. P2 : arrivée / accueil. P6 : service. P8 : jeux / sortie E2. P9 : terrasse / bassin.',58,9.5)
scale_bar(p,35,251,200);t(p,100,253,'Plantations projetées. Espèces et dimensions adultes à valider.',9)
p=base(pdf,6,'06 / Coupe de principe et évolution','RDC +0,00 / R+1 +3,30 / toiture +6,60. Deux niveaux futurs à étudier.','A3 / 1:100 / imprimer à 100 %')
chart(p,section_doc(),'07_Coupe',(-2.5,-3,34.5,15),100,23,51)
para(p,23,244,'Schéma longitudinal de trame, sans détail d’exécution. R+2 et R+3 sont des gabarits futurs. Fondations, contreventement et sections porteuses restent à dimensionner par le BET après étude de sol.',155);scale_bar(p,23,267,100)
save(pdf,'3431_Plans_Capitude_RevB.pdf','apercu')

notice=fitz.open()
p=base(notice,1,'Notice / Programme, surfaces et budget','Complément aux six planches - révision B')
rows=[('Terrain déclaré / calculé','1 120,00 / 1 120,27 m²'),('Hôtel : enveloppe par niveau','291,60 m²'),('Pavillon RDC','98,00 m²'),('Enveloppes de planchers (2 hôtel + pavillon)','681,20 m²'),('Passerelle + palier E2 supplémentaires','15,24 m²'),('12 unités, chacune avec salle d’eau','22,69 m² nets / unité'),('Restaurant / cible de capacité','52,80 m² / 28 couverts'),('Sport / réunion / accueil / office','23,12 m² nets chacun'),('Massage / sanitaires publics','8,48 m² nets chacun'),('Piscine / soccer cage / foot pong','25 / 84 / 21 m²')]
y=60
for a,b in rows:
 t(p,18,y,a,11);t(p,230,y,b,11);p.draw_line((18*MM,(y+3)*MM),(400*MM,(y+3)*MM),color=(.85,)*3,width=.4);y+=12
y=190
for s in ['Budget client : 250 à 300 M F CFA, honoraires compris. Compatibilité non démontrée à ce stade.','Allocation cible à 300 M : bâtiment 171 ; adaptation R+3 18 ; loisirs 16 ; VRD/jardin 24 ; équipements 24 ; honoraires/études 22 ; aléas 25 M F CFA. Ce sont des plafonds, pas des devis.','Le ratio historique du dépôt (477 279 F CFA/m²) donnerait environ 325 M sur 681,20 m² avant plusieurs postes. Comparaison indicative : ratio de SU et enveloppe brute ne sont pas équivalents. Un métré et des offres locales sont nécessaires.','Standing : 12 chambres compactes, sans suites premium ni loggias privatives. Matériaux, confort, acoustique et services à valider avec le client. Foncier et futurs niveaux R+2/R+3 exclus de l’allocation.']:y=para(p,18,y,s,160,10,4.7)
p=base(notice,2,'Notice / Composition paysagère','Diagnostic explicite, usages et critères de choix. Aucune espèce botanique n’est prescrite.');y=58
for h,s in [('SITE ET INCONNUES','Jacqueville selon le dossier. Limite ouest donnée comme voie dans geo_source.py ; contour issu du levé repris dans le dépôt. Climat mesuré, vents, salinité, sol, infiltration, niveaux, réseaux et végétation existante : non documentés. Aucune mesure ni essence existante n’est inventée.'),('PARTI DE COMPOSITION','Arrivée lisible, passage continu devant le restaurant, plantations basses face aux chambres, lisières discontinues. Les espaces libres restent respirants, sans remplissage uniforme de la parcelle. Les trois couronnes sont des intentions d’ombrage, dont une paire répétée à l’est.'),('PARCOURS AVANT PLANTATIONS','P1 relie la limite ouest à la coursive (1,80 m proposé). P2 dessert jardin, accueil et restaurant. P3 et P4 desservent les portes ajoutées. P6 et P9 rejoignent cuisine, massage, WC et piscine ; P8 relie E2 et les jeux. Les chambres rejoignent le jardin par les circulations communes.'),('MATÉRIAUX ET EAU','Passages continus à revêtement stable à définir ; pierre en bandes proposée sur la terrasse sud. Piscine distincte des massifs. Aucun jardin de pluie sans étude hydraulique. Niveaux, pentes, drainage, antidérapance et protection du bassin à développer.'),('ENTRETIEN ET MATURITÉ','Besoins d’arrosage à estimer après choix des plantes et analyse d’eau. Vérifier racines, feuilles près du bassin, visibilité, accès aux réseaux et volume adulte. Les couronnes dessinées sont contrôlées sans conflit d’emprise ; elles ne prouvent pas le gabarit biologique futur.'),('RÉFÉRENCES ADAPTÉES','Primaveras p.132/138 : strates, parcours, seuils et hiérarchie de dessin. Candela p.152 : terrasse/piscine et lisière discontinue. Burle Marx, Ng Sek San et Damian Tang : synthèses de la règle Capitude, appliquées comme principes. Le cercle d’El Tecuan n’est pas imposé à cette parcelle.')]:
 t(p,18,y,h,11,bold=True);y=para(p,18,y+7,s,159,10,4.7)+4
p=base(notice,3,'Notice / Palette fonctionnelle et légende','Table de plantation provisoire à confirmer avec un paysagiste local.');y=56
for z in ZONES:
 t(p,18,y,f"{z['id']} / {z['plant_id']} / {z['name']} - {z['poly'].area:.1f} m²",11,bold=True)
 y=para(p,18,y+6,f"Usage / strate : {z['role']}. Milieu : {z['microclimate']}. Fonction provisoire ; espèce, hauteur et étalement adultes : non renseignés. Nappes discontinues ; quantité et espacement après choix d’essence. Eau / entretien : à qualifier, accès manuel maintenu.",160,9.5,4.3)+2
para(p,18,237,'A01 (J1) : accent d’entrée ; A02-A03 (J4) : paire d’ombrage de lisière. Bloc arbre_feuillage_dense, échelle 0,40 ; couronne graphique environ 2,2 x 2,3 m. Trois sujets projetés, fonctions provisoires ; gabarit adulte inconnu. Opacités : 90 / 55 / 60 %. La rotation ne représente pas une diversité botanique.',160,9.5,4.3)
para(p,18,259,'P01/P03/P05 = texture_couvre_sol (60 %) ; P02/P04/P06 = texture_massif_tropical (65 %). Sources : catalogue Capitude v1 et composition révision B. Tous les végétaux représentés sont projetés.',160,9,4)
p=base(notice,4,'Notice / Sources et points à résoudre','Traçabilité Capitude et limites du dossier');y=58
for r in json.loads((BASE/'references/regles_capitude_2026-10-31.json').read_text(encoding='utf-8')):
 t(p,18,y,f"{r['code']} / v{r['version']} / {r['maj_le'][:10]}",10);y+=7
for s in ['Règles et catalogue lus dans Supabase capitude via MCP autorisé. Cache des blocs vérifié par SHA-256 ; références vérifiées par SHA-256 du manifeste, taille et ETag Storage live. Primaveras p.132/138 et Candela p.152 ouvertes visuellement. Images privées non republiées dans le dépôt.','Dérogation demandée par Jean Marc : aplats pastel par usage à l’intérieur des pièces. Murs, cotes et textes noirs ; jardin et textures en gris. Coupé 0,40 mm ; vu 0,20 mm ; portes 0,15 mm ; repères 0,13 mm ; textures 0,09 mm.','À compléter avec Jean Marc / Stéphanie : escalier droit E1/E2, élévateur EL, fenêtres, lits, placards et mobilier restaurant, sport, massage. Les contours étoilés sont des réservations neutres, pas des composants exécutables.','Avant validation : accès et stationnement, évacuation/incendie, accessibilité et chambre adaptée, dégagements sportifs, garde-corps et piscine, autonomie technique, logistique, acoustique, ventilation. Avant travaux : permis, levé authentifié, géotechnique, BET R+3 et chiffrage.','Impression : A3 paysage, taille réelle 100 %, sans ajuster à la page. Masse/paysage au 1:200 ; niveaux/pavillon/coupe au 1:100 ; chambre au 1:50. Les échelles graphiques permettent le contrôle d’une copie imprimée.']:
 y=para(p,18,y+4,s,160,10,4.7)
save(notice,'3431_Notice_Capitude_RevB.pdf','notice')
lc=landscape_checks();assert not lc['errors'],lc
with (OUT/'surfaces.csv').open('w',encoding='utf-8-sig',newline='') as h:
 rows=schedule();w=csv.DictWriter(h,fieldnames=rows[0].keys(),delimiter=';');w.writeheader();w.writerows(rows)
(OUT/'verification_plans_RevB.json').write_text(json.dumps(dict(geometry=check(),landscape=lc,dxf_audits=AUDIT,strict_texture_clips=CLIPS,scales=SCALES,pastel_override='Demande utilisateur explicite, 31.10.2026'),ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(pages_plans=6,pages_notice=4,landscape=lc,dxf=AUDIT),ensure_ascii=False))
