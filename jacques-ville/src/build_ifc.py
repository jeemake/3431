"""IFC4 architectural concept model; no claim of structural adequacy."""
import os,json,hashlib,uuid
from pathlib import Path
import numpy as np
import ifcopenshell as ios
import ifcopenshell.api as api
import ifcopenshell.geom
import ifcopenshell.validate
from shapely.geometry import box
from project import *

OUT=Path(__file__).resolve().parents[1]/'output'
OUT.mkdir(exist_ok=True)
f=ios.file(schema='IFC4')
def root(cls,name):return api.run('root.create_entity',f,ifc_class=cls,name=name)
project=root('IfcProject','3431 - Jacques Ville - C-R1 - 31 octobre 2026')
api.run('unit.assign_unit',f,units=[api.run('unit.add_si_unit',f,unit_type='LENGTHUNIT'),api.run('unit.add_si_unit',f,unit_type='AREAUNIT'),api.run('unit.add_si_unit',f,unit_type='VOLUMEUNIT')])
ctx=api.run('context.add_context',f,context_type='Model')
body=api.run('context.add_context',f,context_type='Model',context_identifier='Body',target_view='MODEL_VIEW',parent=ctx)
ctx.TrueNorth=f.createIfcDirection((float(S),float(C)))
site=root('IfcSite','Lot 2511 - ilot 225 - 1120 m2 declares')
building=root('IfcBuilding','Le Jardin du Onze - R+1')
api.run('aggregate.assign_object',f,products=[site],relating_object=project)
api.run('aggregate.assign_object',f,products=[building],relating_object=site)
storeys={}
for k,z,n in [(0,0.,'RDC'),(1,3.3,'R+1'),(2,6.6,'Toiture technique - non occupee')]:
    st=root('IfcBuildingStorey',n);st.Elevation=z
    api.run('aggregate.assign_object',f,products=[st],relating_object=building)
    storeys[k]=st
def props(e,name,data):
    p=api.run('pset.add_pset',f,product=e,name=name)
    api.run('pset.edit_pset',f,pset=p,properties=data)
props(project,'JV_Brief',dict(DateRevision='2026-10-31',Terrain_m2=1120.,Unites=12,NiveauxRealises='R+1',Evolution='R+3 a dimensionner par BET',BudgetMinFCFA=250000000.,BudgetMaxFCFA=300000000.,HonorairesInclus=True,BudgetValide=False,Statut='ESQUISSE - NE PAS UTILISER POUR EXECUTION'))
props(site,'JV_Origine',dict(Source='geo.py branche claude/great-gates-cp292d - leve source a verifier',Coordonnees='UTM 30N, selon fichier source; datum a confirmer',OrigineE=E0,OrigineN=N0,RotationDeg=math.degrees(ANGLE),SurfaceCalculee=SITE.area))
props(building,'JV_Limites',dict(Structure='Sections indicatives; etude sol, BET et stabilite R+3 non realises',Escaliers='Reservations E1/E2 sans marches: blocs droits absents',Accessibilite='Non validee; chambre adaptee et elevateur a reprendre en APS',SecuriteIncendie='Non validee; deux reservations de sorties a verifier'))
def placement(e,x=0.,y=0.,z=0.):
    m=np.eye(4);m[:3,3]=[x,y,z];api.run('geometry.edit_object_placement',f,product=e,matrix=m,is_si=True)
def shape(e,poly,z,h,color=None):
    coords=[(float(x),float(y)) for x,y in list(poly.exterior.coords)]
    curve=f.createIfcPolyline([f.createIfcCartesianPoint(p) for p in coords])
    profile=f.createIfcArbitraryClosedProfileDef('AREA',None,curve)
    solid=f.createIfcExtrudedAreaSolid(profile,f.createIfcAxis2Placement3D(f.createIfcCartesianPoint((0.,0.,float(z))),None,None),f.createIfcDirection((0.,0.,1.)),float(h))
    rep=f.createIfcShapeRepresentation(body,'Body','SweptSolid',[solid])
    e.Representation=f.createIfcProductDefinitionShape(None,None,[rep])
    placement(e)
    if color:
        style=api.run('style.add_style',f,name=e.is_a()+' style')
        api.run('style.add_surface_style',f,style=style,attributes={'SurfaceColour':dict(zip(['Red','Green','Blue'],color)),'Transparency':0.0})
        api.run('style.assign_representation_styles',f,shape_representation=rep,styles=[style])
    return e
def element(cls,name,poly,z,h,level=0,color=None):
    e=root(cls,name);shape(e,poly,z,h,color)
    api.run('spatial.assign_container',f,products=[e],relating_structure=storeys[level])
    return e
