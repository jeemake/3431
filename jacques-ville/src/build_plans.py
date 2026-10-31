import os,sys,json,csv,textwrap,re
import xml.etree.ElementTree as ET
from pathlib import Path
import fitz
from shapely.geometry import box,Polygon
from shapely.ops import unary_union
from ezdxf.enums import TextEntityAlignment
from ezdxf import colors
from project import *
sys.path.insert(0,str(Path(os.environ['ARCHIBOOKS_BLOCS'])/'lib'))
import archibooks_blocs as ab

OUT=Path(__file__).resolve().parents[1]/'output';OUT.mkdir(exist_ok=True)
PALETTE={'mur':(28,45,53),'chambre':(226,239,241),'sde':(214,233,240),'circulation':(239,243,245),'commun':(235,240,232),'restaurant':(229,238,230),'service':(236,238,240),'massage':(238,230,240)}
def lay(doc,n,col):
    if n not in doc.layers:doc.layers.add(n)
    doc.layers.get(n).rgb=col
def poly(m,p,layer='CONTOUR',fill=None):
    if p.is_empty:return
    if p.geom_type=='MultiPolygon':
        for a in p.geoms:poly(m,a,layer,fill)
        return
    pts=list(p.exterior.coords)
    if fill:
        n='FILL_'+fill;lay(m.doc,n,PALETTE[fill]);h=m.add_hatch(color=256,dxfattribs={'layer':n});h.paths.add_polyline_path(pts,is_closed=True)
    m.add_lwpolyline(pts,close=True,dxfattribs={'layer':layer})
def txt(m,s,x,y,h=.25,layer='TEXT',align='center'):
    t=m.add_text(s,dxfattribs={'height':h,'layer':layer,'style':'JV'})
    t.set_placement((x,y),align=TextEntityAlignment.MIDDLE_CENTER if align=='center' else TextEntityAlignment.MIDDLE_LEFT)
def new():
    doc=ab.nouveau_plan();doc.styles.new('JV',dxfattribs={'font':'arial.ttf'})
    for n,c in [('CONTOUR',(80,100,108)),('TEXT',(25,48,60)),('MURS',(25,40,48)),('RESERVES',(174,65,83)),('COTES',(38,109,144)),('AXES',(130,140,150))]:lay(doc,n,c)
    return doc,doc.modelspace()
def dim(m,x1,x2,y,label):
    m.add_line((x1,y),(x2,y),dxfattribs={'layer':'COTES'})
    for x in [x1,x2]:m.add_line((x-.12,y-.15),(x+.12,y+.15),dxfattribs={'layer':'COTES'})
    txt(m,label,(x1+x2)/2,y+.35,.25,'COTES')
def finish(doc,name):
    # Preserve catalogue block geometry; adjust line colors only in the composed drawing.
    for layer in doc.layers:
        if layer.dxf.name.startswith('BLOC_'):layer.rgb=(95,114,120)
    doc.saveas(OUT/(name+'.dxf'));ab.to_svg(doc,str(OUT/(name+'.svg')))
    # MuPDF's SVG importer does not resolve CSS classes: inline the exact styles.
    path=OUT/(name+'.svg');tree=ET.parse(path);root=tree.getroot();css={}
    for st in root.iter('{http://www.w3.org/2000/svg}style'):
        for cls,rules in re.findall(r'\.([\w]+)\s*\{([^}]+)\}',st.text or ''):
            css[cls]=dict(pair.strip().split(':',1) for pair in rules.split(';') if ':' in pair)
    for el in root.iter():
        for cls in el.attrib.get('class','').split():
            for k,v in css.get(cls,{}).items():el.set(k,v.strip())
    vb=list(map(float,root.attrib['viewBox'].split()))
    wm=float(root.attrib['width'].replace('mm',''));hm=float(root.attrib['height'].replace('mm',''))
    px=vb[2]*9/wm;py=vb[3]*9/hm
    root.set('viewBox',f'{vb[0]+px} {vb[1]+py} {vb[2]-2*px} {vb[3]-2*py}')
    root.set('width',f'{wm-18}mm');root.set('height',f'{hm-18}mm')
    ET.register_namespace('','http://www.w3.org/2000/svg');tree.write(path,encoding='utf-8',xml_declaration=True)
    svg=fitz.open(path);pdf=fitz.open('pdf',svg.convert_to_pdf())
    page=pdf[0]
    pix=page.get_pixmap(matrix=fitz.Matrix(10,10));pix.save(OUT/(name+'.png'))
    return pdf
