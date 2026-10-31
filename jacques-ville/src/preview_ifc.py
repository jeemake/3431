"""Deterministic axonometric previews tessellated from the delivered IFC."""
from pathlib import Path
import numpy as np
import ifcopenshell
import ifcopenshell.geom
from PIL import Image,ImageDraw,ImageFont

out=Path(__file__).resolve().parents[1]/'output'
f=ifcopenshell.open(str(out/'3431_JacquesVille_C-R1.ifc'))
settings=ifcopenshell.geom.settings();settings.set('use-world-coords',True)
right=np.array([.70710678,.70710678,0.]);up=np.array([-.408248,.408248,.816497]);view=np.cross(right,up)
light=np.array([-.3,-.4,.86]);light/=np.linalg.norm(light)
objects=[]
for e in f.by_type('IfcProduct'):
    if not e.Representation or e.is_a('IfcSpace') or e.is_a('IfcOpeningElement'):continue
    if 'FONDATION' in (e.Name or ''):continue
    shape=ifcopenshell.geom.create_shape(settings,e)
    v=np.array(shape.geometry.verts).reshape(-1,3);faces=np.array(shape.geometry.faces).reshape(-1,3)
    color={'IfcWall':(223,228,229),'IfcSlab':(180,193,197),'IfcDoor':(96,124,130),'IfcColumn':(159,178,183),'IfcRailing':(74,105,115),'IfcFurnishingElement':(220,229,231)}.get(e.is_a(),(130,172,156))
    name=e.Name or ''
    if 'Terrain' in name:color=(231,241,234)
    if 'Eau' in name:color=(67,154,188)
    if 'RESERVATION' in name:color=(126,186,203)
    if name.startswith(('E1','E2','Reserve')):color=(205,139,148)
    objects.append((name,v,faces,color))
all_v=np.vstack([v for n,v,faces,c in objects])
px=all_v@right;py=all_v@up
scale=min(1400/(px.max()-px.min()),760/(py.max()-py.min()))
cx=(px.min()+px.max())/2;cy=(py.min()+py.max())/2
fontpath=Path('C:/Windows/Fonts/arial.ttf')
font=ImageFont.truetype(str(fontpath),23);small=ImageFont.truetype(str(fontpath),17)
for cut in [False,True]:
    image=Image.new('RGB',(1600,1100),'white');draw=ImageDraw.Draw(image)
    canvas=np.full((1100,1600,3),255,dtype=np.uint8)
    zbuffer=np.full((1100,1600),-np.inf,dtype=np.float32)
    for name,v,faces,color in objects:
        if cut and name in ['Dalle 2','Pavillon toiture']:continue
        for face in faces:
            pts=v[face];norm=np.cross(pts[1]-pts[0],pts[2]-pts[0]);length=np.linalg.norm(norm)
            if length<1e-10:continue
            norm/=length
            if norm@view<-.01:continue
            shade=.72+.28*abs(norm@light)
            c=tuple(int(a*shade) for a in color)
            coords=[(800+(float(p@right)-cx)*scale,550-(float(p@up)-cy)*scale) for p in pts]
            xy=np.array(coords);zz=pts@view
            xmin=max(0,int(np.floor(xy[:,0].min())));xmax=min(1599,int(np.ceil(xy[:,0].max())))
            ymin=max(0,int(np.floor(xy[:,1].min())));ymax=min(1099,int(np.ceil(xy[:,1].max())))
            if xmin>xmax or ymin>ymax:continue
            x0,y0=xy[0];x1,y1=xy[1];x2,y2=xy[2]
            den=(y1-y2)*(x0-x2)+(x2-x1)*(y0-y2)
            if abs(den)<1e-8:continue
            gy,gx=np.mgrid[ymin:ymax+1,xmin:xmax+1]
            aa=((y1-y2)*(gx+.5-x2)+(x2-x1)*(gy+.5-y2))/den
            bb=((y2-y0)*(gx+.5-x2)+(x0-x2)*(gy+.5-y2))/den
            cc=1-aa-bb;depth=aa*zz[0]+bb*zz[1]+cc*zz[2]
            sub=zbuffer[ymin:ymax+1,xmin:xmax+1]
            mask=(aa>=-1e-6)&(bb>=-1e-6)&(cc>=-1e-6)&(depth>sub)
            sub[mask]=depth[mask];canvas[ymin:ymax+1,xmin:xmax+1][mask]=c
    image=Image.fromarray(canvas);draw=ImageDraw.Draw(image)
    draw.text((55,40),'3431 / JACQUES VILLE / VARIANTE C-R1',font=font,fill='#193a49')
    draw.text((55,80),'Axonometrie IFC - toitures retirees pour lecture' if cut else 'Axonometrie issue du fichier IFC4 livre',font=small,fill='#4a6672')
    draw.text((55,1015),'ESQUISSE : escaliers et fondations en reservation ; structure R+3 non calculee.',font=small,fill='#4a6672')
    image.save(out/('05_IFC_ecorche.png' if cut else '05_IFC_axonometrie.png'))
print('IFC previews generated')