element('IfcBuildingElementProxy','Terrain - limite source',SITE,-.25,.05,color=(.85,.9,.86))
for lev in [0,1,2]:
    slab=element('IfcSlab','Dalle '+str(lev),HOTEL,lev*3.3-.2,.2,lev,(.76,.79,.8));slab.PredefinedType='ROOF' if lev==2 else 'FLOOR'
    if lev==1:
        op=root('IfcOpeningElement','Tremie E1');shape(op,rect(6.3,7.4,2.8,4.8),3.0,.6)
        f.createIfcRelVoidsElement(ios.guid.new(),None,None,None,slab,op)
element('IfcSlab','Pavillon sol',PAVILION,-.2,.2,color=(.8,.82,.83))
element('IfcSlab','Pavillon toiture',PAVILION,3.1,.2,color=(.77,.79,.8))
walls=[]
for w in WALLS:
    e=element('IfcWall',w['name'],w['poly'],w['level']*3.3,3.1,w['level'],(.94,.94,.93));walls.append((w,e))
for d in DOORS:
    x,y,width=d['x'],d['y'],d['width'];lev=d['level'];poly=box(x,y-.04,x+width,y+.24)
    candidates=[(w,e) for w,e in walls if w['level']==lev and w['poly'].intersection(poly).area>.02]
    if not candidates:raise ValueError('Door without wall '+d['name'])
    host=max(candidates,key=lambda t:t[0]['poly'].intersection(poly).area)[1]
    op=root('IfcOpeningElement','Baie porte '+d['name']);shape(op,poly,lev*3.3,2.2)
    f.createIfcRelVoidsElement(ios.guid.new(),None,None,None,host,op)
    e=element('IfcDoor',d['name'],box(x,y+.06,x+width,y+.10),lev*3.3,2.2,lev,(.35,.43,.44));e.OverallWidth=float(width);e.OverallHeight=2.2
    f.createIfcRelFillsElement(ios.guid.new(),None,None,None,op,e)
    props(e,'JV_Representation',{'Type':'Vantail schematique; famille PB1D1 non adaptee a la baie de 0.90 m'})
for d in WINDOWS:
    lev=d['level'];x,y,w=d['x'],d['y'],d['width'];poly=box(x,y-.05,x+w,y+.25)
    host=next(e for a,e in walls if a['level']==lev and a['name']=='Facade jardin')
    op=root('IfcOpeningElement',d['name']);shape(op,poly,lev*3.3+.8,1.7)
    f.createIfcRelVoidsElement(ios.guid.new(),None,None,None,host,op)
    e=element('IfcBuildingElementProxy','RESERVATION MENUISERIE '+d['name'],box(x,y+.09,x+w,y+.11),lev*3.3+.8,1.7,lev,(.4,.7,.8))
    props(e,'JV_Representation',{'Type':'Repere neutre - famille de fenetre correspondante absente'})
for s in SPACES:
    e=root('IfcSpace',s['code']);e.LongName=s['name'];e.PredefinedType='INTERNAL' if s['category']!='circulation' else 'NOTDEFINED'
    shape(e,s['poly'],s['level']*3.3,3.1)
    api.run('aggregate.assign_object',f,products=[e],relating_object=storeys[s['level']])
    props(e,'JV_Programme',dict(Code=s['code'],Unite=s['unit'] or '',Fonction=s['category'],SurfaceNette_m2=round(s['poly'].area,3)))
    q=api.run('pset.add_qto',f,product=e,name='Qto_SpaceBaseQuantities');api.run('pset.edit_qto',f,qto=q,properties={'NetFloorArea':s['poly'].area,'NetVolume':s['poly'].area*3.1,'Height':3.1})
for i in range(10):
    for v in [6.,12.8]:
        x=6.+3.6*i
        for lev in [0,1]:
            e=element('IfcColumn','Poteau indicatif 30x30',rect(x-.15,v-.15,.3,.3),lev*3.3,3.1,lev,(.63,.67,.69))
            props(e,'JV_Structure',{'Statut':'Section non calculee; dimensionnement R+3 requis'})
        e=element('IfcBuildingElementProxy','ZONE FONDATION A DIMENSIONNER',rect(x-.6,v-.6,1.2,1.2),-.8,.3,0,(.74,.55,.6))
        props(e,'JV_Structure',{'Statut':'Emprise indicative, ni semelle calculee ni profondeur geotechnique'})
for m in MARKERS:
    if m['name'].startswith(('E1','E2','Reserve')):
        e=element('IfcBuildingElementProxy',m['name'],m['poly'],m['level']*3.3,.04,m['level'],(.85,.4,.35))
        props(e,'JV_Representation',{'Type':'Reservation uniquement - objet manquant au catalogue'})