def map_base(m):
    poly(m,SITE)
    for k,(x,y) in BOUNDARY.items():txt(m,k,x+.4,y+.5,.3)
    # True north relative to the plan axes.
    x,y=2,-10;dx,dy=S,C
    m.add_line((x,y),(x+dx*2,y+dy*2),dxfattribs={'layer':'COTES'})
    txt(m,'N',x+dx*2,y+dy*2+.5,.4,'COTES')
    dim(m,8,13,-31,'5 m')
def floor(level):
    doc,m=new();map_base(m)
    spaces=[s for s in SPACES if s['level']==level]
    for s in spaces:poly(m,s['poly'],fill=s['category'])
    cuts=[box(d['x'],d['y']-.05,d['x']+d['width'],d['y']+.25) for d in DOORS if d['level']==level]
    cuts += [box(d['x'],d['y']-.05,d['x']+d['width'],d['y']+.25) for d in WINDOWS if d['level']==level]
    for w in WALLS:
        if w['level']==level:poly(m,w['poly'].difference(unary_union(cuts)),'MURS','mur')
    for d in DOORS:
        if d['level']!=level:continue
        bid='porte_double' if d['kind']=='double' else 'porte_battante_90'
        scale=d['width']/(1.4 if d['kind']=='double' else .9)
        bath=d['name'].endswith('salle eau')
        flip=d['name'].endswith('entree') or d['name']=='Acces noyau' or bath
        ab.place(m,bid,d['x']+(d['width'] if flip else 0),d['y']+((.1 if bath else .2) if flip else 0),scale=scale,rotation=180 if flip else 0)
    for d in WINDOWS:
        if d['level']==level:
            m.add_line((d['x'],d['y']+.1),(d['x']+d['width'],d['y']+.1),dxfattribs={'layer':'RESERVES'})
            txt(m,'F?',d['x']+d['width']/2,d['y']-.3,.18,'RESERVES')
    for s in spaces:
        p=s['poly'];x,y=p.centroid.coords[0]
        if s['category']=='chambre':x=(p.bounds[0]+p.bounds[2])/2;y=-8.8
        if s['code'].startswith(('GAL','CORE','PASS')):continue
        txt(m,s['code'],x,y+.15,.26)
        txt(m,f"{p.area:.1f} m2",x,y-.25,.21)
    for mk in MARKERS:
        if mk['level']!=level:continue
        p=mk['poly'];poly(m,p,'RESERVES')
        x,y=p.centroid.coords[0]
        short='E1 ?' if mk['name'].startswith('E1') else 'E2 ?' if mk['name'].startswith('E2') else 'EL ?' if mk['name'].startswith('Reserve') else mk['name'].split(' ')[0]+' ?'
        if short.startswith('SAN'):continue
        labely=y if short.startswith(('E1','E2','EL','LIT','PL')) else p.bounds[1]+.25
        txt(m,short,x,labely,.19,'RESERVES')
    txt(m,'COURSIVE OUVERTE - 1.80 m',22,-4.85,.3)
    dim(m,5.9,38.3,1.8,'32.40 m = 9 travees de 3.60 m')
    for i in range(9):dim(m,5.9+i*3.6,9.5+i*3.6,.7,'3.60')
    if level==0:
        for n,p,c in EXTERIOR:
            poly(m,p)
            x,y=p.centroid.coords[0]
            short={'eau':'PISCINE 25 m2','tech':'TECH 12 m2','acces':'DEPOSE','sport':('SOCCER 84 m2' if 'Soccer' in n else 'FOOT PONG 21 m2')}[c]
            if c=='eau':ab.fill_texture(m,'texture_eau',list(p.exterior.coords)[:-1])
            txt(m,short,x,y,.28)
        for x,v,scale in TREES:ab.place(m,'arbre_feuillage_dense',x,-v,scale=scale)
        ab.fill_texture(m,'texture_paves',(8,-16.3,21.5,-15.2))
        txt(m,'JARDIN / CHEMINEMENTS',14,-14.2,.28)
    else:
        poly(m,PAVILION);txt(m,'TOIT PAVILLON RDC',15,-20.5,.35)
        txt(m,'PASSERELLE E2',38.9,-15.3,.18,'RESERVES')
    return finish(doc,'02_RDC' if level==0 else '03_R1')
def mass():
    doc,m=new();map_base(m)
    poly(m,HOTEL,fill='chambre');poly(m,PAVILION,fill='restaurant');poly(m,STAIR2,'RESERVES')
    txt(m,'HEBERGEMENT R+1 - 12 CLES',22,-8,.5)
    txt(m,'4 au RDC / 8 au R+1',22,-9,.35)
    txt(m,'PAVILLON RESTAURANT',15,-19.5,.35)
    txt(m,'Cuisine + massage + sanitaires',15,-20.3,.27)
    for n,p,c in EXTERIOR:
        poly(m,p)
        if c=='eau':ab.fill_texture(m,'texture_eau',list(p.exterior.coords)[:-1])
        x,y=p.centroid.coords[0]
        if c=='sport':
            txt(m,'SOCCER CAGE' if 'Soccer' in n else 'FOOT PONG',x,y+.3,.3)
            txt(m,'12 x 7 m - loisir' if 'Soccer' in n else '6 x 3.5 m - reserve',x,y-.25,.25)
        else:txt(m,{'eau':'PISCINE 25 m2','tech':'TECH.','acces':'DEPOSE'}[c],x,y,.28)
    for x,v,scale in TREES:ab.place(m,'arbre_feuillage_dense',x,-v,scale=scale)
    ab.fill_texture(m,'texture_paves',(8,-16.3,21.5,-15.2))
    dim(m,5.9,38.3,1.5,'32.40 m')
    txt(m,'ACCES OUEST',2.7,-15.8,.3,'COTES')
    txt(m,'1 120 m2 declares / 1 120.27 m2 calcules',21,-30.3,.35)
    return finish(doc,'01_Masse')
def section():
    doc,m=new()
    for z in [0,3.3,6.6]:poly(m,box(0,z-.2,32.4,z),'MURS','mur')
    for x in [i*3.6 for i in range(10)]:poly(m,box(x,0,x+.2,6.4),'MURS','mur')
    for z in [0,3.3,6.6]:txt(m,f'+{z:.2f}',-1.6,z,.3,'COTES')
    for i in range(9):
        txt(m,'NOYAU' if i==0 else ('CH'+str(i+4).zfill(2)),1.8+i*3.6,4.7,.25)
    for z in [9.9,13.2]:
        m.add_line((0,z),(32.4,z),dxfattribs={'layer':'RESERVES'})
        txt(m,'R+2 FUTUR' if z==9.9 else 'R+3 FUTUR',16,z-.7,.4,'RESERVES')
    txt(m,'VOLUMES FUTURS INDICATIFS - NON CONSTRUITS / NON DIMENSIONNES',16,14.2,.35,'RESERVES')
    txt(m,'Toiture technique non accessible au public',16,7.2,.35)
    txt(m,'FONDATIONS : ETUDE GEOTECHNIQUE + CALCUL R+3 REQUIS',16,-1.5,.35,'RESERVES')
    dim(m,0,32.4,-2.5,'32.40 m')
    return finish(doc,'04_Coupe')