# Guardrails are architectural continuous safety envelopes, not engineered details.
for y in [-4.04,-13.05]:element('IfcRailing','Garde-corps enveloppe indicative',box(5.9,y,38.3,y+.05),3.3,1.1,1,(.3,.4,.43))
element('IfcSlab','Passerelle est vers E2',rect(38.3,4,1.2,10.4),3.1,.2,1,(.7,.74,.76))
element('IfcSlab','Palier E2',rect(37.5,13.2,.8,1.2),3.1,.2,1,(.7,.74,.76))
element('IfcRailing','Garde-corps passerelle est',rect(39.45,4,.05,10.4),3.3,1.1,1,(.3,.4,.43))
for n,p,c in EXTERIOR:
    if c=='eau':
        element('IfcSlab','Fond de bassin indicatif',p,-1.4,.2,color=(.35,.7,.78))
        element('IfcBuildingElementProxy','Eau piscine',p,-.1,.02,color=(.35,.68,.85))
        b=p.bounds
        for q in [box(b[0]-.2,b[1]-.2,b[2]+.2,b[1]),box(b[0]-.2,b[3],b[2]+.2,b[3]+.2),box(b[0]-.2,b[1],b[0],b[3]),box(b[2],b[1],b[2]+.2,b[3])]:element('IfcWall','Paroi bassin indicative',q,-1.4,1.4,color=(.75,.82,.85))
    else:element('IfcBuildingElementProxy',n,p,0,.05,color=(.63,.8,.72))

# Reuse authenticated local copies of Capitude families, verify checksums.
lib=Path(os.environ['CAPITUDE_IFC_LIBRARY'])
catalog=json.loads((lib/'catalogue.json').read_text(encoding='utf-8'))
manifest=[];mesh_cache={}
for code in ['RDF-IFC-WC-SUSPENDU','RDF-IFC-MEUBLE-VASQUE','RDF-IFC-DOUCHE']:
    item=next(a for a in catalog['families'] if a['code']==code)
    path=lib/'ifc'/Path(item['file_path']).name
    assert hashlib.sha256(path.read_bytes()).hexdigest()==item['sha256']
    source=ios.open(str(path));setting=ios.geom.settings();setting.set('use-world-coords',False)
    obj=next(a for a in source.by_type('IfcElement') if a.Representation)
    shp=ios.geom.create_shape(setting,obj)
    vertices=np.array(shp.geometry.verts).reshape(-1,3);faces=np.array(shp.geometry.faces).reshape(-1,3)
    # Explicit insertion: local bounding-box lower-left; z bottom raised per fixture.
    anchor=vertices.min(axis=0);vertices-=anchor
    rep=api.run('geometry.add_mesh_representation',f,context=body,vertices=[vertices.tolist()],faces=[faces.tolist()])
    mesh_cache[code]=(rep,vertices.max(axis=0))
    import ifcopenshell.util.placement
    manifest.append(dict(code=code,version=item['version'],sha256=item['sha256'],family_id=item['family_id'],source_anchor_m=anchor.tolist(),source_placement_declared_units=ios.util.placement.get_local_placement(obj.ObjectPlacement).tolist(),size_m=vertices.max(axis=0).tolist(),insertion='minimum local bbox; mesh already in metres'))
for s in SPACES:
    if not s['unit'] or s['category']!='sde':continue
    x,y,x1,y1=s['poly'].bounds;lev=s['level']
    for code,dx,dy,dz in [('RDF-IFC-MEUBLE-VASQUE',.10,1.5,.45),('RDF-IFC-WC-SUSPENDU',.1,.1,0),('RDF-IFC-DOUCHE',1.25,.15,.67)]:
        rep,size=mesh_cache[code]
        e=root('IfcFurnishingElement',code+' '+s['unit']);e.Representation=f.createIfcProductDefinitionShape(None,None,[rep]);placement(e,x+dx,y+dy,lev*3.3+dz)
        api.run('spatial.assign_container',f,products=[e],relating_structure=storeys[lev])
        props(e,'JV_SourceCapitude',{'Code':code,'Version':1,'SourceSHA256':next(a['sha256'] for a in manifest if a['code']==code)})

# Stable identifiers make regenerated models reviewable in Git / BIM comparisons.
seen={}
for e in f.by_type('IfcRoot'):
    key=f'{e.is_a()}|{e.Name or ""}';num=seen.get(key,0);seen[key]=num+1
    e.GlobalId=ios.guid.compress(uuid.uuid5(uuid.NAMESPACE_URL,'3431-C-R1|'+key+'|'+str(num)).hex)
path=OUT/'3431_JacquesVille_C-R1.ifc';f.write(str(path))
(OUT/'familles_utilisees.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
reopened=ios.open(str(path));logger=ios.validate.json_logger();ios.validate.validate(reopened,logger)
errors=logger.statements
settings=ios.geom.settings();failed=[];count=0
for e in reopened.by_type('IfcProduct'):
    if e.Representation:
        try:ios.geom.create_shape(settings,e);count+=1
        except Exception as ex:failed.append(dict(id=e.id(),name=e.Name,error=str(ex)))
report=check();report.update(ifc_schema=reopened.schema,ifc_entities=len(list(reopened)),represented_products_checked=count,schema_errors=[str(a) for a in errors],geometry_errors=failed,scope='Schema et tessellation; pas de validation structure, incendie, accessibilite, budget ni collisions exhaustives')
(OUT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=True,indent=2))
assert not report['errors'] and not errors and not failed