pdf=fitz.open();W,H=1190.55,841.89
blue=(.10,.23,.29);grey=(.32,.4,.45)
def text(page,x,y,s,size=11,col=blue):page.insert_text((x,y),s,fontsize=size,color=col,fontname='helv')
def base(num,title,subtitle):
    p=pdf.new_page(width=W,height=H)
    text(p,45,42,'KOFFI & DIABATE  /  DOSSIER 3431',11)
    text(p,45,80,title,25)
    text(p,45,104,subtitle,11,grey)
    p.draw_line((45,119),(1145,119),color=blue,width=.7)
    text(p,45,814,'JACQUES VILLE  |  C-R1  |  31.10.2026  |  ESQUISSE - NON EXECUTOIRE',10,grey)
    text(p,1115,814,f'{num:02d}',10)
    return p
def note(p,title,lines):
    x=875;y=160;text(p,x,y,title,14);y+=28
    for para in lines:
        for line in textwrap.wrap(para,40):text(p,x,y,line,10.5,grey);y+=15
        y+=13
charts=[mass(),floor(0),floor(1),section()]
titles=['01 / Une cour pour douze cles','02 / Rez-de-chaussee','03 / Premier etage','04 / Coupe et evolution']
notes=[
 ['Terrain source du depot : lot 2511, ilot 225. Coordonnees reprises sans deformation.', 'Hotel : 32.40 x 9.00 m. Pavillon : 14.00 x 7.00 m.', 'Soccer cage de loisir : 84 m2. Format compact, non terrain de competition.', 'Foot pong : emprise de 21 m2. Degagements a confirmer selon equipement.', 'Depose et livraison uniquement. Stationnement client reste a resoudre.', 'Reculs proposes, non reglementaires. Extension R+3 conditionnee au droit a construire.'],
 ['CH01 a CH04 : 4 cles. Chaque unite : 22.69 m2 nets, salle d eau de 4.40 m2 incluse.', 'ACC : accueil / lounge, 23.12 m2. SPORT : 23.12 m2. REUN : 23.12 m2.', 'BOH : lingerie / office / personnel, 23.12 m2. Organisation a detailler.', 'REST : 52.80 m2, cible 28 couverts. CUIS : 8.61 m2. RES : 8.61 m2.', 'MASS : 8.48 m2. WC : 8.48 m2.', 'Rouge : reperes neutres pour blocs manquants. Portes, arbres et eau : blocs Archibooks.'],
 ['CH05 a CH12 : 8 cles de 22.69 m2 nets chacune.', 'Coursive : 1.80 m de large. Passerelle est vers E2 : 1.20 m.', 'E1 et E2 : emprises reservees. Les escaliers droits ne sont pas dessines : bloc absent.', 'EL : reserve indicative, dimensions et accessibilite a reprendre avec le fournisseur.', 'F? : baie de fenetre, sans bloc correspondant. LIT?, PL?, SAN? : reperes identifies.', 'Le nombre de sorties, les paliers et le desenfumage doivent etre valides en APS.'],
 ['RDC : +0.00. R+1 : +3.30. Toiture : +6.60.', 'R+2 / R+3 : volumes de principe uniquement, exclus du modele construit.', 'Trame repetee de 3.60 m ; gaines sanitaires superposees.', 'Poteaux de 30 x 30 cm : gabarits indicatifs, pas des sections calculees.', 'Fondations : zones reservees dans IFC, pas de semelles dimensionnees.', 'Etude sol, charges futures, vent, stabilite, corrosion littorale et fondations a traiter par le BET.']]
for i,(chart,title,lines) in enumerate(zip(charts,titles,notes),1):
    p=base(i,title,'Variante C recomposee en R+1 - toutes les cotes sont en metres')
    p.show_pdf_page(fitz.Rect(38,135,850,780),chart,0,keep_proportion=True)
    note(p,'LECTURE DU PLAN',lines)
    chart.close()
p=base(5,'05 / Surfaces et arbitrages','12 unites retenues - le standing reste un objectif qualitatif a confirmer')
rows=[('Terrain declare','1 120.00 m2'),('Emprise hotel','291.60 m2'),('Pavillon RDC','98.00 m2'),('Enveloppes de planchers (2 hotel + pavillon)','681.20 m2'),('Passerelle et palier E2 supplementaires','13.44 m2'),('Hebergement net (12 x 22.69)','272.28 m2'),('Restaurant net / cible de capacite','52.80 m2 / 28 couverts'),('Massage compact net','8.48 m2'),('Piscine / soccer cage / foot pong','25 / 84 / 21 m2')]
y=165
for a,b in rows:
    text(p,55,y,a,13);text(p,660,y,b,13);p.draw_line((55,y+10),(1100,y+10),color=(.85,.89,.9));y+=39
for j,s in enumerate(['La superette et le spa complet sont supprimes.','Les 15 cles ne sont pas retenues : elles augmenteraient les surfaces ou reduiraient les chambres.','Pas de suite premium ni de loggia privative dans cette variante compacte : standing a valider avec le client.','Accessibilite, stationnement, vestiaires du personnel et traitement acoustique restent a developper.','Les surfaces de plancher ci-dessus sont des enveloppes geometriques, pas des surfaces reglementaires.']):text(p,55,570+j*32,s,12,grey)
p=base(6,'06 / Enveloppe financiere','Objectif de 250 a 300 M F CFA, honoraires compris - faisabilite non acquise')
text(p,55,163,'ALLOCATION CIBLE AU PLAFOND DE 300 M',15)
budget=[('Batiment R+1 + pavillon, lots techniques et finitions',171),('Provision adaptation structure / fondations au R+3',18),('Piscine + soccer cage + foot pong',16),('VRD, assainissement, eau, energie, cloture, jardin',24),('Equipements cuisine et mobilier hotelier',24),('Honoraires et etudes',22),('Aleas et ajustements',25)]
y=203
for a,b in budget:text(p,55,y,a,12);text(p,775,y,f'{b:.0f} M F CFA',12);y+=34
text(p,55,458,'TOTAL CIBLE : 300 M F CFA',18)
lines=['Ces montants sont des plafonds a consulter, pas des devis ni un estimatif valide. Ils ne certifient pas le maintien du standing.', 'Enveloppe tous debours recherchee : fiscalite, assurances, raccordements et inclusions fournisseurs a preciser par Mr Adicko. Foncier non compte ; R+2/R+3 futurs exclus.', 'Alerte : le seul ratio historique du depot (477 279 F CFA/m2, deja divise par deux) applique aux 681.20 m2 donne environ 325 M F CFA avant plusieurs autres postes. Comparaison indicative : le ratio historique porte sur la SU, non sur cette enveloppe brute.', 'Il faut donc un chiffrage metrique et des offres locales avant de conclure a la compatibilite avec 300 M. Le seuil de 250 M n est pas demontre.', 'Sources : brief du 31.10.2026 ; ancienne option C du depot ; regles_agents et design_patterns de Supabase capitude ; blocs DWG Archibooks convertis en DXF avec AutoCAD 2023.']
y=500
for para in lines:
    for line in textwrap.wrap(para,135):text(p,55,y,line,11,grey);y+=16
    y+=12
pdf.save(OUT/'3431_Plans_C-R1.pdf',garbage=4,deflate=True)
for i,page in enumerate(pdf):page.get_pixmap(matrix=fitz.Matrix(1.2,1.2)).save(OUT/f'apercu_{i+1:02d}.png')
pdf.close()
with (OUT/'surfaces.csv').open('w',encoding='utf-8-sig',newline='') as h:
    rows=schedule();writer=csv.DictWriter(h,fieldnames=rows[0].keys(),delimiter=';');writer.writeheader();writer.writerows(rows)
print(json.dumps(check(),ensure_ascii=True,indent=2))
